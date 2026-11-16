from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User, FarmerProfile
from app.schemas.user import UserOut, FarmerProfileOut
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class FarmerProfileUpdate(BaseModel):
    experience_years: Optional[int] = None
    primary_irrigation_source: Optional[str] = None
    has_kisan_credit_card: Optional[bool] = None
    kcc_limit: Optional[float] = None
    soil_health_card_number: Optional[str] = None
    annual_income_bracket: Optional[str] = None
    preferred_language: Optional[str] = None
    full_name: Optional[str] = None


@router.get("/profile", response_model=UserOut)
def get_farmer_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserOut)
def update_farmer_profile(
    profile_in: FarmerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if profile_in.full_name:
        current_user.full_name = profile_in.full_name
    if profile_in.preferred_language:
        current_user.preferred_language = profile_in.preferred_language

    profile = current_user.profile
    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)

    if profile_in.experience_years is not None:
        profile.experience_years = profile_in.experience_years
    if profile_in.primary_irrigation_source is not None:
        profile.primary_irrigation_source = profile_in.primary_irrigation_source
    if profile_in.has_kisan_credit_card is not None:
        profile.has_kisan_credit_card = profile_in.has_kisan_credit_card
    if profile_in.kcc_limit is not None:
        profile.kcc_limit = profile_in.kcc_limit
    if profile_in.soil_health_card_number is not None:
        profile.soil_health_card_number = profile_in.soil_health_card_number
    if profile_in.annual_income_bracket is not None:
        profile.annual_income_bracket = profile_in.annual_income_bracket

    db.commit()
    db.refresh(current_user)
    return current_user
