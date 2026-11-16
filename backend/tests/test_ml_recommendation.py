import os
import sys
import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

# Ensure backend is on PYTHONPATH
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
_PROJECT_ROOT = os.path.abspath(os.path.join(_BACKEND_DIR, ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app.main import app
from app.ml.crop_recommendation.preprocessing import load_dataset, split_data, FEATURE_NAMES
from app.ml.crop_recommendation.fuzzy_model import AgronomicFuzzyCropExpert
from app.ml.crop_recommendation.gaussian_nb import GaussianNBCropExpert
from app.ml.crop_recommendation.decision_tree import DecisionTreeCropExpert
from app.ml.crop_recommendation.ensemble import HybridWeightedCropEnsemble
from app.ml.crop_recommendation.explainability import CropExplainabilityEngine
from app.ml.crop_recommendation.model_registry import ModelRegistry
from app.ml.crop_recommendation.predictor import CropRecommendationPredictor


@pytest.fixture(scope="module")
def dataset_data():
    X, y, classes = load_dataset()
    return X, y, classes


@pytest.fixture(scope="module")
def data_splits(dataset_data):
    X, y, _ = dataset_data
    return split_data(X, y, train_size=0.70, val_size=0.15, test_size=0.15, random_state=42)


# ==========================================
# 1. DATASET & PREPROCESSING TESTS
# ==========================================

def test_dataset_schema_and_integrity(dataset_data):
    X, y, classes = dataset_data
    assert len(X) == 2200, f"Expected 2200 records, got {len(X)}"
    assert len(classes) == 22, f"Expected 22 distinct crop classes, got {len(classes)}"
    assert list(X.columns) == FEATURE_NAMES
    assert X.isnull().sum().sum() == 0, "Dataset must not have missing values"
    # Ensure perfect balance (100 samples per class)
    counts = y.value_counts()
    assert (counts == 100).all(), "Every class must have exactly 100 samples"


def test_stratified_split_integrity(data_splits):
    X_train, y_train, X_val, y_val, X_test, y_test = data_splits
    assert len(X_train) == 1540  # 70%
    assert len(X_val) == 330     # 15%
    assert len(X_test) == 330    # 15%

    # Verify all 22 classes exist in all 3 partitions
    assert len(set(y_train)) == 22
    assert len(set(y_val)) == 22
    assert len(set(y_test)) == 22

    # Verify no overlap between partitions
    assert len(set(X_train.index).intersection(set(X_val.index))) == 0
    assert len(set(X_train.index).intersection(set(X_test.index))) == 0
    assert len(set(X_val.index).intersection(set(X_test.index))) == 0


# ==========================================
# 2. INDIVIDUAL AI EXPERT TESTS
# ==========================================

def test_fuzzy_expert_properties(data_splits):
    X_train, y_train, X_val, y_val, _, _ = data_splits
    fuzzy = AgronomicFuzzyCropExpert()
    fuzzy.fit(X_train, y_train)

    assert fuzzy.is_fitted
    assert len(fuzzy.classes_) == 22

    # Predict suitability scores
    scores = fuzzy.predict_suitability_scores(X_val.head(10))
    assert scores.shape == (10, 22)
    # Check bounded in [0, 1]
    assert np.all(scores >= 0.0) and np.all(scores <= 1.0)
    # Check row-wise normalization
    row_sums = np.sum(scores, axis=1)
    assert np.allclose(row_sums, 1.0, atol=1e-5)


def test_gaussian_nb_cv_and_canonical_alignment(data_splits):
    X_train, y_train, X_val, _, _, _ = data_splits
    gnb = GaussianNBCropExpert()
    cv_res = gnb.tune_with_cross_validation(X_train, y_train, n_splits=5)

    assert "best_var_smoothing" in cv_res
    assert cv_res["best_cv_macro_f1"] > 0.95
    assert gnb.is_fitted

    probs = gnb.predict_proba(X_val.head(10))
    assert probs.shape == (10, 22)
    assert np.allclose(np.sum(probs, axis=1), 1.0, atol=1e-5)


def test_decision_tree_cv_and_importances(data_splits):
    X_train, y_train, X_val, _, _, _ = data_splits
    dt = DecisionTreeCropExpert(random_state=42)
    cv_res = dt.tune_with_cross_validation(X_train, y_train, n_splits=5)

    assert "best_params" in cv_res
    assert cv_res["best_cv_macro_f1"] > 0.95
    assert dt.is_fitted

    probs = dt.predict_proba(X_val.head(10))
    assert probs.shape == (10, 22)
    assert np.allclose(np.sum(probs, axis=1), 1.0, atol=1e-5)

    # Check Gini and Permutation importances
    gini = dt.get_feature_importances()
    assert len(gini) == 7
    assert np.isclose(sum(gini.values()), 1.0, atol=1e-4)

    perm = dt.get_permutation_importances(X_train.head(200), y_train.head(200), n_repeats=2)
    assert len(perm) == 7


# ==========================================
# 3. HYBRID ENSEMBLE & CLASS ALIGNMENT TESTS
# ==========================================

def test_ensemble_class_alignment_and_simplex_weights(data_splits):
    X_train, y_train, X_val, y_val, _, _ = data_splits
    fuzzy = AgronomicFuzzyCropExpert().fit(X_train, y_train)
    gnb = GaussianNBCropExpert().fit(X_train, y_train)
    dt = DecisionTreeCropExpert().fit(X_train, y_train)

    ensemble = HybridWeightedCropEnsemble(fuzzy, gnb, dt)
    assert ensemble.classes_ == sorted(list(y_train.unique()))

    # Simplex weight optimization
    opt_rep = ensemble.optimize_weights_on_validation(X_val, y_val, step=0.05)
    w1, w2, w3 = ensemble.weights

    assert np.isclose(w1 + w2 + w3, 1.0, atol=1e-4)
    assert w1 >= 0.0 and w2 >= 0.0 and w3 >= 0.0
    assert "optimized_weighted_ensemble_validation" in opt_rep

    # Verify probability distribution
    ens_probs = ensemble.predict_proba(X_val.head(15))
    assert ens_probs.shape == (15, 22)
    assert np.allclose(np.sum(ens_probs, axis=1), 1.0, atol=1e-5)


# ==========================================
# 4. EXPLAINABILITY & RUNNER-UP LOGIC TESTS
# ==========================================

def test_explainability_runner_up_and_reconciliation(data_splits):
    X_train, y_train, _, _, _, _ = data_splits
    fuzzy = AgronomicFuzzyCropExpert().fit(X_train, y_train)
    gnb = GaussianNBCropExpert().fit(X_train, y_train)
    dt = DecisionTreeCropExpert().fit(X_train, y_train)
    ensemble = HybridWeightedCropEnsemble(fuzzy, gnb, dt)
    explainer = CropExplainabilityEngine(ensemble)

    sample = {
        'N': 90.0, 'P': 42.0, 'K': 43.0,
        'temperature': 24.5, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 220.0
    }
    res = explainer.explain_recommendation(sample, top_k=3)

    top_crops = res["top_crops"]
    assert len(top_crops) == 3
    assert top_crops[0]["rank"] == 1
    assert top_crops[1]["rank"] == 2
    assert top_crops[2]["rank"] == 3

    # Reconciled score check
    for c in top_crops:
        contribs = c["weighted_contributions"]
        reconciled = round(contribs["fuzzy_contribution"] + contribs["gaussian_nb_contribution"] + contribs["decision_tree_contribution"], 2)
        assert np.isclose(c["ensemble_score"], reconciled, atol=0.05)

    # Runner-up verification: Must be Rank #2
    contrastive = res["contrastive_analysis"]
    assert contrastive["runner_up_crop"] == top_crops[1]["crop_name"]
    assert contrastive["first_excluded_crop"]["rank"] == 4


# ==========================================
# 5. PREDICTOR INPUT BOUNDARY VALIDATION
# ==========================================

def test_predictor_input_validation():
    # 1. Missing feature
    errs = CropRecommendationPredictor.validate_inputs({'N': 50, 'P': 50})
    assert any("Missing required agricultural feature" in e for e in errs)

    # 2. Strict Boolean rejection
    errs_bool = CropRecommendationPredictor.validate_inputs({
        'N': True, 'P': 40, 'K': 40, 'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100
    })
    assert any("cannot be boolean" in e for e in errs_bool)

    # 3. NaN rejection
    errs_nan = CropRecommendationPredictor.validate_inputs({
        'N': np.nan, 'P': 40, 'K': 40, 'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100
    })
    assert any("cannot be NaN" in e for e in errs_nan)

    # 4. Infinity rejection
    errs_inf = CropRecommendationPredictor.validate_inputs({
        'N': np.inf, 'P': 40, 'K': 40, 'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100
    })
    assert any("cannot be infinite" in e for e in errs_inf)

    # 5. Out of bounds (e.g. pH = 12.0)
    errs_ph = CropRecommendationPredictor.validate_inputs({
        'N': 50, 'P': 40, 'K': 40, 'temperature': 25, 'humidity': 60, 'ph': 12.0, 'rainfall': 100
    })
    assert any("Soil pH must be between" in e for e in errs_ph)


# ==========================================
# 6. FASTAPI ENDPOINT INTEGRATION TESTS
# ==========================================

def test_fastapi_recommendation_endpoint():
    client = TestClient(app)

    # A. Valid request with all 7 features
    payload_valid = {
        "farm_id": "farm-demo-01",
        "season": "Kharif",
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 24.5,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 220.0
    }
    resp = client.post("/api/v1/recommendations/", json=payload_valid)
    assert resp.status_code == 200, f"Endpoint failed: {resp.text}"

    data = resp.json()
    assert data["is_demo"] is False
    assert len(data["recommended_crops"]) == 3
    top1 = data["recommended_crops"][0]
    assert "rice" in top1["crop_name"].lower()
    assert top1["rank"] == 1
    assert "fuzzy_score" in top1
    assert "bayesian_probability" in top1
    assert "decision_tree_score" in top1
    assert data["contrastive_analysis"] is not None
    assert data["feature_importances"] is not None

    # B. Missing required features without farm fallback should return 422
    payload_missing = {
        "farm_id": "farm-demo-01",
        "season": "Kharif"
        # Soil test on farm-demo-01 provides N,P,K,pH, but if temperature & humidity are missing and no weather record:
    }
    # Test with invalid out-of-bounds inputs
    payload_invalid_bounds = {
        "farm_id": "farm-demo-01",
        "season": "Kharif",
        "N": -50.0,  # Negative N
        "P": 42.0,
        "K": 43.0,
        "temperature": 24.5,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 220.0
    }
    resp_inv = client.post("/api/v1/recommendations/", json=payload_invalid_bounds)
    assert resp_inv.status_code == 422
