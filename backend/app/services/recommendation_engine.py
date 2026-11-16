from typing import List, Dict, Any
from app.models.crop import Crop
from app.schemas.recommendation import (
    RecommendationInput,
    RecommendationResultItem,
    RecommendationResponse,
    CultivationStep
)
import uuid
from datetime import datetime, timezone


class FuzzyLogicEngine:
    """
    Evaluates agronomic fuzzy membership degrees for continuous environmental variables:
    - Soil pH membership (Acidic, Optimal, Alkaline)
    - Soil Nitrogen, Phosphorus, Potassium
    """
    @staticmethod
    def calculate_ph_membership(actual_ph: float, min_ph: float, max_ph: float) -> float:
        optimal_mid = (min_ph + max_ph) / 2.0
        tolerance = (max_ph - min_ph) / 2.0
        if actual_ph < (min_ph - 0.5) or actual_ph > (max_ph + 0.5):
            return 0.1
        diff = abs(actual_ph - optimal_mid)
        score = max(0.2, 1.0 - (diff / (tolerance + 0.5)))
        return round(score * 100, 1)

    @staticmethod
    def calculate_nutrient_score(n: float, p: float, k: float) -> float:
        # Standard ideal soil benchmark for Himalayan hill soils: N: 280, P: 22, K: 200
        n_ratio = min(1.0, n / 280.0)
        p_ratio = min(1.0, p / 22.0)
        k_ratio = min(1.0, k / 200.0)
        return round(((n_ratio * 0.4) + (p_ratio * 0.3) + (k_ratio * 0.3)) * 100, 1)


class BayesianEngine:
    """
    Bayesian network prior estimation based on historical crop performance
    in Uttarakhand agro-climatic zones (Sub-tropical Plain, Sub-temperate Mid-hills, High Hills).
    """
    @staticmethod
    def calculate_prior_probability(crop_name: str, district: str, season: str) -> float:
        # Higher priors for indigenous Himalayan crops in hill districts
        hill_districts = ["Almora", "Pithoragarh", "Chamoli", "Tehri Garhwal", "Pauri Garhwal", "Rudraprayag", "Uttarkashi", "Bageshwar", "Champawat"]
        plains_districts = ["Haridwar", "Udham Singh Nagar", "Dehradun"]
        
        is_hill = district in hill_districts
        
        if "Millet" in crop_name or "Mandua" in crop_name or "Jhangora" in crop_name or "Rajma" in crop_name or "Black Soybean" in crop_name:
            prior = 0.92 if is_hill else 0.70
        elif "Basmati" in crop_name or "Wheat" in crop_name or "Mustard" in crop_name:
            prior = 0.94 if not is_hill else 0.75
        elif "Apple" in crop_name or "Potato" in crop_name:
            prior = 0.90 if is_hill else 0.40
        else:
            prior = 0.82
            
        return round(prior * 100, 1)


class DecisionTreeEngine:
    """
    Rule-based pruning: evaluates hard agronomic constraints like irrigation availability,
    budget ceiling, and climatic tolerance.
    """
    @staticmethod
    def evaluate_constraints(crop: Crop, budget: float, irrigation: bool) -> float:
        score = 100.0
        # If crop requires heavy water but farmer has no irrigation
        if crop.water_requirement_mm > 700 and not irrigation:
            score -= 35.0
        # If cultivation cost exceeds farmer's budget by > 20%
        if crop.cost_of_cultivation_per_acre > (budget * 1.2):
            score -= 25.0
        return max(30.0, round(score, 1))


class TriModelEnsembleService:
    """
    Decoupled Tri-Model Ensemble recommendation service.
    Combines Fuzzy Logic (35%), Bayesian Probability (35%), and Decision Tree (30%).
    """
    def __init__(self):
        self.fuzzy = FuzzyLogicEngine()
        self.bayesian = BayesianEngine()
        self.tree = DecisionTreeEngine()

    def generate_recommendations(
        self,
        request_input: RecommendationInput,
        crops: List[Crop],
        district: str = "Almora"
    ) -> RecommendationResponse:
        results: List[RecommendationResultItem] = []

        ph = request_input.soil_ph or 6.5
        n = request_input.nitrogen_kg_ha or 280.0
        p = request_input.phosphorus_kg_ha or 22.0
        k = request_input.potassium_kg_ha or 210.0

        for crop in crops:
            # 1. Fuzzy Logic Score
            ph_score = self.fuzzy.calculate_ph_membership(ph, crop.min_ph, crop.max_ph)
            nutrient_score = self.fuzzy.calculate_nutrient_score(n, p, k)
            fuzzy_score = round((ph_score * 0.6) + (nutrient_score * 0.4), 1)

            # 2. Bayesian Prior
            bayes_score = self.bayesian.calculate_prior_probability(crop.crop_name, district, request_input.season)

            # 3. Decision Tree Constraint Evaluation
            tree_score = self.tree.evaluate_constraints(crop, request_input.budget_per_acre, request_input.irrigation_available)

            # Legacy Heuristic Score (Note: Production recommendation uses CropRecommendationPredictor
            # with simplex-calibrated weights: Fuzzy: 0.00, GaussianNB: 0.62, Decision Tree: 0.38)
            ensemble_score = round((fuzzy_score * 0.35) + (bayes_score * 0.35) + (tree_score * 0.30), 1)

            # Economic projection
            avg_yield = crop.average_yield_quintal_per_acre
            est_cost = crop.cost_of_cultivation_per_acre
            # Projected mandi price heuristic
            price_heuristic = 3500.0 if "Millet" in crop.crop_name or "Rajma" in crop.crop_name else 2800.0
            gross_rev = avg_yield * price_heuristic
            net_prof = gross_rev - est_cost

            # Cultivation Steps
            steps = [
                CultivationStep(
                    phase="Seed Bed Preparation",
                    timeline="15-20 days prior to sowing",
                    action=f"Deep ploughing followed by 2 cross-harrowings. Incorporate 4-5 tonnes/acre well-rotted FYM.",
                    inputs="FYM / Compost, Trichoderma seed treatment"
                ),
                CultivationStep(
                    phase="Sowing & Basal Nutrition",
                    timeline=f"{crop.season} onset",
                    action=f"Sow treated seed at 3-4 cm depth with line spacing of 22.5 cm. Apply basal dose of NPK.",
                    inputs="Certified seed, Neem-coated Urea, SSP, MOP"
                ),
                CultivationStep(
                    phase="Vegetative Care & Weed Control",
                    timeline="25-35 DAS (Days After Sowing)",
                    action="Hand weeding or light hoeing to ensure soil aeration. First irrigation if dry spell exceeds 10 days.",
                    inputs="Manual weeding / mulching"
                ),
                CultivationStep(
                    phase="Maturity & Harvesting",
                    timeline=f"{crop.growing_duration_days} days post sowing",
                    action="Harvest when 85% of grain turns golden/straw color. Dry to 12% moisture before storage.",
                    inputs="Sickle / Thresher, moisture meter"
                )
            ]

            risk_factors = [
                f"Sensitivity to extreme rainfall deviations (> {crop.rainfall_max_mm} mm)",
                "Foliar blight risk during persistent high humidity conditions",
                "Market price volatility during peak mandi arrival weeks"
            ]

            results.append(
                RecommendationResultItem(
                    crop_id=crop.id,
                    crop_name=crop.crop_name,
                    hindi_name=crop.hindi_name,
                    category=crop.category,
                    suitability_score=ensemble_score,
                    fuzzy_score=fuzzy_score,
                    bayesian_probability=bayes_score,
                    decision_tree_score=tree_score,
                    rank=1,
                    reasoning_summary=f"Optimal match for {district} soils (pH {ph}) under {request_input.season} climatic conditions.",
                    agronomic_justification=f"Crop thrives in {crop.category} agronomic profiles with {crop.growing_duration_days} days duration and moderate water requirement of {crop.water_requirement_mm} mm.",
                    expected_yield_per_acre=avg_yield,
                    estimated_revenue_per_acre=gross_rev,
                    estimated_cost_per_acre=est_cost,
                    net_profit_per_acre=net_prof,
                    risk_factors=risk_factors,
                    cultivation_steps=steps
                )
            )

        # Sort descending by suitability score
        results.sort(key=lambda x: x.suitability_score, reverse=True)
        for idx, item in enumerate(results):
            item.rank = idx + 1

        return RecommendationResponse(
            request_id=str(uuid.uuid4()),
            farm_id=request_input.farm_id,
            district=district,
            season=request_input.season,
            is_demo=True,
            recommended_crops=results[:5],
            created_at=datetime.now(timezone.utc)
        )


recommendation_service = TriModelEnsembleService()
