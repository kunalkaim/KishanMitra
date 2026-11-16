from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.market import Mandi, MarketPrice
from app.models.crop import Crop
from app.schemas.market import MandiOut, MarketPriceOut, MandiComparison

router = APIRouter()


@router.get("/mandis", response_model=List[MandiOut])
def list_mandis(district: Optional[str] = None, db: Session = Depends(get_db)):
    """Lists operational mandis in Uttarakhand and nearby markets."""
    query = db.query(Mandi).filter(Mandi.is_operational == True)
    if district:
        query = query.filter(Mandi.district_name.ilike(f"%{district}%"))
    return query.order_by(Mandi.mandi_name.asc()).all()


@router.get("/prices", response_model=List[MarketPriceOut])
def get_market_prices(
    district: Optional[str] = None,
    crop_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves current daily mandi arrival prices across Uttarakhand markets."""
    query = db.query(MarketPrice).join(Mandi).join(Crop)
    if district:
        query = query.filter(Mandi.district_name.ilike(f"%{district}%"))
    if crop_name:
        query = query.filter(Crop.crop_name.ilike(f"%{crop_name}%"))

    prices = query.order_by(MarketPrice.arrival_date.desc()).all()
    out = []
    for p in prices:
        out.append(
            MarketPriceOut(
                id=p.id,
                mandi_id=p.mandi_id,
                mandi_name=p.mandi.mandi_name,
                district_name=p.mandi.district_name,
                crop_id=p.crop_id,
                crop_name=p.crop.crop_name,
                arrival_date=p.arrival_date,
                min_price_per_quintal=p.min_price_per_quintal,
                max_price_per_quintal=p.max_price_per_quintal,
                modal_price_per_quintal=p.modal_price_per_quintal,
                arrivals_in_tonnes=p.arrivals_in_tonnes,
                trend="rising" if p.modal_price_per_quintal > 3000 else "stable"
            )
        )
    return out


@router.get("/comparison", response_model=MandiComparison)
def compare_mandi_prices(
    crop_name: str = Query(default="Finger Millet (Mandua / Ragi)"),
    db: Session = Depends(get_db)
):
    """Compares prices for a crop across different mandis to identify arbitrage opportunities."""
    prices = (
        db.query(MarketPrice)
        .join(Mandi)
        .join(Crop)
        .filter(Crop.crop_name.ilike(f"%{crop_name}%"))
        .order_by(MarketPrice.modal_price_per_quintal.desc())
        .all()
    )

    if not prices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No price records found for {crop_name}")

    price_outs = [
        MarketPriceOut(
            id=p.id,
            mandi_id=p.mandi_id,
            mandi_name=p.mandi.mandi_name,
            district_name=p.mandi.district_name,
            crop_id=p.crop_id,
            crop_name=p.crop.crop_name,
            arrival_date=p.arrival_date,
            min_price_per_quintal=p.min_price_per_quintal,
            max_price_per_quintal=p.max_price_per_quintal,
            modal_price_per_quintal=p.modal_price_per_quintal,
            arrivals_in_tonnes=p.arrivals_in_tonnes,
            trend="rising"
        )
        for p in prices
    ]

    highest = price_outs[0]
    lowest = price_outs[-1]

    diff = highest.modal_price_per_quintal - lowest.modal_price_per_quintal
    recommendation = (
        f"Transporting to {highest.mandi_name} yields a premium of ₹{diff:.0f}/quintal compared to {lowest.mandi_name}. "
        "Factor in transportation cost (~₹120-180/quintal) for net arbitrage margin."
    )

    return MandiComparison(
        crop_name=crop_name,
        prices=price_outs,
        highest_mandi=highest.mandi_name,
        highest_price=highest.modal_price_per_quintal,
        lowest_mandi=lowest.mandi_name,
        lowest_price=lowest.modal_price_per_quintal,
        recommendation=recommendation
    )
