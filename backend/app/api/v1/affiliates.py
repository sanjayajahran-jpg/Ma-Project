from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.user import User
from app.models.car import Car
from app.models.affiliate import CarAffiliate
from app.schemas.affiliate import (
    CarAffiliateCreate,
    CarAffiliateUpdate,
    CarAffiliateResponse
)

router = APIRouter()


def trigger_export():
    """Helper untuk memicu auto-export frontend saat data affiliate berubah"""
    try:
        from app.api.v1.cars import trigger_frontend_export
        trigger_frontend_export()
    except Exception:
        pass


@router.get("/car/{car_identifier}", response_model=List[CarAffiliateResponse], summary="Ambil produk affiliate untuk satu mobil")
def get_car_affiliates(
    car_identifier: str,
    db: Session = Depends(get_db)
):
    """
    Mengambil seluruh produk affiliate dan aksesoris khusus untuk satu mobil (berdasarkan ID atau Slug mobil).
    """
    car = None
    if car_identifier.isdigit():
        car = db.query(Car).filter(Car.id == int(car_identifier)).first()
    if not car:
        car = db.query(Car).filter(Car.slug == car_identifier.lower().strip()).first()

    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mobil '{car_identifier}' tidak ditemukan"
        )

    affiliates = db.query(CarAffiliate).filter(
        CarAffiliate.car_id == car.id,
        CarAffiliate.is_active == True
    ).order_by(CarAffiliate.sort_order.asc(), CarAffiliate.id.asc()).all()

    return affiliates


@router.get("/{id}", response_model=CarAffiliateResponse, summary="Ambil detail satu produk affiliate")
def get_affiliate_by_id(id: int, db: Session = Depends(get_db)):
    item = db.query(CarAffiliate).filter(CarAffiliate.id == id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produk affiliate dengan ID {id} tidak ditemukan"
        )
    return item


@router.post("/", response_model=CarAffiliateResponse, status_code=status.HTTP_201_CREATED, summary="Tambah produk affiliate baru")
def create_car_affiliate(
    affiliate_in: CarAffiliateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Admin: Menambahkan produk affiliate baru untuk mobil tertentu.
    """
    car = db.query(Car).filter(Car.id == affiliate_in.car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mobil dengan ID {affiliate_in.car_id} tidak ditemukan"
        )

    item = CarAffiliate(
        car_id=affiliate_in.car_id,
        title=affiliate_in.title,
        image_url=affiliate_in.image_url,
        affiliate_url=affiliate_in.affiliate_url,
        price=affiliate_in.price,
        merchant=affiliate_in.merchant or "Tokopedia",
        badge=affiliate_in.badge,
        description=affiliate_in.description,
        sort_order=affiliate_in.sort_order or 1,
        is_active=affiliate_in.is_active if affiliate_in.is_active is not None else True
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    trigger_export()
    return item


@router.put("/{id}", response_model=CarAffiliateResponse, summary="Perbarui produk affiliate")
def update_car_affiliate(
    id: int,
    affiliate_in: CarAffiliateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Admin: Memperbarui judul, link, gambar, harga, atau status aktif produk affiliate.
    """
    item = db.query(CarAffiliate).filter(CarAffiliate.id == id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produk affiliate dengan ID {id} tidak ditemukan"
        )

    update_data = affiliate_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(item, field, val)

    db.commit()
    db.refresh(item)

    trigger_export()
    return item


@router.delete("/{id}", summary="Hapus produk affiliate")
def delete_car_affiliate(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Admin: Menghapus produk affiliate dari database.
    """
    item = db.query(CarAffiliate).filter(CarAffiliate.id == id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produk affiliate dengan ID {id} tidak ditemukan"
        )

    car_id = item.car_id
    db.delete(item)
    db.commit()

    trigger_export()
    return {
        "id": id,
        "car_id": car_id,
        "message": "Produk affiliate berhasil dihapus"
    }
