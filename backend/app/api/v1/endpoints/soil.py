from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.farm import Farm
from app.models.soil import SoilTest
from app.schemas.soil import SoilTestCreate, SoilTestOut

router = APIRouter()


@router.get("/", response_model=List[SoilTestOut])
def list_soil_tests(
    farm_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SoilTest).join(Farm).filter(Farm.farmer_id == current_user.id)
    if farm_id:
        query = query.filter(SoilTest.farm_id == farm_id)
    return query.order_by(SoilTest.test_date.desc()).all()


@router.post("/", response_model=SoilTestOut, status_code=status.HTTP_201_CREATED)
def record_soil_test(
    soil_in: SoilTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.query(Farm).filter(Farm.id == soil_in.farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found.")
    
    if farm.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    soil_test = SoilTest(
        farm_id=soil_in.farm_id,
        test_date=soil_in.test_date,
        soil_ph=soil_in.soil_ph,
        organic_carbon_percent=soil_in.organic_carbon_percent,
        nitrogen_kg_ha=soil_in.nitrogen_kg_ha,
        phosphorus_kg_ha=soil_in.phosphorus_kg_ha,
        potassium_kg_ha=soil_in.potassium_kg_ha,
        sulphur_ppm=soil_in.sulphur_ppm,
        zinc_ppm=soil_in.zinc_ppm,
        iron_ppm=soil_in.iron_ppm,
        electrical_conductivity=soil_in.electrical_conductivity,
        testing_lab_name=soil_in.testing_lab_name
    )
    db.add(soil_test)
    db.commit()
    db.refresh(soil_test)
    return soil_test


@router.get("/{soil_id}", response_model=SoilTestOut)
def get_soil_test(
    soil_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    soil_test = db.query(SoilTest).filter(SoilTest.id == soil_id).first()
    if not soil_test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soil test record not found.")
    
    if soil_test.farm.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return soil_test
