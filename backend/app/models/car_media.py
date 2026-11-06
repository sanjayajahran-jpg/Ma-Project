from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class MediaCategory(str, enum.Enum):
    hero = "hero"          # Foto utama katalog / cover
    exterior = "exterior"  # Tampak depan, samping, velg, grill, lampu
    interior = "interior"  # Kabin, kemudi, kursi, konsol, bagasi
    feature = "feature"    # Layar MID, V2L, ADAS, socket charging
    brochure = "brochure"  # Dokumen PDF brosur resmi


class CarMedia(Base):
    __tablename__ = "car_media"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(Integer, ForeignKey("car_variants.id", ondelete="SET NULL"), nullable=True)

    category = Column(Enum(MediaCategory), default=MediaCategory.exterior, nullable=False)
    file_url = Column(String(500), nullable=False)       # Full CDN / Public URL
    s3_key = Column(String(300), nullable=False)         # Internal S3 key untuk operasi delete cloud
    file_name = Column(String(200), nullable=False)      # Nama file asli saat diunggah
    mime_type = Column(String(50), nullable=False)       # image/webp, image/jpeg, application/pdf
    file_size_bytes = Column(Integer, nullable=True)     # Ukuran file dalam bytes
    caption = Column(String(200), nullable=True)         # Keterangan / Alt text foto
    sort_order = Column(Integer, default=1)              # Urutan foto di slider
    is_active = Column(Boolean, default=True)            # Status aktif
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    car = relationship("Car", back_populates="media")
    variant = relationship("CarVariant", back_populates="media")
