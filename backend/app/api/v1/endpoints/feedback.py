from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.farm import Farm
from app.models.feedback import FarmerFeedback, FarmingOutcome
from app.schemas.feedback import FeedbackCreate, FeedbackOut, FarmingOutcomeCreate, FarmingOutcomeOut

router = APIRouter()


@router.post("/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    fb_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submits farmer feedback, platform rating, and agronomic satisfaction notes."""
    fb = FarmerFeedback(
        farmer_id=current_user.id,
        category=fb_in.category,
        subject=fb_in.subject,
        message=fb_in.message,
        rating=fb_in.rating
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@router.get("/feedback", response_model=List[FeedbackOut])
def list_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(FarmerFeedback).filter(FarmerFeedback.farmer_id == current_user.id).all()


@router.post("/outcomes", response_model=FarmingOutcomeOut, status_code=status.HTTP_201_CREATED)
def record_outcome(
    out_in: FarmingOutcomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Records real harvest yield and financial outcome to validate AI recommendations."""
    farm = db.query(Farm).filter(Farm.id == out_in.farm_id).first()
    if not farm or (farm.farmer_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    outcome = FarmingOutcome(
        farm_id=out_in.farm_id,
        crop_id=out_in.crop_id,
        season=out_in.season,
        year=out_in.year,
        recommendation_followed=out_in.recommendation_followed,
        actual_yield_per_acre=out_in.actual_yield_per_acre,
        actual_sale_price_per_quintal=out_in.actual_sale_price_per_quintal,
        actual_profit_per_acre=out_in.actual_profit_per_acre,
        satisfaction_score=out_in.satisfaction_score,
        lessons_learned=out_in.lessons_learned
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome


@router.get("/outcomes", response_model=List[FarmingOutcomeOut])
def list_outcomes(
    farm_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FarmingOutcome).join(Farm).filter(Farm.farmer_id == current_user.id)
    if farm_id:
        query = query.filter(FarmingOutcome.farm_id == farm_id)
    return query.order_by(FarmingOutcome.created_at.desc()).all()
