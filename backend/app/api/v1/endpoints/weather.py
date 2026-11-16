from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.weather import WeatherOut
from app.services.weather_service import weather_service

router = APIRouter()


@router.get("/", response_model=WeatherOut)
def get_weather(
    district: str = Query(default="Almora", description="Uttarakhand District Name"),
    elevation: Optional[float] = Query(default=None, description="Farm Elevation in meters"),
    db: Session = Depends(get_db)
):
    """
    Returns 7-day agro-meteorological forecast and IMD agromet alerts for the specified district.
    Integrates 3-tier resilient resolution: Live Open-Meteo API -> DB Cached WeatherRecord -> Elevation Agromet Model.
    """
    return weather_service.get_district_weather(district=district, elevation=elevation, db=db)
