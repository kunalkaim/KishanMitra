import os
import json
import joblib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from app.ml.crop_recommendation.fuzzy_model import AgronomicFuzzyCropExpert
from app.ml.crop_recommendation.gaussian_nb import GaussianNBCropExpert
from app.ml.crop_recommendation.decision_tree import DecisionTreeCropExpert
from app.ml.crop_recommendation.ensemble import HybridWeightedCropEnsemble
from app.ml.crop_recommendation.explainability import CropExplainabilityEngine

import os
import json
import joblib
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from app.ml.crop_recommendation.fuzzy_model import AgronomicFuzzyCropExpert
from app.ml.crop_recommendation.gaussian_nb import GaussianNBCropExpert
from app.ml.crop_recommendation.decision_tree import DecisionTreeCropExpert
from app.ml.crop_recommendation.ensemble import HybridWeightedCropEnsemble
from app.ml.crop_recommendation.explainability import CropExplainabilityEngine

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", ".."))

DEFAULT_ARTIFACTS_DIR = os.environ.get(
    "MODEL_ARTIFACTS_DIR",
    os.path.join(_BACKEND_DIR, "model_artifacts", "crop_recommendation")
)
if not os.path.exists(DEFAULT_ARTIFACTS_DIR):
    # Fallback checks
    cand1 = os.path.join("model_artifacts", "crop_recommendation")
    cand2 = os.path.join("backend", "model_artifacts", "crop_recommendation")
    if os.path.exists(cand1):
        DEFAULT_ARTIFACTS_DIR = cand1
    elif os.path.exists(cand2):
        DEFAULT_ARTIFACTS_DIR = cand2


def to_json_serializable(val: Any) -> Any:
    """Recursively converts NumPy arrays, scalars, and non-serializable objects to native Python."""
    if isinstance(val, (np.ndarray, list)):
        return [to_json_serializable(x) for x in val]
    elif isinstance(val, dict):
        return {str(k): to_json_serializable(v) for k, v in val.items()}
    elif isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    elif isinstance(val, (np.floating, np.float64, np.float32)):
        return float(val)
    elif isinstance(val, np.bool_):
        return bool(val)
    elif isinstance(val, datetime):
        return val.isoformat()
    return val


class ModelRegistry:
    """
    Manages atomic serialization, validation, and versioning of trained model artifacts.
    Prevents corruption of production models by verifying complete round-trip loading
    before updating active metadata.
    """
    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = artifacts_dir or DEFAULT_ARTIFACTS_DIR
        self.fuzzy_dir = os.path.join(self.artifacts_dir, "fuzzy")
        self.gnb_dir = os.path.join(self.artifacts_dir, "gaussian_nb")
        self.dt_dir = os.path.join(self.artifacts_dir, "decision_tree")
        self.ensemble_dir = os.path.join(self.artifacts_dir, "ensemble")
        
        for d in [self.fuzzy_dir, self.gnb_dir, self.dt_dir, self.ensemble_dir]:
            os.makedirs(d, exist_ok=True)

    def save_models(
        self,
        fuzzy_expert: AgronomicFuzzyCropExpert,
        gnb_expert: GaussianNBCropExpert,
        dt_expert: DecisionTreeCropExpert,
        ensemble: HybridWeightedCropEnsemble,
        metadata: Dict[str, Any],
        version: str = "v1.1"
    ):
        """
        Safely serializes all three expert models and ensemble.
        Performs immediate round-trip validation and atomically updates active_model_metadata.json.
        """
        fuzzy_filename = f"fuzzy_expert_{version}.joblib"
        gnb_filename = f"gaussian_nb_{version}.joblib"
        dt_filename = f"decision_tree_{version}.joblib"
        ensemble_filename = f"ensemble_{version}.joblib"

        fuzzy_path = os.path.join(self.fuzzy_dir, fuzzy_filename)
        gnb_path = os.path.join(self.gnb_dir, gnb_filename)
        dt_path = os.path.join(self.dt_dir, dt_filename)
        ensemble_path = os.path.join(self.ensemble_dir, ensemble_filename)
        metadata_path = os.path.join(self.artifacts_dir, "active_model_metadata.json")
        temp_metadata_path = os.path.join(self.artifacts_dir, "active_model_metadata.json.tmp")

        # 1. Save all components
        fuzzy_expert.save(fuzzy_path)
        gnb_expert.save(gnb_path)
        dt_expert.save(dt_path)
        ensemble.save(ensemble_path)

        # 2. Round-trip validation check
        try:
            test_fuzzy = AgronomicFuzzyCropExpert.load(fuzzy_path)
            test_gnb = GaussianNBCropExpert.load(gnb_path)
            test_dt = DecisionTreeCropExpert.load(dt_path)
            test_ens = HybridWeightedCropEnsemble.load(ensemble_path, test_fuzzy, test_gnb, test_dt)
            assert len(test_ens.classes_) == len(ensemble.classes_)
        except Exception as e:
            raise RuntimeError(f"Artifact round-trip validation failed for version {version}: {e}")

        # 3. Assemble serializable metadata
        meta = {
            "model_version": version,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "classes": list(ensemble.classes_),
            "classes_count": len(ensemble.classes_),
            "feature_order": ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'],
            "ensemble_weights": [float(w) for w in ensemble.weights],
            "artifacts": {
                "fuzzy": fuzzy_filename,
                "gaussian_nb": gnb_filename,
                "decision_tree": dt_filename,
                "ensemble": ensemble_filename
            },
            "evaluation_metrics": to_json_serializable(metadata.get("evaluation_metrics", {})),
            "hyperparameters": to_json_serializable(metadata.get("hyperparameters", {})),
            "dataset_info": to_json_serializable(metadata.get("dataset_info", {}))
        }

        # 4. Atomic metadata replacement
        with open(temp_metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        if os.path.exists(metadata_path):
            os.replace(temp_metadata_path, metadata_path)
        else:
            os.rename(temp_metadata_path, metadata_path)

        print(f"Model artifacts and metadata for version {version} validated and activated successfully.")

    def load_active_ensemble(self) -> Optional[Tuple[HybridWeightedCropEnsemble, CropExplainabilityEngine, Dict[str, Any]]]:
        """Loads and initializes the active validated hybrid ensemble and explainability engine."""
        metadata_path = os.path.join(self.artifacts_dir, "active_model_metadata.json")
        if not os.path.exists(metadata_path):
            return None

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            artifacts = meta["artifacts"]
            
            # Resolve relative filenames
            def resolve_path(directory: str, stored_val: str) -> str:
                if os.path.isabs(stored_val) and os.path.exists(stored_val):
                    return stored_val
                # Extract basename
                basename = os.path.basename(stored_val)
                direct = os.path.join(directory, basename)
                if os.path.exists(direct):
                    return direct
                if os.path.exists(stored_val):
                    return stored_val
                raise FileNotFoundError(f"Artifact not found: {stored_val} in {directory}")

            fuzzy_file = resolve_path(self.fuzzy_dir, artifacts["fuzzy"])
            gnb_file = resolve_path(self.gnb_dir, artifacts["gaussian_nb"])
            dt_file = resolve_path(self.dt_dir, artifacts["decision_tree"])
            ensemble_file = resolve_path(self.ensemble_dir, artifacts["ensemble"])

            fuzzy = AgronomicFuzzyCropExpert.load(fuzzy_file)
            gnb = GaussianNBCropExpert.load(gnb_file)
            dt = DecisionTreeCropExpert.load(dt_file)
            ensemble = HybridWeightedCropEnsemble.load(ensemble_file, fuzzy, gnb, dt)
            explainer = CropExplainabilityEngine(ensemble)

            return ensemble, explainer, meta
        except Exception as e:
            print(f"Error loading active ensemble from {self.artifacts_dir}: {e}")
            return None
