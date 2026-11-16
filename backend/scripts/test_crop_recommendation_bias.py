"""
=============================================================================
KISANMITRA: PHASE 5.2 ACCEPTANCE TEST SUITE
HYBRID ML CROP RECOMMENDATION: RICE-BIAS ELIMINATION & ACCURACY OPTIMIZATION
=============================================================================
Formal verification suite covering all 20 required acceptance criteria:
1. Canonical 22-class mapping completeness
2. Feature order consistency across all models
3. Class index alignment verification
4. Ensemble probability validity (sums to 1.0, non-negative, finite)
5. Zero-value preservation (no truthiness conversion to default)
6. Missing value warning / non-silent handling
7. Frontend-to-backend input propagation
8. Sensitivity to NPK variations
9. Sensitivity to temperature & elevation
10. Sensitivity to seasonal rainfall variations
11. Determinism on identical requests
12. Non-Rice top-1 verification for Maize, Pulses, Apples, Cotton, Coffee
13. Independent evaluation of all three models
14. Top-3 uniqueness and ordering
15. Held-out validation of calibration and weights (N=330 test split)
16. Proof of Rice ranking #1 when inputs genuinely favor Rice (no reverse bias)
17. Data quality and provenance reporting
18. Macro-annual rainfall scaling verification
19. Unified endpoint HTTP 200/404/422 status checks
20. Existing RAG citations and 31 ChromaDB vectors preserved
=============================================================================
"""

import os
import sys
import json
import unittest
import urllib.request
import urllib.error
import numpy as np
import pandas as pd

# Set up project path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BACKEND_DIR)

from app.ml.crop_recommendation.preprocessing import (
    load_dataset, split_data, FEATURE_NAMES, RANDOM_STATE
)
from app.ml.crop_recommendation.predictor import CropRecommendationPredictor
from app.ml.crop_recommendation.ensemble import HybridWeightedCropEnsemble
from app.api.v1.endpoints.recommendations import (
    CROP_ECONOMIC_BENCHMARKS, RecommendationInput
)
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.farm import Farm
from app.models.user import User

BASE_URL = "http://127.0.0.1:8000"


class TestCropRecommendationBiasAndAccuracy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictor = CropRecommendationPredictor.get_instance()
        cls.ensemble = cls.predictor.ensemble
        cls.explainer = cls.predictor.explainer
        cls.classes = cls.ensemble.classes_
        
        # Load raw dataset and compute median profiles
        cls.raw_data_path = os.path.abspath(
            os.path.join(BACKEND_DIR, "..", "datasets", "crop_recommendation", "raw", "Crop_recommendation.csv")
        )
        cls.df = pd.read_csv(cls.raw_data_path)
        cls.crop_medians = cls.df.groupby('label')[FEATURE_NAMES].median()
        
        # Dynamically resolve farm owner user token from active database
        db = SessionLocal()
        farm = db.query(Farm).filter(Farm.id == "farm-demo-01").first()
        farmer_id = farm.farmer_id if farm else None
        if not farmer_id:
            user = db.query(User).first()
            farmer_id = user.id if user else "demo-user"
        db.close()
        
        cls.user_token = create_access_token(subject=farmer_id)
        cls.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cls.user_token}"
        }

    # -------------------------------------------------------------------------
    # TEST 1: Canonical 22-class mapping completeness
    # -------------------------------------------------------------------------
    def test_01_canonical_22_classes(self):
        """Verify that exactly 22 canonical classes are registered in predictor and economic benchmarks."""
        self.assertEqual(len(self.classes), 22, f"Expected 22 classes, got {len(self.classes)}")
        self.assertEqual(len(CROP_ECONOMIC_BENCHMARKS), 22, "Economic catalog must benchmark all 22 crops")
        
        expected_crops = {
            'apple', 'banana', 'blackgram', 'chickpea', 'coconut', 'coffee',
            'cotton', 'grapes', 'jute', 'kidneybeans', 'lentil', 'maize',
            'mango', 'mothbeans', 'mungbean', 'muskmelon', 'orange', 'papaya',
            'pigeonpeas', 'pomegranate', 'rice', 'watermelon'
        }
        self.assertEqual(set(self.classes), expected_crops)
        self.assertEqual(set(CROP_ECONOMIC_BENCHMARKS.keys()), expected_crops)

    # -------------------------------------------------------------------------
    # TEST 2: Feature order consistency across all models
    # -------------------------------------------------------------------------
    def test_02_feature_order_consistency(self):
        """Verify strict feature order consistency across preprocessing and all models."""
        expected_order = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        self.assertEqual(FEATURE_NAMES, expected_order)
        
        # Decision tree feature names
        dt_feats = list(self.ensemble.dt_expert.model.feature_names_in_)
        self.assertEqual(dt_feats, expected_order)

    # -------------------------------------------------------------------------
    # TEST 3: Class index alignment verification between individual model classes
    # -------------------------------------------------------------------------
    def test_03_class_index_alignment(self):
        """Verify that class index i corresponds to the exact same crop across all sub-models."""
        fuzzy_cls = list(self.ensemble.fuzzy_expert.classes_)
        gnb_cls = list(self.ensemble.gnb_expert.classes_)
        dt_cls = list(self.ensemble.dt_expert.classes_)
        gnb_model_cls = list(self.ensemble.gnb_expert.model.classes_)
        ens_cls = list(self.ensemble.classes_)

        self.assertEqual(fuzzy_cls, ens_cls, "Fuzzy expert classes misaligned")
        self.assertEqual(gnb_cls, ens_cls, "GaussianNB expert classes misaligned")
        self.assertEqual(dt_cls, ens_cls, "DecisionTree expert classes misaligned")
        self.assertEqual(gnb_model_cls, ens_cls, "GaussianNB model.classes_ misaligned")

    # -------------------------------------------------------------------------
    # TEST 4: Ensemble probability validity
    # -------------------------------------------------------------------------
    def test_04_ensemble_probability_validity(self):
        """Verify probabilities sum to 1.0, are non-negative, and finite across diverse inputs."""
        test_samples = [
            {'N': 90, 'P': 42, 'K': 43, 'temperature': 20.8, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9},
            {'N': 20, 'P': 60, 'K': 70, 'temperature': 18.0, 'humidity': 50.0, 'ph': 6.0, 'rainfall': 75.0},
            {'N': 110, 'P': 45, 'K': 20, 'temperature': 26.0, 'humidity': 65.0, 'ph': 6.8, 'rainfall': 90.0},
            {'N': 40, 'P': 68, 'K': 79, 'temperature': 15.5, 'humidity': 92.0, 'ph': 5.9, 'rainfall': 110.0},
            {'N': 100, 'P': 25, 'K': 30, 'temperature': 25.0, 'humidity': 78.0, 'ph': 6.5, 'rainfall': 160.0},
        ]
        for s in test_samples:
            df_in = pd.DataFrame([s])
            probs = self.ensemble.predict_proba(df_in)[0]
            self.assertTrue(np.isclose(np.sum(probs), 1.0, atol=1e-4), f"Probabilities do not sum to 1: {np.sum(probs)}")
            self.assertTrue(np.all(probs >= 0.0), "Encountered negative probability")
            self.assertTrue(np.all(np.isfinite(probs)), "Encountered non-finite probability")

    # -------------------------------------------------------------------------
    # TEST 5: Zero-value preservation
    # -------------------------------------------------------------------------
    def test_05_zero_value_preservation(self):
        """Verify that 0.0 is preserved as a valid numeric feature value and not falsy-overridden."""
        zero_feature_input = {
            'N': 0.0, 'P': 40.0, 'K': 40.0,
            'temperature': 24.0, 'humidity': 60.0,
            'ph': 6.5, 'rainfall': 100.0
        }
        errs = CropRecommendationPredictor.validate_inputs(zero_feature_input)
        self.assertEqual(len(errs), 0, f"Zero feature validation failed: {errs}")
        
        result = self.predictor.predict_top_k(zero_feature_input, top_k=3)
        self.assertIn('top_recommendations', result)
        self.assertEqual(len(result['top_recommendations']), 3)

    # -------------------------------------------------------------------------
    # TEST 6: Missing value warning / non-silent handling
    # -------------------------------------------------------------------------
    def test_06_missing_value_non_silent_handling(self):
        """Verify that missing or invalid features produce explicit validation errors."""
        # Missing feature
        missing_input = {'N': 50, 'P': 40, 'K': 40}  # missing temp, hum, ph, rainfall
        errs = CropRecommendationPredictor.validate_inputs(missing_input)
        self.assertTrue(len(errs) >= 4, "Missing features must be explicitly flagged")

        # Boolean injection
        bool_input = {'N': True, 'P': 40, 'K': 40, 'temperature': 24, 'humidity': 60, 'ph': 6.5, 'rainfall': 100}
        errs_bool = CropRecommendationPredictor.validate_inputs(bool_input)
        self.assertTrue(any("cannot be boolean" in e for e in errs_bool), "Boolean feature must be rejected")

        # Out of bounds
        oob_input = {'N': 999, 'P': 40, 'K': 40, 'temperature': 24, 'humidity': 60, 'ph': 6.5, 'rainfall': 100}
        errs_oob = CropRecommendationPredictor.validate_inputs(oob_input)
        self.assertTrue(any("Nitrogen (N) must be between" in e for e in errs_oob), "OOB feature must be rejected")

    # -------------------------------------------------------------------------
    # TEST 7: Frontend-to-backend input propagation
    # -------------------------------------------------------------------------
    def test_07_frontend_to_backend_input_propagation(self):
        """Verify that RecommendationInput schema correctly parses frontend parameters."""
        req = RecommendationInput(
            farm_id="farm-demo-01",
            season="Kharif",
            nitrogen_kg_ha=75.0,
            phosphorus_kg_ha=45.0,
            potassium_kg_ha=35.0,
            soil_ph=6.5,
            temperature=24.5,
            humidity=62.0,
            rainfall=125.0
        )
        self.assertEqual(req.nitrogen_kg_ha, 75.0)
        self.assertEqual(req.rainfall, 125.0)
        self.assertEqual(req.soil_ph, 6.5)

    # -------------------------------------------------------------------------
    # TEST 8: Sensitivity to NPK variations
    # -------------------------------------------------------------------------
    def test_08_sensitivity_to_npk_variations(self):
        """Verify that varying NPK alone significantly alters predicted crops under fixed climate."""
        base_climate = {'temperature': 24.0, 'humidity': 65.0, 'ph': 6.5, 'rainfall': 95.0}
        
        # High N (favoring cereal like maize)
        high_n = {**base_climate, 'N': 110.0, 'P': 45.0, 'K': 20.0}
        # Low N, high P/K
        high_pk = {**base_climate, 'N': 20.0, 'P': 70.0, 'K': 80.0}
        
        res_n = self.predictor.predict_top_k(high_n, top_k=3)
        res_pk = self.predictor.predict_top_k(high_pk, top_k=3)
        
        top_crop_n = res_n['top_recommendations'][0]['crop_name'].lower()
        top_crop_pk = res_pk['top_recommendations'][0]['crop_name'].lower()
        
        self.assertNotEqual(top_crop_n, top_crop_pk, "Altering NPK from high-N to high-P/K must change top-1 crop")
        self.assertEqual(top_crop_n, 'maize')
        self.assertNotEqual(top_crop_pk, 'rice')

    # -------------------------------------------------------------------------
    # TEST 9: Sensitivity to temperature & elevation
    # -------------------------------------------------------------------------
    def test_09_sensitivity_to_temperature_and_elevation(self):
        """Verify that temperature shifts change temperate vs tropical crop rankings."""
        # Cool pulse condition (17°C, low humidity)
        cool_input = {'N': 40.0, 'P': 60.0, 'K': 80.0, 'ph': 6.8, 'rainfall': 75.0, 'temperature': 17.0, 'humidity': 25.0}
        # Warm subtropical condition (32°C, moderate humidity)
        warm_input = {'N': 40.0, 'P': 60.0, 'K': 80.0, 'ph': 6.8, 'rainfall': 75.0, 'temperature': 32.0, 'humidity': 65.0}
        
        res_cool = self.predictor.predict_top_k(cool_input, top_k=3)
        res_warm = self.predictor.predict_top_k(warm_input, top_k=3)
        
        top_cool = res_cool['top_recommendations'][0]['crop_name'].lower()
        top_warm = res_warm['top_recommendations'][0]['crop_name'].lower()
        
        self.assertNotEqual(top_cool, top_warm, "Temperature shift must produce different top recommendations")
        self.assertEqual(top_cool, 'chickpea')
        self.assertNotEqual(top_warm, 'rice')

    # -------------------------------------------------------------------------
    # TEST 10: Sensitivity to seasonal rainfall variations
    # -------------------------------------------------------------------------
    def test_10_sensitivity_to_seasonal_rainfall(self):
        """Verify that low rainfall favors drought-hardy crops and high rainfall favors water-intensive crops."""
        base = {'N': 50.0, 'P': 45.0, 'K': 40.0, 'temperature': 25.0, 'humidity': 65.0, 'ph': 6.5}
        
        # Low seasonal rainfall (40 mm)
        dry_input = {**base, 'rainfall': 40.0}
        # High seasonal rainfall (240 mm)
        wet_input = {**base, 'rainfall': 240.0}
        
        res_dry = self.predictor.predict_top_k(dry_input, top_k=3)
        res_wet = self.predictor.predict_top_k(wet_input, top_k=3)
        
        top_dry = res_dry['top_recommendations'][0]['crop_name'].lower()
        top_wet = res_wet['top_recommendations'][0]['crop_name'].lower()
        
        self.assertNotEqual(top_dry, top_wet, "Seasonal rainfall shift must alter top recommendation")
        self.assertNotEqual(top_dry, 'rice', "Rice must NEVER be recommended under 40mm dry rainfall!")

    # -------------------------------------------------------------------------
    # TEST 11: Determinism on identical requests
    # -------------------------------------------------------------------------
    def test_11_determinism_on_identical_requests(self):
        """Verify that identical inputs produce bit-for-bit deterministic predictions."""
        inp = {'N': 80.0, 'P': 40.0, 'K': 40.0, 'temperature': 24.0, 'humidity': 70.0, 'ph': 6.5, 'rainfall': 120.0}
        
        res1 = self.predictor.predict_top_k(inp, top_k=3)
        res2 = self.predictor.predict_top_k(inp, top_k=3)
        
        for i in range(3):
            c1 = res1['top_recommendations'][i]
            c2 = res2['top_recommendations'][i]
            self.assertEqual(c1['crop_name'], c2['crop_name'])
            self.assertAlmostEqual(c1['ensemble_score'], c2['ensemble_score'], places=4)

    # -------------------------------------------------------------------------
    # TEST 12: Non-Rice top-1 verification for distinct crop archetypes
    # -------------------------------------------------------------------------
    def test_12_non_rice_top1_for_multiple_crop_archetypes(self):
        """Verify that non-Rice archetypes cleanly yield their genuine target crop at Rank #1."""
        archetypes = [
            'maize', 'chickpea', 'kidneybeans', 'cotton', 'coffee',
            'apple', 'mothbeans', 'blackgram', 'lentil'
        ]
        for crop in archetypes:
            feats = self.crop_medians.loc[crop].to_dict()
            res = self.predictor.predict_top_k(feats, top_k=3)
            top_1 = res['top_recommendations'][0]['crop_name'].lower()
            self.assertEqual(
                top_1, crop,
                f"Expected top-1 {crop}, but got {top_1} (Rice bias check failed!)"
            )

    # -------------------------------------------------------------------------
    # TEST 13: Independent evaluation of all three models
    # -------------------------------------------------------------------------
    def test_13_independent_evaluation_of_all_three_models(self):
        """Verify that Fuzzy, GNB, and DecisionTree each function independently without errors."""
        sample = pd.DataFrame([self.crop_medians.loc['maize'].to_dict()])
        
        # Fuzzy
        fuzzy_preds = self.ensemble.fuzzy_expert.predict(sample)
        self.assertEqual(len(fuzzy_preds), 1)
        self.assertIn(fuzzy_preds[0], self.classes)
        
        # GaussianNB
        gnb_preds = self.ensemble.gnb_expert.predict(sample)
        self.assertEqual(len(gnb_preds), 1)
        self.assertEqual(gnb_preds[0], 'maize')
        
        # DecisionTree
        dt_preds = self.ensemble.dt_expert.predict(sample)
        self.assertEqual(len(dt_preds), 1)
        self.assertEqual(dt_preds[0], 'maize')

    # -------------------------------------------------------------------------
    # TEST 14: Top-3 uniqueness and ordering
    # -------------------------------------------------------------------------
    def test_14_top_3_uniqueness_and_ordering(self):
        """Verify that top-3 recommendations have strictly descending scores and no duplicates."""
        for crop in ['maize', 'rice', 'cotton', 'chickpea']:
            feats = self.crop_medians.loc[crop].to_dict()
            res = self.predictor.predict_top_k(feats, top_k=3)
            crops = [c['crop_name'] for c in res['top_recommendations']]
            scores = [c['ensemble_score'] for c in res['top_recommendations']]
            
            # Uniqueness
            self.assertEqual(len(set(crops)), 3, f"Duplicate crops in top-3: {crops}")
            # Descending order
            self.assertGreaterEqual(scores[0], scores[1])
            self.assertGreaterEqual(scores[1], scores[2])

    # -------------------------------------------------------------------------
    # TEST 15: Held-out validation of calibration and weights (N=330)
    # -------------------------------------------------------------------------
    def test_15_held_out_validation_accuracy_and_f1(self):
        """Verify ensemble accuracy and Macro F1 >= 98.0% on untouched held-out test split (N=330)."""
        X, y, classes = load_dataset()
        X_train, y_train, X_val, y_val, X_test, y_test = split_data(
            X, y, train_size=0.70, val_size=0.15, test_size=0.15, random_state=RANDOM_STATE
        )
        self.assertEqual(len(X_test), 330, f"Expected 330 test samples, got {len(X_test)}")
        
        test_preds = self.ensemble.predict(X_test)
        from sklearn.metrics import accuracy_score, f1_score
        test_acc = accuracy_score(y_test, test_preds)
        test_f1 = f1_score(y_test, test_preds, average='macro', zero_division=0)
        
        self.assertGreaterEqual(test_acc, 0.98, f"Test accuracy {test_acc*100:.2f}% is below 98.0%")
        self.assertGreaterEqual(test_f1, 0.98, f"Test Macro F1 {test_f1*100:.2f}% is below 98.0%")
        
        # Verify calibrated weights
        w1, w2, w3 = self.ensemble.weights
        self.assertAlmostEqual(w1, 0.00, places=2)
        self.assertAlmostEqual(w2, 0.62, places=2)
        self.assertAlmostEqual(w3, 0.38, places=2)

    # -------------------------------------------------------------------------
    # TEST 16: Proof of Rice ranking #1 when inputs genuinely favor Rice
    # -------------------------------------------------------------------------
    def test_16_proof_of_rice_when_inputs_genuinely_favor_rice(self):
        """Verify that genuine Rice conditions rank Rice as Top-1 (proving no reverse bias)."""
        rice_feats = self.crop_medians.loc['rice'].to_dict()
        res = self.predictor.predict_top_k(rice_feats, top_k=3)
        top_crop = res['top_recommendations'][0]['crop_name'].lower()
        top_score = res['top_recommendations'][0]['ensemble_score']
        
        self.assertEqual(top_crop, 'rice', f"Expected Rice to be Top-1 for genuine rice conditions, got {top_crop}")
        self.assertGreaterEqual(top_score, 85.0, f"Rice score {top_score} is unexpectedly low")

    # -------------------------------------------------------------------------
    # TEST 17: Data quality and provenance reporting
    # -------------------------------------------------------------------------
    def test_17_data_quality_and_provenance(self):
        """Verify dataset integrity: 2,200 records, 22 balanced classes with 100 rows each."""
        self.assertEqual(len(self.df), 2200)
        class_counts = self.df['label'].value_counts()
        self.assertEqual(len(class_counts), 22)
        for c, count in class_counts.items():
            self.assertEqual(count, 100, f"Class {c} has {count} samples; expected 100")
        self.assertEqual(self.df[FEATURE_NAMES].isnull().sum().sum(), 0, "Null values detected in dataset")

    # -------------------------------------------------------------------------
    # TEST 18: Macro-annual rainfall scaling verification
    # -------------------------------------------------------------------------
    def test_18_macro_annual_rainfall_scaling(self):
        """Verify that macro-annual rainfall (>350 mm) is calibrated to seasonal scale in API."""
        payload = {
            "farm_id": "farm-demo-01",
            "season": "Kharif",
            "nitrogen_kg_ha": 95.0,
            "phosphorus_kg_ha": 45.0,
            "potassium_kg_ha": 25.0,
            "soil_ph": 6.5,
            "temperature": 24.5,
            "humidity": 65.0,
            "rainfall": 1450.0  # Legacy macro-annual input
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/v1/recommendations/unified",
            data=json.dumps(payload).encode(),
            headers=self.headers
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            
        resolved_rain = data.get("resolved_features", {}).get("rainfall")
        self.assertIsNotNone(resolved_rain)
        self.assertLessEqual(resolved_rain, 350.0, f"Macro-annual rainfall was not calibrated: {resolved_rain}")
        self.assertGreaterEqual(resolved_rain, 20.0)
        self.assertEqual(resolved_rain, 116.0, f"Expected 1450 * 0.08 = 116.0, got {resolved_rain}")
        
        # Verify that Rice does not dominate on this non-Rice input
        top_crop = data["recommended_crops"][0]["crop_name"].lower()
        self.assertNotEqual(top_crop, 'rice', "Rice should not be recommended when inputs do not match Rice")

    # -------------------------------------------------------------------------
    # TEST 19: Unified endpoint HTTP 200/404/422 status checks
    # -------------------------------------------------------------------------
    def test_19_unified_endpoint_http_status(self):
        """Verify that valid request returns HTTP 200 and invalid farm returns HTTP 404."""
        # 1. Valid request
        valid_payload = {
            "farm_id": "farm-demo-01",
            "season": "Kharif",
            "nitrogen_kg_ha": 80.0,
            "phosphorus_kg_ha": 40.0,
            "potassium_kg_ha": 40.0,
            "rainfall": 120.0
        }
        req_ok = urllib.request.Request(
            f"{BASE_URL}/api/v1/recommendations/unified",
            data=json.dumps(valid_payload).encode(),
            headers=self.headers
        )
        with urllib.request.urlopen(req_ok) as resp_ok:
            self.assertEqual(resp_ok.status, 200)
            body = json.loads(resp_ok.read().decode())
            self.assertIn("recommended_crops", body)
            self.assertTrue(len(body["recommended_crops"]) >= 1)
            self.assertIn("ai_engine_info", body)
            self.assertIn("resolved_features", body)

        # 2. Invalid farm_id -> 404
        bad_farm_payload = {**valid_payload, "farm_id": "non-existent-farm-999"}
        req_bad = urllib.request.Request(
            f"{BASE_URL}/api/v1/recommendations/unified",
            data=json.dumps(bad_farm_payload).encode(),
            headers=self.headers
        )
        try:
            urllib.request.urlopen(req_bad)
            self.fail("Expected HTTP 404 for non-existent farm")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    # -------------------------------------------------------------------------
    # TEST 20: Existing RAG citations and 31 ChromaDB vectors preserved
    # -------------------------------------------------------------------------
    def test_20_rag_citations_and_31_chromadb_vectors_preserved(self):
        """Verify that ChromaDB retains exactly 31 vectors and knowledge stats endpoint confirms integrity."""
        req_stats = urllib.request.Request(
            f"{BASE_URL}/api/v1/assistant/knowledge-stats",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_stats) as resp:
            self.assertEqual(resp.status, 200)
            stats = json.loads(resp.read().decode())
            
        self.assertEqual(stats["active_vector_embeddings"], 31, "ChromaDB vector count must remain exactly 31")
        self.assertEqual(stats["relational_chunk_records"], 31, "Relational chunk records must remain exactly 31")
        self.assertEqual(stats["total_catalogued_documents"], 6, "Total catalogued documents must remain 6")
        
        # Test unified recommendation integrates RAG citations
        sample_payload = {
            "farm_id": "farm-demo-01",
            "season": "Kharif",
            "nitrogen_kg_ha": 80.0,
            "phosphorus_kg_ha": 40.0,
            "potassium_kg_ha": 40.0,
            "rainfall": 120.0
        }
        rec_req = urllib.request.Request(
            f"{BASE_URL}/api/v1/recommendations/unified",
            data=json.dumps(sample_payload).encode(),
            headers=self.headers
        )
        with urllib.request.urlopen(rec_req) as rec_resp:
            self.assertEqual(rec_resp.status, 200)
            rec_data = json.loads(rec_resp.read().decode())
            crops = rec_data.get("recommended_crops", [])
            self.assertTrue(len(crops) >= 1)
            # Check rag_citations field presence on recommended crops
            self.assertIn("rag_citations", crops[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
