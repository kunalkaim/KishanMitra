from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FarmBase(BaseModel):
    farm_name: str = Field(..., example="Nanda Devi Valley Orchard")
    state: str = Field(default="Uttarakhand", example="Uttarakhand")
    district: str = Field(..., example="Almora")
    block: Optional[str] = Field(default="Hawalbagh", example="Hawalbagh")
    village: Optional[str] = Field(default="Dhaula Devi", example="Dhaula Devi")
    pincode: Optional[str] = Field(default="263601", example="263601")
    total_area_acres: float = Field(..., gt=0, example=3.5)
    cultivated_area_acres: float = Field(..., gt=0, example=3.0)
    irrigation_type: str = Field(default="Canal / Gravity Channel", example="Canal / Gravity Channel")
    soil_type: str = Field(default="Brown Forest Soil", example="Brown Forest Soil")
    ownership_type: str = Field(default="Owned", example="Owned")
    latitude: Optional[float] = Field(default=29.5992, example=29.5992)
    longitude: Optional[float] = Field(default=79.6586, example=79.6586)
    elevation_meters: Optional[float] = Field(default=1650.0, example=1650.0)


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    farm_name: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    village: Optional[str] = None
    pincode: Optional[str] = None
    total_area_acres: Optional[float] = None
    cultivated_area_acres: Optional[float] = None
    irrigation_type: Optional[str] = None
    soil_type: Optional[str] = None
    ownership_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_meters: Optional[float] = None
    is_active: Optional[bool] = None


class FarmOut(FarmBase):
    id: str
    farmer_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
