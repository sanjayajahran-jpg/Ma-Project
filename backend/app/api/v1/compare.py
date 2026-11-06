from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.api import deps
from app.models.car import Car, CarStatus
from app.schemas.compare import CompareRequest, CompareResponse
from app.api.v1.cars import _populate_car_relations

router = APIRouter()


@router.post("/", response_model=CompareResponse)
def compare_cars(
    payload: CompareRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Compare 2 to 4 cars side-by-side with complete technical specifications.
    """
    ids = payload.ids or []
    slugs = payload.slugs or []

    if not ids and not slugs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide 'ids' or 'slugs' array with 2 to 4 items"
        )

    target_count = len(ids) if ids else len(slugs)
    if target_count < 2 or target_count > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comparison requires between 2 and 4 cars"
        )

    query = (
        db.query(Car)
        .options(
            joinedload(Car.brand),
            joinedload(Car.engine_type),
            joinedload(Car.body_type),
            joinedload(Car.specs),
            joinedload(Car.variants),
        )
        .filter(Car.status == CarStatus.active)
    )

    if ids:
        cars = query.filter(Car.id.in_(ids)).all()
    else:
        cars = query.filter(Car.slug.in_(slugs)).all()

    if len(cars) < 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough valid cars found for comparison"
        )

    result_cars = []
    for c in cars:
        cdict = _populate_car_relations(c, db)
        cdict["specs"] = c.specs
        cdict["variants"] = c.variants
        result_cars.append(cdict)

    return {"cars": result_cars}
