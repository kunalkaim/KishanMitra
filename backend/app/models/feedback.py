from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class FarmerFeedback(Base, TimestampMixin):
    __tablename__ = "farmer_feedback"

    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), default="Platform Usability", nullable=False) # Usability, Recommendation Quality, Advisory, Bug
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    rating = Column(Integer, default=5, nullable=False) # 1 to 5 stars

    farmer = relationship("User", back_populates="feedback")


class FarmingOutcome(Base, TimestampMixin):
    __tablename__ = "farming_outcomes"

    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    season = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    recommendation_followed = Column(Boolean, default=True, nullable=False)
    
    actual_yield_per_acre = Column(Float, nullable=False)
    actual_sale_price_per_quintal = Column(Float, nullable=False)
    actual_profit_per_acre = Column(Float, nullable=False)
    satisfaction_score = Column(Integer, default=5, nullable=False)
    lessons_learned = Column(Text, nullable=True)

    farm = relationship("Farm", back_populates="outcomes")
    crop = relationship("Crop", back_populates="outcomes")
