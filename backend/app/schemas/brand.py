from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BrandBase(BaseModel):
    name: str
    slug: str
    country: Optional[str] = None
    logo_url: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None


class BrandResponse(BrandBase):
    id: int
    created_at: datetime
    car_count: Optional[int] = None

    class Config:
        from_attributes = True
