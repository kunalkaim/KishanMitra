import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from sklearn.metrics import accuracy_score, f1_score, log_loss
from app.ml.crop_recommendation.fuzzy_model import AgronomicFuzzyCropExpert
from app.ml.crop_recommendation.gaussian_nb import GaussianNBCropExpert
from app.ml.crop_recommendation.decision_tree import DecisionTreeCropExpert
import joblib

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']


class HybridWeightedCropEnsemble:
    """
    KisanMitra Hybrid AI Weighted Ensemble Engine.
    Fuses three complementary AI paradigms with strict canonical class alignment:
    1. Fuzzy Logic (Data-derived Agronomic Suitability Distribution)
    2. Gaussian Naive Bayes (Probabilistic Likelihood Densities)
    3. Decision Tree (Deterministic Orthogonal Space Partitioning)
    
    Formula: FinalScore_c = W1 * FuzzyScore_c + W2 * GNBProb_c + W3 * DTProb_c
    Constraint: W1 + W2 + W3 = 1.0,  W_i >= 0.0
    """
    def __init__(
        self,
        fuzzy_expert: AgronomicFuzzyCropExpert,
        gnb_expert: GaussianNBCropExpert,
        dt_expert: DecisionTreeCropExpert,
        weights: Tuple[float, float, float] = (0.3333, 0.3333, 0.3334),
        classes: Optional[List[str]] = None
    ):
        self.fuzzy_expert = fuzzy_expert
        self.gnb_expert = gnb_expert
        self.dt_expert = dt_expert

        # Establish ONE canonical crop class ordering
        if classes is not None:
            self.classes_ = sorted(list(classes))
        else:
            self.classes_ = sorted(list(fuzzy_expert.classes_))

        # Verify all three experts contain all canonical classes
        for name, exp_classes in [
            ("Fuzzy Expert", self.fuzzy_expert.classes_),
            ("GaussianNB Expert", self.gnb_expert.classes_),
            ("DecisionTree Expert", self.dt_expert.classes_)
        ]:
            missing = set(self.classes_) - set(exp_classes)
            if missing:
                raise ValueError(f"{name} is missing expected canonical crop classes: {missing}")
        
        # Normalize initial weights
        w_sum = sum(weights)
        if w_sum <= 0:
            self.weights = (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
        else:
            self.weights = (weights[0] / w_sum, weights[1] / w_sum, weights[2] / w_sum)
            
        self.optimization_report_: Dict[str, Any] = {}

    def _align_to_canonical(self, raw_matrix: np.ndarray, expert_classes: List[str], expert_name: str) -> np.ndarray:
        """
        Validates, canonicalizes class column alignment, ensures non-negativity, 
        finite values, and row-wise normalization.
        """
        if raw_matrix.ndim != 2:
            raise ValueError(f"{expert_name} output must be 2D array, got shape {raw_matrix.shape}")
        
        n_samples = raw_matrix.shape[0]
        n_canonical = len(self.classes_)

        if raw_matrix.shape[1] != len(expert_classes):
            raise ValueError(
                f"{expert_name} column count ({raw_matrix.shape[1]}) does not match its classes count ({len(expert_classes)})."
            )

        if expert_classes == self.classes_:
            aligned = raw_matrix.copy()
        else:
            aligned = np.zeros((n_samples, n_canonical), dtype=np.float64)
            for target_idx, cls_name in enumerate(self.classes_):
                if cls_name in expert_classes:
                    src_idx = expert_classes.index(cls_name)
                    aligned[:, target_idx] = raw_matrix[:, src_idx]
                else:
                    raise ValueError(f"Crop class '{cls_name}' missing from {expert_name} classes.")

        # Numerical integrity checks
        if not np.all(np.isfinite(aligned)):
            raise ValueError(f"{expert_name} output contains NaN or Inf values.")

        aligned = np.clip(aligned, 0.0, None)
        row_sums = np.sum(aligned, axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return aligned / row_sums

    def predict_component_scores(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generates probability / suitability distributions from each of the three experts
        strictly aligned to self.classes_.
        Each returned array is of shape (N_samples, N_classes) and sums to 1.0 per row.
        """
        raw_fuzzy = self.fuzzy_expert.predict_suitability_scores(X)
        raw_gnb = self.gnb_expert.predict_proba(X)
        raw_dt = self.dt_expert.predict_proba(X)

        fuzzy_aligned = self._align_to_canonical(raw_fuzzy, self.fuzzy_expert.classes_, "Fuzzy Expert")
        gnb_aligned = self._align_to_canonical(raw_gnb, self.gnb_expert.classes_, "GaussianNB Expert")
        dt_aligned = self._align_to_canonical(raw_dt, self.dt_expert.classes_, "Decision Tree Expert")

        return fuzzy_aligned, gnb_aligned, dt_aligned

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Computes weighted ensemble scores across all crop classes.
        Output is guaranteed canonically ordered and normalized.
        """
        fuzzy_scores, gnb_probs, dt_probs = self.predict_component_scores(X)
        w1, w2, w3 = self.weights
        ensemble_scores = (w1 * fuzzy_scores) + (w2 * gnb_probs) + (w3 * dt_probs)
        
        # Ensure row-wise normalization
        row_sums = np.sum(ensemble_scores, axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return ensemble_scores / row_sums

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        probs = self.predict_proba(X)
        best_indices = np.argmax(probs, axis=1)
        return np.array([self.classes_[idx] for idx in best_indices])

    def optimize_weights_on_validation(
        self,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        step: float = 0.02
    ) -> Dict[str, Any]:
        """
        Performs fine grid search over the full 2D simplex Delta^2 (W_i >= 0.0, sum W_i = 1.0)
        to find optimal weights (W1, W2, W3) maximizing validation Macro F1.
        Uses validation observations exclusively; never inspects test observations.
        """
        fuzzy_val, gnb_val, dt_val = self.predict_component_scores(X_val)

        # Baseline evaluations of single models
        fuzzy_preds = np.array([self.classes_[idx] for idx in np.argmax(fuzzy_val, axis=1)])
        gnb_preds = np.array([self.classes_[idx] for idx in np.argmax(gnb_val, axis=1)])
        dt_preds = np.array([self.classes_[idx] for idx in np.argmax(dt_val, axis=1)])

        fuzzy_acc = float(accuracy_score(y_val, fuzzy_preds))
        fuzzy_f1 = float(f1_score(y_val, fuzzy_preds, average='macro', zero_division=0))

        gnb_acc = float(accuracy_score(y_val, gnb_preds))
        gnb_f1 = float(f1_score(y_val, gnb_preds, average='macro', zero_division=0))

        dt_acc = float(accuracy_score(y_val, dt_preds))
        dt_f1 = float(f1_score(y_val, dt_preds, average='macro', zero_division=0))

        # Equal weights evaluation (1/3, 1/3, 1/3)
        eq_scores = (fuzzy_val / 3.0) + (gnb_val / 3.0) + (dt_val / 3.0)
        eq_preds = np.array([self.classes_[idx] for idx in np.argmax(eq_scores, axis=1)])
        eq_acc = float(accuracy_score(y_val, eq_preds))
        eq_f1 = float(f1_score(y_val, eq_preds, average='macro', zero_division=0))

        best_f1 = -1.0
        best_acc = -1.0
        best_weights = self.weights

        grid_history = []
        # Full simplex grid search without artificial minimum-weight restriction
        w1_range = np.arange(0.0, 1.0 + 1e-5, step)

        for w1 in w1_range:
            w2_range = np.arange(0.0, 1.0 - w1 + 1e-5, step)
            for w2 in w2_range:
                w3 = max(0.0, 1.0 - w1 - w2)
                if abs(w1 + w2 + w3 - 1.0) > 1e-4:
                    continue

                combined = (w1 * fuzzy_val) + (w2 * gnb_val) + (w3 * dt_val)
                preds = np.array([self.classes_[idx] for idx in np.argmax(combined, axis=1)])
                f1 = float(f1_score(y_val, preds, average='macro', zero_division=0))
                acc = float(accuracy_score(y_val, preds))

                if f1 > best_f1 or (np.isclose(f1, best_f1) and acc > best_acc):
                    best_f1 = f1
                    best_acc = acc
                    best_weights = (round(float(w1), 4), round(float(w2), 4), round(float(w3), 4))

        self.weights = best_weights

        self.optimization_report_ = {
            "individual_experts_validation": {
                "fuzzy_logic": {"accuracy": fuzzy_acc, "macro_f1": fuzzy_f1, "weight": 1.0},
                "gaussian_nb": {"accuracy": gnb_acc, "macro_f1": gnb_f1, "weight": 1.0},
                "decision_tree": {"accuracy": dt_acc, "macro_f1": dt_f1, "weight": 1.0}
            },
            "equal_weight_ensemble_validation": {
                "weights": [0.3333, 0.3333, 0.3334],
                "accuracy": eq_acc,
                "macro_f1": eq_f1
            },
            "optimized_weighted_ensemble_validation": {
                "weights": list(self.weights),
                "accuracy": float(best_acc),
                "macro_f1": float(best_f1)
            },
            "ensemble_benefit_analysis": {
                "improves_over_fuzzy": bool(best_f1 > fuzzy_f1),
                "improves_over_gnb": bool(best_f1 > gnb_f1),
                "improves_over_dt": bool(best_f1 > dt_f1),
                "improves_over_equal_weight": bool(best_f1 > eq_f1),
                "uncontributing_experts": [
                    name for name, w in zip(["Fuzzy", "GaussianNB", "DecisionTree"], self.weights) if w == 0.0
                ]
            }
        }
        return self.optimization_report_

    def save(self, filepath: str):
        joblib.dump({
            "weights": self.weights,
            "classes_": self.classes_,
            "optimization_report": self.optimization_report_
        }, filepath)

    @classmethod
    def load(
        cls, 
        filepath: str, 
        fuzzy_expert: AgronomicFuzzyCropExpert, 
        gnb_expert: GaussianNBCropExpert, 
        dt_expert: DecisionTreeCropExpert
    ) -> 'HybridWeightedCropEnsemble':
        data = joblib.load(filepath)
        ensemble = cls(
            fuzzy_expert=fuzzy_expert,
            gnb_expert=gnb_expert,
            dt_expert=dt_expert,
            weights=tuple(data["weights"])
        )
        ensemble.classes_ = data["classes_"]
        ensemble.optimization_report_ = data.get("optimization_report", {})
        return ensemble
