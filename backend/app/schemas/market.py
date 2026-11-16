from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class MandiOut(BaseModel):
    id: str
    mandi_name: str
    district_name: str
    state_name: str
    contact_number: Optional[str]
    is_operational: bool

    class Config:
        from_attributes = True


class MarketPriceOut(BaseModel):
    id: str
    mandi_id: str
    mandi_name: str
    district_name: str
    crop_id: str
    crop_name: str
    arrival_date: date
    min_price_per_quintal: float
    max_price_per_quintal: float
    modal_price_per_quintal: float
    arrivals_in_tonnes: float
    trend: str = "stable"  # "rising", "falling", "stable"

    class Config:
        from_attributes = True


class MandiComparison(BaseModel):
    crop_name: str
    prices: List[MarketPriceOut]
    highest_mandi: str
    highest_price: float
    lowest_mandi: str
    lowest_price: float
    recommendation: str
