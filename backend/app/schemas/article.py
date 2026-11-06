from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class TagSchema(BaseModel):
    id: Optional[str] = None
    slug: str
    name: str


class ArticleBase(BaseModel):
    id: str
    portal_id: Optional[str] = None
    slug: str
    title: str
    excerpt: Optional[str] = None
    content: Optional[str] = None
    content_html: Optional[str] = None
    url: Optional[str] = None
    category_slug: Optional[str] = None
    category_name: Optional[str] = None
    author_name: Optional[str] = None
    cover_url: Optional[str] = None
    cover_alt: Optional[str] = None
    cover_caption: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    reading_time: int = 3
    view_count: int = 0
    is_featured: bool = False
    is_pinned: bool = False
    published_at: Optional[datetime] = None
    remote_updated_at: Optional[datetime] = None


class ArticleResponse(ArticleBase):
    synced_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    items: List[ArticleResponse]
    total: int
    skip: int
    limit: int


class SyncStatusResponse(BaseModel):
    portal_id: str
    last_synced_at: Optional[datetime] = None
    last_checkpoint_timestamp: Optional[str] = None
    total_synced_articles: int = 0
    sync_status: str
    last_error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TriggerSyncRequest(BaseModel):
    portal_id: Optional[str] = None
    force_full_sync: bool = False
    limit_per_page: int = 50
    max_pages: int = 10


class LinkedCarSummary(BaseModel):
    id: int
    name: str
    slug: str
    brand_name: Optional[str] = None
    brand_slug: Optional[str] = None
    year: int
    price_start: Optional[int] = None
    price_end: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str
    is_primary: bool = False
    relation_type: str = "featured"

    model_config = ConfigDict(from_attributes=True)


class ArticleCarLinkCreate(BaseModel):
    car_id: int
    is_primary: bool = False
    relation_type: str = "featured"  # 'featured', 'review', 'launch', 'comparison', 'spec'


class ArticleCarLinkResponse(BaseModel):
    id: int
    article_id: str
    car_id: int
    is_primary: bool
    relation_type: str
    created_at: datetime
    car: Optional[LinkedCarSummary] = None

    model_config = ConfigDict(from_attributes=True)
