from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.fuel_price import FuelPrice
from app.schemas.calculator import FuelCostRequest, FuelCostResponse, FuelCostResultItem, FuelCostSummary

router = APIRouter()


@router.post("/fuel-cost", response_model=FuelCostResponse)
def calculate_fuel_cost(
    payload: FuelCostRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Calculate and compare monthly & yearly fuel or electricity costs.
    """
    if not payload.comparisons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one fuel comparison item"
        )

    # Fetch fuel prices from DB
    prices = db.query(FuelPrice).all()
    price_map = {p.fuel_type: p for p in prices}

    results = []
    for comp in payload.comparisons:
        price_obj = price_map.get(comp.fuel_type)
        price_per_unit = price_obj.price_per_unit if price_obj else 0.0
        unit = price_obj.unit if price_obj else "L"

        if comp.consumption_kmpl <= 0:
            fuel_needed = 0.0
            monthly_cost = 0.0
        else:
            fuel_needed = payload.distance_km / comp.consumption_kmpl
            monthly_cost = fuel_needed * price_per_unit

        yearly_cost = monthly_cost * 12.0

        results.append(
            FuelCostResultItem(
                fuel_type=comp.fuel_type,
                price_per_unit=price_per_unit,
                unit=unit,
                consumption=comp.consumption_kmpl,
                distance_km=payload.distance_km,
                fuel_needed=round(fuel_needed, 2),
                monthly_cost=round(monthly_cost, 2),
                yearly_cost=round(yearly_cost, 2),
            )
        )

    # Sort results by monthly cost
    sorted_results = sorted(results, key=lambda r: r.monthly_cost)
    cheapest = sorted_results[0]
    most_expensive = sorted_results[-1]
    monthly_saving = most_expensive.monthly_cost - cheapest.monthly_cost
    yearly_saving = most_expensive.yearly_cost - cheapest.yearly_cost

    summary = FuelCostSummary(
        cheapest=cheapest.fuel_type,
        most_expensive=most_expensive.fuel_type,
        monthly_saving=round(monthly_saving, 2),
        yearly_saving=round(yearly_saving, 2),
    )

    return FuelCostResponse(
        distance_km=payload.distance_km,
        results=results,
        summary=summary,
    )
