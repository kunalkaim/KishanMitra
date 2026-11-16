from sqlalchemy import Column, String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    preferred_language = Column(String(10), default="hi", nullable=False)
    role = Column(String(50), default="farmer", nullable=False)  # 'farmer', 'admin', 'extension_officer'
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    profile = relationship("FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    farms = relationship("Farm", back_populates="farmer", cascade="all, delete-orphan")
    recommendation_requests = relationship("RecommendationRequest", back_populates="farmer", cascade="all, delete-orphan")
    advisory_cases = relationship("AdvisoryCase", back_populates="farmer", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="farmer", cascade="all, delete-orphan")
    feedback = relationship("FarmerFeedback", back_populates="farmer", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="farmer", cascade="all, delete-orphan")


class FarmerProfile(Base, TimestampMixin):
    __tablename__ = "farmer_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    experience_years = Column(Integer, default=5, nullable=False)
    primary_irrigation_source = Column(String(100), default="Canal / River", nullable=True)
    has_kisan_credit_card = Column(Boolean, default=False, nullable=False)
    kcc_limit = Column(Float, default=0.0, nullable=False)
    soil_health_card_number = Column(String(100), nullable=True)
    annual_income_bracket = Column(String(100), default="₹1,50,000 - ₹3,00,000", nullable=True)

    user = relationship("User", back_populates="profile")
