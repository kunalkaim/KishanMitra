import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, f1_score, log_loss, brier_score_loss
from sklearn.model_selection import StratifiedKFold
import joblib

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']


class GaussianNBCropExpert:
    """
    Expert 2: Gaussian Naive Bayes Classifier.
    Models conditional feature likelihoods under Gaussian assumption:
    P(x_j | y = c) ~ Normal(mu_{c,j}, sigma_{c,j}^2).
    
    Tuned strictly via Stratified Cross-Validation on the training partition.
    Outputs are probability distributions across canonically aligned crop classes.
    """
    def __init__(self, var_smoothing: float = 1e-9):
        self.var_smoothing = var_smoothing
        self.model = GaussianNB(var_smoothing=var_smoothing)
        self.classes_: List[str] = []
        self.is_fitted = False
        self.tuning_history: List[Dict[str, Any]] = []

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        self.classes_ = sorted(list(y_train.unique()))
        self.model.fit(X_train[FEATURE_NAMES], y_train)
        self.is_fitted = True
        return self

    def tune_with_cross_validation(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        n_splits: int = 5,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Sweeps var_smoothing hyperparameter across log space using stratified cross-validation
        strictly on the training partition. Does NOT use validation or test observations.
        """
        self.classes_ = sorted(list(y_train.unique()))
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        smoothing_candidates = np.logspace(-11, -1, 25)
        
        best_smoothing = self.var_smoothing
        best_cv_f1 = -1.0
        tuning_history = []

        X_feats = X_train[FEATURE_NAMES].values
        y_vals = y_train.values

        for smoothing in smoothing_candidates:
            fold_f1s = []
            fold_accs = []
            for train_idx, val_idx in skf.split(X_feats, y_vals):
                X_tr, y_tr = X_feats[train_idx], y_vals[train_idx]
                X_va, y_va = X_feats[val_idx], y_vals[val_idx]

                temp_model = GaussianNB(var_smoothing=smoothing)
                temp_model.fit(X_tr, y_tr)
                preds = temp_model.predict(X_va)

                fold_f1s.append(f1_score(y_va, preds, average='macro', zero_division=0))
                fold_accs.append(accuracy_score(y_va, preds))

            mean_f1 = float(np.mean(fold_f1s))
            mean_acc = float(np.mean(fold_accs))

            tuning_history.append({
                "var_smoothing": float(smoothing),
                "cv_macro_f1": mean_f1,
                "cv_accuracy": mean_acc
            })

            if mean_f1 > best_cv_f1:
                best_cv_f1 = mean_f1
                best_smoothing = smoothing

        # Fit final model with best smoothing on full training set
        self.var_smoothing = float(best_smoothing)
        self.model = GaussianNB(var_smoothing=best_smoothing)
        self.model.fit(X_train[FEATURE_NAMES], y_train)
        self.is_fitted = True
        self.tuning_history = tuning_history

        return {
            "best_var_smoothing": float(best_smoothing),
            "best_cv_macro_f1": float(best_cv_f1),
            "tuning_history": tuning_history
        }

    def tune_on_validation(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        X_val: Optional[pd.DataFrame] = None, 
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """Backward-compatible wrapper: delegates strictly to CV on training partition."""
        return self.tune_with_cross_validation(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("GaussianNB expert must be fitted before predict.")
        return self.model.predict(X[FEATURE_NAMES])

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Returns predicted probabilities aligned strictly to the canonical crop class order self.classes_.
        """
        if not self.is_fitted:
            raise RuntimeError("GaussianNB expert must be fitted before predict_proba.")
        
        raw_probs = self.model.predict_proba(X[FEATURE_NAMES])
        model_classes = list(self.model.classes_)

        # Ensure canonical class alignment
        if model_classes == self.classes_:
            return raw_probs

        aligned_probs = np.zeros_like(raw_probs)
        for target_idx, cls_name in enumerate(self.classes_):
            if cls_name in model_classes:
                src_idx = model_classes.index(cls_name)
                aligned_probs[:, target_idx] = raw_probs[:, src_idx]
            else:
                raise ValueError(f"Crop class '{cls_name}' missing from GaussianNB model classes.")

        return aligned_probs

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Evaluates accuracy, macro F1, log loss, and multi-class Brier score.
        Brier Score Convention: Mean sum of squared errors between one-hot indicators and predicted probabilities:
        BS = (1/N) * sum_i sum_c (p_{ic} - y_{ic})^2
        """
        preds = self.predict(X)
        probs = self.predict_proba(X)
        acc = float(accuracy_score(y, preds))
        macro_f1 = float(f1_score(y, preds, average='macro', zero_division=0))
        
        # Log loss & multi-class Brier score
        loss = float(log_loss(y, probs, labels=self.classes_))
        
        # Multi-class Brier score
        y_indices = np.array([self.classes_.index(label) for label in y])
        y_one_hot = np.zeros_like(probs)
        y_one_hot[np.arange(len(y)), y_indices] = 1.0
        brier = float(np.mean(np.sum((probs - y_one_hot) ** 2, axis=1)))

        return {
            "accuracy": acc,
            "macro_f1": macro_f1,
            "log_loss": loss,
            "brier_score": brier
        }

        return {
            "accuracy": float(acc),
            "macro_f1": float(macro_f1),
            "log_loss": float(loss),
            "brier_score": brier
        }

    def save(self, filepath: str):
        joblib.dump({
            "model": self.model,
            "classes_": self.classes_,
            "var_smoothing": self.var_smoothing,
            "is_fitted": self.is_fitted
        }, filepath)

    @classmethod
    def load(cls, filepath: str) -> 'GaussianNBCropExpert':
        data = joblib.load(filepath)
        expert = cls(var_smoothing=data.get("var_smoothing", 1e-9))
        expert.model = data["model"]
        expert.classes_ = data["classes_"]
        expert.is_fitted = data["is_fitted"]
        return expert
