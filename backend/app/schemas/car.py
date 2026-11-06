from pydantic import BaseModel
from typing import Optional, List, Union, Any
from datetime import datetime
from app.models.car import CarStatus, RangeStandard


# ----------------------------------------------------
# EngineType & BodyType Schemas
# ----------------------------------------------------
class EngineTypeResponse(BaseModel):
    id: int
    name: str
    slug: str
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True


class BodyTypeResponse(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


# ----------------------------------------------------
# Car Spec Schemas
# ----------------------------------------------------
class CarSpecBase(BaseModel):
    # 1. Status Perakitan, Baterai, Jangkauan & V2L
    assembly_status: Optional[str] = None
    battery_type: Optional[str] = None
    battery_capacity_kwh: Optional[float] = None
    electric_range_km: Optional[int] = None
    range_standard: Optional[str] = "WLTP"
    v2l_support: Optional[str] = None
    energy_consumption: Optional[str] = None

    # 2. Powertrain & Performa
    engine_name: Optional[str] = None
    engine_capacity_cc: Optional[int] = None
    horsepower: Optional[int] = None
    torque_nm: Optional[int] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    acceleration_0_100: Optional[float] = None
    top_speed_kmh: Optional[int] = None
    fuel_consumption_kmpl: Optional[float] = None

    # 3. Dimensi, Sasis & Kapasitas
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    wheelbase_mm: Optional[int] = None
    ground_clearance_mm: Optional[int] = None
    curb_weight_kg: Optional[int] = None
    seating_capacity: Optional[int] = None
    trunk_volume_liters: Optional[int] = None
    fuel_tank_liters: Optional[int] = None

    # 4. Kokpit, Layar & Warna
    cluster_display: Optional[str] = None
    colors_json: Optional[str] = None

    # 5. Keselamatan & ADAS
    airbags: Optional[int] = None
    abs_ebd: Optional[bool] = False
    esc: Optional[bool] = False
    adas: Optional[bool] = False
    adas_name: Optional[str] = None
    adas_features_json: Optional[str] = None
    safety_rating: Optional[float] = None
    comfort_rating: Optional[float] = None
    performance_rating: Optional[float] = None
    value_rating: Optional[float] = None

    # 6. Pajak, Garansi & Paket Pengisian Rumah
    annual_tax_estimate: Optional[Union[int, str]] = None
    warranty_vehicle: Optional[str] = None
    warranty_battery: Optional[str] = None
    wall_charger_info: Optional[str] = None


class CarSpecCreate(CarSpecBase):
    pass


class CarSpecResponse(CarSpecBase):
    id: int
    car_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# Car Variant Schemas
# ----------------------------------------------------
class CarVariantBase(BaseModel):
    # Identitas & Harga Trim
    name: str
    price: int
    highlights: Optional[str] = None

    # Powertrain & Baterai Trim
    power_output: Optional[str] = None
    battery_range: Optional[str] = None
    range_standard: Optional[str] = None
    battery_type: Optional[str] = None
    v2l_support: Optional[str] = None
    charging_time: Optional[str] = None
    wall_charger_info: Optional[str] = None

    # Fitur Kabin, Kenyamanan & Aksesoris Pembeda Trim
    wheel_spec: Optional[str] = None
    interior_spec: Optional[str] = None
    seating_layout: Optional[str] = None
    cluster_display: Optional[str] = None
    audio_display: Optional[str] = None
    tailgate_feature: Optional[str] = None
    sunroof: Optional[str] = None
    telematics_feature: Optional[str] = None
    camera_vision: Optional[str] = None
    lighting_spec: Optional[str] = None
    climate_air: Optional[str] = None
    convenience_extras: Optional[str] = None
    styling_kit: Optional[str] = None
    safety_adas: Optional[str] = None


    # Pajak & Galeri Khusus Trim
    annual_tax: Optional[Union[int, str]] = None
    gallery_json: Optional[str] = None


class CarVariantCreate(CarVariantBase):
    pass






class CarVariantResponse(CarVariantBase):
    id: int
    car_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# Car Schemas
# ----------------------------------------------------
class CarBase(BaseModel):
    name: str
    slug: str
    brand_id: int
    engine_type_id: int
    body_type_id: Optional[int] = None
    year: int
    price_start: Optional[int] = None
    price_end: Optional[int] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    brochure_url: Optional[str] = None
    is_featured: Optional[bool] = False
    is_new: Optional[bool] = True
    status: Optional[CarStatus] = CarStatus.active
    gallery_json: Optional[str] = None
    deleted_at: Optional[datetime] = None


class CarCreate(CarBase):
    specs: Optional[CarSpecCreate] = None
    variants: Optional[List[CarVariantCreate]] = None


class CarUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    brand_id: Optional[int] = None
    engine_type_id: Optional[int] = None
    body_type_id: Optional[int] = None
    year: Optional[int] = None
    price_start: Optional[int] = None
    price_end: Optional[int] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    brochure_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_new: Optional[bool] = None
    status: Optional[CarStatus] = None
    gallery_json: Optional[str] = None
    specs: Optional[CarSpecCreate] = None
    variants: Optional[List[CarVariantCreate]] = None


class CarListResponse(CarBase):
    id: int
    created_at: datetime
    brand_name: Optional[str] = None
    brand_slug: Optional[str] = None
    engine_type_name: Optional[str] = None
    engine_type_slug: Optional[str] = None
    body_type_name: Optional[str] = None
    body_type_slug: Optional[str] = None

    class Config:
        from_attributes = True


class CarMediaResponse(BaseModel):
    id: int
    car_id: int
    variant_id: Optional[int] = None
    category: str
    file_url: str
    s3_key: str
    file_name: str
    mime_type: str
    file_size_bytes: Optional[int] = None
    caption: Optional[str] = None
    sort_order: int = 1
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class CarDetailResponse(CarListResponse):
    specs: Optional[CarSpecResponse] = None
    variants: List[CarVariantResponse] = []
    media: List[CarMediaResponse] = []
    affiliates: List[Any] = []
    articles: List["LinkedArticleSummary"] = []

    class Config:
        from_attributes = True


class LinkedArticleSummary(BaseModel):
    id: str
    slug: str
    title: str
    excerpt: Optional[str] = None
    cover_url: Optional[str] = None
    category_slug: Optional[str] = None
    category_name: Optional[str] = None
    published_at: Optional[datetime] = None
    is_primary: bool = False
    relation_type: str = "featured"

    class Config:
        from_attributes = True


class CarPaginatedResponse(BaseModel):
    items: List[CarListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
