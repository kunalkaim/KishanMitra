import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.soil import SoilTest
from app.models.region import District
from app.models.weather import WeatherRecord
from app.models.market import Mandi, MarketPrice
from app.models.recommendation import RecommendationRequest, RecommendationResult
from app.schemas.recommendation import (
    RecommendationInput, RecommendationResponse, RecommendationResultItem, CultivationStep,
    UnifiedCropItem, UnifiedRecommendationResponse, RAGCitationItem
)
from app.ml.crop_recommendation.predictor import CropRecommendationPredictor
from app.services.weather_service import weather_service
from app.rag.retrieval.hybrid_retriever import HybridAgriculturalRetriever

router = APIRouter()

_rag_retriever: Optional[HybridAgriculturalRetriever] = None


def get_rag_retriever() -> HybridAgriculturalRetriever:
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = HybridAgriculturalRetriever()
    return _rag_retriever

# Default economic and agronomic benchmarks for catalog
CROP_ECONOMIC_BENCHMARKS = {
    'rice': {'yield': 18.0, 'cost': 22000.0, 'price': 4200.0, 'category': 'cereal', 'hindi': 'धान / चावल'},
    'maize': {'yield': 16.0, 'cost': 16000.0, 'price': 2400.0, 'category': 'cereal', 'hindi': 'मक्का'},
    'chickpea': {'yield': 9.5, 'cost': 14000.0, 'price': 5800.0, 'category': 'pulse', 'hindi': 'चना'},
    'kidneybeans': {'yield': 8.5, 'cost': 19000.0, 'price': 11800.0, 'category': 'pulse', 'hindi': 'राजमा'},
    'pigeonpeas': {'yield': 8.0, 'cost': 15000.0, 'price': 7200.0, 'category': 'pulse', 'hindi': 'अरहर / तूर दाल'},
    'mothbeans': {'yield': 6.5, 'cost': 11000.0, 'price': 6500.0, 'category': 'pulse', 'hindi': 'मोठ दाल'},
    'mungbean': {'yield': 7.0, 'cost': 12000.0, 'price': 7600.0, 'category': 'pulse', 'hindi': 'मूंग दाल'},
    'blackgram': {'yield': 7.5, 'cost': 12500.0, 'price': 7400.0, 'category': 'pulse', 'hindi': 'उड़द / काली दाल'},
    'lentil': {'yield': 8.0, 'cost': 13500.0, 'price': 6800.0, 'category': 'pulse', 'hindi': 'मसूर दाल'},
    'pomegranate': {'yield': 35.0, 'cost': 45000.0, 'price': 6500.0, 'category': 'fruit', 'hindi': 'अनार'},
    'banana': {'yield': 120.0, 'cost': 55000.0, 'price': 2200.0, 'category': 'fruit', 'hindi': 'केला'},
    'mango': {'yield': 40.0, 'cost': 35000.0, 'price': 4500.0, 'category': 'fruit', 'hindi': 'आम'},
    'grapes': {'yield': 55.0, 'cost': 60000.0, 'price': 5200.0, 'category': 'fruit', 'hindi': 'अंगूर'},
    'watermelon': {'yield': 80.0, 'cost': 24000.0, 'price': 1600.0, 'category': 'fruit', 'hindi': 'तरबूज'},
    'muskmelon': {'yield': 70.0, 'cost': 22000.0, 'price': 1900.0, 'category': 'fruit', 'hindi': 'खरबूजा'},
    'apple': {'yield': 45.0, 'cost': 50000.0, 'price': 7500.0, 'category': 'fruit', 'hindi': 'सेब'},
    'orange': {'yield': 50.0, 'cost': 38000.0, 'price': 4200.0, 'category': 'fruit', 'hindi': 'संतरा / माल्टा'},
    'papaya': {'yield': 90.0, 'cost': 32000.0, 'price': 2100.0, 'category': 'fruit', 'hindi': 'पपीता'},
    'coconut': {'yield': 60.0, 'cost': 30000.0, 'price': 3500.0, 'category': 'cash_crop', 'hindi': 'नारियल'},
    'cotton': {'yield': 11.0, 'cost': 26000.0, 'price': 6800.0, 'category': 'cash_crop', 'hindi': 'कपास'},
    'jute': {'yield': 14.0, 'cost': 18000.0, 'price': 4800.0, 'category': 'cash_crop', 'hindi': 'पटसन / जूट'},
    'coffee': {'yield': 8.0, 'cost': 42000.0, 'price': 18000.0, 'category': 'cash_crop', 'hindi': 'कॉफी'}
}


def get_or_create_crop(db: Session, crop_key: str) -> Crop:
    """Finds existing crop or provisions an entry in the Crop catalog."""
    crop_info = CROP_ECONOMIC_BENCHMARKS.get(crop_key, {
        'yield': 12.0, 'cost': 18000.0, 'price': 3500.0, 'category': 'cereal', 'hindi': crop_key.capitalize()
    })
    
    # Check by name ilike
    crop = db.query(Crop).filter(Crop.crop_name.ilike(f"%{crop_key}%")).first()
    if not crop:
        crop = Crop(
            id=str(uuid.uuid4()),
            crop_name=crop_key.capitalize(),
            scientific_name=f"{crop_key.capitalize()} sp.",
            hindi_name=crop_info['hindi'],
            category=crop_info['category'],
            season="Kharif",
            min_ph=5.5,
            max_ph=7.5,
            water_requirement_mm=600.0,
            growing_duration_days=115,
            average_yield_quintal_per_acre=crop_info['yield'],
            cost_of_cultivation_per_acre=crop_info['cost'],
            recommended_soil_types=["Alluvial Loam", "Sandy Loam", "Brown Forest Soil"]
        )
        db.add(crop)
        db.flush()
    return crop


@router.post("/", response_model=RecommendationResponse)
def generate_crop_recommendation(
    request_in: RecommendationInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes the validated Hybrid AI Crop Recommendation Engine (Fuzzy Logic + GaussianNB + Decision Tree).
    Features are strictly resolved using user inputs, latest farm soil tests, or verified meteorological records.
    Returns the top 3 recommended crops with explainability, individual model breakdown, and model agreement.
    """
    # 0. Check engine readiness
    predictor = CropRecommendationPredictor.get_instance()
    if not predictor.is_ready:
        predictor = CropRecommendationPredictor.reload()
        if not predictor.is_ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Hybrid AI crop recommendation engine is initializing or artifacts are not yet ready."
            )

    farm = db.query(Farm).filter(Farm.id == request_in.farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found.")

    if farm.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this farm record.")

    # 1. Resolve 7 input features with explicit priority:
    # Priority 1: User-supplied parameters (explicit None checks, 0 is valid)
    # Priority 2: Latest linked SoilTest for this farm
    # Priority 3: Verified District / Weather records
    latest_soil = (
        db.query(SoilTest)
        .filter(SoilTest.farm_id == farm.id)
        .order_by(SoilTest.test_date.desc())
        .first()
    )

    district_record = (
        db.query(District)
        .filter(District.district_name.ilike(f"%{farm.district}%"))
        .first()
    )

    latest_weather = (
        db.query(WeatherRecord)
        .filter(WeatherRecord.district_name.ilike(f"%{farm.district}%"))
        .order_by(WeatherRecord.recorded_date.desc())
        .first()
    )

    # Nitrogen (N)
    n_val = None
    if request_in.N is not None:
        n_val = float(request_in.N)
    elif request_in.nitrogen_kg_ha is not None:
        n_val = float(request_in.nitrogen_kg_ha)
    elif latest_soil and latest_soil.nitrogen_kg_ha is not None:
        n_val = float(latest_soil.nitrogen_kg_ha)

    # Phosphorus (P)
    p_val = None
    if request_in.P is not None:
        p_val = float(request_in.P)
    elif request_in.phosphorus_kg_ha is not None:
        p_val = float(request_in.phosphorus_kg_ha)
    elif latest_soil and latest_soil.phosphorus_kg_ha is not None:
        p_val = float(latest_soil.phosphorus_kg_ha)

    # Potassium (K)
    k_val = None
    if request_in.K is not None:
        k_val = float(request_in.K)
    elif request_in.potassium_kg_ha is not None:
        k_val = float(request_in.potassium_kg_ha)
    elif latest_soil and latest_soil.potassium_kg_ha is not None:
        k_val = float(latest_soil.potassium_kg_ha)

    # Soil pH
    ph_val = None
    if request_in.ph is not None:
        ph_val = float(request_in.ph)
    elif request_in.soil_ph is not None:
        ph_val = float(request_in.soil_ph)
    elif latest_soil and latest_soil.soil_ph is not None:
        ph_val = float(latest_soil.soil_ph)

    # Temperature
    temp_val = None
    if request_in.temperature is not None:
        temp_val = float(request_in.temperature)
    elif latest_weather and latest_weather.temperature_min_c is not None and latest_weather.temperature_max_c is not None:
        temp_val = float((latest_weather.temperature_min_c + latest_weather.temperature_max_c) / 2.0)

    # Humidity
    humidity_val = None
    if request_in.humidity is not None:
        humidity_val = float(request_in.humidity)
    elif latest_weather and latest_weather.humidity_percent is not None:
        humidity_val = float(latest_weather.humidity_percent)

    # Rainfall
    rainfall_val = None
    if request_in.rainfall is not None:
        raw_rf = float(request_in.rainfall)
        if raw_rf > 350.0:
            s_factor = 0.08 if request_in.season and request_in.season.lower() == "kharif" else 0.06
            rainfall_val = round(min(280.0, max(25.0, raw_rf * s_factor)), 1)
        else:
            rainfall_val = raw_rf
    elif latest_weather and latest_weather.rainfall_mm is not None and latest_weather.rainfall_mm > 0:
        rainfall_val = float(latest_weather.rainfall_mm)
    elif district_record and district_record.average_annual_rainfall_mm is not None:
        rainfall_val = round(float(district_record.average_annual_rainfall_mm * 0.08), 1)

    resolved_features = {
        'N': n_val,
        'P': p_val,
        'K': k_val,
        'temperature': temp_val,
        'humidity': humidity_val,
        'ph': ph_val,
        'rainfall': rainfall_val
    }

    missing_fields = [feat for feat, val in resolved_features.items() if val is None]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Missing required agronomic features",
                "missing_fields": missing_fields,
                "message": (
                    f"Features {missing_fields} could not be resolved from user input, farm soil tests, "
                    f"or verified meteorological records for {farm.district}. Please provide them explicitly."
                )
            }
        )

    # 2. Invoke real trained ML predictor
    try:
        prediction_result = predictor.predict_top_k(resolved_features, top_k=3)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference Engine Error: {str(e)}"
        )

    # 3. Create database records in safe transaction
    try:
        rec_req = RecommendationRequest(
            id=str(uuid.uuid4()),
            farmer_id=current_user.id,
            farm_id=farm.id,
            soil_test_id=latest_soil.id if latest_soil else None,
            season=request_in.season,
            target_market=request_in.target_market,
            budget_per_acre=request_in.budget_per_acre,
            irrigation_available=request_in.irrigation_available
        )
        db.add(rec_req)
        db.flush()

        top_items: List[RecommendationResultItem] = []
        
        for rec in prediction_result["top_recommendations"]:
            crop_key = rec["crop_name"].lower().strip()
            crop_db = get_or_create_crop(db, crop_key)
            
            econ = CROP_ECONOMIC_BENCHMARKS.get(crop_key, {
                'yield': crop_db.average_yield_quintal_per_acre,
                'cost': crop_db.cost_of_cultivation_per_acre,
                'price': 3500.0
            })

            avg_yield = econ['yield']
            cost_per_acre = econ['cost']
            rev_per_acre = avg_yield * econ['price']
            profit_per_acre = rev_per_acre - cost_per_acre

            cultivation_steps = [
                CultivationStep(
                    phase="Land Preparation & Basal Nutrition",
                    timeline="15-20 days before sowing",
                    action=f"Deep ploughing followed by 2 harrowings. Incorporate well-decomposed organic manure for {crop_db.crop_name}.",
                    inputs="Compost / FYM, Trichoderma viride"
                ),
                CultivationStep(
                    phase="Sowing & Spacing",
                    timeline=f"{request_in.season} onset",
                    action="Line sowing at recommended row spacing. Maintain optimal depth of 3-4 cm.",
                    inputs="Certified seed, Rhizobium/Azotobacter biofertilizer"
                ),
                CultivationStep(
                    phase="Canopy Care & Weed Eradication",
                    timeline="25-35 DAS",
                    action="Hand weeding or light hoeing. First critical irrigation if rain spell delays > 10 days.",
                    inputs="Manual weeding tools / Mulch"
                ),
                CultivationStep(
                    phase="Harvest & Drying",
                    timeline="Physiological maturity",
                    action="Harvest during clear morning hours. Sun dry grains to safe moisture before storage.",
                    inputs="Moisture meter, Clean jute bags"
                )
            ]

            risk_factors = [
                f"Foliar fungal risk if relative humidity exceeds 85% for prolonged spells.",
                f"Sensitivity to extreme seasonal rainfall deviations outside optimal band.",
                f"Market price variance during peak mandi arrival weeks."
            ]

            result_item = RecommendationResultItem(
                crop_id=crop_db.id,
                crop_name=crop_db.crop_name,
                hindi_name=crop_db.hindi_name,
                category=crop_db.category,
                suitability_score=rec["ensemble_score"],
                fuzzy_score=rec["model_scores"]["fuzzy_logic_score"],
                bayesian_probability=rec["model_scores"]["gaussian_nb_prob"],
                decision_tree_score=rec["model_scores"]["decision_tree_prob"],
                rank=rec["rank"],
                reasoning_summary=rec["why_recommended"],
                agronomic_justification=rec["why_recommended"],
                expected_yield_per_acre=avg_yield,
                estimated_revenue_per_acre=rev_per_acre,
                estimated_cost_per_acre=cost_per_acre,
                net_profit_per_acre=profit_per_acre,
                risk_factors=risk_factors,
                cultivation_steps=cultivation_steps,
                model_agreement=rec["model_agreement"]["label"],
                why_recommended=rec["why_recommended"],
                primary_favorable_factors=rec.get("primary_favorable_factors", []),
                limiting_factors=rec.get("limiting_factors", []),
                weighted_contributions=rec.get("weighted_contributions"),
                detailed_feature_influences=rec.get("detailed_feature_influences", [])
            )
            top_items.append(result_item)

            # Persist result record
            db_res = RecommendationResult(
                request_id=rec_req.id,
                crop_id=crop_db.id,
                suitability_score=rec["ensemble_score"],
                fuzzy_score=rec["model_scores"]["fuzzy_logic_score"],
                bayesian_probability=rec["model_scores"]["gaussian_nb_prob"],
                decision_tree_score=rec["model_scores"]["decision_tree_prob"],
                rank=rec["rank"],
                reasoning_summary=rec["why_recommended"],
                agronomic_justification=rec["why_recommended"],
                economic_projection={
                    "expected_yield_per_acre": avg_yield,
                    "estimated_cost_per_acre": cost_per_acre,
                    "estimated_revenue_per_acre": rev_per_acre,
                    "net_profit_per_acre": profit_per_acre,
                    "benchmark_provenance": "ICAR/GBPUAT Regional Crop Catalog Reference (Non-guaranteed estimate)"
                },
                risk_factors=risk_factors,
                cultivation_steps=[s.model_dump() for s in cultivation_steps]
            )
            db.add(db_res)

        db.commit()
    except Exception as db_err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database transaction failure: {str(db_err)}"
        )

    return RecommendationResponse(
        request_id=rec_req.id,
        farm_id=farm.id,
        district=farm.district,
        season=request_in.season,
        is_demo=False,
        model_version=prediction_result["model_version"],
        ai_engine_info={
            "ensemble_architecture": "Fuzzy Logic + Gaussian Naive Bayes + Decision Tree",
            "ensemble_weights": prediction_result["ensemble_weights"],
            "trained_at": prediction_result["trained_at"],
            "classes_supported": prediction_result.get("classes_supported", 22),
            "is_production_ml": True
        },
        recommended_crops=top_items,
        contrastive_analysis=prediction_result.get("contrastive_analysis"),
        feature_importances=prediction_result.get("feature_importances"),
        created_at=rec_req.created_at
    )


@router.get("/history", response_model=List[RecommendationResponse])
def get_recommendation_history(
    farm_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves previous recommendation history for the authenticated farmer."""
    query = db.query(RecommendationRequest).filter(RecommendationRequest.farmer_id == current_user.id)
    if farm_id:
        query = query.filter(RecommendationRequest.farm_id == farm_id)
    requests = query.order_by(RecommendationRequest.created_at.desc()).limit(10).all()

    history: List[RecommendationResponse] = []
    for req in requests:
        rec_items = []
        for r in req.results:
            crop = r.crop
            rec_items.append(
                RecommendationResultItem(
                    crop_id=r.crop_id,
                    crop_name=crop.crop_name if crop else "Crop",
                    hindi_name=crop.hindi_name if crop else "फसल",
                    category=crop.category if crop else "cereal",
                    suitability_score=r.suitability_score,
                    fuzzy_score=r.fuzzy_score,
                    bayesian_probability=r.bayesian_probability,
                    decision_tree_score=r.decision_tree_score,
                    rank=r.rank,
                    reasoning_summary=r.reasoning_summary,
                    agronomic_justification=r.agronomic_justification,
                    expected_yield_per_acre=r.economic_projection.get("expected_yield_per_acre", 15.0),
                    estimated_revenue_per_acre=r.economic_projection.get("estimated_revenue_per_acre", 45000.0),
                    estimated_cost_per_acre=r.economic_projection.get("estimated_cost_per_acre", 20000.0),
                    net_profit_per_acre=r.economic_projection.get("net_profit_per_acre", 25000.0),
                    risk_factors=r.risk_factors or [],
                    cultivation_steps=[
                        CultivationStep(**s) if isinstance(s, dict) else s for s in (r.cultivation_steps or [])
                    ]
                )
            )
        history.append(
            RecommendationResponse(
                request_id=req.id,
                farm_id=req.farm_id,
                district=req.farm.district if req.farm else "Uttarakhand",
                season=req.season,
                is_demo=False,
                model_version="v1.0-HybridEnsemble",
                recommended_crops=rec_items,
                created_at=req.created_at
            )
        )
    return history


@router.post("/unified", response_model=UnifiedRecommendationResponse)
def generate_unified_crop_recommendation(
    request_in: RecommendationInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unified Agricultural Decision Intelligence Endpoint.
    Orchestrates:
    1. Hybrid ML Crop Recommendation Engine v1.1 (Fuzzy 0.35 + GNB 0.35 + DT 0.30)
    2. Contextualized RAG Knowledge Retrieval (31 ChromaDB vectors: GBPUAT & ICAR-VPKAS)
    3. Dynamic APMC Mandi Market Economics (District modal rates, BCR, Breakeven thresholds)
    4. Elevation-Calibrated Agro-Meteorological Telemetry & Regional Risk Advisory
    """
    # 0. Engine readiness check
    predictor = CropRecommendationPredictor.get_instance()
    if not predictor.is_ready:
        predictor = CropRecommendationPredictor.reload()
        if not predictor.is_ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Hybrid AI crop recommendation engine is initializing or artifacts are not yet ready."
            )

    farm = db.query(Farm).filter(Farm.id == request_in.farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found.")

    if farm.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this farm record.")

    # 1. Feature resolution with source tracking
    latest_soil = (
        db.query(SoilTest)
        .filter(SoilTest.farm_id == farm.id)
        .order_by(SoilTest.test_date.desc())
        .first()
    )

    district_record = (
        db.query(District)
        .filter(District.district_name.ilike(f"%{farm.district}%"))
        .first()
    )

    latest_weather = (
        db.query(WeatherRecord)
        .filter(WeatherRecord.district_name.ilike(f"%{farm.district}%"))
        .order_by(WeatherRecord.recorded_date.desc())
        .first()
    )

    # Resolve NPK & pH
    n_val = request_in.N if request_in.N is not None else (
        request_in.nitrogen_kg_ha if request_in.nitrogen_kg_ha is not None else (
            float(latest_soil.nitrogen_kg_ha) if latest_soil and latest_soil.nitrogen_kg_ha is not None else None
        )
    )
    p_val = request_in.P if request_in.P is not None else (
        request_in.phosphorus_kg_ha if request_in.phosphorus_kg_ha is not None else (
            float(latest_soil.phosphorus_kg_ha) if latest_soil and latest_soil.phosphorus_kg_ha is not None else None
        )
    )
    k_val = request_in.K if request_in.K is not None else (
        request_in.potassium_kg_ha if request_in.potassium_kg_ha is not None else (
            float(latest_soil.potassium_kg_ha) if latest_soil and latest_soil.potassium_kg_ha is not None else None
        )
    )
    ph_val = request_in.ph if request_in.ph is not None else (
        request_in.soil_ph if request_in.soil_ph is not None else (
            float(latest_soil.soil_ph) if latest_soil and latest_soil.soil_ph is not None else None
        )
    )

    if latest_soil and request_in.N is None:
        soil_source = f"Farm Soil Test ({latest_soil.test_date.strftime('%Y-%m-%d')})"
        soil_status = "verified_farm_soil_card"
    elif request_in.N is not None:
        soil_source = "Farmer Direct Parameter Input"
        soil_status = "direct_user_input"
    else:
        soil_source = "Regional Benchmark Default (No Soil Test Card Linked - Standard Mid-Hills Nutrient Profile)"
        soil_status = "imputed_regional_default"

    # Resolve Weather (temperature, humidity, rainfall)
    temp_val = request_in.temperature if request_in.temperature is not None else (
        float((latest_weather.temperature_min_c + latest_weather.temperature_max_c) / 2.0)
        if latest_weather and latest_weather.temperature_min_c is not None and latest_weather.temperature_max_c is not None else 22.0
    )
    humidity_val = request_in.humidity if request_in.humidity is not None else (
        float(latest_weather.humidity_percent) if latest_weather and latest_weather.humidity_percent is not None else 65.0
    )
    # ML model expects seasonal/crop-cycle aggregate rainfall (mean 103.5mm, range 20-300mm).
    # Open-Meteo telemetry provides daily precipitation (0-5mm), which must NOT be passed directly as seasonal rainfall.
    rainfall_override = request_in.rainfall if request_in.rainfall is not None else getattr(request_in, "rainfall_mm", None)
    if rainfall_override is not None:
        raw_rf = float(rainfall_override)
        # Handle annual macro-rainfall input scale if passed (e.g. > 350mm) to prevent right-tail probability distortion
        if raw_rf > 350.0:
            seasonal_factor = 0.08 if request_in.season and request_in.season.lower() == "kharif" else 0.06
            rainfall_val = round(min(280.0, max(25.0, raw_rf * seasonal_factor)), 1)
            rainfall_mode = "calibrated_from_macro_annual_input"
        else:
            rainfall_val = round(max(20.0, min(300.0, raw_rf)), 1)
            rainfall_mode = "explicit_seasonal_crop_cycle_input"
    elif district_record and district_record.average_annual_rainfall_mm:
        # Calibrated seasonal rainfall based on Uttarakhand cropping season
        seasonal_factor = 0.08
        if request_in.season and request_in.season.lower() == "kharif":
            seasonal_factor = 0.08
        elif request_in.season and request_in.season.lower() == "rabi":
            seasonal_factor = 0.06
        rainfall_val = round(float(district_record.average_annual_rainfall_mm * seasonal_factor), 1)
        rainfall_mode = "district_climatological_seasonal"
    else:
        rainfall_val = 120.0  # Climatological baseline for Uttarakhand mid-hills
        rainfall_mode = "regional_mid_hills_baseline"

    elevation = farm.elevation_meters or 1250.0
    weather_source = f"{farm.district} Agromet Telemetry ({int(elevation)}m ASL)"

    resolved_features = {
        'N': n_val if n_val is not None else 120.0,
        'P': p_val if p_val is not None else 40.0,
        'K': k_val if k_val is not None else 45.0,
        'temperature': temp_val,
        'humidity': humidity_val,
        'ph': ph_val if ph_val is not None else 6.5,
        'rainfall': rainfall_val
    }

    # 2. Invoke real trained ML predictor with proper validation error handling
    try:
        prediction_result = predictor.predict_top_k(resolved_features, top_k=3)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid feature inputs for crop recommendation: {str(ve)}"
        )

    # 3. Weather telemetry and district alerts
    weather_data = weather_service.get_district_weather(farm.district)
    agromet_alert = weather_data.agricultural_alert

    # 4. RAG Knowledge Retriever
    retriever = get_rag_retriever()

    # 5. Build Unified Crop Items
    unified_items: List[UnifiedCropItem] = []
    
    # Save recommendation request in DB
    rec_req = RecommendationRequest(
        id=str(uuid.uuid4()),
        farmer_id=current_user.id,
        farm_id=farm.id,
        soil_test_id=latest_soil.id if latest_soil else None,
        season=request_in.season,
        target_market=request_in.target_market,
        budget_per_acre=request_in.budget_per_acre,
        irrigation_available=request_in.irrigation_available
    )
    db.add(rec_req)
    db.flush()

    for rec in prediction_result["top_recommendations"]:
        crop_key = rec["crop_name"].lower().strip()
        crop_db = get_or_create_crop(db, crop_key)

        # 5a. RAG Knowledge Cross-Referencing
        rag_citations: List[RAGCitationItem] = []
        verified_practices: List[str] = []
        try:
            rag_chunks = retriever.retrieve(
                query=f"{crop_db.crop_name} {crop_db.hindi_name} cultivation advisory Uttarakhand",
                top_k=2,
                crop_filter=crop_db.crop_name
            )
            # Enforce similarity cutoff (>= 0.60) to prevent citation leakage for uncovered crops
            valid_rag_chunks = [rc for rc in rag_chunks if rc.get("hybrid_score", 0.0) >= 0.60]
            for rc in valid_rag_chunks:
                cit = rc.get("citation", {})
                snippet_text = rc.get("text", "")
                rag_citations.append(
                    RAGCitationItem(
                        document_title=cit.get("document_title", "Agricultural Extension Bulletin"),
                        publisher=cit.get("publisher", "GBPUAT Pantnagar / ICAR-VPKAS Almora"),
                        publication_date=cit.get("publication_date", "2025-2026"),
                        page_start=int(cit.get("page_start", 1)) if str(cit.get("page_start", 1)).isdigit() else 1,
                        page_end=int(cit.get("page_end", 1)) if str(cit.get("page_end", 1)).isdigit() else 1,
                        source_url=cit.get("source_url") or "",
                        is_historical=cit.get("is_historical", False),
                        retrieval_score=round(rc.get("hybrid_score", 0.5) * 100, 1),
                        snippet=snippet_text[:280] + ("..." if len(snippet_text) > 280 else "")
                    )
                )
                # Extract first verified sentence
                sentences = [s.strip() for s in snippet_text.split(".") if len(s.strip()) > 30]
                if sentences and len(verified_practices) < 2:
                    verified_practices.append(sentences[0] + ".")
        except Exception:
            pass

        if not verified_practices:
            verified_practices.append(
                f"Follow official package of practices from GBPUAT Pantnagar / ICAR-VPKAS for {crop_db.crop_name} in {farm.district}."
            )

        # 5b. Dynamic Mandi & Economics
        mkt_record = (
            db.query(MarketPrice)
            .join(Mandi)
            .join(Crop)
            .filter(Crop.id == crop_db.id)
            .filter(Mandi.district_name.ilike(f"%{farm.district}%"))
            .order_by(MarketPrice.arrival_date.desc())
            .first()
        )
        if not mkt_record:
            mkt_record = (
                db.query(MarketPrice)
                .join(Mandi)
                .join(Crop)
                .filter(Crop.id == crop_db.id)
                .order_by(MarketPrice.arrival_date.desc())
                .first()
            )

        econ_benchmarks = CROP_ECONOMIC_BENCHMARKS.get(crop_key, {
            'yield': crop_db.average_yield_quintal_per_acre or 14.0,
            'cost': crop_db.cost_of_cultivation_per_acre or 18000.0,
            'price': 3500.0
        })

        if mkt_record:
            mandi_name = f"{mkt_record.mandi.mandi_name} ({mkt_record.mandi.district_name})"
            modal_price = mkt_record.modal_price_per_quintal
            trend = "rising" if modal_price > 3000 else "stable"
            is_benchmark = False
        else:
            mandi_name = f"State APMC Benchmark ({farm.district} Region)"
            modal_price = econ_benchmarks['price']
            trend = "stable"
            is_benchmark = True

        expected_yield = econ_benchmarks['yield']
        cost_per_acre = econ_benchmarks['cost']
        gross_rev = round(expected_yield * modal_price, 2)
        net_profit = round(gross_rev - cost_per_acre, 2)
        bcr = round(gross_rev / cost_per_acre, 2) if cost_per_acre > 0 else 1.0
        breakeven_yield = round(cost_per_acre / modal_price, 2) if modal_price > 0 else 0.0
        breakeven_price = round(cost_per_acre / expected_yield, 2) if expected_yield > 0 else 0.0

        if is_benchmark:
            economic_disclaimer = (
                f"Financial projections are non-guaranteed estimates based on state-level APMC benchmark constants for {crop_db.crop_name}. "
                f"No direct spot market arrivals were recorded in {farm.district} mandis for this commodity. "
                "Actual returns will depend on localized harvesting windows, transport costs, and farmgate negotiation."
            )
        else:
            economic_disclaimer = (
                f"Financial projections are non-guaranteed estimates derived from recent APMC mandi spot arrivals at {mandi_name}. "
                "Actual farm yields and net returns depend on micro-climate, seasonal rainfall distribution, "
                "input quality, and auction day price fluctuations."
            )

        # 5c. Agro-Meteorological Suitability & Risks
        weather_flag = "Optimal"
        if resolved_features['humidity'] > 78.0:
            weather_flag = "Watch Alert"
        elif resolved_features['rainfall'] < 80.0 and not request_in.irrigation_available:
            weather_flag = "Moisture Deficit"

        agronomic_risks = [
            f"Foliar fungal risk if relative humidity remains above 78% during flowering and pod/grain filling.",
            f"Elevation thermal envelope: optimal for mid-to-high hill terraced farming at {int(elevation)}m ASL.",
            f"Market arrival variance: modal prices at {mandi_name} may fluctuate during peak harvest weeks."
        ]

        cultivation_steps = [
            CultivationStep(
                phase="Land Preparation & Basal Nutrition",
                timeline="15-20 days before sowing",
                action=f"Deep summer ploughing followed by 2 cross-harrowings. Incorporate well-decomposed FYM/compost for {crop_db.crop_name}.",
                inputs="Compost / FYM (5-8 tonnes/acre), Trichoderma viride"
            ),
            CultivationStep(
                phase="Sowing & Spacing Geometry",
                timeline=f"{request_in.season} onset",
                action="Line sowing at recommended row spacing to ensure optimal plant population and light interception.",
                inputs="Certified university-recommended seed, Biofertilizer (Rhizobium/Azotobacter)"
            ),
            CultivationStep(
                phase="Canopy Health & Weed Management",
                timeline="25-35 DAS",
                action="Hand hoeing or weeding. Provide protective irrigation if monsoon dry spell exceeds 10 days.",
                inputs="Organic mulch / Manual weeding implements"
            ),
            CultivationStep(
                phase="Harvest & Post-Harvest Storage",
                timeline="Physiological maturity",
                action="Harvest during clear morning weather. Dry grains to below 12% moisture before storage in clean bags.",
                inputs="Moisture meter, Clean jute bags"
            )
        ]

        item = UnifiedCropItem(
            crop_id=crop_db.id,
            crop_name=crop_db.crop_name,
            hindi_name=crop_db.hindi_name,
            category=crop_db.category,
            suitability_score=rec["ensemble_score"],
            rank=rec["rank"],
            model_agreement=rec["model_agreement"]["label"],
            model_scores={
                "fuzzy_logic": rec["model_scores"]["fuzzy_logic_score"],
                "gaussian_nb": rec["model_scores"]["gaussian_nb_prob"],
                "decision_tree": rec["model_scores"]["decision_tree_prob"]
            },
            why_recommended=rec["why_recommended"],
            primary_favorable_factors=rec.get("primary_favorable_factors", []),
            limiting_factors=rec.get("limiting_factors", []),
            contrastive_insight=prediction_result.get("contrastive_analysis", {}).get("distinguishing_insights"),
            detailed_feature_influences=rec.get("detailed_feature_influences", []),
            verified_package_of_practices=verified_practices,
            rag_citations=rag_citations,
            mandi_name=mandi_name,
            modal_price_per_quintal=modal_price,
            price_trend=trend,
            expected_yield_per_acre=expected_yield,
            estimated_cost_per_acre=cost_per_acre,
            estimated_gross_revenue=gross_rev,
            estimated_net_profit=net_profit,
            benefit_cost_ratio=bcr,
            breakeven_yield_per_acre=breakeven_yield,
            breakeven_price_per_quintal=breakeven_price,
            economic_disclaimer=economic_disclaimer,
            weather_suitability_flag=weather_flag,
            weather_advisory_alert=agromet_alert,
            agronomic_risks=agronomic_risks,
            cultivation_steps=cultivation_steps
        )
        unified_items.append(item)

        # Persist result record
        db_res = RecommendationResult(
            request_id=rec_req.id,
            crop_id=crop_db.id,
            suitability_score=rec["ensemble_score"],
            fuzzy_score=rec["model_scores"]["fuzzy_logic_score"],
            bayesian_probability=rec["model_scores"]["gaussian_nb_prob"],
            decision_tree_score=rec["model_scores"]["decision_tree_prob"],
            rank=rec["rank"],
            reasoning_summary=rec["why_recommended"],
            agronomic_justification=rec["why_recommended"],
            economic_projection={
                "mandi_name": mandi_name,
                "modal_price_per_quintal": modal_price,
                "expected_yield_per_acre": expected_yield,
                "estimated_cost_per_acre": cost_per_acre,
                "estimated_revenue_per_acre": gross_rev,
                "net_profit_per_acre": net_profit,
                "benefit_cost_ratio": bcr,
                "breakeven_yield_per_acre": breakeven_yield,
                "breakeven_price_per_quintal": breakeven_price,
                "rag_citations_count": len(rag_citations)
            },
            risk_factors=agronomic_risks,
            cultivation_steps=[s.model_dump() for s in cultivation_steps]
        )
        db.add(db_res)

    db.commit()

    return UnifiedRecommendationResponse(
        request_id=rec_req.id,
        farm_id=farm.id,
        farm_name=farm.farm_name,
        district=farm.district,
        elevation_meters=elevation,
        season=request_in.season,
        is_demo=False,
        model_version=prediction_result["model_version"],
        ai_engine_info={
            "ensemble_architecture": "Fuzzy Logic + Gaussian Naive Bayes + Decision Tree",
            "ensemble_weights": prediction_result["ensemble_weights"],
            "trained_at": prediction_result["trained_at"],
            "classes_supported": prediction_result.get("classes_supported", 22),
            "is_production_ml": True,
            "soil_data_provenance": soil_status,
            "rainfall_resolution_mode": rainfall_mode
        },
        soil_source=soil_source,
        weather_source=weather_source,
        resolved_features=resolved_features,
        recommended_crops=unified_items,
        contrastive_analysis=prediction_result.get("contrastive_analysis"),
        feature_importances=prediction_result.get("feature_importances"),
        created_at=rec_req.created_at
    )

