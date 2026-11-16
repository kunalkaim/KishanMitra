import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.model_selection import ParameterGrid, StratifiedKFold
from sklearn.inspection import permutation_importance
import joblib

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
RANDOM_STATE = 42


class DecisionTreeCropExpert:
    """
    Expert 3: Decision Tree Classifier.
    Hierarchically partitions the 7D feature space using deterministic orthogonal cutoffs.
    Provides clear decision paths, leaf node impurity values, Gini feature importances,
    and permutation feature importances.
    
    Tuned strictly via Stratified Cross-Validation on the training partition.
    Note: Feature importances measure statistical partitioning utility within this dataset
    and do NOT constitute causal agronomic evidence.
    """
    def __init__(
        self,
        criterion: str = 'gini',
        max_depth: Optional[int] = 10,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = RANDOM_STATE
    ):
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state

        self.model = DecisionTreeClassifier(
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state
        )
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
        n_splits: int = 5
    ) -> Dict[str, Any]:
        """
        Performs stratified cross-validation on training partition only to prevent overfitting
        while optimizing tree depth and leaf regularization.
        """
        self.classes_ = sorted(list(y_train.unique()))
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)

        param_grid = {
            'criterion': ['gini', 'entropy'],
            'max_depth': [6, 8, 10, 12, 15],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        best_score = -1.0
        best_params = {}
        tuning_log = []

        X_feats = X_train[FEATURE_NAMES].values
        y_vals = y_train.values

        for params in ParameterGrid(param_grid):
            fold_f1s = []
            fold_accs = []
            for train_idx, val_idx in skf.split(X_feats, y_vals):
                X_tr, y_tr = X_feats[train_idx], y_vals[train_idx]
                X_va, y_va = X_feats[val_idx], y_vals[val_idx]

                tree = DecisionTreeClassifier(
                    criterion=params['criterion'],
                    max_depth=params['max_depth'],
                    min_samples_split=params['min_samples_split'],
                    min_samples_leaf=params['min_samples_leaf'],
                    random_state=self.random_state
                )
                tree.fit(X_tr, y_tr)
                val_preds = tree.predict(X_va)
                fold_f1s.append(f1_score(y_va, val_preds, average='macro', zero_division=0))
                fold_accs.append(accuracy_score(y_va, val_preds))

            mean_f1 = float(np.mean(fold_f1s))
            mean_acc = float(np.mean(fold_accs))

            tuning_log.append({
                "params": params,
                "cv_macro_f1": mean_f1,
                "cv_accuracy": mean_acc
            })

            if mean_f1 > best_score:
                best_score = mean_f1
                best_params = params

        # Train final tree with optimal params on full training set
        self.criterion = best_params['criterion']
        self.max_depth = best_params['max_depth']
        self.min_samples_split = best_params['min_samples_split']
        self.min_samples_leaf = best_params['min_samples_leaf']

        self.model = DecisionTreeClassifier(
            criterion=self.criterion,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            random_state=self.random_state
        )
        self.model.fit(X_train[FEATURE_NAMES], y_train)
        self.classes_ = sorted(list(y_train.unique()))
        self.is_fitted = True
        self.tuning_history = tuning_log

        return {
            "best_params": best_params,
            "best_cv_macro_f1": float(best_score),
            "effective_depth": int(self.model.get_depth()),
            "leaf_count": int(self.model.get_n_leaves()),
            "tuning_history": tuning_log
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
            raise RuntimeError("Decision tree expert must be fitted before predict.")
        return self.model.predict(X[FEATURE_NAMES])

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Returns predicted probabilities aligned strictly to canonical crop class order self.classes_.
        """
        if not self.is_fitted:
            raise RuntimeError("Decision tree expert must be fitted before predict_proba.")
        
        raw_probs = self.model.predict_proba(X[FEATURE_NAMES])
        model_classes = list(self.model.classes_)

        # Canonical alignment
        if model_classes == self.classes_:
            return raw_probs

        aligned_probs = np.zeros_like(raw_probs)
        for target_idx, cls_name in enumerate(self.classes_):
            if cls_name in model_classes:
                src_idx = model_classes.index(cls_name)
                aligned_probs[:, target_idx] = raw_probs[:, src_idx]
            else:
                raise ValueError(f"Crop class '{cls_name}' missing from Decision Tree model classes.")

        return aligned_probs

    def get_feature_importances(self) -> Dict[str, float]:
        """Returns Gini feature importances across the 7 input features."""
        if not self.is_fitted:
            raise RuntimeError("Decision tree expert must be fitted.")
        importances = self.model.feature_importances_
        return {feat: float(importances[idx]) for idx, feat in enumerate(FEATURE_NAMES)}

    def get_permutation_importances(self, X: pd.DataFrame, y: pd.Series, n_repeats: int = 5) -> Dict[str, float]:
        """
        Calculates permutation feature importances (mean decrease in accuracy upon shuffling).
        Provides a secondary, less biased importance metric than pure Gini impurity decrease.
        """
        if not self.is_fitted:
            raise RuntimeError("Decision tree expert must be fitted.")
        perm = permutation_importance(
            self.model, X[FEATURE_NAMES], y, 
            n_repeats=n_repeats, random_state=self.random_state, scoring='accuracy'
        )
        return {feat: float(perm.importances_mean[idx]) for idx, feat in enumerate(FEATURE_NAMES)}

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        preds = self.predict(X)
        probs = self.predict_proba(X)
        acc = accuracy_score(y, preds)
        macro_f1 = f1_score(y, preds, average='macro', zero_division=0)
        loss = log_loss(y, probs, labels=self.classes_)

        return {
            "accuracy": float(acc),
            "macro_f1": float(macro_f1),
            "log_loss": float(loss),
            "feature_importances": self.get_feature_importances()
        }

    def save(self, filepath: str):
        joblib.dump({
            "model": self.model,
            "classes_": self.classes_,
            "criterion": self.criterion,
            "max_depth": self.max_depth,
            "min_samples_split": self.min_samples_split,
            "min_samples_leaf": self.min_samples_leaf,
            "random_state": self.random_state,
            "is_fitted": self.is_fitted
        }, filepath)

    @classmethod
    def load(cls, filepath: str) -> 'DecisionTreeCropExpert':
        data = joblib.load(filepath)
        expert = cls(
            criterion=data.get("criterion", "gini"),
            max_depth=data.get("max_depth", 10),
            min_samples_split=data.get("min_samples_split", 5),
            min_samples_leaf=data.get("min_samples_leaf", 2),
            random_state=data.get("random_state", 42)
        )
        expert.model = data["model"]
        expert.classes_ = data["classes_"]
        expert.is_fitted = data["is_fitted"]
        return expert
