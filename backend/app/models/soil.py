from sqlalchemy import Column, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class SoilTest(Base, TimestampMixin):
    __tablename__ = "soil_tests"

    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    test_date = Column(Date, nullable=False)
    
    # Chemical & Nutrient Parameters
    soil_ph = Column(Float, nullable=False)  # e.g., 6.5
    organic_carbon_percent = Column(Float, nullable=False)  # e.g., 0.75
    nitrogen_kg_ha = Column(Float, nullable=False)  # e.g., 280.0
    phosphorus_kg_ha = Column(Float, nullable=False)  # e.g., 18.5
    potassium_kg_ha = Column(Float, nullable=False)  # e.g., 210.0
    
    sulphur_ppm = Column(Float, default=12.0, nullable=True)
    zinc_ppm = Column(Float, default=0.85, nullable=True)
    iron_ppm = Column(Float, default=5.2, nullable=True)
    electrical_conductivity = Column(Float, default=0.45, nullable=True)  # dS/m
    
    testing_lab_name = Column(String(200), default="District Agriculture Testing Lab", nullable=True)

    # Relationships
    farm = relationship("Farm", back_populates="soil_tests")
    recommendation_requests = relationship("RecommendationRequest", back_populates="soil_test")
