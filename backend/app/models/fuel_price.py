from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base


class FuelPrice(Base):
    __tablename__ = "fuel_prices"

    id = Column(Integer, primary_key=True, index=True)
    fuel_type = Column(String(50), unique=True, index=True, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    unit = Column(String(20), default="L")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
