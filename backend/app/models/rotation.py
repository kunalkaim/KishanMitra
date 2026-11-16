from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class CropRotationPlan(Base, TimestampMixin):
    __tablename__ = "crop_rotation_plans"

    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_name = Column(String(200), default="Sustainable Rotation Plan", nullable=False)
    target_duration_seasons = Column(Integer, default=4, nullable=False)
    notes = Column(String(500), nullable=True)

    farm = relationship("Farm", back_populates="rotation_plans")
    items = relationship("CropRotationItem", back_populates="plan", cascade="all, delete-orphan")


class CropRotationItem(Base, TimestampMixin):
    __tablename__ = "crop_rotation_items"

    plan_id = Column(String(36), ForeignKey("crop_rotation_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    season_sequence = Column(Integer, nullable=False)  # 1, 2, 3, 4
    season_name = Column(String(50), nullable=False)   # Kharif, Rabi, Zaid
    year = Column(Integer, nullable=False)
    crop_name = Column(String(100), nullable=False)
    soil_benefit_description = Column(String(300), nullable=False)
    pest_break_description = Column(String(300), nullable=False)
    economic_stability_factor = Column(Float, default=0.85, nullable=False)

    plan = relationship("CropRotationPlan", back_populates="items")
