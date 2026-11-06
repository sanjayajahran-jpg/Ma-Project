from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class FuelPriceResponse(BaseModel):
    id: int
    fuel_type: str
    price_per_unit: float
    unit: str
    updated_at: datetime

    class Config:
        from_attributes = True


class FuelPriceCreate(BaseModel):
    fuel_type: str = Field(..., example="Pertamax Turbo")
    price_per_unit: float = Field(..., example=15100.0)
    unit: str = Field(default="L", example="L")


class FuelPriceUpdate(BaseModel):
    fuel_type: Optional[str] = None
    price_per_unit: float
    unit: Optional[str] = None


class FuelComparisonItem(BaseModel):
    fuel_type: str = Field(..., example="Pertamax")
    consumption_kmpl: float = Field(..., example=12.0, description="km/L for gas/diesel, or km/kWh for EV")


class FuelCostRequest(BaseModel):
    distance_km: float = Field(default=1500.0, description="Estimated monthly driving distance in km")
    comparisons: List[FuelComparisonItem]


class FuelCostResultItem(BaseModel):
    fuel_type: str
    price_per_unit: float
    unit: str
    consumption: float
    distance_km: float
    fuel_needed: float
    monthly_cost: float
    yearly_cost: float


class FuelCostSummary(BaseModel):
    cheapest: str
    most_expensive: str
    monthly_saving: float
    yearly_saving: float


class FuelCostResponse(BaseModel):
    distance_km: float
    results: List[FuelCostResultItem]
    summary: FuelCostSummary
