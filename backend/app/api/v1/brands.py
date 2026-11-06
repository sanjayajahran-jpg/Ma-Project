from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.models.brand import Brand
from app.models.car import Car, CarStatus
from app.models.user import User
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse

router = APIRouter()


@router.get("/", response_model=List[BrandResponse])
def get_brands(
    db: Session = Depends(deps.get_db),
    with_count: bool = Query(False, description="Include count of active cars per brand"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Retrieve all automotive brands.
    """
    if with_count:
        results = (
            db.query(Brand, func.count(Car.id).label("car_count"))
            .outerjoin(Car, (Car.brand_id == Brand.id) & (Car.status == CarStatus.active))
            .group_by(Brand.id)
            .order_by(Brand.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        output = []
        for brand, count in results:
            b_resp = BrandResponse.model_validate(brand)
            b_resp.car_count = count
            output.append(b_resp)
        return output

    brands = db.query(Brand).order_by(Brand.name.asc()).offset(skip).limit(limit).all()
    return brands


@router.get("/{id_or_slug}", response_model=BrandResponse)
def get_brand(
    id_or_slug: str,
    db: Session = Depends(deps.get_db)
):
    """
    Get brand by ID or Slug.
    """
    if id_or_slug.isdigit():
        brand = db.query(Brand).filter(Brand.id == int(id_or_slug)).first()
    else:
        brand = db.query(Brand).filter(Brand.slug == id_or_slug).first()

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new brand (Admin only).
    """
    existing = db.query(Brand).filter(Brand.slug == brand_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Brand with this slug already exists")

    brand = Brand(**brand_in.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)

    try:
        from app.api.v1.cars import trigger_frontend_export
        trigger_frontend_export()
    except Exception:
        pass

    return brand


@router.put("/{id}", response_model=BrandResponse)
def update_brand(
    id: int,
    brand_in: BrandUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update a brand (Admin only).
    """
    brand = db.query(Brand).filter(Brand.id == id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    update_data = brand_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)

    db.commit()
    db.refresh(brand)

    try:
        from app.api.v1.cars import trigger_frontend_export
        trigger_frontend_export()
    except Exception:
        pass

    return brand


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a brand (Admin only).
    """
    brand = db.query(Brand).filter(Brand.id == id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    db.delete(brand)
    db.commit()

    try:
        from app.api.v1.cars import trigger_frontend_export
        trigger_frontend_export()
    except Exception:
        pass

    return None


@router.get("/{id_or_slug}/cars")
def get_brand_cars(
    id_or_slug: str,
    db: Session = Depends(deps.get_db)
):
    """
    Retrieve all cars and their specifications under a specific brand.
    """
    if id_or_slug.isdigit():
        brand = db.query(Brand).filter(Brand.id == int(id_or_slug)).first()
    else:
        brand = db.query(Brand).filter(Brand.slug == id_or_slug).first()

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    cars = (
        db.query(Car)
        .filter(Car.brand_id == brand.id, Car.status == CarStatus.active)
        .order_by(Car.year.desc(), Car.name.asc())
        .all()
    )

    result = []
    for c in cars:
        result.append({
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "year": c.year,
            "price_start": c.price_start,
            "price_end": c.price_end,
            "tagline": c.tagline,
            "image_url": c.image_url,
            "brochure_url": getattr(c, "brochure_url", None),
            "engine_type_slug": c.engine_type.slug if c.engine_type else None,
            "engine_type_name": c.engine_type.name if c.engine_type else None,
            "body_type_name": c.body_type.name if c.body_type else None,
            "brand_slug": brand.slug,
            "brand_name": brand.name,
        })

    return {
        "brand": {
            "id": brand.id,
            "name": brand.name,
            "slug": brand.slug,
            "logo_url": brand.logo_url,
            "country": brand.country,
        },
        "cars": result,
        "total": len(result)
    }

