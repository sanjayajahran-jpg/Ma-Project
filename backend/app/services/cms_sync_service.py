import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.config import settings
from app.models.article import CMSArticle, CMSSyncCheckpoint, ArticleCarLink
from app.models.car import Car
from app.services.cms_client import InovaCMSClient, CMSClientError

logger = logging.getLogger(__name__)


def auto_link_article_to_cars(db: Session, article_id: str, title: str, excerpt: Optional[str], tags: Optional[list], cars_catalog: list):
    """
    Secara cerdas menghubungkan artikel yang baru disinkronisasi dengan model mobil di katalog.
    Menghindari manual tagging berulang dan memastikan integritas relasi foreign key.
    """
    text_haystack = f"{title} {excerpt or ''}".lower()
    tag_names = [t.get("name", "").lower() for t in (tags or []) if isinstance(t, dict)]

    for car_id, car_name, car_slug in cars_catalog:
        c_name_lower = car_name.lower()
        if len(c_name_lower) < 3:
            continue

        is_matched = False
        is_primary = False

        # 1. Jika nama lengkap model mobil muncul di Judul -> Prioritas Utama (Primary)
        if c_name_lower in title.lower():
            is_matched = True
            is_primary = True
        # 2. Jika nama mobil ada di Tags atau Excerpt
        elif any(c_name_lower in tag for tag in tag_names) or (len(c_name_lower) >= 5 and c_name_lower in text_haystack):
            is_matched = True
            is_primary = False

        if is_matched:
            existing_link = db.query(ArticleCarLink).filter(
                ArticleCarLink.article_id == article_id,
                ArticleCarLink.car_id == car_id
            ).first()

            rel_type = "launch" if any(w in text_haystack for w in ["luncur", "resmi rilis", "mengaspal", "debut"]) else "featured"

            if not existing_link:
                new_link = ArticleCarLink(
                    article_id=article_id,
                    car_id=car_id,
                    is_primary=is_primary,
                    relation_type=rel_type
                )
                db.add(new_link)


def slugify(text: str) -> str:
    """Helper untuk menghasilkan slug jika artikel tidak memiliki slug eksplisit."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def extract_slug_from_url(url: Optional[str], fallback_title: str) -> str:
    """Ekstrak slug dari URL artikel (misal https://sewaktu.id/ekonomi/judul-artikel -> judul-artikel)."""
    if url:
        path = urlparse(url).path.strip("/")
        if path:
            parts = path.split("/")
            if parts[-1]:
                return parts[-1]
    return slugify(fallback_title)


def parse_rfc3339(ts_str: Optional[str]) -> Optional[datetime]:
    if not ts_str:
        return None
    try:
        # Handles 2026-10-15T03:10:00+00:00 or Z
        clean = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean)
    except Exception:
        return None


class CMSSyncService:
    """
    Service pipeline sinkronisasi artikel Inova CMS ke Neon Lakebase Postgres.
    Mengadopsi pola sinkronisasi incremental cursor dari plugin WordPress.
    """

    def __init__(self, client: Optional[InovaCMSClient] = None):
        self.client = client or InovaCMSClient()

    def sync_articles(
        self,
        db: Session,
        portal_id: Optional[str] = None,
        force_full_sync: bool = False,
        limit_per_page: int = 50,
        max_pages: int = 20
    ) -> Dict[str, Any]:
        """
        Menjalankan sinkronisasi berkala artikel dari CMS Open API ke Supabase.
        """
        target_portal = portal_id or self.client.portal_id or "default-portal"

        if not self.client.is_configured:
            return {
                "ok": False,
                "error": "CMS credentials not configured in environment (CMS_ACCESS_KEY, CMS_SECRET).",
                "synced_count": 0,
                "inserted_count": 0,
                "updated_count": 0
            }

        # 1. Ambil atau buat checkpoint sinkronisasi
        checkpoint = db.query(CMSSyncCheckpoint).filter(
            CMSSyncCheckpoint.portal_id == target_portal
        ).first()

        if not checkpoint:
            checkpoint = CMSSyncCheckpoint(
                portal_id=target_portal,
                sync_status="syncing"
            )
            db.add(checkpoint)
            db.commit()
            db.refresh(checkpoint)
        else:
            checkpoint.sync_status = "syncing"
            db.commit()

        updated_after = None
        if not force_full_sync and checkpoint.last_checkpoint_timestamp:
            updated_after = checkpoint.last_checkpoint_timestamp
            logger.info("Melakukan incremental sync dengan checkpoint: %s", updated_after)

        inserted_count = 0
        updated_count = 0
        current_cursor = None
        pages_processed = 0
        latest_seen_updated_at = checkpoint.last_checkpoint_timestamp

        # Muat katalog mobil untuk pencocokan otomatis relasi artikel-kendaraan
        cars_catalog = db.query(Car.id, Car.name, Car.slug).all()

        try:
            while pages_processed < max_pages:
                pages_processed += 1
                res = self.client.get_articles(
                    portal_id=target_portal,
                    limit=limit_per_page,
                    cursor=current_cursor,
                    order_by="updated_at",
                    updated_after=updated_after,
                    include="contentHtml"
                )

                items = res.get("items", [])
                page_info = res.get("page", {})

                if not items:
                    break

                for item in items:
                    article_id = str(item.get("id"))
                    title = item.get("title", "Untitled")
                    url = item.get("url")
                    slug = extract_slug_from_url(url, title)

                    category_data = item.get("category") or {}
                    author_data = item.get("author") or {}
                    media_data = item.get("featuredMedia") or {}
                    tags_data = item.get("tags") or []

                    published_at_dt = parse_rfc3339(item.get("publishedAt"))
                    updated_at_dt = parse_rfc3339(item.get("updatedAt"))

                    # Lacak timestamp updatedAt terbesar untuk checkpoint berikutnya
                    if item.get("updatedAt"):
                        if not latest_seen_updated_at or item.get("updatedAt") > latest_seen_updated_at:
                            latest_seen_updated_at = item.get("updatedAt")

                    existing = db.query(CMSArticle).filter(CMSArticle.id == article_id).first()

                    if existing:
                        # Update artikel yang ada
                        existing.title = title
                        existing.slug = slug
                        existing.excerpt = item.get("excerpt")
                        existing.content = item.get("content")
                        existing.content_html = item.get("contentHtml")
                        existing.url = url
                        existing.category_slug = category_data.get("slug")
                        existing.category_name = category_data.get("name")
                        existing.author_name = author_data.get("name")
                        existing.cover_url = media_data.get("url")
                        existing.cover_alt = media_data.get("alt")
                        existing.cover_caption = media_data.get("caption")
                        existing.tags = tags_data
                        existing.published_at = published_at_dt
                        existing.remote_updated_at = updated_at_dt
                        updated_count += 1
                    else:
                        # Insert artikel baru
                        new_article = CMSArticle(
                            id=article_id,
                            portal_id=target_portal,
                            slug=slug,
                            title=title,
                            excerpt=item.get("excerpt"),
                            content=item.get("content"),
                            content_html=item.get("contentHtml"),
                            url=url,
                            category_slug=category_data.get("slug"),
                            category_name=category_data.get("name"),
                            author_name=author_data.get("name"),
                            cover_url=media_data.get("url"),
                            cover_alt=media_data.get("alt"),
                            cover_caption=media_data.get("caption"),
                            tags=tags_data,
                            published_at=published_at_dt,
                            remote_updated_at=updated_at_dt
                        )
                        db.add(new_article)
                        inserted_count += 1

                    # Otomatis hubungkan artikel dengan mobil jika ada keterkaitan
                    auto_link_article_to_cars(db, article_id, title, item.get("excerpt"), tags_data, cars_catalog)

                db.commit()

                has_more = page_info.get("hasMore", False)
                next_cursor = page_info.get("nextCursor")

                if not has_more or not next_cursor:
                    break

                current_cursor = next_cursor

            # Sukses: Update checkpoint
            checkpoint.sync_status = "success"
            checkpoint.last_synced_at = datetime.now(timezone.utc)
            if latest_seen_updated_at:
                checkpoint.last_checkpoint_timestamp = latest_seen_updated_at
            checkpoint.total_synced_articles += (inserted_count + updated_count)
            checkpoint.last_error = None
            db.commit()

            return {
                "ok": True,
                "portal_id": target_portal,
                "inserted_count": inserted_count,
                "updated_count": updated_count,
                "total_processed": inserted_count + updated_count,
                "checkpoint": latest_seen_updated_at,
                "pages_processed": pages_processed
            }

        except Exception as e:
            logger.exception("Gagal sinkronisasi artikel dari CMS: %s", str(e))
            db.rollback()
            checkpoint.sync_status = "failed"
            checkpoint.last_error = str(e)
            db.commit()
            return {
                "ok": False,
                "error": str(e),
                "portal_id": target_portal,
                "inserted_count": inserted_count,
                "updated_count": updated_count
            }


cms_sync_service = CMSSyncService()
