from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.region import State, District, Block
from app.schemas.region import StateOut, DistrictOut

router = APIRouter()


@router.get("/districts", response_model=List[DistrictOut])
def list_districts(state_name: str = "Uttarakhand", db: Session = Depends(get_db)):
    """Lists all 13 agricultural districts of Uttarakhand with agro-climatic profiles."""
    districts = db.query(District).join(State).filter(State.state_name == state_name).order_by(District.district_name.asc()).all()
    return districts


@router.get("/districts/{district_id}", response_model=DistrictOut)
def get_district_details(district_id: str, db: Session = Depends(get_db)):
    """Retrieves district agro-climatic details, rainfall, soils, and primary crops."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District not found.")
    return district
