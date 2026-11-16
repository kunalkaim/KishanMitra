import os
import numpy as np
from typing import Dict, Any, List, Optional
from app.ml.crop_recommendation.model_registry import ModelRegistry
from app.ml.crop_recommendation.ensemble import HybridWeightedCropEnsemble
from app.ml.crop_recommendation.explainability import CropExplainabilityEngine

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']


class CropRecommendationPredictor:
    """
    Singleton inference predictor for production FastAPI serving.
    Safely loads the active trained hybrid ensemble and explainability engine.
    """
    _instance: Optional['CropRecommendationPredictor'] = None

    def __init__(self, artifacts_dir: Optional[str] = None):
        self.registry = ModelRegistry(artifacts_dir) if artifacts_dir else ModelRegistry()
        self.ensemble: Optional[HybridWeightedCropEnsemble] = None
        self.explainer: Optional[CropExplainabilityEngine] = None
        self.metadata: Dict[str, Any] = {}
        self.is_ready = False
        self._load()

    def _load(self):
        loaded = self.registry.load_active_ensemble()
        if loaded:
            ensemble, explainer, metadata = loaded
            # Verify all essential sub-components are present and fitted
            if (
                ensemble is not None 
                and explainer is not None 
                and getattr(ensemble, 'fuzzy_expert', None) is not None
                and getattr(ensemble, 'gnb_expert', None) is not None
                and getattr(ensemble, 'dt_expert', None) is not None
                and getattr(ensemble.fuzzy_expert, 'is_fitted', False)
                and getattr(ensemble.gnb_expert, 'is_fitted', False)
                and getattr(ensemble.dt_expert, 'is_fitted', False)
            ):
                self.ensemble = ensemble
                self.explainer = explainer
                self.metadata = metadata
                self.is_ready = True
            else:
                self.is_ready = False
        else:
            self.is_ready = False

    @classmethod
    def get_instance(cls) -> 'CropRecommendationPredictor':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reload(cls):
        cls._instance = cls()
        return cls._instance

    @staticmethod
    def validate_inputs(features: Dict[str, Any]) -> List[str]:
        """
        Validates all 7 agricultural input features:
        - Absence of missing values
        - Numeric type enforcement (strict rejection of boolean types)
        - NaN / Inf rejection
        - Agronomic physical boundary checks
        """
        errors = []
        if not isinstance(features, dict):
            return ["Input features must be provided as a dictionary."]

        for feat in FEATURE_NAMES:
            if feat not in features or features[feat] is None:
                errors.append(f"Missing required agricultural feature: '{feat}'")
                continue

            val = features[feat]
            # Boolean is a subclass of int in Python; explicitly reject
            if type(val) is bool:
                errors.append(f"Feature '{feat}' cannot be boolean. Numeric value expected.")
                continue

            if not isinstance(val, (int, float, np.number)):
                errors.append(f"Feature '{feat}' must be numeric. Received type: {type(val).__name__}")
                continue

            float_val = float(val)
            if np.isnan(float_val):
                errors.append(f"Feature '{feat}' cannot be NaN (not-a-number).")
                continue

            if np.isinf(float_val):
                errors.append(f"Feature '{feat}' cannot be infinite.")
                continue

            # Agronomic physical boundary checks
            if feat == 'N' and (float_val < 0.0 or float_val > 300.0):
                errors.append(f"Nitrogen (N) must be between 0 and 300 kg/ha. Received: {float_val}")
            elif feat == 'P' and (float_val < 0.0 or float_val > 250.0):
                errors.append(f"Phosphorus (P) must be between 0 and 250 kg/ha. Received: {float_val}")
            elif feat == 'K' and (float_val < 0.0 or float_val > 300.0):
                errors.append(f"Potassium (K) must be between 0 and 300 kg/ha. Received: {float_val}")
            elif feat == 'ph' and (float_val < 3.0 or float_val > 10.0):
                errors.append(f"Soil pH must be between 3.0 and 10.0. Received: {float_val}")
            elif feat == 'humidity' and (float_val < 0.0 or float_val > 100.0):
                errors.append(f"Humidity must be between 0% and 100%. Received: {float_val}")
            elif feat == 'rainfall' and (float_val < 0.0 or float_val > 3000.0):
                errors.append(f"Rainfall must be between 0 and 3000 mm. Received: {float_val}")
            elif feat == 'temperature' and (float_val < -10.0 or float_val > 60.0):
                errors.append(f"Temperature must be between -10°C and 60°C. Received: {float_val}")

        return errors

    def predict_top_k(
        self,
        features: Dict[str, Any],
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Executes end-to-end inference using the trained hybrid ensemble.
        Returns top-k recommendations with explainability and model agreement.
        """
        if not self.is_ready or self.ensemble is None or self.explainer is None:
            raise RuntimeError(
                "Trained crop recommendation model is not available or incomplete. Please run training pipeline first."
            )

        validation_errors = self.validate_inputs(features)
        if validation_errors:
            raise ValueError(f"Input validation error(s): {'; '.join(validation_errors)}")

        num_classes = len(self.ensemble.classes_)
        if not isinstance(top_k, int) or top_k < 1 or top_k > num_classes:
            raise ValueError(f"top_k must be an integer between 1 and {num_classes}. Received: {top_k}")

        x_dict = {k: float(features[k]) for k in FEATURE_NAMES}
        explanation_result = self.explainer.explain_recommendation(x_dict, top_k=top_k)

        return {
            "status": "success",
            "model_version": self.metadata.get("model_version", "v1.1"),
            "trained_at": self.metadata.get("trained_at"),
            "classes_supported": num_classes,
            "classes": self.ensemble.classes_,
            "input_features": x_dict,
            "top_recommendations": explanation_result["top_crops"],
            "ensemble_weights": explanation_result["ensemble_weights"],
            "contrastive_analysis": explanation_result["contrastive_analysis"],
            "feature_importances": explanation_result["decision_tree_global_importances"],
            "is_demo": False
        }
