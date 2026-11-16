from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.crop import Crop
from app.schemas.crop import CropOut, CropDetailOut

router = APIRouter()


@router.get("/", response_model=List[CropOut])
def list_crops(
    season: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists agricultural crops suitable for Indian and Himalayan agro-climates."""
    query = db.query(Crop)
    if season:
        query = query.filter(Crop.season.ilike(f"%{season}%"))
    if category:
        query = query.filter(Crop.category.ilike(f"%{category}%"))
    return query.order_by(Crop.crop_name.asc()).all()


@router.get("/{crop_id}", response_model=CropDetailOut)
def get_crop(crop_id: str, db: Session = Depends(get_db)):
    """Retrieves full crop agronomic profile and seasonal sowing windows."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found.")
    return crop
