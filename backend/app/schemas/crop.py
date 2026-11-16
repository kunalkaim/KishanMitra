from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class CropSeasonOut(BaseModel):
    id: str
    season_name: str
    sowing_window_start: str
    sowing_window_end: str
    harvest_window_start: str
    harvest_window_end: str
    suitable_districts: List[str]

    class Config:
        from_attributes = True


class CropOut(BaseModel):
    id: str
    crop_name: str
    scientific_name: Optional[str]
    hindi_name: str
    category: str
    season: str
    min_ph: float
    max_ph: float
    water_requirement_mm: float
    growing_duration_days: int
    temperature_min_c: float
    temperature_max_c: float
    rainfall_min_mm: float
    rainfall_max_mm: float
    recommended_soil_types: List[str]
    average_yield_quintal_per_acre: float
    cost_of_cultivation_per_acre: float

    class Config:
        from_attributes = True


class CropDetailOut(CropOut):
    seasons: List[CropSeasonOut] = []
