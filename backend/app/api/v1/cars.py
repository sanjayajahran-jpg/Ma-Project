from typing import List, Optional
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, asc, func
from app.api import deps
from app.models.car import Car, CarSpec, CarVariant, EngineType, BodyType, CarStatus
from app.models.brand import Brand
from app.models.user import User
from app.models.article import ArticleCarLink
from app.schemas.car import (
    CarCreate, CarUpdate, CarListResponse, CarDetailResponse,
    CarPaginatedResponse, EngineTypeResponse, BodyTypeResponse,
    CarSpecCreate, CarSpecResponse, CarVariantCreate, CarVariantResponse,
    LinkedArticleSummary
)

router = APIRouter()


def _populate_car_relations(car: Car, db: Session) -> dict:
    """Helper to convert Car ORM model to dictionary with joined names."""
    data = {
        "id": car.id,
        "name": car.name,
        "slug": car.slug,
        "brand_id": car.brand_id,
        "engine_type_id": car.engine_type_id,
        "body_type_id": car.body_type_id,
        "year": car.year,
        "price_start": car.price_start,
        "price_end": car.price_end,
        "tagline": car.tagline,
        "description": car.description,
        "image_url": car.image_url,
        "thumbnail_url": car.thumbnail_url,
        "brochure_url": getattr(car, "brochure_url", None),
        "gallery_json": getattr(car, "gallery_json", None),
        "is_featured": car.is_featured,
        "is_new": car.is_new,
        "status": car.status,
        "deleted_at": getattr(car, "deleted_at", None),
        "created_at": car.created_at,
        "brand_name": car.brand.name if car.brand else None,
        "brand_slug": car.brand.slug if car.brand else None,
        "engine_type_name": car.engine_type.name if car.engine_type else None,
        "engine_type_slug": car.engine_type.slug if car.engine_type else None,
        "body_type_name": car.body_type.name if car.body_type else None,
        "body_type_slug": car.body_type.slug if car.body_type else None,
    }
    return data


def trigger_frontend_export():
    """Trigger direct export to src/data/electrified-cars.json so web frontend is immediately in sync."""
    backend_dir = Path(__file__).resolve().parent.parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    try:
        from export_frontend_cars import export_cars
        export_cars()
    except Exception as e:
        import subprocess
        export_script = backend_dir / "export_frontend_cars.py"
        if export_script.exists():
            subprocess.run([sys.executable, str(export_script)], cwd=str(backend_dir), capture_output=True, text=True)


@router.get("/engine-types", response_model=List[EngineTypeResponse])
def get_engine_types(db: Session = Depends(deps.get_db)):
    """List all available engine types (EV, Hybrid, ICE, Diesel)."""
    return db.query(EngineType).all()


@router.get("/body-types", response_model=List[BodyTypeResponse])
def get_body_types(db: Session = Depends(deps.get_db)):
    """List all available car body types (SUV, Sedan, MPV, etc)."""
    return db.query(BodyType).all()


@router.get("/", response_model=CarPaginatedResponse)
def get_cars(
    db: Session = Depends(deps.get_db),
    brand: Optional[str] = Query(None, description="Brand slug (e.g. toyota, byd)"),
    engine: Optional[str] = Query(None, description="Engine type slug (e.g. ev, hybrid, bensin, diesel)"),
    body: Optional[str] = Query(None, description="Body type slug (e.g. suv, sedan, hatchback)"),
    year: Optional[int] = Query(None, description="Filter by year (e.g. 2026)"),
    featured: Optional[bool] = Query(None, description="Filter featured cars only"),
    search: Optional[str] = Query(None, description="Search term in car name or tagline"),
    min_price: Optional[int] = Query(None, description="Minimum price filter in IDR"),
    max_price: Optional[int] = Query(None, description="Maximum price filter in IDR"),
    sort: str = Query("newest", description="Sort order: newest, price_asc, price_desc, name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
):
    """
    Search and filter automotive catalog with pagination.
    """
    query = (
        db.query(Car)
        .join(Brand, Car.brand_id == Brand.id)
        .join(EngineType, Car.engine_type_id == EngineType.id)
        .outerjoin(BodyType, Car.body_type_id == BodyType.id)
        .filter(Car.status == CarStatus.active)
    )

    if brand:
        query = query.filter(Brand.slug == brand)
    if engine:
        query = query.filter(EngineType.slug == engine)
    if body:
        query = query.filter(BodyType.slug == body)
    if year:
        query = query.filter(Car.year == year)
    if featured is not None:
        query = query.filter(Car.is_featured == featured)
    if min_price is not None:
        query = query.filter(Car.price_start >= min_price)
    if max_price is not None:
        query = query.filter(Car.price_start <= max_price)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                Car.name.ilike(search_fmt),
                Car.tagline.ilike(search_fmt),
                Brand.name.ilike(search_fmt),
            )
        )

    # Sorting
    if sort == "price_asc":
        query = query.order_by(asc(Car.price_start))
    elif sort == "price_desc":
        query = query.order_by(desc(Car.price_start))
    elif sort == "name":
        query = query.order_by(asc(Car.name))
    else:  # newest default
        query = query.order_by(desc(Car.is_featured), desc(Car.year), desc(Car.created_at))

    total = query.count()
    offset = (page - 1) * page_size
    cars = query.offset(offset).limit(page_size).all()

    items = [_populate_car_relations(c, db) for c in cars]
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{id_or_slug}", response_model=CarDetailResponse)
def get_car_detail(
    id_or_slug: str,
    db: Session = Depends(deps.get_db)
):
    """
    Get full car details including technical specifications and variants.
    """
    query = (
        db.query(Car)
        .options(
            joinedload(Car.brand),
            joinedload(Car.engine_type),
            joinedload(Car.body_type),
            joinedload(Car.specs),
            joinedload(Car.variants),
        )
    )

    if id_or_slug.isdigit():
        car = query.filter(Car.id == int(id_or_slug)).first()
    else:
        car = query.filter(Car.slug == id_or_slug).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    car_dict = _populate_car_relations(car, db)
    car_dict["specs"] = car.specs
    car_dict["variants"] = car.variants

    # Fetch explicitly linked articles
    links = db.query(ArticleCarLink).options(
        joinedload(ArticleCarLink.article)
    ).filter(ArticleCarLink.car_id == car.id).order_by(
        desc(ArticleCarLink.is_primary),
        desc(ArticleCarLink.created_at)
    ).limit(6).all()

    car_dict["articles"] = [
        {
            "id": l.article.id,
            "slug": l.article.slug,
            "title": l.article.title,
            "excerpt": l.article.excerpt,
            "cover_url": l.article.cover_url,
            "category_slug": l.article.category_slug,
            "category_name": l.article.category_name,
            "published_at": l.article.published_at,
            "is_primary": l.is_primary,
            "relation_type": l.relation_type or "featured"
        }
        for l in links if l.article
    ]
    return car_dict


@router.post("/", response_model=CarDetailResponse, status_code=status.HTTP_201_CREATED)
def create_car(
    car_in: CarCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new car record with optional specs & variants (Admin only).
    """
    existing = db.query(Car).filter(Car.slug == car_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Car with this slug already exists")

    # Verify Brand & EngineType exist
    brand = db.query(Brand).filter(Brand.id == car_in.brand_id).first()
    if not brand:
        raise HTTPException(status_code=400, detail="Brand not found")

    engine_type = db.query(EngineType).filter(EngineType.id == car_in.engine_type_id).first()
    if not engine_type:
        raise HTTPException(status_code=400, detail="Engine type not found")

    car_data = car_in.model_dump(exclude={"specs", "variants"})
    car = Car(**car_data)
    db.add(car)
    db.flush()

    # Add Specs if provided
    if car_in.specs:
        spec_data = car_in.specs.model_dump()
        car_spec = CarSpec(car_id=car.id, **spec_data)
        db.add(car_spec)

    # Add Variants if provided
    if car_in.variants:
        for v in car_in.variants:
            car_var = CarVariant(car_id=car.id, **v.model_dump())
            db.add(car_var)

    db.commit()
    db.refresh(car)

    # Immediately synchronize database with frontend electrified-cars.json
    trigger_frontend_export()

    car_dict = _populate_car_relations(car, db)
    car_dict["specs"] = car.specs
    car_dict["variants"] = car.variants
    return car_dict


@router.put("/{id}", response_model=CarDetailResponse)
def update_car(
    id: int,
    car_in: CarUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update car basic details, technical specifications, and variants (Admin only).
    """
    car = db.query(Car).filter(Car.id == id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    update_data = car_in.model_dump(exclude_unset=True, exclude={"specs", "variants"})
    for field, value in update_data.items():
        setattr(car, field, value)

    # Handle Specs update
    if car_in.specs is not None:
        spec_data = car_in.specs.model_dump(exclude_unset=True)
        if car.specs:
            for s_field, s_val in spec_data.items():
                setattr(car.specs, s_field, s_val)
        else:
            new_spec = CarSpec(car_id=car.id, **spec_data)
            db.add(new_spec)

    # Handle Variants update if provided
    if car_in.variants is not None:
        # Clear existing variants and replace with new list
        db.query(CarVariant).filter(CarVariant.car_id == car.id).delete()
        for v in car_in.variants:
            new_var = CarVariant(car_id=car.id, **v.model_dump())
            db.add(new_var)

    db.commit()
    db.refresh(car)

    # Immediately synchronize database with frontend electrified-cars.json
    trigger_frontend_export()

    car_dict = _populate_car_relations(car, db)
    car_dict["specs"] = car.specs
    car_dict["variants"] = car.variants
    return car_dict


@router.get("/{id_or_slug}/articles", response_model=List[LinkedArticleSummary])
def get_car_articles(
    id_or_slug: str,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(deps.get_db)
):
    """
    Mengambil daftar artikel berita yang terhubung secara eksplisit dengan mobil ini.
    """
    car = None
    if id_or_slug.isdigit():
        car = db.query(Car).filter(Car.id == int(id_or_slug)).first()
    if not car:
        car = db.query(Car).filter(Car.slug == id_or_slug).first()

    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    links = db.query(ArticleCarLink).options(
        joinedload(ArticleCarLink.article)
    ).filter(
        ArticleCarLink.car_id == car.id
    ).order_by(
        desc(ArticleCarLink.is_primary),
        desc(ArticleCarLink.created_at)
    ).limit(limit).all()

    results = []
    for link in links:
        if not link.article:
            continue
        art = link.article
        results.append({
            "id": art.id,
            "slug": art.slug,
            "title": art.title,
            "excerpt": art.excerpt,
            "cover_url": art.cover_url,
            "category_slug": art.category_slug,
            "category_name": art.category_name,
            "published_at": art.published_at,
            "is_primary": link.is_primary,
            "relation_type": link.relation_type or "featured"
        })
    return results


@router.delete("/{id}")
def delete_car(
    id: int,
    hard_delete: bool = Query(False, description="Jika True, hapus permanen dari DB jika tidak ada relasi"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Menonaktifkan (soft-delete / status=discontinued) atau menghapus permanen mobil (Admin only).
    Jika mobil memiliki artikel terkait, hard delete akan ditolak demi menjaga integritas data & SEO.
    """
    car = db.query(Car).filter(Car.id == id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    # Cek relasi artikel yang terhubung
    linked_articles_count = db.query(ArticleCarLink).filter(ArticleCarLink.car_id == id).count()

    if hard_delete:
        if linked_articles_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tidak dapat menghapus permanen: Mobil '{car.name}' terhubung ke {linked_articles_count} artikel berita. Ubah status menjadi 'discontinued' (soft-delete) untuk menjaga riwayat berita dan mencegah broken link."
            )
        db.delete(car)
        message = f"Mobil '{car.name}' berhasil dihapus permanen dari database."
    else:
        # Soft-delete: ubah status menjadi discontinued dan catat deleted_at
        car.status = CarStatus.discontinued
        car.deleted_at = datetime.utcnow()
        message = f"Mobil '{car.name}' berhasil dinonaktifkan (status diubah menjadi 'discontinued'). Riwayat berita dan arsip spesifikasi tetap aman."

    db.commit()

    # Immediately synchronize database with frontend electrified-cars.json
    trigger_frontend_export()

    return {"status": "ok", "message": message, "car_id": id, "hard_deleted": hard_delete}


@router.post("/sync-frontend", summary="Sinkronisasi database ke frontend electrified-cars.json")
def sync_frontend_data(db: Session = Depends(deps.get_db)):
    """
    Menyinkronkan data mobil terbaru dari database ke frontend (src/data/electrified-cars.json).
    """
    try:
        trigger_frontend_export()
        return {
            "status": "ok",
            "message": "Data database mobil berhasil disinkronkan ke web frontend!"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gagal menjalankan sinkronisasi: {str(e)}"
        }

