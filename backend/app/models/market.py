from sqlalchemy import Column, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class Mandi(Base, TimestampMixin):
    __tablename__ = "mandis"

    mandi_name = Column(String(150), nullable=False, index=True)
    district_name = Column(String(100), nullable=False, index=True)
    state_name = Column(String(100), default="Uttarakhand", nullable=False)
    contact_number = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_operational = Column(Boolean, default=True, nullable=False)

    prices = relationship("MarketPrice", back_populates="mandi", cascade="all, delete-orphan")


class MarketPrice(Base, TimestampMixin):
    __tablename__ = "market_prices"

    mandi_id = Column(String(36), ForeignKey("mandis.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True)
    arrival_date = Column(Date, nullable=False, index=True)
    
    min_price_per_quintal = Column(Float, nullable=False)
    max_price_per_quintal = Column(Float, nullable=False)
    modal_price_per_quintal = Column(Float, nullable=False)
    arrivals_in_tonnes = Column(Float, default=10.0, nullable=False)

    mandi = relationship("Mandi", back_populates="prices")
    crop = relationship("Crop", back_populates="market_prices")
