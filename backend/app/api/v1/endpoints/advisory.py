from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.farm import Farm
from app.models.advisory import AdvisoryCase
from app.schemas.advisory import AdvisoryInput, AdvisoryResponse
from app.services.advisory_service import advisory_service

router = APIRouter()


@router.post("/cases", response_model=AdvisoryResponse, status_code=status.HTTP_201_CREATED)
def submit_advisory_case(
    input_data: AdvisoryInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits a text-based pest or disease inquiry.
    Uses agronomic diagnostic rules (ICAR-VPKAS Almora / GBPUAT Pantnagar)
    to identify suspected pathogens and generate organic IPM interventions.
    Strictly text-based, no computer vision.
    """
    farm_id = input_data.farm_id
    if not farm_id:
        # Default to first active farm if not explicitly provided
        farm = db.query(Farm).filter(Farm.farmer_id == current_user.id).first()
        farm_id = farm.id if farm else None

    if not farm_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="A registered farm is required to record this advisory case."
        )

    # Generate expert agronomic advisory based on symptoms and environmental conditions
    response = advisory_service.generate_advisory(input_data)

    # Persist advisory case
    advisory_case = AdvisoryCase(
        id=response.id,
        farmer_id=current_user.id,
        farm_id=farm_id,
        crop_name=input_data.crop_name,
        crop_growth_stage=input_data.crop_growth_stage,
        observed_symptoms=input_data.observed_symptoms,
        farming_conditions=input_data.farming_conditions,
        affected_area_percentage=input_data.affected_area_percentage,
        suspected_pest_or_pathogen=response.suspected_pest_or_pathogen,
        diagnostic_category=response.diagnostic_category,
        confidence_level=response.confidence_level,
        advisory_response=response.advisory_response,
        recommended_interventions=[item.model_dump() for item in response.recommended_interventions],
        preventive_measures=response.preventive_measures,
        disclaimer=response.disclaimer
    )
    db.add(advisory_case)
    db.commit()
    db.refresh(advisory_case)

    return response


@router.get("/cases", response_model=List[AdvisoryResponse])
def get_farmer_advisory_history(
    farm_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves history of text-based pest & disease inquiries submitted by the farmer."""
    query = db.query(AdvisoryCase).filter(AdvisoryCase.farmer_id == current_user.id)
    if farm_id:
        query = query.filter(AdvisoryCase.farm_id == farm_id)

    cases = query.order_by(AdvisoryCase.created_at.desc()).all()
    results: List[AdvisoryResponse] = []
    for c in cases:
        results.append(
            AdvisoryResponse(
                id=c.id,
                crop_name=c.crop_name,
                crop_growth_stage=c.crop_growth_stage,
                suspected_pest_or_pathogen=c.suspected_pest_or_pathogen,
                diagnostic_category=c.diagnostic_category,
                confidence_level=c.confidence_level,
                advisory_response=c.advisory_response,
                recommended_interventions=c.recommended_interventions or [],
                preventive_measures=c.preventive_measures or [],
                disclaimer=c.disclaimer,
                is_demo=True,
                created_at=c.created_at
            )
        )
    return results


@router.get("/cases/{case_id}", response_model=AdvisoryResponse)
def get_advisory_case_detail(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves single advisory case by ID with IDOR protection."""
    c = db.query(AdvisoryCase).filter(AdvisoryCase.id == case_id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advisory case not found.")

    if c.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return AdvisoryResponse(
        id=c.id,
        crop_name=c.crop_name,
        crop_growth_stage=c.crop_growth_stage,
        suspected_pest_or_pathogen=c.suspected_pest_or_pathogen,
        diagnostic_category=c.diagnostic_category,
        confidence_level=c.confidence_level,
        advisory_response=c.advisory_response,
        recommended_interventions=c.recommended_interventions or [],
        preventive_measures=c.preventive_measures or [],
        disclaimer=c.disclaimer,
        is_demo=True,
        created_at=c.created_at
    )
