from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CropRotationItemSchema(BaseModel):
    season_sequence: int
    season_name: str
    year: int
    crop_name: str
    soil_benefit_description: str
    pest_break_description: str
    economic_stability_factor: float


class CropRotationPlanCreate(BaseModel):
    farm_id: str
    plan_name: Optional[str] = "4-Season Himalayan Conservation Rotation"
    target_duration_seasons: Optional[int] = 4
    notes: Optional[str] = "Nitrogen fixing legume rotation following cereal staple"


class CropRotationPlanOut(BaseModel):
    id: str
    farm_id: str
    plan_name: str
    target_duration_seasons: int
    notes: Optional[str]
    items: List[CropRotationItemSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True
