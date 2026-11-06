from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class CarAffiliateBase(BaseModel):
    title: str
    image_url: Optional[str] = None
    affiliate_url: str
    price: Optional[int] = None
    merchant: Optional[str] = "Tokopedia"
    badge: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = 1
    is_active: Optional[bool] = True


class CarAffiliateCreate(CarAffiliateBase):
    car_id: int


class CarAffiliateUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    affiliate_url: Optional[str] = None
    price: Optional[int] = None
    merchant: Optional[str] = None
    badge: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CarAffiliateResponse(CarAffiliateBase):
    id: int
    car_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
