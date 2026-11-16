from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.economics import ProfitabilityScenario
from app.schemas.economics import ProfitabilityInput, ProfitabilityOut
from app.services.economics_service import economics_service

router = APIRouter()


@router.post("/calculate", response_model=ProfitabilityOut)
def calculate_profitability(
    input_data: ProfitabilityInput,
    db: Session = Depends(get_db)
):
    """Calculates gross revenue, itemized production expenses, net profit, BCR, and breakeven thresholds."""
    crop = db.query(Crop).filter(Crop.id == input_data.crop_id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found.")

    return economics_service.calculate_scenario(input_data, crop)


@router.post("/save", response_model=ProfitabilityOut, status_code=status.HTTP_201_CREATED)
def save_profitability_scenario(
    input_data: ProfitabilityInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Saves a farmer's crop cultivation cost scenario for future monitoring."""
    if not input_data.farm_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="farm_id is required to save scenario.")

    farm = db.query(Farm).filter(Farm.id == input_data.farm_id).first()
    if not farm or (farm.farmer_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this farm.")

    crop = db.query(Crop).filter(Crop.id == input_data.crop_id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found.")

    res = economics_service.calculate_scenario(input_data, crop)

    scenario = ProfitabilityScenario(
        farm_id=input_data.farm_id,
        crop_id=input_data.crop_id,
        scenario_title=input_data.scenario_title or f"{crop.crop_name} Scenario",
        area_acres=input_data.area_acres,
        expected_yield_per_acre=input_data.expected_yield_per_acre,
        expected_sale_price_per_quintal=input_data.expected_sale_price_per_quintal,
        seed_cost=input_data.seed_cost,
        fertilizer_cost=input_data.fertilizer_cost,
        pesticide_cost=input_data.pesticide_cost,
        irrigation_cost=input_data.irrigation_cost,
        labor_cost=input_data.labor_cost,
        machinery_cost=input_data.machinery_cost,
        miscellaneous_cost=input_data.miscellaneous_cost,
        gross_income=res.gross_income,
        total_expenses=res.total_expenses,
        net_profit=res.net_profit,
        benefit_cost_ratio=res.benefit_cost_ratio,
        breakeven_yield_per_acre=res.breakeven_yield_per_acre,
        breakeven_price_per_quintal=res.breakeven_price_per_quintal
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    res.id = scenario.id
    res.created_at = scenario.created_at
    return res


@router.get("/saved", response_model=List[ProfitabilityOut])
def get_saved_scenarios(
    farm_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves saved profitability projections for the farmer's farms."""
    query = db.query(ProfitabilityScenario).join(Farm).filter(Farm.farmer_id == current_user.id)
    if farm_id:
        query = query.filter(ProfitabilityScenario.farm_id == farm_id)

    scenarios = query.order_by(ProfitabilityScenario.created_at.desc()).all()
    out = []
    for s in scenarios:
        area = s.area_acres
        cost_breakdown = {
            "seed": s.seed_cost * area,
            "fertilizer": s.fertilizer_cost * area,
            "pesticide": s.pesticide_cost * area,
            "irrigation": s.irrigation_cost * area,
            "labor": s.labor_cost * area,
            "machinery": s.machinery_cost * area,
            "miscellaneous": s.miscellaneous_cost * area
        }
        out.append(
            ProfitabilityOut(
                id=s.id,
                crop_id=s.crop_id,
                crop_name=s.crop.crop_name if s.crop else "Crop",
                scenario_title=s.scenario_title,
                area_acres=s.area_acres,
                expected_yield_per_acre=s.expected_yield_per_acre,
                expected_sale_price_per_quintal=s.expected_sale_price_per_quintal,
                gross_income=s.gross_income,
                total_expenses=s.total_expenses,
                net_profit=s.net_profit,
                profit_per_acre=round(s.net_profit / s.area_acres, 2) if s.area_acres > 0 else 0.0,
                benefit_cost_ratio=s.benefit_cost_ratio,
                breakeven_yield_per_acre=s.breakeven_yield_per_acre,
                breakeven_price_per_quintal=s.breakeven_price_per_quintal,
                cost_breakdown=cost_breakdown,
                created_at=s.created_at
            )
        )
    return out
