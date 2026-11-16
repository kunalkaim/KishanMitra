import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
import joblib

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

# Feature-aware minimum dispersion bandwidths to ensure numerical stability
# without distorting narrow-range variables like pH (where std is naturally 0.2 - 0.5)
MIN_FEATURE_BANDWIDTH = {
    'N': 1.0,
    'P': 1.0,
    'K': 1.0,
    'temperature': 0.5,
    'humidity': 1.0,
    'ph': 0.15,
    'rainfall': 2.0
}


class AgronomicFuzzyCropExpert:
    """
    Expert 1: Data-Derived Fuzzy Crop Suitability Inference Engine.
    Constructs continuous empirical compatibility profiles fitted exclusively on the training split.
    
    For each candidate crop c and feature j, a continuous smooth trapezoidal/Gaussian membership 
    function mu_{c,j}(x_j) in [0, 1] measures data-derived agronomic compatibility against observed
    empirical distribution bounds (15th - 85th percentiles of training samples).
    
    Note: These represent observed empirical compatibility bounds from training data,
    not scientifically verified universal agronomic invariants.
    """
    def __init__(self, name: str = "AgronomicFuzzyExpert_v1.1"):
        self.name = name
        self.classes_: List[str] = []
        self.crop_profiles_: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.global_linguistic_bounds_: Dict[str, Dict[str, float]] = {}
        self.feature_weights_: Dict[str, float] = {
            'N': 1.0,
            'P': 1.0,
            'K': 1.0,
            'temperature': 1.2,
            'humidity': 1.1,
            'ph': 1.1,
            'rainfall': 1.3
        }
        self.is_fitted = False

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        Derives empirical fuzzy membership profiles for every crop class
        from the training split using medians, standard deviations, and empirical quantile bounds.
        """
        self.classes_ = sorted(list(y_train.unique()))
        df = X_train[FEATURE_NAMES].copy()
        df['target'] = y_train.values

        # 1. Establish global linguistic distribution bounds
        for feat in FEATURE_NAMES:
            q25 = float(df[feat].quantile(0.25))
            q50 = float(df[feat].quantile(0.50))
            q75 = float(df[feat].quantile(0.75))
            self.global_linguistic_bounds_[feat] = {
                "low_threshold": q25,
                "medium_threshold": q50,
                "high_threshold": q75
            }

        # 2. Derive crop-specific empirical compatibility profiles
        self.crop_profiles_ = {}
        for crop in self.classes_:
            crop_df = df[df['target'] == crop]
            self.crop_profiles_[crop] = {}
            for feat in FEATURE_NAMES:
                mean_val = float(crop_df[feat].mean())
                std_val = float(crop_df[feat].std())
                min_bw = MIN_FEATURE_BANDWIDTH.get(feat, 0.5)
                if std_val < min_bw:
                    std_val = min_bw
                min_val = float(crop_df[feat].min())
                max_val = float(crop_df[feat].max())
                q1_val = float(crop_df[feat].quantile(0.15))
                q3_val = float(crop_df[feat].quantile(0.85))

                self.crop_profiles_[crop][feat] = {
                    "mean": mean_val,
                    "std": std_val,
                    "min": min_val,
                    "max": max_val,
                    "observed_compat_lower": q1_val,
                    "observed_compat_upper": q3_val,
                    # Backward-compatibility aliases
                    "optimal_low": q1_val,
                    "optimal_high": q3_val
                }

        self.is_fitted = True
        return self

    def _compute_feature_membership(self, x_val: float, profile: Dict[str, float], feat_name: str) -> float:
        """
        Calculates data-derived continuous membership degree mu(x) in [0, 1] using
        smooth Gaussian roll-off outside empirical compatibility bounds.
        """
        if np.isnan(x_val) or np.isinf(x_val):
            return 0.0

        compat_low = profile.get("observed_compat_lower", profile.get("optimal_low", 0.0))
        compat_high = profile.get("observed_compat_upper", profile.get("optimal_high", 0.0))
        
        # Minimum bandwidth scaling to prevent over-steep roll-off
        min_bw = MIN_FEATURE_BANDWIDTH.get(feat_name, 0.5)
        std = max(min_bw, profile.get("std", min_bw))
        
        # In observed compatibility plateau: full compatibility 1.0
        if compat_low <= x_val <= compat_high:
            return 1.0
        
        # Smooth exponential roll-off outside plateau
        if x_val < compat_low:
            diff = (compat_low - x_val) / (1.5 * std)
            raw_mu = float(np.exp(-0.5 * (diff ** 2)))
        else:
            diff = (x_val - compat_high) / (1.5 * std)
            raw_mu = float(np.exp(-0.5 * (diff ** 2)))

        return float(np.clip(raw_mu, 0.0, 1.0))

    def evaluate_sample_memberships(self, x_dict: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Returns per-crop, per-feature membership degrees for explainability."""
        results = {}
        for crop in self.classes_:
            results[crop] = {}
            for feat in FEATURE_NAMES:
                val = x_dict[feat]
                results[crop][feat] = self._compute_feature_membership(val, self.crop_profiles_[crop][feat], feat)
        return results

    def predict_suitability_scores(self, X: pd.DataFrame) -> np.ndarray:
        """
        Computes normalized suitability scores for each crop across all samples.
        Returns a 2D numpy array of shape (N_samples, N_classes) summing to 1 per sample.
        """
        if not self.is_fitted:
            raise RuntimeError("Fuzzy expert must be fitted before predict.")

        n_samples = len(X)
        n_classes = len(self.classes_)
        scores = np.zeros((n_samples, n_classes), dtype=np.float64)

        feature_matrix = X[FEATURE_NAMES].values

        for i in range(n_samples):
            sample_feats = {feat: feature_matrix[i, j] for j, feat in enumerate(FEATURE_NAMES)}
            raw_suitability = np.zeros(n_classes, dtype=np.float64)

            for c_idx, crop in enumerate(self.classes_):
                crop_prof = self.crop_profiles_[crop]
                # Weighted fuzzy t-norm product
                log_score = 0.0
                total_weight = sum(self.feature_weights_.values())

                for feat in FEATURE_NAMES:
                    val = sample_feats[feat]
                    mu = self._compute_feature_membership(val, crop_prof[feat], feat)
                    mu = max(1e-6, mu)  # avoid log(0)
                    w = self.feature_weights_[feat]
                    log_score += w * np.log(mu)

                # Convert back to suitability
                raw_suitability[c_idx] = np.exp(log_score / total_weight)

            # Softmax / ratio normalization to form valid suitability distribution
            total_sum = np.sum(raw_suitability)
            if total_sum > 0:
                scores[i, :] = raw_suitability / total_sum
            else:
                scores[i, :] = np.ones(n_classes) / n_classes

        return scores

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Alias for ensemble compatibility returning (N_samples, N_classes) suitability scores."""
        return self.predict_suitability_scores(X)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts class labels based on argmax of fuzzy suitability scores."""
        scores = self.predict_suitability_scores(X)
        best_indices = np.argmax(scores, axis=1)
        return np.array([self.classes_[idx] for idx in best_indices])

    def save(self, filepath: str):
        joblib.dump({
            "name": self.name,
            "classes_": self.classes_,
            "crop_profiles_": self.crop_profiles_,
            "global_linguistic_bounds_": self.global_linguistic_bounds_,
            "feature_weights_": self.feature_weights_,
            "is_fitted": self.is_fitted
        }, filepath)

    @classmethod
    def load(cls, filepath: str) -> 'AgronomicFuzzyCropExpert':
        data = joblib.load(filepath)
        expert = cls(name=data.get("name", "AgronomicFuzzyExpert"))
        expert.classes_ = data["classes_"]
        expert.crop_profiles_ = data["crop_profiles_"]
        expert.global_linguistic_bounds_ = data["global_linguistic_bounds_"]
        expert.feature_weights_ = data["feature_weights_"]
        expert.is_fitted = data["is_fitted"]
        return expert
