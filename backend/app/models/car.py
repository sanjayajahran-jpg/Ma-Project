from sqlalchemy import (
    Column, Integer, String, BigInteger, Text, Boolean,
    DateTime, ForeignKey, Float, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class CarStatus(str, enum.Enum):
    active = "active"
    draft = "draft"
    discontinued = "discontinued"


class RangeStandard(str, enum.Enum):
    NEDC = "NEDC"
    WLTP = "WLTP"
    CLTC = "CLTC"
    EPA = "EPA"
    JC08 = "JC08"
    REAL_WORLD = "Real-World"


class EngineType(Base):
    __tablename__ = "engine_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    icon_url = Column(String(500), nullable=True)

    cars = relationship("Car", back_populates="engine_type")


class BodyType(Base):
    __tablename__ = "body_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, index=True, nullable=False)

    cars = relationship("Car", back_populates="body_type")


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    engine_type_id = Column(Integer, ForeignKey("engine_types.id"), nullable=False)
    body_type_id = Column(Integer, ForeignKey("body_types.id"), nullable=True)

    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    year = Column(Integer, nullable=False)
    price_start = Column(BigInteger, nullable=True)
    price_end = Column(BigInteger, nullable=True)
    tagline = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    brochure_url = Column(String(500), nullable=True)
    is_featured = Column(Boolean, default=False)
    is_new = Column(Boolean, default=True)
    status = Column(Enum(CarStatus), default=CarStatus.active)
    gallery_json = Column(Text, nullable=True) # JSON array galeri foto eksterior, interior, & fitur
    deleted_at = Column(DateTime, nullable=True) # Soft-delete timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = relationship("Brand", back_populates="cars")
    engine_type = relationship("EngineType", back_populates="cars")
    body_type = relationship("BodyType", back_populates="cars")
    specs = relationship("CarSpec", back_populates="car", uselist=False, cascade="all, delete-orphan")
    variants = relationship("CarVariant", back_populates="car", cascade="all, delete-orphan")
    media = relationship("CarMedia", back_populates="car", cascade="all, delete-orphan")
    affiliates = relationship("CarAffiliate", back_populates="car", cascade="all, delete-orphan", order_by="CarAffiliate.sort_order")
    article_links = relationship("ArticleCarLink", back_populates="car")


class CarSpec(Base):
    __tablename__ = "car_specs"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), unique=True, nullable=False)

    # 1. Status Perakitan, Baterai, Jangkauan & V2L
    assembly_status = Column(String(255), nullable=True)     # e.g. "CKD (Rakit Lokal Indonesia - TKDN 40%)" or "CBU (Impor Utuh)"
    battery_type = Column(String(255), nullable=True)       # e.g. "LFP (Lithium Iron Phosphate / Blade Battery)" or "Ternary Lithium NMC"
    battery_capacity_kwh = Column(Float, nullable=True)     # Kapasitas baterai (kWh)
    electric_range_km = Column(Integer, nullable=True)      # Jarak tempuh EV murni (km)
    range_standard = Column(String(100), nullable=True, default="WLTP") # NEDC, WLTP, CLTC, EPA, JC08, Real-World
    v2l_support = Column(String(255), nullable=True)        # e.g. "Ya, Daya 3.300 Watt (3.3 kW) V2L Adapter Luar & Kabin"
    energy_consumption = Column(String(255), nullable=True) # e.g. "14.2 kWh/100 km (7.0 km/kWh)" or "21.0 km/L"

    # 2. Powertrain & Performa
    engine_name = Column(String(255), nullable=True)        # Nama Arsitektur Mesin / Motor Listrik
    engine_capacity_cc = Column(Integer, nullable=True)     # Kapasitas mesin bensin (cc), None jika BEV
    horsepower = Column(Integer, nullable=True)             # Tenaga total (HP)
    torque_nm = Column(Integer, nullable=True)              # Torsi total (Nm)
    transmission = Column(String(255), nullable=True)       # Single Reduction Gear / e-CVT / DHT / dll.
    drivetrain = Column(String(100), nullable=True)          # FWD / RWD / AWD / 4WD
    acceleration_0_100 = Column(Float, nullable=True)       # 0-100 km/j (detik)
    top_speed_kmh = Column(Integer, nullable=True)          # Kecepatan maksimal (km/j)
    fuel_consumption_kmpl = Column(Float, nullable=True)    # Konsumsi BBM (km/L), None jika BEV

    # 3. Dimensi, Sasis & Kapasitas
    length_mm = Column(Integer, nullable=True)              # Panjang (mm)
    width_mm = Column(Integer, nullable=True)               # Lebar (mm)
    height_mm = Column(Integer, nullable=True)              # Tinggi (mm)
    wheelbase_mm = Column(Integer, nullable=True)           # Sumbu roda (mm)
    ground_clearance_mm = Column(Integer, nullable=True)    # Ground clearance (mm)
    curb_weight_kg = Column(Integer, nullable=True)         # Bobot kosong (kg)
    seating_capacity = Column(Integer, nullable=True)       # Kapasitas tempat duduk
    trunk_volume_liters = Column(Integer, nullable=True)    # Volume bagasi (Liter)
    fuel_tank_liters = Column(Integer, nullable=True)       # Tangki BBM (Liter), None jika BEV

    # 4. Kokpit, Layar & Warna
    cluster_display = Column(String(255), nullable=True)    # Layar Speedometer: "10.25-inch Full Digital TFT + HUD"
    colors_json = Column(Text, nullable=True)               # JSON array pilihan warna resmi APM

    # 5. Keselamatan & ADAS
    airbags = Column(Integer, nullable=True)                # Jumlah airbags
    abs_ebd = Column(Boolean, default=False)
    esc = Column(Boolean, default=False)
    adas = Column(Boolean, default=False)
    adas_name = Column(String(255), nullable=True)          # e.g. "Toyota Safety Sense 3.0 / Hyundai SmartSense"
    adas_features_json = Column(Text, nullable=True)        # JSON array seluruh fitur ADAS aktif
    safety_rating = Column(Float, nullable=True)            # Rating 0.0 - 5.0
    comfort_rating = Column(Float, nullable=True)
    performance_rating = Column(Float, nullable=True)
    value_rating = Column(Float, nullable=True)

    # 6. Pajak, Garansi & Paket Pengisian Rumah
    annual_tax_estimate = Column(BigInteger, nullable=True) # Estimasi Pajak Tahunan PKB Jakarta (Rp)
    warranty_vehicle = Column(String(255), nullable=True)   # Garansi Kendaraan, e.g. "5 Tahun / 150.000 km"
    warranty_battery = Column(String(255), nullable=True)   # Garansi Baterai, e.g. "8 Tahun / 160.000 km (Garansi Seumur Hidup)"
    wall_charger_info = Column(String(300), nullable=True)  # e.g. "Gratis Wallbox 7.4 kW + Gratis Instalasi Kabel s/d 10m & Tambah Daya PLN" / "Opsional Rp 12.000.000"

    # Relationship
    car = relationship("Car", back_populates="specs")


class CarVariant(Base):
    __tablename__ = "car_variants"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)

    # Identitas & Harga Trim
    name = Column(String(200), nullable=False)              # Nama Trim / Varian
    price = Column(BigInteger, nullable=False)              # Harga OTR Resmi (Rp)
    highlights = Column(Text, nullable=True)                # Ringkasan keunggulan trim

    # Powertrain & Baterai Trim
    power_output = Column(String(255), nullable=True)       # e.g. "320 HP / 605 Nm (Dual Motor AWD)"
    battery_range = Column(String(255), nullable=True)      # e.g. "Baterai 77.4 kWh (Jarak 481 km WLTP)"
    range_standard = Column(String(100), nullable=True)      # NEDC, WLTP, CLTC, EPA, JC08, Real-World
    battery_type = Column(String(255), nullable=True)       # e.g. "Blade LFP Battery" / "Ternary NMC"
    v2l_support = Column(String(255), nullable=True)        # e.g. "Ya, Daya 3.3 kW"
    charging_time = Column(String(255), nullable=True)      # e.g. "DC 350 kW (18 mnt 10-80%) / AC 11 kW"
    wall_charger_info = Column(String(300), nullable=True)  # Paket Wall Charger khusus trim

    # Fitur Kabin, Kenyamanan & Aksesoris Pembeda Trim
    wheel_spec = Column(String(255), nullable=True)         # e.g. "Velg Alloy 19-inch Two-Tone 235/55 R19"
    interior_spec = Column(String(255), nullable=True)      # e.g. "Jok Kulit Nappa Premium + Ventilated Seats + Memory"
    seating_layout = Column(String(255), nullable=True)     # e.g. "7-Seater Bench Seat" / "6-Seater Captain Seats + Ottoman"
    cluster_display = Column(String(255), nullable=True)    # e.g. "12.3-inch Curved Digital Cluster + HUD"
    audio_display = Column(String(255), nullable=True)      # e.g. "Head Unit 15.6\" Rotating + BOSE 10-Speaker"
    tailgate_feature = Column(String(255), nullable=True)   # e.g. "Hands-free Kick Sensor + Walk-Away Auto Close"
    sunroof = Column(String(255), nullable=True)            # e.g. "Panoramic Glass Roof dengan Power Shade"
    telematics_feature = Column(String(255), nullable=True) # e.g. "Honda CONNECT / Bluelink (Remote Engine/AC & GPS)"
    camera_vision = Column(String(255), nullable=True)      # e.g. "360° Multi-Angle Surround View Camera + LaneWatch"
    lighting_spec = Column(String(255), nullable=True)      # e.g. "Adaptive Driving Beam (Matrix LED) + Active Cornering Light"
    climate_air = Column(String(255), nullable=True)        # e.g. "Tri-Zone Auto Climate Control + Nanoe-X Air Purifier"
    convenience_extras = Column(String(255), nullable=True) # e.g. "Qi Wireless Charger 15W + USB-C 45W All Rows"
    styling_kit = Column(String(255), nullable=True)        # e.g. "RS Aero Body Kit + Dark Chrome Grille + Roof Rail"
    safety_adas = Column(Text, nullable=True)               # e.g. "Full Level 2+ ADAS Suite: ACC, AEB, LKA, BSD, 360 Camera"

    # Pajak & Galeri Khusus Trim
    annual_tax = Column(String(100), nullable=True)          # e.g. "0" atau "Rp 0 - 350.000 / tahun"
    gallery_json = Column(Text, nullable=True)              # JSON string galeri foto khusus trim ini

    car = relationship("Car", back_populates="variants")
    media = relationship("CarMedia", back_populates="variant")

