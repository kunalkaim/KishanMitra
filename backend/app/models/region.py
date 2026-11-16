from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class State(Base, TimestampMixin):
    __tablename__ = "states"

    state_name = Column(String(100), unique=True, nullable=False, index=True)
    state_code = Column(String(10), unique=True, nullable=False)

    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")


class District(Base, TimestampMixin):
    __tablename__ = "districts"

    state_id = Column(String(36), ForeignKey("states.id", ondelete="CASCADE"), nullable=False)
    district_name = Column(String(100), nullable=False, index=True)
    agro_climatic_zone = Column(String(100), nullable=False)  # e.g., 'Sub-temperate Mid-hills'
    elevation_bracket = Column(String(100), nullable=False)  # e.g., '1200m - 2400m'
    average_annual_rainfall_mm = Column(Float, default=1100.0, nullable=False)
    dominant_soil_types = Column(JSON, default=list, nullable=False)
    primary_crops = Column(JSON, default=list, nullable=False)

    state = relationship("State", back_populates="districts")
    blocks = relationship("Block", back_populates="district", cascade="all, delete-orphan")


class Block(Base, TimestampMixin):
    __tablename__ = "blocks"

    district_id = Column(String(36), ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    block_name = Column(String(100), nullable=False, index=True)

    district = relationship("District", back_populates="blocks")
