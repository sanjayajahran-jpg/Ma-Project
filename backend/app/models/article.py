from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CMSArticle(Base):
    """
    Model artikel hasil sinkronisasi dari Inova CMS Open API (Grup Indosatu).
    Tersimpan langsung di Neon Lakebase Postgres.
    """
    __tablename__ = "cms_articles"

    id = Column(String(64), primary_key=True, index=True)  # UUID remote dari CMS
    portal_id = Column(String(64), index=True, nullable=True)
    slug = Column(String(255), index=True, nullable=False)
    title = Column(String(500), nullable=False)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    
    # Metadata Taksonomi & Kepenulisan
    category_slug = Column(String(100), index=True, nullable=True)
    category_name = Column(String(100), nullable=True)
    author_name = Column(String(150), nullable=True)
    
    # Media Unggulan (Featured Media)
    cover_url = Column(Text, nullable=True)
    cover_alt = Column(String(500), nullable=True)
    cover_caption = Column(Text, nullable=True)
    
    # Tag dan Atribut Tambahan
    tags = Column(JSON, nullable=True)  # [{id, name, slug}, ...]
    reading_time = Column(Integer, default=3)
    view_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    
    # Timestamp
    published_at = Column(DateTime(timezone=True), index=True, nullable=True)
    remote_updated_at = Column(DateTime(timezone=True), index=True, nullable=True)
    synced_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)

    # Relasi ke Mobil Terkait (Explicit Junction)
    car_links = relationship("ArticleCarLink", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CMSArticle(id='{self.id}', title='{self.title[:30]}...', slug='{self.slug}')>"


class ArticleCarLink(Base):
    """
    Tabel relasi eksplisit Many-to-Many antara Berita/Artikel (CMSArticle) dan Model Mobil (Car).
    Memungkinkan rekomendasi berita di halaman detail mobil dan widget mobil di artikel berita.
    """
    __tablename__ = "article_car_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(64), ForeignKey("cms_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="RESTRICT"), nullable=False, index=True)
    is_primary = Column(Boolean, default=False)  # Apakah mobil ini fokus utama berita
    relation_type = Column(String(50), default="featured")  # 'featured', 'review', 'launch', 'comparison', 'spec'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        UniqueConstraint("article_id", "car_id", name="uq_article_car"),
    )

    article = relationship("CMSArticle", back_populates="car_links")
    car = relationship("Car", back_populates="article_links")

    def __repr__(self):
        return f"<ArticleCarLink(article='{self.article_id}', car={self.car_id}, primary={self.is_primary})>"


class CMSSyncCheckpoint(Base):
    """
    Checkpoint dan log status sinkronisasi berkala per portal.
    """
    __tablename__ = "cms_sync_checkpoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portal_id = Column(String(64), unique=True, index=True, nullable=False)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    last_checkpoint_timestamp = Column(String(50), nullable=True)  # RFC3339 string (e.g. 2026-10-15T04:22:11Z)
    total_synced_articles = Column(Integer, default=0)
    sync_status = Column(String(30), default="idle")  # 'idle', 'syncing', 'success', 'failed'
    last_error = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CMSSyncCheckpoint(portal='{self.portal_id}', status='{self.sync_status}', checkpoint='{self.last_checkpoint_timestamp}')>"
