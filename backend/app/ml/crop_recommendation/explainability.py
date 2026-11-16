import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from app.ml.crop_recommendation.ensemble import HybridWeightedCropEnsemble
from app.ml.crop_recommendation.fuzzy_model import AgronomicFuzzyCropExpert
from app.ml.crop_recommendation.gaussian_nb import GaussianNBCropExpert
from app.ml.crop_recommendation.decision_tree import DecisionTreeCropExpert

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

CROP_HINDI_NAMES = {
    'apple': 'सेब',
    'banana': 'केला',
    'blackgram': 'उड़द / काली दाल',
    'chickpea': 'चना',
    'coconut': 'नारियल',
    'coffee': 'कॉफी',
    'cotton': 'कपास',
    'grapes': 'अंगूर',
    'jute': 'पटसन / जूट',
    'kidneybeans': 'राजमा',
    'lentil': 'मसूर दाल',
    'maize': 'मक्का',
    'mango': 'आम',
    'mothbeans': 'मोठ दाल',
    'mungbean': 'मूंग दाल',
    'muskmelon': 'खरबूजा',
    'orange': 'संतरा / माल्टा',
    'papaya': 'पपीता',
    'pigeonpeas': 'अरहर / तूर दाल',
    'pomegranate': 'अनार',
    'rice': 'धान / चावल',
    'watermelon': 'तरबूज'
}


class CropExplainabilityEngine:
    """
    Transparent Explainable AI (XAI) engine for KisanMitra.
    Synthesizes rule-based fuzzy memberships, Bayesian likelihoods, 
    and decision tree feature contributions.
    """
    def __init__(self, ensemble: HybridWeightedCropEnsemble):
        self.ensemble = ensemble
        self.fuzzy_expert: AgronomicFuzzyCropExpert = ensemble.fuzzy_expert
        self.gnb_expert: GaussianNBCropExpert = ensemble.gnb_expert
        self.dt_expert: DecisionTreeCropExpert = ensemble.dt_expert
        self.classes = ensemble.classes_
        self.weights = ensemble.weights

    def explain_recommendation(
        self,
        input_features: Dict[str, float],
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Generates full XAI report for a single input record.
        """
        df_input = pd.DataFrame([input_features])[FEATURE_NAMES]
        
        # 1. Component predictions
        fuzzy_scores, gnb_probs, dt_probs = self.ensemble.predict_component_scores(df_input)
        fuzzy_scores = fuzzy_scores[0]
        gnb_probs = gnb_probs[0]
        dt_probs = dt_probs[0]

        # 2. Weighted ensemble scores
        w1, w2, w3 = self.weights
        ensemble_scores = (w1 * fuzzy_scores) + (w2 * gnb_probs) + (w3 * dt_probs)
        ensemble_scores = ensemble_scores / np.sum(ensemble_scores)

        # 3. Rank crops descending
        ranked_indices = np.argsort(ensemble_scores)[::-1]
        
        top_crops = []
        for rank_idx in range(top_k):
            c_idx = ranked_indices[rank_idx]
            crop_name = self.classes[c_idx]
            crop_score = float(ensemble_scores[c_idx])
            
            # Individual expert metrics
            f_score = float(fuzzy_scores[c_idx])
            g_prob = float(gnb_probs[c_idx])
            d_prob = float(dt_probs[c_idx])
            
            # Top choice of each expert
            fuzzy_top = self.classes[int(np.argmax(fuzzy_scores))]
            gnb_top = self.classes[int(np.argmax(gnb_probs))]
            dt_top = self.classes[int(np.argmax(dt_probs))]

            # Model Agreement
            agreeing_models = []
            if fuzzy_top == crop_name:
                agreeing_models.append("Fuzzy Logic")
            if gnb_top == crop_name:
                agreeing_models.append("Gaussian Naive Bayes")
            if dt_top == crop_name:
                agreeing_models.append("Decision Tree")

            agreement_pct = round(len(agreeing_models) / 3.0 * 100, 1)
            agreement_label = "Unanimous (3/3 Experts)" if len(agreeing_models) == 3 else (
                "Majority (2/3 Experts)" if len(agreeing_models) == 2 else "Expert Disagreement / Diverse Scoring"
            )

            # Feature-level contributions from Fuzzy profile
            crop_prof = self.fuzzy_expert.crop_profiles_.get(crop_name, {})
            feature_influences = []
            
            for feat in FEATURE_NAMES:
                val = input_features[feat]
                if feat in crop_prof:
                    compat_low = crop_prof[feat].get("observed_compat_lower", crop_prof[feat].get("optimal_low", 0.0))
                    compat_high = crop_prof[feat].get("observed_compat_upper", crop_prof[feat].get("optimal_high", 0.0))
                    mean_val = crop_prof[feat]["mean"]
                    mu = self.fuzzy_expert._compute_feature_membership(val, crop_prof[feat], feat)
                    
                    if compat_low <= val <= compat_high:
                        status = "Within Observed Band"
                        impact_score = round(mu * 100, 1)
                        desc = f"{feat} ({val:.1f}) falls within observed compatibility band [{compat_low:.1f} - {compat_high:.1f}]."
                    elif val < compat_low:
                        status = "Sub-optimal (Low)"
                        impact_score = round(mu * 100, 1)
                        desc = f"{feat} ({val:.1f}) is below observed compatibility band [{compat_low:.1f} - {compat_high:.1f}], training mean is {mean_val:.1f}."
                    else:
                        status = "Sub-optimal (High)"
                        impact_score = round(mu * 100, 1)
                        desc = f"{feat} ({val:.1f}) is above observed compatibility band [{compat_low:.1f} - {compat_high:.1f}], training mean is {mean_val:.1f}."
                        
                    feature_influences.append({
                        "feature": feat,
                        "value": float(val),
                        "observed_compatibility_range": [round(float(compat_low), 1), round(float(compat_high), 1)],
                        # Backward-compatibility alias
                        "optimal_range": [round(float(compat_low), 1), round(float(compat_high), 1)],
                        "membership_compatibility": round(float(mu * 100), 1),
                        "status": status,
                        "explanation": desc
                    })

            # Sort feature influences by compatibility descending
            feature_influences.sort(key=lambda x: x["membership_compatibility"], reverse=True)

            f_contrib = round(w1 * f_score * 100, 2)
            g_contrib = round(w2 * g_prob * 100, 2)
            d_contrib = round(w3 * d_prob * 100, 2)
            reconciled_score = round(f_contrib + g_contrib + d_contrib, 2)

            top_crops.append({
                "rank": rank_idx + 1,
                "crop_name": crop_name,
                "hindi_name": CROP_HINDI_NAMES.get(crop_name, crop_name),
                "ensemble_score": reconciled_score,
                "model_scores": {
                    "fuzzy_logic_score": round(f_score * 100, 2),
                    "gaussian_nb_prob": round(g_prob * 100, 2),
                    "decision_tree_prob": round(d_prob * 100, 2)
                },
                "weighted_contributions": {
                    "fuzzy_contribution": f_contrib,
                    "gaussian_nb_contribution": g_contrib,
                    "decision_tree_contribution": d_contrib
                },
                "model_agreement": {
                    "percentage": agreement_pct,
                    "label": agreement_label,
                    "supporting_models": agreeing_models,
                    "model_top_picks": {
                        "fuzzy_logic": fuzzy_top,
                        "gaussian_nb": gnb_top,
                        "decision_tree": dt_top
                    },
                    "note": "Measures tri-expert algorithmic consensus, not calibrated empirical certainty."
                },
                "why_recommended": (
                    f"{crop_name.capitalize()} achieves rank #{rank_idx + 1} with an ensemble suitability score of "
                    f"{reconciled_score:.1f}%. Supported with {agreement_label.lower()} across "
                    f"Gaussian Naive Bayes ({round(g_prob * 100, 1)}%), Decision Tree ({round(d_prob * 100, 1)}%), "
                    f"and Fuzzy agronomic membership ({round(f_score * 100, 1)}%)."
                ),
                "primary_favorable_factors": [
                    item["explanation"] for item in feature_influences if item["status"] == "Within Observed Band"
                ][:3],
                "limiting_factors": [
                    item["explanation"] for item in feature_influences if item["status"] != "Within Observed Band"
                ][:2],
                "detailed_feature_influences": feature_influences
            })

        # Contrastive Analysis: Top 1 vs Runner-up (Rank 2) and Excluded Crops
        contrastive_explanation = {}
        if len(ranked_indices) >= 2:
            runner_up_idx = ranked_indices[1]
            runner_up_crop = self.classes[runner_up_idx]
            runner_up_score = float(ensemble_scores[runner_up_idx])
            top_score = top_crops[0]["ensemble_score"]

            contrastive_explanation = {
                "runner_up_crop": runner_up_crop,
                "runner_up_hindi": CROP_HINDI_NAMES.get(runner_up_crop, runner_up_crop),
                "runner_up_score": round(runner_up_score * 100, 2),
                "score_deficit": round(top_score - (runner_up_score * 100), 2),
                "reason_not_selected": (
                    f"{runner_up_crop.capitalize()} is the immediate runner-up (Rank #2). "
                    f"It received a lower ensemble suitability score ({round(runner_up_score * 100, 1)}% vs "
                    f"{top_score}% for {top_crops[0]['crop_name']}) under the current input conditions."
                )
            }

        if len(ranked_indices) > top_k:
            first_excluded_idx = ranked_indices[top_k]
            first_excluded_crop = self.classes[first_excluded_idx]
            first_excluded_score = float(ensemble_scores[first_excluded_idx])
            contrastive_explanation["first_excluded_crop"] = {
                "crop_name": first_excluded_crop,
                "rank": top_k + 1,
                "score": round(first_excluded_score * 100, 2),
                "reason": (
                    f"{first_excluded_crop.capitalize()} placed #{top_k + 1} and fell outside the top-{top_k} display threshold."
                )
            }

        return {
            "top_crops": top_crops,
            "ensemble_weights": {
                "fuzzy_logic": round(w1, 3),
                "gaussian_nb": round(w2, 3),
                "decision_tree": round(w3, 3)
            },
            "contrastive_analysis": contrastive_explanation,
            "decision_tree_global_importances": self.dt_expert.get_feature_importances()
        }
