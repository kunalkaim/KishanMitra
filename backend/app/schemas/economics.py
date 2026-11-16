from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProfitabilityInput(BaseModel):
    farm_id: Optional[str] = None
    crop_id: str
    scenario_title: Optional[str] = "Crop Profitability Analysis"
    area_acres: float = Field(default=1.0, gt=0, example=2.0)
    expected_yield_per_acre: float = Field(..., gt=0, example=18.0)
    expected_sale_price_per_quintal: float = Field(..., gt=0, example=3200.0)
    seed_cost: float = Field(default=2500.0, ge=0)
    fertilizer_cost: float = Field(default=4200.0, ge=0)
    pesticide_cost: float = Field(default=1800.0, ge=0)
    irrigation_cost: float = Field(default=2000.0, ge=0)
    labor_cost: float = Field(default=6500.0, ge=0)
    machinery_cost: float = Field(default=3000.0, ge=0)
    miscellaneous_cost: float = Field(default=1000.0, ge=0)


class ProfitabilityOut(BaseModel):
    id: Optional[str] = None
    crop_id: str
    crop_name: str
    scenario_title: str
    area_acres: float
    expected_yield_per_acre: float
    expected_sale_price_per_quintal: float
    
    # Financial Aggregates
    gross_income: float
    total_expenses: float
    net_profit: float
    profit_per_acre: float
    benefit_cost_ratio: float
    breakeven_yield_per_acre: float
    breakeven_price_per_quintal: float
    
    # Cost Breakdown Percentages
    cost_breakdown: dict
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
