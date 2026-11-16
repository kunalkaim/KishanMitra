from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class WeatherForecastDay(BaseModel):
    date: str
    day: str
    temp_max: float
    temp_min: float
    humidity: float
    rainfall_prob: float
    condition: str
    icon: str
    advisory: str


class WeatherOut(BaseModel):
    district_name: str
    temperature_min_c: float
    temperature_max_c: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_kmh: float
    condition_text: str
    forecast: List[WeatherForecastDay]
    agricultural_alert: Optional[str] = None
