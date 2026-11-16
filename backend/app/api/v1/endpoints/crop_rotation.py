from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.farm import Farm
from app.models.rotation import CropRotationPlan, CropRotationItem
from app.schemas.rotation import CropRotationPlanCreate, CropRotationPlanOut

router = APIRouter()


@router.get("/", response_model=List[CropRotationPlanOut])
def list_rotation_plans(
    farm_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists rotation plans for the farmer's farms."""
    query = db.query(CropRotationPlan).join(Farm).filter(Farm.farmer_id == current_user.id)
    if farm_id:
        query = query.filter(CropRotationPlan.farm_id == farm_id)

    plans = query.order_by(CropRotationPlan.created_at.desc()).all()
    return plans


@router.post("/", response_model=CropRotationPlanOut, status_code=status.HTTP_201_CREATED)
def create_rotation_plan(
    plan_in: CropRotationPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates and stores a 4-season agronomic crop rotation plan."""
    farm = db.query(Farm).filter(Farm.id == plan_in.farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found.")

    if farm.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    plan = CropRotationPlan(
        farm_id=farm.id,
        plan_name=plan_in.plan_name or "Himalayan Sustainable 4-Season Cycle",
        target_duration_seasons=plan_in.target_duration_seasons or 4,
        notes=plan_in.notes or "Alternating cereals with legumes to replenish nitrogen and break foliar pathogen lifecycles."
    )
    db.add(plan)
    db.flush()

    # Pre-populate 4 standard agronomic sequences for hill farming
    rotation_sequences = [
        CropRotationItem(
            plan_id=plan.id,
            season_sequence=1,
            season_name="Kharif Year 1",
            year=2025,
            crop_name="Finger Millet (Mandua / Ragi)",
            soil_benefit_description="Extracts deep nutrients; low water demand leaves residual subsoil moisture.",
            pest_break_description="Breaks root-knot nematode cycle prevalent in continuous paddy cropping.",
            economic_stability_factor=0.88
        ),
        CropRotationItem(
            plan_id=plan.id,
            season_sequence=2,
            season_name="Rabi Year 1",
            year=2025,
            crop_name="Chickpea / Lentil (Masoor)",
            soil_benefit_description="Fixes 45-60 kg atmospheric nitrogen per hectare through Rhizobium nodules.",
            pest_break_description="Starves cereal leaf rust pathogens during winter cycle.",
            economic_stability_factor=0.92
        ),
        CropRotationItem(
            plan_id=plan.id,
            season_sequence=3,
            season_name="Kharif Year 2",
            year=2026,
            crop_name="Rajma / Black Soybean (Bhatt)",
            soil_benefit_description="High biomass canopy suppresses summer weeds and enriches topsoil organic matter.",
            pest_break_description="Disrupts millet foliar blast inoculum reservoirs.",
            economic_stability_factor=0.95
        ),
        CropRotationItem(
            plan_id=plan.id,
            season_sequence=4,
            season_name="Rabi Year 2",
            year=2026,
            crop_name="Wheat (VL Gehun 907) + Mustard Intercrop",
            soil_benefit_description="Deep root system aerates soil; mustard glucosinolates act as natural biofumigant.",
            pest_break_description="Reduces soil-borne damping-off fungi.",
            economic_stability_factor=0.90
        )
    ]

    for item in rotation_sequences:
        db.add(item)

    db.commit()
    db.refresh(plan)
    return plan
