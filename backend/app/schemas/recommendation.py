from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RecommendationInput(BaseModel):
    farm_id: str = Field(..., example="farm-demo-01")
    season: str = Field(default="Kharif", example="Kharif")
    target_market: str = Field(default="Local Mandi", example="Local Mandi")
    budget_per_acre: float = Field(default=25000.0, example=25000.0)
    irrigation_available: bool = Field(default=True, example=True)
    
    # 7 Core ML Features (with graceful aliases)
    N: Optional[float] = Field(default=None, example=90.0)
    P: Optional[float] = Field(default=None, example=42.0)
    K: Optional[float] = Field(default=None, example=43.0)
    temperature: Optional[float] = Field(default=None, example=24.5)
    humidity: Optional[float] = Field(default=None, example=78.0)
    ph: Optional[float] = Field(default=None, example=6.5)
    rainfall: Optional[float] = Field(default=None, example=210.0)
    rainfall_mm: Optional[float] = Field(default=None, example=210.0)

    # Legacy field aliases
    soil_ph: Optional[float] = Field(default=None, example=6.5)
    nitrogen_kg_ha: Optional[float] = Field(default=None, example=90.0)
    phosphorus_kg_ha: Optional[float] = Field(default=None, example=42.0)
    potassium_kg_ha: Optional[float] = Field(default=None, example=43.0)


class CultivationStep(BaseModel):
    phase: str
    timeline: str
    action: str
    inputs: str


class RecommendationResultItem(BaseModel):
    crop_id: str
    crop_name: str
    hindi_name: str
    category: str
    suitability_score: float
    fuzzy_score: float
    bayesian_probability: float
    decision_tree_score: float
    rank: int
    reasoning_summary: str
    agronomic_justification: str
    expected_yield_per_acre: float
    estimated_revenue_per_acre: float
    estimated_cost_per_acre: float
    net_profit_per_acre: float
    risk_factors: List[str]
    cultivation_steps: List[CultivationStep]
    model_agreement: Optional[str] = None
    why_recommended: Optional[str] = None
    primary_favorable_factors: Optional[List[str]] = []
    limiting_factors: Optional[List[str]] = []
    weighted_contributions: Optional[Dict[str, float]] = None
    detailed_feature_influences: Optional[List[Dict[str, Any]]] = []


class RecommendationResponse(BaseModel):
    request_id: str
    farm_id: str
    district: str
    season: str
    is_demo: bool = False
    model_version: str = "v1.0-HybridEnsemble"
    ai_engine_info: Dict[str, Any] = {
        "ensemble_architecture": "Fuzzy Logic + Gaussian Naive Bayes + Decision Tree",
        "ensemble_weights": {"fuzzy": 0.10, "gaussian_nb": 0.48, "decision_tree": 0.42},
        "is_production_ml": True,
        "classes_supported": 22
    }
    recommended_crops: List[RecommendationResultItem]
    contrastive_analysis: Optional[Dict[str, Any]] = None
    feature_importances: Optional[Dict[str, float]] = None
    created_at: datetime


class RAGCitationItem(BaseModel):
    document_title: str
    publisher: str
    publication_date: str
    page_start: int
    page_end: int
    source_url: Optional[str] = ""
    is_historical: bool = False
    retrieval_score: float
    snippet: str


class UnifiedCropItem(BaseModel):
    crop_id: str
    crop_name: str
    hindi_name: str
    category: str
    
    # ML Suitability Layer
    suitability_score: float
    rank: int
    model_agreement: Optional[str] = "High"
    model_scores: Dict[str, float]
    why_recommended: str
    primary_favorable_factors: List[str] = []
    limiting_factors: List[str] = []
    contrastive_insight: Optional[str] = None
    detailed_feature_influences: Optional[List[Dict[str, Any]]] = []
    
    # RAG Knowledge Evidence Layer
    verified_package_of_practices: List[str] = []
    rag_citations: List[RAGCitationItem] = []
    
    # Dynamic Market & Economics Layer
    mandi_name: str
    modal_price_per_quintal: float
    price_trend: str = "stable"
    expected_yield_per_acre: float
    estimated_cost_per_acre: float
    estimated_gross_revenue: float
    estimated_net_profit: float
    benefit_cost_ratio: float
    breakeven_yield_per_acre: float
    breakeven_price_per_quintal: float
    economic_disclaimer: str
    
    # Agro-Meteorological & Agronomic Risk Layer
    weather_suitability_flag: str = "Optimal"
    weather_advisory_alert: str
    agronomic_risks: List[str] = []
    cultivation_steps: List[CultivationStep] = []


class UnifiedRecommendationResponse(BaseModel):
    request_id: str
    farm_id: str
    farm_name: str
    district: str
    elevation_meters: float
    season: str
    is_demo: bool = False
    model_version: str = "v1.1-HybridEnsemble"
    ai_engine_info: Dict[str, Any]
    soil_source: str
    weather_source: str
    resolved_features: Dict[str, float]
    recommended_crops: List[UnifiedCropItem]
    contrastive_analysis: Optional[Dict[str, Any]] = None
    feature_importances: Optional[Dict[str, float]] = None
    created_at: datetime

