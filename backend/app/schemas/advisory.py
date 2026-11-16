from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AdvisoryInput(BaseModel):
    farm_id: Optional[str] = None
    crop_name: str = Field(..., example="Finger Millet (Mandua / Ragi)")
    crop_growth_stage: str = Field(..., example="Tillering / Vegetative")
    observed_symptoms: str = Field(
        ..., 
        min_length=10, 
        example="Spindle-shaped brown lesions with greyish centres on leaf blades and neck of the panicle."
    )
    farming_conditions: str = Field(
        ..., 
        example="Heavy intermittent monsoon rains, morning mist, cloudy weather, high terrace field humidity."
    )
    affected_area_percentage: float = Field(default=15.0, ge=1.0, le=100.0, example=15.0)


class AdvisoryIntervention(BaseModel):
    type: str  # Organic, Biological, Cultural, Chemical (Emergency)
    remedy_name: str
    dosage_per_liter: str
    application_method: str
    precaution: str


class AdvisoryResponse(BaseModel):
    id: str
    crop_name: str
    crop_growth_stage: str
    suspected_pest_or_pathogen: str
    diagnostic_category: str  # Fungal, Bacterial, Viral, Insect Pest, Nutrient Deficiency
    confidence_level: str
    advisory_response: str
    recommended_interventions: List[AdvisoryIntervention]
    preventive_measures: List[str]
    disclaimer: str
    is_demo: bool = True
    created_at: datetime

    class Config:
        from_attributes = True
