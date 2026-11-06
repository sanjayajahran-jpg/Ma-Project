from sqlalchemy import Column, Integer, String, BigInteger, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class CarAffiliate(Base):
    __tablename__ = "car_affiliates"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(200), nullable=False)              # Judul Produk Affiliate (cth: "Portable Charger EV 7kW Type 2")
    image_url = Column(String(500), nullable=True)           # Gambar produk (S3 / CDN / Link)
    affiliate_url = Column(String(500), nullable=False)       # Link pembelian (Tokopedia / Shopee / APM)
    price = Column(BigInteger, nullable=True)                # Harga produk dlm Rupiah (cth: 2850000)
    merchant = Column(String(50), default="Tokopedia")       # Tokopedia / Shopee / Official Store / Blibli
    badge = Column(String(50), nullable=True)                # "Rekomendasi Editor", "Best Seller", "Diskon 10%"
    description = Column(Text, nullable=True)                # Keterangan singkat produk
    sort_order = Column(Integer, default=1)                  # Urutan tampil
    is_active = Column(Boolean, default=True)                # Status tampil publik
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    car = relationship("Car", back_populates="affiliates")
