from typing import List
from pydantic import BaseModel


class BlockOut(BaseModel):
    id: str
    block_name: str

    class Config:
        from_attributes = True


class DistrictOut(BaseModel):
    id: str
    district_name: str
    agro_climatic_zone: str
    elevation_bracket: str
    average_annual_rainfall_mm: float
    dominant_soil_types: List[str]
    primary_crops: List[str]
    blocks: List[BlockOut] = []

    class Config:
        from_attributes = True


class StateOut(BaseModel):
    id: str
    state_name: str
    state_code: str
    districts: List[DistrictOut] = []

    class Config:
        from_attributes = True
