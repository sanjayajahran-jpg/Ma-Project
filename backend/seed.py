import sys
import os
import json
import re
import ast

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.brand import Brand
from app.models.car import Car, CarSpec, CarVariant, EngineType, BodyType, CarStatus
from app.models.fuel_price import FuelPrice


def load_cars_from_listmobil():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, 'data', 'compiled_cars.json'),
        os.path.join(base_dir, 'compiled_cars.json'),
    ]
    for p in candidates:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
    return []


def seed_database():
    print("[*] Initializing EVnesia database schema...")
    # Drop and recreate schema to apply latest models and 16-parameter taxonomy
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()


    try:
        # 1. Admin User
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@evnesia.id",
                full_name="EVnesia Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
            )
            db.add(admin)
            print("  [+] Admin user ready: admin / admin123")

        # 2. Electrified Powertrain Engine Types (100% Electrification & Clean Energy)
        engine_types_data = [
            ("BEV (Listrik Murni)", "bev", "⚡"),
            ("PHEV (Plug-in Hybrid)", "phev", "🔋"),
            ("HEV (Full Hybrid)", "hev", "🍃"),
            ("FCEV (Hidrogen & Clean Tech)", "fcev", "💧"),
        ]
        et_map = {}
        for name, slug, icon in engine_types_data:
            et = db.query(EngineType).filter(EngineType.slug == slug).first()
            if not et:
                et = EngineType(name=name, slug=slug, icon_url=icon)
                db.add(et)
                db.flush()
            else:
                et.name = name
                et.icon_url = icon
            et_map[slug] = et
        print(f"  [+] {len(et_map)} Electrified Powertrain Types ready")

        # 3. Body Types
        body_types_data = [
            ("SUV", "suv"),
            ("Sedan", "sedan"),
            ("Hatchback", "hatchback"),
            ("MPV", "mpv"),
            ("Crossover", "crossover"),
            ("Coupe", "coupe"),
            ("Wagon", "wagon"),
        ]
        bt_map = {}
        for name, slug in body_types_data:
            bt = db.query(BodyType).filter(BodyType.slug == slug).first()
            if not bt:
                bt = BodyType(name=name, slug=slug)
                db.add(bt)
                db.flush()
            bt_map[slug] = bt
        print(f"  [+] {len(bt_map)} Body Types ready")

        # 4. Comprehensive Electrified Automotive Brands in Indonesia
        brands_data = [
            ("Aletra", "aletra", "Indonesia / Tiongkok"),
            ("BAIC", "baic", "Tiongkok"),
            ("BMW", "bmw", "Jerman"),
            ("BYD", "byd", "Tiongkok"),
            ("Changan", "changan", "Tiongkok"),
            ("Chery", "chery", "Tiongkok"),
            ("Citroën", "citroen", "Prancis"),
            ("Daihatsu", "daihatsu", "Jepang"),
            ("Denza", "denza", "Tiongkok"),
            ("DFSK", "dfsk", "Tiongkok"),
            ("Foton", "foton", "Tiongkok"),
            ("GAC Aion", "gac", "Tiongkok"),
            ("Geely", "geely", "Tiongkok"),
            ("GWM (Great Wall Motor)", "gwm", "Tiongkok"),
            ("Honda", "honda", "Jepang"),
            ("Hyundai", "hyundai", "Korea Selatan"),
            ("iCar", "icar", "Tiongkok"),
            ("Jaecoo", "jaecoo", "Tiongkok"),
            ("Jetour", "jetour", "Tiongkok"),
            ("Kia", "kia", "Korea Selatan"),
            ("Leapmotor", "leapmotor", "Tiongkok"),
            ("Lepas", "lepas", "Tiongkok"),
            ("Lexus", "lexus", "Jepang"),
            ("Mazda", "mazda", "Jepang"),
            ("Mercedes-Benz", "mercedes-benz", "Jerman"),
            ("MG (Morris Garages)", "mg", "Inggris / Tiongkok"),
            ("MINI", "mini", "Inggris / Jerman"),
            ("Mitsubishi", "mitsubishi", "Jepang"),
            ("Neta", "neta", "Tiongkok"),
            ("Nissan", "nissan", "Jepang"),
            ("Polytron", "polytron", "Indonesia"),
            ("Porsche", "porsche", "Jerman"),
            ("Subaru", "subaru", "Jepang"),
            ("Tesla", "tesla", "Amerika Serikat"),
            ("Toyota", "toyota", "Jepang"),
            ("VinFast", "vinfast", "Vietnam"),
            ("Volkswagen", "volkswagen", "Jerman"),
            ("Volvo", "volvo", "Swedia"),
            ("Wuling", "wuling", "Tiongkok"),
            ("XPENG", "xpeng", "Tiongkok"),
            ("Zeekr", "zeekr", "Tiongkok"),
        ]
        brand_map = {}
        for name, slug, country in brands_data:
            b = db.query(Brand).filter(Brand.slug == slug).first()
            if not b:
                b = Brand(name=name, slug=slug, country=country)
                db.add(b)
                db.flush()
            else:
                b.name = name
                b.country = country
            brand_map[slug] = b
        print(f"  [+] {len(brand_map)} Electrified Automotive Brands ready")

        # Populate brand logo if available in uploads/brands
        brands_upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'brands')
        if os.path.exists(brands_upload_dir):
            for b_file in os.listdir(brands_upload_dir):
                f_stem = b_file.lower().replace('-logo.svg', '').replace('-seeklogo.svg', '').replace('.svg', '').replace('.png', '')
                for b_slug, b_inst in brand_map.items():
                    if b_slug == f_stem or b_slug in f_stem or f_stem in b_slug:
                        b_inst.logo_url = f"/images/brands/{b_file}"
                        db.flush()

        # 5. Fuel & Energy Prices Indonesia 2026
        fuel_data = [
            ("SPKLU Fast Charging (Listrik)", 2466.00, "kWh"),
            ("Home Charging PLN Malam (Diskon 30%)", 1187.00, "kWh"),
            ("Pertalite (Subsidi)", 10000.00, "L"),
            ("Pertamax (RON 92)", 15950.00, "L"),
            ("Pertamax Turbo (RON 98)", 16250.00, "L"),
            ("Dexlite (Cetane 51)", 16100.00, "L"),
        ]
        for ftype, price, unit in fuel_data:
            fp = db.query(FuelPrice).filter(FuelPrice.fuel_type == ftype).first()
            if not fp:
                fp = FuelPrice(fuel_type=ftype, price_per_unit=price, unit=unit)
                db.add(fp)
            else:
                fp.price_per_unit = price
        print(f"  [+] Energy & SPKLU tariff initialized")

        # 6. Load 100% Electrified Cars Catalog (BEV, PHEV, HEV) from listmobil.py
        cars_data = load_cars_from_listmobil()
        print(f"  [*] Ingesting {len(cars_data)} cars from verified master data...")

        cars_upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'cars')
        car_files = os.listdir(cars_upload_dir) if os.path.exists(cars_upload_dir) else []

        for cdata in cars_data:
            c_slug = cdata.get("slug", "")
            # Resolve image url
            img_url = cdata.get("image_url")
            if not img_url:
                clean_slug = c_slug.lower().replace('_', '-').replace(' ', '-')
                slug_alphanum = re.sub(r'[^a-z0-9]', '', clean_slug)
                best_match = None
                best_score = -1
                for f_name in car_files:
                    clean_f_stem = os.path.splitext(f_name)[0].lower().replace('_', '-').replace(' ', '-')
                    stem_alphanum = re.sub(r'[^a-z0-9]', '', clean_f_stem)
                    score = -1
                    if clean_f_stem == clean_slug:
                        score = 1000
                    elif stem_alphanum == slug_alphanum:
                        score = 900
                    elif stem_alphanum in slug_alphanum and len(stem_alphanum) >= 5:
                        score = 500 + len(stem_alphanum)
                    elif clean_f_stem in clean_slug:
                        score = 400 + len(clean_f_stem)
                    elif clean_slug in clean_f_stem:
                        score = 300 + len(clean_slug)
                    elif slug_alphanum in stem_alphanum:
                        score = 200 + len(slug_alphanum)

                    if score > best_score:
                        best_score = score
                        best_match = f_name
                if best_match and best_score > 0:
                    img_url = f"/images/cars/{best_match}"

            # Map brand name to brand model
            brand_slug = cdata.get("brand_name", "").lower().replace(" ", "-").replace("ë", "e")
            if "citro" in brand_slug:
                brand_slug = "citroen"
            elif "gac" in brand_slug or "aion" in brand_slug:
                brand_slug = "gac"
            elif "gwm" in brand_slug:
                brand_slug = "gwm"
            elif "mg" in brand_slug:
                brand_slug = "mg"
                
            brand_obj = brand_map.get(brand_slug)
            if not brand_obj:
                # Find by exact or partial match
                for b_slug, b_inst in brand_map.items():
                    if b_slug in brand_slug or brand_slug in b_slug:
                        brand_obj = b_inst
                        break
            if not brand_obj:
                brand_obj = brand_map.get("byd")

            # Engine & Body mapping
            engine_slug = cdata.get("engine_type_slug", "bev").lower()
            engine_obj = et_map.get(engine_slug, et_map["bev"])

            body_slug = cdata.get("body_type_slug", "suv").lower()
            body_obj = bt_map.get(body_slug, bt_map["suv"])

            car = db.query(Car).filter(Car.slug == cdata["slug"]).first()
            if not car:
                car = Car(
                    name=cdata["name"],
                    slug=cdata["slug"],
                    brand_id=brand_obj.id,
                    engine_type_id=engine_obj.id,
                    body_type_id=body_obj.id,
                    year=cdata.get("year", 2026),
                    price_start=cdata.get("price_start", 0),
                    price_end=cdata.get("price_end", 0),
                    tagline=cdata.get("tagline"),
                    description=cdata.get("description"),
                    image_url=img_url,
                    thumbnail_url=img_url,
                    is_featured=cdata.get("is_featured", False),
                    is_new=True,
                    status=CarStatus.active,
                )
                db.add(car)
                db.flush()
            else:
                car.name = cdata["name"]
                car.brand_id = brand_obj.id
                car.engine_type_id = engine_obj.id
                car.body_type_id = body_obj.id
                car.year = cdata.get("year", 2026)
                car.price_start = cdata.get("price_start", 0)
                car.price_end = cdata.get("price_end", 0)
                car.tagline = cdata.get("tagline")
                car.description = cdata.get("description")
                if img_url:
                    car.image_url = img_url
                    car.thumbnail_url = img_url

            # Add or update Specs
            if "specs" in cdata and isinstance(cdata["specs"], dict):
                spec_data = cdata["specs"]
                existing_spec = db.query(CarSpec).filter(CarSpec.car_id == car.id).first()
                if existing_spec:
                    for k, v in spec_data.items():
                        if hasattr(existing_spec, k):
                            setattr(existing_spec, k, v)
                else:
                    valid_spec_attrs = {
                        k: v for k, v in spec_data.items()
                        if hasattr(CarSpec, k)
                    }
                    spec = CarSpec(car_id=car.id, **valid_spec_attrs)
                    db.add(spec)

            # Add or update Trim Variants (All 16+ Parameters)
            if "variants" in cdata and isinstance(cdata["variants"], list):
                db.query(CarVariant).filter(CarVariant.car_id == car.id).delete()
                for v in cdata["variants"]:
                    if not isinstance(v, dict):
                        continue
                    gallery_str = v.get("gallery_json")
                    if isinstance(v.get("gallery"), list):
                        gallery_str = json.dumps(v["gallery"])
                        
                    var = CarVariant(
                        car_id=car.id,
                        name=v.get("name", "Standard Trim"),
                        price=v.get("price", cdata.get("price_start", 0)) or 0,
                        highlights=v.get("highlights"),
                        power_output=v.get("power_output"),
                        battery_range=v.get("battery_range"),
                        battery_type=v.get("battery_type"),
                        v2l_support=v.get("v2l_support"),
                        charging_time=v.get("charging_time"),
                        wall_charger_info=v.get("wall_charger_info"),
                        wheel_spec=v.get("wheel_spec"),
                        interior_spec=v.get("interior_spec"),
                        seating_layout=v.get("seating_layout"),
                        cluster_display=v.get("cluster_display"),
                        audio_display=v.get("audio_display"),
                        tailgate_feature=v.get("tailgate_feature"),
                        sunroof=v.get("sunroof"),
                        telematics_feature=v.get("telematics_feature"),
                        camera_vision=v.get("camera_vision"),
                        lighting_spec=v.get("lighting_spec"),
                        climate_air=v.get("climate_air"),
                        convenience_extras=v.get("convenience_extras"),
                        styling_kit=v.get("styling_kit"),
                        safety_adas=v.get("safety_adas"),
                        annual_tax=v.get("annual_tax", 0),
                        gallery_json=gallery_str
                    )
                    db.add(var)

        db.commit()
        total_cars_in_db = db.query(Car).count()
        total_variants_in_db = db.query(CarVariant).count()
        print(f"  [+] Successfully Seeded {total_cars_in_db} Cars with {total_variants_in_db} Trim Variants into EVnesia Database!")
        print("\n[+] EVnesia database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"[-] Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
