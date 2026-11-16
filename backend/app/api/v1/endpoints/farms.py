from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut

router = APIRouter()


@router.get("/", response_model=List[FarmOut])
def list_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all farms belonging to the authenticated farmer."""
    farms = db.query(Farm).filter(Farm.farmer_id == current_user.id).order_by(Farm.created_at.desc()).all()
    return farms


@router.post("/", response_model=FarmOut, status_code=status.HTTP_201_CREATED)
def create_farm(
    farm_in: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registers a new farm under the authenticated farmer."""
    farm = Farm(
        farmer_id=current_user.id,
        farm_name=farm_in.farm_name,
        state=farm_in.state,
        district=farm_in.district,
        block=farm_in.block,
        village=farm_in.village,
        pincode=farm_in.pincode,
        total_area_acres=farm_in.total_area_acres,
        cultivated_area_acres=farm_in.cultivated_area_acres,
        irrigation_type=farm_in.irrigation_type,
        soil_type=farm_in.soil_type,
        ownership_type=farm_in.ownership_type,
        latitude=farm_in.latitude,
        longitude=farm_in.longitude,
        elevation_meters=farm_in.elevation_meters,
        is_active=True
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(
    farm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves a farm by ID with IDOR protection."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found.")
    
    if farm.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this farm record.")
    
    return farm


@router.put("/{farm_id}", response_model=FarmOut)
def update_farm(
    farm_id: str,
    farm_in: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates farm details with IDOR protection."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found.")
    
    if farm.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this farm record.")

    update_data = farm_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)

    db.commit()
    db.refresh(farm)
    return farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes a farm with IDOR protection."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found.")
    
    if farm.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this farm record.")

    db.delete(farm)
    db.commit()
    return None
