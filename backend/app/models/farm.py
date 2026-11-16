from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_name = Column(String(200), nullable=False)
    state = Column(String(100), default="Uttarakhand", nullable=False)
    district = Column(String(100), nullable=False, index=True)
    block = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    
    total_area_acres = Column(Float, nullable=False)
    cultivated_area_acres = Column(Float, nullable=False)
    irrigation_type = Column(String(100), default="Canal", nullable=False)
    soil_type = Column(String(100), default="Loamy", nullable=False)
    ownership_type = Column(String(50), default="Owned", nullable=False)  # 'Owned', 'Leased', 'Sharecropped'
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    elevation_meters = Column(Float, default=1500.0, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    farmer = relationship("User", back_populates="farms")
    soil_tests = relationship("SoilTest", back_populates="farm", cascade="all, delete-orphan")
    crop_history = relationship("FarmCropHistory", back_populates="farm", cascade="all, delete-orphan")
    recommendation_requests = relationship("RecommendationRequest", back_populates="farm", cascade="all, delete-orphan")
    profitability_scenarios = relationship("ProfitabilityScenario", back_populates="farm", cascade="all, delete-orphan")
    rotation_plans = relationship("CropRotationPlan", back_populates="farm", cascade="all, delete-orphan")
    advisory_cases = relationship("AdvisoryCase", back_populates="farm", cascade="all, delete-orphan")
    outcomes = relationship("FarmingOutcome", back_populates="farm", cascade="all, delete-orphan")
