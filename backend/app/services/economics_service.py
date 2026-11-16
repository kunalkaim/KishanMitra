from app.schemas.economics import ProfitabilityInput, ProfitabilityOut
from app.models.crop import Crop
from datetime import datetime, timezone
import uuid


class EconomicsService:
    @staticmethod
    def calculate_scenario(input_data: ProfitabilityInput, crop: Crop) -> ProfitabilityOut:
        area = input_data.area_acres
        yield_per_acre = input_data.expected_yield_per_acre
        sale_price = input_data.expected_sale_price_per_quintal

        total_yield = area * yield_per_acre
        gross_income = round(total_yield * sale_price, 2)

        # Sum of expenses across the entire cultivated area
        seed = input_data.seed_cost * area
        fertilizer = input_data.fertilizer_cost * area
        pesticide = input_data.pesticide_cost * area
        irrigation = input_data.irrigation_cost * area
        labor = input_data.labor_cost * area
        machinery = input_data.machinery_cost * area
        misc = input_data.miscellaneous_cost * area

        total_expenses = round(seed + fertilizer + pesticide + irrigation + labor + machinery + misc, 2)
        net_profit = round(gross_income - total_expenses, 2)
        profit_per_acre = round(net_profit / area, 2)

        # Benefit Cost Ratio (BCR = Gross Income / Total Expenses)
        bcr = round(gross_income / total_expenses, 2) if total_expenses > 0 else 0.0

        # Breakeven Yield (Quintals/acre) = Expenses per acre / Sale price per quintal
        expenses_per_acre = total_expenses / area
        breakeven_yield = round(expenses_per_acre / sale_price, 2) if sale_price > 0 else 0.0

        # Breakeven Price (₹/Quintal) = Expenses per acre / Yield per acre
        breakeven_price = round(expenses_per_acre / yield_per_acre, 2) if yield_per_acre > 0 else 0.0

        cost_breakdown = {
            "seed": seed,
            "fertilizer": fertilizer,
            "pesticide": pesticide,
            "irrigation": irrigation,
            "labor": labor,
            "machinery": machinery,
            "miscellaneous": misc
        }

        return ProfitabilityOut(
            id=str(uuid.uuid4()),
            crop_id=crop.id,
            crop_name=crop.crop_name,
            scenario_title=input_data.scenario_title or f"{crop.crop_name} Financial Projection",
            area_acres=area,
            expected_yield_per_acre=yield_per_acre,
            expected_sale_price_per_quintal=sale_price,
            gross_income=gross_income,
            total_expenses=total_expenses,
            net_profit=net_profit,
            profit_per_acre=profit_per_acre,
            benefit_cost_ratio=bcr,
            breakeven_yield_per_acre=breakeven_yield,
            breakeven_price_per_quintal=breakeven_price,
            cost_breakdown=cost_breakdown,
            created_at=datetime.now(timezone.utc)
        )


economics_service = EconomicsService()
