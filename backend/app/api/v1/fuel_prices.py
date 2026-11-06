from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.fuel_price import FuelPrice
from app.models.user import User
from app.schemas.calculator import FuelPriceResponse, FuelPriceCreate, FuelPriceUpdate

router = APIRouter()


@router.get("/", response_model=List[FuelPriceResponse])
def get_fuel_prices(db: Session = Depends(deps.get_db)):
    """
    Get all current fuel and electricity (SPKLU) prices in Indonesia.
    """
    return db.query(FuelPrice).order_by(FuelPrice.fuel_type.asc()).all()


@router.post("/", response_model=FuelPriceResponse, status_code=status.HTTP_201_CREATED)
def create_fuel_price(
    price_in: FuelPriceCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Add a new fuel or electricity price (Admin only).
    """
    existing = db.query(FuelPrice).filter(FuelPrice.fuel_type.ilike(price_in.fuel_type.strip())).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tarif energi ini sudah terdaftar")

    fp = FuelPrice(
        fuel_type=price_in.fuel_type.strip(),
        price_per_unit=price_in.price_per_unit,
        unit=price_in.unit.strip() if price_in.unit else "L"
    )
    db.add(fp)
    db.commit()
    db.refresh(fp)

    try:
        from app.api.v1.cars import trigger_frontend_export
        trigger_frontend_export()
    except Exception:
        pass

    return fp


@router.put("/{id_or_type}", response_model=FuelPriceResponse)
def update_fuel_price(
    id_or_type: str,
    price_in: FuelPriceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update a fuel/electricity price by ID or Name (Admin only).
    """
    if id_or_type.isdigit():
        fp = db.query(FuelPrice).filter(FuelPrice.id == int(id_or_type)).first()
    else:
        fp = db.query(FuelPrice).filter(FuelPrice.fuel_type.ilike(id_or_type.strip())).first()

    if not fp:
        raise HTTPException(status_code=404, detail="Tarif energi tidak ditemukan")

    if price_in.fuel_type:
        new_name = price_in.fuel_type.strip()
        existing = db.query(FuelPrice).filter(
            FuelPrice.fuel_type.ilike(new_name),
            FuelPrice.id != fp.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Nama tarif energi ini sudah digunakan oleh data lain")
        fp.fuel_type = new_name
    if price_in.price_per_unit is not None:
        fp.price_per_unit = price_in.price_per_unit
    if price_in.unit:
        fp.unit = price_in.unit.strip()

    db.commit()
    db.refresh(fp)

    try:
        from app.api.v1.cars import trigger_frontend_export
        trigger_frontend_export()
    except Exception:
        pass

    return fp


@router.delete("/{id_or_type}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_price(
    id_or_type: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a fuel/electricity price by ID or Name (Admin only).
    """
    if id_or_type.isdigit():
        fp = db.query(FuelPrice).filter(FuelPrice.id == int(id_or_type)).first()
    else:
        fp = db.query(FuelPrice).filter(FuelPrice.fuel_type.ilike(id_or_type.strip())).first()

    if not fp:
        raise HTTPException(status_code=404, detail="Tarif energi tidak ditemukan")

    db.delete(fp)
    db.commit()

    try:
        from app.api.v1.cars import trigger_frontend_export
        trigger_frontend_export()
    except Exception:
        pass

    return None
