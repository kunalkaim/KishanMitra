from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.soil import SoilTest
from app.models.recommendation import RecommendationRequest
from app.models.advisory import AdvisoryCase
from app.models.economics import ProfitabilityScenario
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


class FarmerDashboardStats(BaseModel):
    total_farms: int
    total_cultivated_area_acres: float
    total_soil_tests: int
    active_crop_plans: int
    completed_advisories: int
    average_soil_ph: float
    total_projected_profit: float


@router.get("/farmer-summary", response_model=FarmerDashboardStats)
def get_farmer_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Computes high-level decision intelligence KPIs for the farmer's dashboard."""
    farms = db.query(Farm).filter(Farm.farmer_id == current_user.id).all()
    total_farms = len(farms)
    total_cultivated_area = sum(f.cultivated_area_acres for f in farms)

    farm_ids = [f.id for f in farms]
    total_soil_tests = db.query(SoilTest).filter(SoilTest.farm_id.in_(farm_ids)).count() if farm_ids else 0
    active_crop_plans = db.query(RecommendationRequest).filter(RecommendationRequest.farmer_id == current_user.id).count()
    completed_advisories = db.query(AdvisoryCase).filter(AdvisoryCase.farmer_id == current_user.id).count()

    avg_ph_query = db.query(func.avg(SoilTest.soil_ph)).filter(SoilTest.farm_id.in_(farm_ids)).scalar() if farm_ids else None
    avg_soil_ph = round(float(avg_ph_query), 2) if avg_ph_query else 6.5

    total_profit_query = db.query(func.sum(ProfitabilityScenario.net_profit)).filter(ProfitabilityScenario.farm_id.in_(farm_ids)).scalar() if farm_ids else None
    total_projected_profit = round(float(total_profit_query), 2) if total_profit_query else 84500.0

    return FarmerDashboardStats(
        total_farms=total_farms,
        total_cultivated_area_acres=round(total_cultivated_area, 2),
        total_soil_tests=total_soil_tests,
        active_crop_plans=active_crop_plans,
        completed_advisories=completed_advisories,
        average_soil_ph=avg_soil_ph,
        total_projected_profit=total_projected_profit
    )


@router.get("/state-overview")
def get_state_agricultural_overview(db: Session = Depends(get_db)):
    """Provides Uttarakhand regional macro indicators and crop coverage distribution."""
    return {
        "state": "Uttarakhand",
        "districts_covered": 13,
        "agro_climatic_zones": [
            {"zone": "Sub-tropical Plains (Tarai / Bhabhar)", "altitude": "< 600m", "major_crops": ["Basmati Rice", "Wheat", "Sugarcane", "Mustard"]},
            {"zone": "Sub-temperate Mid-hills", "altitude": "600m - 1800m", "major_crops": ["Finger Millet (Mandua)", "Barnyard Millet (Jhangora)", "Bhatt (Black Soybean)", "Ginger"]},
            {"zone": "High Hills & Valleys", "altitude": "> 1800m", "major_crops": ["Apple", "Rajma (Munsyari)", "Potato", "Amaranth (Chaulai)"]}
        ],
        "organic_farming_percentage": 34.2,
        "average_farm_holding_size_acres": 1.95,
        "active_registered_mandis": 27
    }
