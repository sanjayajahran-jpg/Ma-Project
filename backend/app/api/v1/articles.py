from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc

from app.api import deps
from app.models.article import CMSArticle, ArticleCarLink
from app.models.car import Car
from app.models.user import User
from app.schemas.article import (
    ArticleListResponse, ArticleResponse, 
    ArticleCarLinkCreate, LinkedCarSummary
)

router = APIRouter()


@router.get("/", response_model=ArticleListResponse)
def list_articles(
    db: Session = Depends(deps.get_db),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    search: Optional[str] = Query(None, description="Search query in title or excerpt"),
    portal_id: Optional[str] = Query(None, description="Filter by portal ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Mengambil daftar artikel tersinkronisasi dari Supabase PostgreSQL.
    """
    query = db.query(CMSArticle)

    if portal_id:
        query = query.filter(CMSArticle.portal_id == portal_id)

    if category:
        query = query.filter(CMSArticle.category_slug == category.lower())

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                CMSArticle.title.ilike(search_pattern),
                CMSArticle.excerpt.ilike(search_pattern)
            )
        )

    total = query.count()
    items = query.order_by(desc(CMSArticle.published_at)).offset(skip).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{id_or_slug}", response_model=ArticleResponse)
def get_article(
    id_or_slug: str,
    db: Session = Depends(deps.get_db)
):
    """
    Mengambil satu artikel berdasarkan slug atau ID remote CMS.
    """
    article = db.query(CMSArticle).filter(
        or_(
            CMSArticle.id == id_or_slug,
            CMSArticle.slug == id_or_slug
        )
    ).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artikel '{id_or_slug}' tidak ditemukan di database Supabase."
        )

    return article


@router.get("/{id_or_slug}/cars", response_model=List[LinkedCarSummary])
def get_article_linked_cars(
    id_or_slug: str,
    db: Session = Depends(deps.get_db)
):
    """
    Mengambil daftar kendaraan yang terhubung secara eksplisit dengan artikel ini (untuk Car Widget).
    """
    article = db.query(CMSArticle).filter(
        or_(CMSArticle.id == id_or_slug, CMSArticle.slug == id_or_slug)
    ).first()

    if not article:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")

    links = db.query(ArticleCarLink).options(
        joinedload(ArticleCarLink.car).joinedload(Car.brand)
    ).filter(ArticleCarLink.article_id == article.id).all()

    results = []
    for link in links:
        if not link.car:
            continue
        c = link.car
        results.append({
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "brand_name": c.brand.name if c.brand else None,
            "brand_slug": c.brand.slug if c.brand else None,
            "year": c.year,
            "price_start": c.price_start,
            "price_end": c.price_end,
            "image_url": c.image_url,
            "thumbnail_url": c.thumbnail_url,
            "status": str(c.status.value if hasattr(c.status, "value") else c.status),
            "is_primary": link.is_primary,
            "relation_type": link.relation_type or "featured"
        })
    return results


@router.post("/{article_id}/link-car", status_code=status.HTTP_201_CREATED)
def link_car_to_article(
    article_id: str,
    payload: ArticleCarLinkCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Menghubungkan artikel dengan mobil tertentu (Admin only).
    """
    article = db.query(CMSArticle).filter(CMSArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")

    car = db.query(Car).filter(Car.id == payload.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    # Cek apakah relasi sudah ada
    existing = db.query(ArticleCarLink).filter(
        ArticleCarLink.article_id == article_id,
        ArticleCarLink.car_id == payload.car_id
    ).first()

    if existing:
        existing.is_primary = payload.is_primary
        existing.relation_type = payload.relation_type
        db.commit()
        return {"status": "ok", "message": "Relasi mobil diperbarui"}

    new_link = ArticleCarLink(
        article_id=article_id,
        car_id=payload.car_id,
        is_primary=payload.is_primary,
        relation_type=payload.relation_type
    )
    db.add(new_link)
    db.commit()
    return {"status": "ok", "message": "Mobil berhasil dihubungkan ke artikel"}


@router.delete("/{article_id}/link-car/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_car_from_article(
    article_id: str,
    car_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Memutuskan relasi antara mobil dan artikel (Admin only).
    """
    link = db.query(ArticleCarLink).filter(
        ArticleCarLink.article_id == article_id,
        ArticleCarLink.car_id == car_id
    ).first()

    if link:
        db.delete(link)
        db.commit()

    return None
