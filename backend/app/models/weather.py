from sqlalchemy import Column, String, Float, Date, JSON
from app.db.session import Base
from app.db.base import TimestampMixin


class WeatherRecord(Base, TimestampMixin):
    __tablename__ = "weather_records"

    district_name = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    recorded_date = Column(Date, nullable=False, index=True)
    
    temperature_min_c = Column(Float, nullable=False)
    temperature_max_c = Column(Float, nullable=False)
    humidity_percent = Column(Float, nullable=False)
    rainfall_mm = Column(Float, default=0.0, nullable=False)
    wind_speed_kmh = Column(Float, default=10.0, nullable=False)
    condition_text = Column(String(100), default="Partly Cloudy", nullable=False)
    forecast_json = Column(JSON, default=list, nullable=False)
