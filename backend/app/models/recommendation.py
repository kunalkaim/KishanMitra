from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class RecommendationRequest(Base, TimestampMixin):
    __tablename__ = "recommendation_requests"

    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    soil_test_id = Column(String(36), ForeignKey("soil_tests.id", ondelete="SET NULL"), nullable=True)
    
    season = Column(String(50), nullable=False)  # Kharif, Rabi, Zaid
    target_market = Column(String(100), default="Local Mandi", nullable=False)
    budget_per_acre = Column(Float, default=20000.0, nullable=False)
    irrigation_available = Column(Boolean, default=True, nullable=False)

    farmer = relationship("User", back_populates="recommendation_requests")
    farm = relationship("Farm", back_populates="recommendation_requests")
    soil_test = relationship("SoilTest", back_populates="recommendation_requests")
    results = relationship("RecommendationResult", back_populates="request", cascade="all, delete-orphan")


class RecommendationResult(Base, TimestampMixin):
    __tablename__ = "recommendation_results"

    request_id = Column(String(36), ForeignKey("recommendation_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    
    suitability_score = Column(Float, nullable=False)  # 0 to 100
    fuzzy_score = Column(Float, nullable=False)
    bayesian_probability = Column(Float, nullable=False)
    decision_tree_score = Column(Float, nullable=False)
    rank = Column(Integer, default=1, nullable=False)
    
    reasoning_summary = Column(String(500), nullable=False)
    agronomic_justification = Column(String(1000), nullable=False)
    economic_projection = Column(JSON, default=dict, nullable=False)
    risk_factors = Column(JSON, default=list, nullable=False)
    cultivation_steps = Column(JSON, default=list, nullable=False)

    request = relationship("RecommendationRequest", back_populates="results")
    crop = relationship("Crop", back_populates="recommendation_results")
