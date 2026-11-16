from sqlalchemy import Column, String, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class AdvisoryCase(Base, TimestampMixin):
    """
    Text-Based Pest & Disease Advisory Case.
    Strictly text-based diagnostic and agronomic advisory.
    No computer vision or image processing.
    """
    __tablename__ = "advisory_cases"

    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Farmer Input Fields (Text Only)
    crop_name = Column(String(100), nullable=False, index=True)
    crop_growth_stage = Column(String(100), nullable=False)  # Vegetative, Flowering, Fruiting, Maturity
    observed_symptoms = Column(Text, nullable=False)        # Detailed text description of foliar/stem/root symptoms
    farming_conditions = Column(Text, nullable=False)       # Soil moisture, recent rains, high humidity, frost
    affected_area_percentage = Column(Float, default=10.0, nullable=False)
    
    # Advisory Intelligence & Prescriptions
    suspected_pest_or_pathogen = Column(String(200), nullable=False)
    diagnostic_category = Column(String(100), default="Fungal Disease", nullable=False) # Fungal, Bacterial, Viral, Insect Pest, Nutrient Deficiency
    confidence_level = Column(String(50), default="High Confidence (Rule-Based Agronomic Evaluation)", nullable=False)
    advisory_response = Column(Text, nullable=False)
    recommended_interventions = Column(JSON, default=list, nullable=False)  # Organic IPM & biological controls
    preventive_measures = Column(JSON, default=list, nullable=False)
    disclaimer = Column(
        Text, 
        default="Advisory provided for agronomic guidance based on reported symptoms. Verify acute chemical interventions with your local Block Agriculture Officer or Krishi Vigyan Kendra (KVK).",
        nullable=False
    )

    farmer = relationship("User", back_populates="advisory_cases")
    farm = relationship("Farm", back_populates="advisory_cases")
