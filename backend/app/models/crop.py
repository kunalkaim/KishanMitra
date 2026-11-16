from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class Crop(Base, TimestampMixin):
    __tablename__ = "crops"

    crop_name = Column(String(100), unique=True, nullable=False, index=True)
    scientific_name = Column(String(150), nullable=True)
    hindi_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # cereal, pulse, oilseed, vegetable, fruit, cash_crop, spice
    season = Column(String(50), nullable=False)    # kharif, rabi, zaid, perennial
    
    # Agronomic Thresholds
    min_ph = Column(Float, default=5.5, nullable=False)
    max_ph = Column(Float, default=7.8, nullable=False)
    water_requirement_mm = Column(Float, default=600.0, nullable=False)
    growing_duration_days = Column(Integer, default=120, nullable=False)
    temperature_min_c = Column(Float, default=15.0, nullable=False)
    temperature_max_c = Column(Float, default=32.0, nullable=False)
    rainfall_min_mm = Column(Float, default=400.0, nullable=False)
    rainfall_max_mm = Column(Float, default=1200.0, nullable=False)
    
    recommended_soil_types = Column(JSON, default=list, nullable=False)
    average_yield_quintal_per_acre = Column(Float, default=15.0, nullable=False)
    cost_of_cultivation_per_acre = Column(Float, default=18000.0, nullable=False)

    # Relationships
    seasons = relationship("CropSeason", back_populates="crop", cascade="all, delete-orphan")
    market_prices = relationship("MarketPrice", back_populates="crop", cascade="all, delete-orphan")
    recommendation_results = relationship("RecommendationResult", back_populates="crop")
    scenarios = relationship("ProfitabilityScenario", back_populates="crop")
    outcomes = relationship("FarmingOutcome", back_populates="crop")


class CropSeason(Base, TimestampMixin):
    __tablename__ = "crop_seasons"

    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    season_name = Column(String(50), nullable=False)  # Kharif, Rabi, Zaid
    sowing_window_start = Column(String(50), nullable=False)  # e.g., "15 June"
    sowing_window_end = Column(String(50), nullable=False)    # e.g., "15 July"
    harvest_window_start = Column(String(50), nullable=False) # e.g., "15 October"
    harvest_window_end = Column(String(50), nullable=False)   # e.g., "15 November"
    suitable_districts = Column(JSON, default=list, nullable=False)

    crop = relationship("Crop", back_populates="seasons")


class FarmCropHistory(Base, TimestampMixin):
    __tablename__ = "farm_crop_history"

    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    season = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    area_sown_acres = Column(Float, nullable=False)
    yield_obtained_quintals = Column(Float, nullable=False)
    fertilizers_used = Column(JSON, default=list, nullable=True)
    pesticides_used = Column(JSON, default=list, nullable=True)
    total_cost_incurred = Column(Float, default=0.0, nullable=True)
    total_revenue_earned = Column(Float, default=0.0, nullable=True)
    notes = Column(String(500), nullable=True)

    farm = relationship("Farm", back_populates="crop_history")
    crop = relationship("Crop")
