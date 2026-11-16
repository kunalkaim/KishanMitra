from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class SoilTestBase(BaseModel):
    test_date: date = Field(default_factory=date.today)
    soil_ph: float = Field(..., ge=3.5, le=10.0, example=6.4)
    organic_carbon_percent: float = Field(..., ge=0.05, le=5.0, example=0.82)
    nitrogen_kg_ha: float = Field(..., ge=10.0, le=800.0, example=295.0)
    phosphorus_kg_ha: float = Field(..., ge=2.0, le=200.0, example=22.4)
    potassium_kg_ha: float = Field(..., ge=10.0, le=800.0, example=240.0)
    sulphur_ppm: Optional[float] = Field(default=12.5, example=12.5)
    zinc_ppm: Optional[float] = Field(default=0.9, example=0.9)
    iron_ppm: Optional[float] = Field(default=6.2, example=6.2)
    electrical_conductivity: Optional[float] = Field(default=0.42, example=0.42)
    testing_lab_name: Optional[str] = Field(default="ICAR-VPKAS Almora Soil Testing Lab", example="ICAR-VPKAS Almora Soil Testing Lab")


class SoilTestCreate(SoilTestBase):
    farm_id: str


class SoilTestOut(SoilTestBase):
    id: str
    farm_id: str
    created_at: datetime

    class Config:
        from_attributes = True
