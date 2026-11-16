import os
import json
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
TARGET_NAME = 'label'
RANDOM_STATE = 42

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))

DEFAULT_DATA_PATH = os.path.join(_PROJECT_ROOT, "datasets", "crop_recommendation", "processed", "cleaned_crop_recommendation.csv")
RAW_DATA_PATH = os.path.join(_PROJECT_ROOT, "datasets", "crop_recommendation", "raw", "Crop_recommendation.csv")


def load_dataset(csv_path: str = DEFAULT_DATA_PATH) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """Loads dataset and extracts feature matrix X, target series y, and class labels."""
    resolved_path = csv_path
    if not os.path.exists(resolved_path):
        if os.path.exists(RAW_DATA_PATH):
            resolved_path = RAW_DATA_PATH
        elif os.path.exists(os.path.join("datasets", "crop_recommendation", "raw", "Crop_recommendation.csv")):
            resolved_path = os.path.join("datasets", "crop_recommendation", "raw", "Crop_recommendation.csv")
        else:
            raise FileNotFoundError(f"Crop recommendation dataset not found at {csv_path} or {RAW_DATA_PATH}")

    df = pd.read_csv(resolved_path)
    df.columns = [c.strip() for c in df.columns]

    X = df[FEATURE_NAMES].copy()
    y = df[TARGET_NAME].astype(str).str.strip().str.lower().copy()
    classes = sorted(list(y.unique()))
    return X, y, classes


def split_data(
    X: pd.DataFrame, 
    y: pd.Series, 
    train_size: float = 0.70, 
    val_size: float = 0.15, 
    test_size: float = 0.15,
    random_state: int = RANDOM_STATE
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Performs leakage-free stratified splitting:
    - 70% Train
    - 15% Validation
    - 15% Test
    """
    assert np.isclose(train_size + val_size + test_size, 1.0), "Splits must sum to 1.0"
    
    # Stage 1: Split into Train (70%) and Temp (30%)
    temp_size = val_size + test_size
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, 
        test_size=temp_size, 
        stratify=y, 
        random_state=random_state
    )
    
    # Stage 2: Split Temp evenly into Val (15% total) and Test (15% total)
    val_ratio_in_temp = val_size / temp_size
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, 
        test_size=(1.0 - val_ratio_in_temp), 
        stratify=y_temp, 
        random_state=random_state
    )
    
    return X_train, y_train, X_val, y_val, X_test, y_test


class DataPreprocessor:
    """Encapsulates scaling and label mapping, fitting strictly on training split."""
    def __init__(self):
        self.scaler = StandardScaler()
        self.classes_: List[str] = []
        self.class_to_idx_: Dict[str, int] = {}
        self.idx_to_class_: Dict[int, str] = {}
        self.is_fitted = False

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        self.scaler.fit(X_train)
        self.classes_ = sorted(list(y_train.unique()))
        self.class_to_idx_ = {cls: idx for idx, cls in enumerate(self.classes_)}
        self.idx_to_class_ = {idx: cls for idx, cls in enumerate(self.classes_)}
        self.is_fitted = True
        return self

    def transform_X(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("DataPreprocessor must be fitted before transform.")
        return self.scaler.transform(X[FEATURE_NAMES])

    def transform_y(self, y: pd.Series) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("DataPreprocessor must be fitted before transform.")
        return np.array([self.class_to_idx_[val] for val in y])

    def inverse_transform_y(self, y_indices: np.ndarray) -> List[str]:
        return [self.idx_to_class_[idx] for idx in y_indices]

    def save(self, filepath: str):
        joblib.dump({
            "scaler": self.scaler,
            "classes_": self.classes_,
            "class_to_idx_": self.class_to_idx_,
            "idx_to_class_": self.idx_to_class_
        }, filepath)

    @classmethod
    def load(cls, filepath: str) -> 'DataPreprocessor':
        data = joblib.load(filepath)
        preprocessor = cls()
        preprocessor.scaler = data["scaler"]
        preprocessor.classes_ = data["classes_"]
        preprocessor.class_to_idx_ = data["class_to_idx_"]
        preprocessor.idx_to_class_ = data["idx_to_class_"]
        preprocessor.is_fitted = True
        return preprocessor
