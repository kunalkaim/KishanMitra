from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    category: str = Field(default="Platform Usability", example="Recommendation Quality")
    subject: str = Field(..., example="Accurate Finger Millet recommendation for Almora")
    message: str = Field(..., example="The fertilizer schedule matched our local KVK advice perfectly.")
    rating: int = Field(default=5, ge=1, le=5, example=5)


class FeedbackOut(FeedbackCreate):
    id: str
    farmer_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class FarmingOutcomeCreate(BaseModel):
    farm_id: str
    crop_id: str
    season: str = "Kharif"
    year: int = 2025
    recommendation_followed: bool = True
    actual_yield_per_acre: float = 14.5
    actual_sale_price_per_quintal: float = 3400.0
    actual_profit_per_acre: float = 31500.0
    satisfaction_score: int = 5
    lessons_learned: Optional[str] = "Mulching before monsoon prevented soil erosion on hill slopes."


class FarmingOutcomeOut(FarmingOutcomeCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
