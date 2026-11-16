from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class ProfitabilityScenario(Base, TimestampMixin):
    __tablename__ = "profitability_scenarios"

    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_title = Column(String(200), default="Default Crop Projection", nullable=False)
    
    area_acres = Column(Float, default=1.0, nullable=False)
    expected_yield_per_acre = Column(Float, nullable=False)
    expected_sale_price_per_quintal = Column(Float, nullable=False)
    
    # Cost Breakdown
    seed_cost = Column(Float, default=0.0, nullable=False)
    fertilizer_cost = Column(Float, default=0.0, nullable=False)
    pesticide_cost = Column(Float, default=0.0, nullable=False)
    irrigation_cost = Column(Float, default=0.0, nullable=False)
    labor_cost = Column(Float, default=0.0, nullable=False)
    machinery_cost = Column(Float, default=0.0, nullable=False)
    miscellaneous_cost = Column(Float, default=0.0, nullable=False)
    
    # Calculated Financial Indicators
    gross_income = Column(Float, nullable=False)
    total_expenses = Column(Float, nullable=False)
    net_profit = Column(Float, nullable=False)
    benefit_cost_ratio = Column(Float, nullable=False)
    breakeven_yield_per_acre = Column(Float, nullable=False)
    breakeven_price_per_quintal = Column(Float, nullable=False)

    farm = relationship("Farm", back_populates="profitability_scenarios")
    crop = relationship("Crop", back_populates="scenarios")
