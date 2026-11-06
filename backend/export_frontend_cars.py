import json
import os
import re
import shutil
from pathlib import Path

def format_single_price_idr(val):
    if not val or val <= 0:
        return ""
    if val >= 1_000_000_000:
        b_val = val / 1_000_000_000
        b_str = f"{b_val:.2f}".rstrip('0').rstrip('.').replace('.', ',')
        return f"{b_str} M"
    else:
        m_val = round(val / 1_000_000, 1)
        m_str = f"{m_val:g}".replace('.', ',')
        return f"{m_str} Jt"

def format_price_display(p_start, p_end):
    if not p_start or p_start <= 0:
        return 'Estimasi / Hubungi APM'
    if not p_end or p_end == p_start:
        return f"Rp {format_single_price_idr(p_start)}"
    
    # Range
    if p_start >= 1_000_000_000 and p_end >= 1_000_000_000:
        s_val = p_start / 1_000_000_000
        e_val = p_end / 1_000_000_000
        s_str = f"{s_val:.2f}".rstrip('0').rstrip('.').replace('.', ',')
        e_str = f"{e_val:.2f}".rstrip('0').rstrip('.').replace('.', ',')
        return f"Rp {s_str} - {e_str} M"
    elif p_start < 1_000_000_000 and p_end < 1_000_000_000:
        s_val = round(p_start / 1_000_000, 1)
        e_val = round(p_end / 1_000_000, 1)
        s_str = f"{s_val:g}".replace('.', ',')
        e_str = f"{e_val:g}".replace('.', ',')
        return f"Rp {s_str} - {e_str} Jt"
    else:
        return f"Rp {format_single_price_idr(p_start)} - {format_single_price_idr(p_end)}"

def extract_hp_clean(text):
    if not text:
        return ""
    # remove anything in parentheses e.g. (Single Motor RWD)
    clean = re.sub(r'\(.*?\)', '', text).strip()
    clean = re.sub(r'\s+', ' ', clean)
    return clean

def format_power_metrics(raw_specs, variants, fallback_hp):
    # Check if variants have different power outputs
    all_hps = []
    all_tqs = []
    for v in variants:
        p_str = v.get('power_output', '')
        m_hp = re.search(r'(\d+)\s*(?:HP|hp|dk|ps)\b', p_str)
        m_tq = re.search(r'(\d+)\s*(?:Nm|nm)\b', p_str)
        if m_hp:
            all_hps.append(int(m_hp.group(1)))
        if m_tq:
            all_tqs.append(int(m_tq.group(1)))
    
    if len(set(all_hps)) > 1:
        if len(set(all_tqs)) > 1:
            return f"{min(all_hps)} - {max(all_hps)} HP / {min(all_tqs)} - {max(all_tqs)} Nm"
        return f"{min(all_hps)} - {max(all_hps)} HP"
    elif variants and variants[-1].get('power_output'):
        return extract_hp_clean(variants[-1]['power_output'])
    elif raw_specs.get('horsepower'):
        hp_v = raw_specs['horsepower']
        tq_v = raw_specs.get('torque_nm')
        if tq_v:
            return f"{hp_v} HP / {tq_v} Nm"
        return f"{hp_v} HP"
    else:
        return extract_hp_clean(fallback_hp)

def format_range_metrics(raw_specs, variants, fallback_consumption):
    ranges = []
    standards = []
    
    for v in variants:
        b_str = v.get('battery_range', '')
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*km(?:\s*([A-Za-z]+))?', b_str, re.IGNORECASE)
        if m:
            ranges.append(float(m.group(1).replace(',', '.')))
            std = m.group(2)
            if std and std.upper() in ['WLTP', 'NEDC', 'CLTC']:
                standards.append(std.upper())
    
    std_label = standards[0] if standards else 'WLTP'
    
    if len(set(ranges)) > 1:
        min_r = int(min(ranges)) if min(ranges).is_integer() else min(ranges)
        max_r = int(max(ranges)) if max(ranges).is_integer() else max(ranges)
        return f"{min_r} - {max_r} km {std_label}"
    elif len(ranges) >= 1:
        r_val = int(ranges[-1]) if ranges[-1].is_integer() else ranges[-1]
        return f"{r_val} km {std_label}"
    elif raw_specs.get('electric_range_km'):
        return f"{raw_specs['electric_range_km']} km WLTP"
    elif raw_specs.get('fuel_consumption_kmpl'):
        return f"{raw_specs['fuel_consumption_kmpl']} km/L"
    else:
        return fallback_consumption

def format_acc_metrics(raw_specs, variants, fallback_acc):
    acc_list = []
    for v in variants:
        h_str = v.get('highlights', '') + ' ' + v.get('power_output', '')
        m = re.search(r'0-100\s*(?:km/h)?\s*(?:dlm|dalam)?\s*(\d+(?:[.,]\d+)?)\s*s', h_str, re.IGNORECASE)
        if m:
            acc_list.append(float(m.group(1).replace(',', '.')))
    
    if raw_specs.get('acceleration_0_100'):
        acc_list.append(float(raw_specs['acceleration_0_100']))
    
    if len(set(acc_list)) > 1:
        min_a = min(acc_list)
        max_a = max(acc_list)
        return f"{min_a:.1f} - {max_a:.1f}s"
    elif acc_list:
        return f"{acc_list[0]:.1f}s"
    else:
        return fallback_acc

def export_cars():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure DATABASE_URL uses absolute path to backend/autodrive.db if default sqlite
    db_file = os.path.join(backend_dir, 'autodrive.db')
    if os.path.exists(db_file):
        os.environ['DATABASE_URL'] = f"sqlite:///{db_file.replace(os.sep, '/')}"

    # Try querying live database first
    cars_data = []
    try:
        import sys
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from app.database import SessionLocal
        from app.models.car import Car, CarStatus
        from sqlalchemy.orm import joinedload
        
        db = SessionLocal()
        db_cars = db.query(Car).options(
            joinedload(Car.brand),
            joinedload(Car.engine_type),
            joinedload(Car.body_type),
            joinedload(Car.specs),
            joinedload(Car.variants),
            joinedload(Car.affiliates)
        ).filter(Car.status.in_([CarStatus.active, CarStatus.discontinued])).order_by(Car.id).all()

        if db_cars:
            for c in db_cars:
                s = c.specs
                v_list = []
                for v in (c.variants or []):
                    v_list.append({
                        'name': v.name,
                        'price': v.price,
                        'highlights': v.highlights,
                        'power_output': v.power_output,
                        'battery_range': v.battery_range,
                        'range_standard': v.range_standard,
                        'battery_type': v.battery_type,
                        'v2l_support': v.v2l_support,
                        'charging_time': v.charging_time,
                        'wall_charger_info': v.wall_charger_info,
                        'wheel_spec': v.wheel_spec,
                        'interior_spec': v.interior_spec,
                        'seating_layout': v.seating_layout,
                        'cluster_display': v.cluster_display,
                        'audio_display': v.audio_display,
                        'tailgate_feature': v.tailgate_feature,
                        'sunroof': v.sunroof,
                        'telematics_feature': v.telematics_feature,
                        'camera_vision': v.camera_vision,
                        'lighting_spec': v.lighting_spec,
                        'safety_adas': v.safety_adas,
                        'annual_tax': v.annual_tax,
                        'gallery_json': v.gallery_json
                    })

                affiliates_list = []
                if hasattr(c, 'affiliates') and c.affiliates:
                    for aff in c.affiliates:
                        if getattr(aff, 'is_active', True):
                            affiliates_list.append({
                                'id': aff.id,
                                'title': aff.title,
                                'image_url': aff.image_url,
                                'affiliate_url': aff.affiliate_url,
                                'price': aff.price,
                                'merchant': aff.merchant or 'Tokopedia',
                                'badge': aff.badge,
                                'description': aff.description
                            })

                c_status_str = c.status.value if hasattr(c.status, 'value') else str(c.status)
                cars_data.append({
                    'id': c.id,
                    'name': c.name,
                    'slug': c.slug,
                    'brand_name': c.brand.name if c.brand else '',
                    'brand_slug': c.brand.slug if c.brand else '',
                    'engine_type_slug': c.engine_type.slug if c.engine_type else 'bev',
                    'body_type_slug': c.body_type.slug if c.body_type else 'suv',
                    'year': c.year,
                    'price_start': c.price_start,
                    'price_end': c.price_end,
                    'tagline': c.tagline,
                    'description': c.description,
                    'image_url': c.image_url,
                    'brochure_url': getattr(c, 'brochure_url', None),
                    'gallery_json': getattr(c, 'gallery_json', None),
                    'is_featured': c.is_featured,
                    'status': c_status_str,
                    'affiliates': affiliates_list,
                    'specs': {
                        'length_mm': s.length_mm if s else None,
                        'width_mm': s.width_mm if s else None,
                        'height_mm': s.height_mm if s else None,
                        'wheelbase_mm': s.wheelbase_mm if s else None,
                        'ground_clearance_mm': s.ground_clearance_mm if s else None,
                        'seating_capacity': s.seating_capacity if s else None,
                        'trunk_volume_liters': s.trunk_volume_liters if s else None,
                        'fuel_tank_liters': s.fuel_tank_liters if s else None,
                        'engine_name': s.engine_name if s else None,
                        'engine_capacity_cc': s.engine_capacity_cc if s else None,
                        'battery_type': s.battery_type if s else None,
                        'battery_capacity_kwh': s.battery_capacity_kwh if s else None,
                        'electric_range_km': s.electric_range_km if s else None,
                        'range_standard': s.range_standard if s else None,
                        'v2l_support': s.v2l_support if s else None,
                        'cluster_display': s.cluster_display if s else None,
                        'airbags': s.airbags if s else None,
                        'abs_ebd': s.abs_ebd if s else False,
                        'esc': s.esc if s else False,
                        'adas': s.adas if s else False,
                        'adas_name': s.adas_name if s else None,
                        'annual_tax_estimate': s.annual_tax_estimate if s else None,
                        'warranty_vehicle': s.warranty_vehicle if s else None,
                        'warranty_battery': s.warranty_battery if s else None,
                        'wall_charger_info': s.wall_charger_info if s else None,
                        'assembly_status': s.assembly_status if s else None,
                        'top_speed_kmh': s.top_speed_kmh if s else None,
                        'transmission': s.transmission if s else None,
                        'drivetrain': s.drivetrain if s else None,
                        'horsepower': s.horsepower if s else None,
                        'torque_nm': s.torque_nm if s else None,
                        'acceleration_0_100': s.acceleration_0_100 if s else None,
                        'fuel_consumption_kmpl': s.fuel_consumption_kmpl if s else None,
                    } if s else {},
                    'variants': v_list
                })
        db.close()
    except Exception as e:
        print(f"Notice: Could not load directly from database ({e}). Falling back to json file.")

    if not cars_data:
        candidates = [
            os.path.join(backend_dir, 'data', 'compiled_cars.json'),
            os.path.join(backend_dir, 'compiled_cars.json'),
        ]
        compiled_file = next((p for p in candidates if os.path.exists(p)), candidates[0])
        with open(compiled_file, 'r', encoding='utf-8') as f:
            cars_data = json.load(f)

    cars = cars_data

    model_images = {
        'aletra-l8': 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=800&auto=format&fit=crop',
        'baic-bj30e': 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=800&auto=format&fit=crop',
        'baic-t1': 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=800&auto=format&fit=crop',
        'bmw-i3s': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800&auto=format&fit=crop',
        'bmw-i4': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800&auto=format&fit=crop',
        'bmw-i5': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800&auto=format&fit=crop',
        'bmw-i7': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800&auto=format&fit=crop',
        'bmw-i8': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800&auto=format&fit=crop',
        'bmw-ix': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800&auto=format&fit=crop',
        'bmw-ix1': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800&auto=format&fit=crop',
        'bmw-ix3': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800&auto=format&fit=crop',
        'byd-atto-1': 'https://images.unsplash.com/photo-1563720223185-11003d516935?q=80&w=800&auto=format&fit=crop',
        'byd-atto-3': 'https://images.unsplash.com/photo-1563720223185-11003d516935?q=80&w=800&auto=format&fit=crop',
        'byd-dolphin': 'https://images.unsplash.com/photo-1563720223185-11003d516935?q=80&w=800&auto=format&fit=crop',
        'byd-seal': 'https://images.unsplash.com/photo-1563720223185-11003d516935?q=80&w=800&auto=format&fit=crop',
        'byd-m6': 'https://images.unsplash.com/photo-1563720223185-11003d516935?q=80&w=800&auto=format&fit=crop',
        'byd-sealion-7': 'https://images.unsplash.com/photo-1563720223185-11003d516935?q=80&w=800&auto=format&fit=crop',
        'changan-lumin': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=800&auto=format&fit=crop',
        'changan-nevo': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=800&auto=format&fit=crop',
        'changan-deepal': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=800&auto=format&fit=crop',
        'chery-e5': 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?q=80&w=800&auto=format&fit=crop',
        'chery-j6': 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?q=80&w=800&auto=format&fit=crop',
        'chery-tiggo': 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?q=80&w=800&auto=format&fit=crop',
        'citroen-e-c3': 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?q=80&w=800&auto=format&fit=crop',
        'citroen-e-c4': 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?q=80&w=800&auto=format&fit=crop',
    }

    # Setup directories and copy assets once
    backend_uploads_dir = Path(__file__).resolve().parent / "uploads" / "cars"
    backend_brands_dir = Path(__file__).resolve().parent / "uploads" / "brands"
    frontend_images_dir = Path(__file__).resolve().parent.parent / "public" / "images" / "cars"
    frontend_brands_dir = Path(__file__).resolve().parent.parent / "public" / "images" / "brands"
    frontend_images_dir.mkdir(parents=True, exist_ok=True)
    frontend_brands_dir.mkdir(parents=True, exist_ok=True)

    if backend_brands_dir.exists():
        for b_file in backend_brands_dir.iterdir():
            if b_file.is_file():
                shutil.copy2(b_file, frontend_brands_dir / b_file.name)

    local_car_images = {}
    if frontend_images_dir.exists():
        for f_file in frontend_images_dir.iterdir():
            if f_file.is_file() and f_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.svg']:
                clean_stem = f_file.stem.lower().replace('_', '-').replace(' ', '-')
                alphanum = re.sub(r'[^a-z0-9]', '', clean_stem)
                local_car_images[f_file.name.lower()] = f"/images/cars/{f_file.name}"
                local_car_images[clean_stem] = f"/images/cars/{f_file.name}"
                local_car_images[alphanum] = f"/images/cars/{f_file.name}"

    if backend_uploads_dir.exists():
        for f_file in backend_uploads_dir.iterdir():
            if f_file.is_file() and f_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.svg']:
                shutil.copy2(f_file, frontend_images_dir / f_file.name)
                clean_stem = f_file.stem.lower().replace('_', '-').replace(' ', '-')
                alphanum = re.sub(r'[^a-z0-9]', '', clean_stem)
                local_car_images[f_file.name.lower()] = f"/images/cars/{f_file.name}"
                local_car_images[clean_stem] = f"/images/cars/{f_file.name}"
                local_car_images[alphanum] = f"/images/cars/{f_file.name}"

    default_img = 'https://images.unsplash.com/photo-1617788138017-80ad40651399?q=80&w=800&auto=format&fit=crop'

    # Build brochure files index from backend/brosur
    brosur_dir = os.path.join(backend_dir, 'brosur')
    available_brochures = {}
    if os.path.exists(brosur_dir):
        for bf in os.listdir(brosur_dir):
            if bf.lower().endswith('.pdf'):
                available_brochures[bf.lower()] = bf
                clean_bf_stem = re.sub(r'[^a-z0-9]', '', os.path.splitext(bf)[0].lower())
                available_brochures[clean_bf_stem] = bf

    frontend_cars = []

    for idx, c in enumerate(cars, 1):
        bname = c.get('brand_name') or 'EVnesia'
        c_slug = c.get('slug') or ''
        raw_c_name = c.get('name') or 'Model Mobil'
        c_name = re.sub(r'\s*CKD\b', '', raw_c_name, flags=re.I).strip()
        # Clean parenthetical text
        c_name = re.sub(r'\(.*?\)', '', c_name).strip()
        eslug = (c.get('engine_type_slug') or 'bev').lower()
        
        if eslug == 'bev':
            elabel = '⚡ Electric (BEV)'
            badge = '100% ELECTRIC BEV'
        elif eslug == 'phev':
            elabel = '🔋 Plug-in Hybrid (PHEV)'
            badge = 'PLUG-IN HYBRID PHEV'
        elif eslug == 'hev':
            elabel = '🍃 Full Hybrid (HEV)'
            badge = 'FULL HYBRID HEV'
        else:
            elabel = '💧 Clean Energy'
            badge = 'ELECTRIFIED 2026'

        # Extract & Normalize Specs from both specs dictionary and root keys
        raw_specs = c.get('specs') or {}
        
        length_mm = raw_specs.get('length_mm') or c.get('length_mm') or c.get('length')
        width_mm = raw_specs.get('width_mm') or c.get('width_mm') or c.get('width')
        height_mm = raw_specs.get('height_mm') or c.get('height_mm') or c.get('height')
        wheelbase_mm = raw_specs.get('wheelbase_mm') or c.get('wheelbase_mm') or c.get('wheelbase')
        ground_clearance_mm = raw_specs.get('ground_clearance_mm') or c.get('ground_clearance_mm') or c.get('ground_clearance')
        seating_capacity = raw_specs.get('seating_capacity') or c.get('seating_capacity') or 5
        trunk_volume = raw_specs.get('trunk_volume_liters') or c.get('luggage_capacity_standard_liters') or c.get('trunk_volume')
        
        motor_type = raw_specs.get('engine_name') or c.get('motor_architecture') or c.get('engine_name') or 'Permanent Magnet Synchronous Motor (PMSM)'
        battery_type = raw_specs.get('battery_type') or c.get('battery_type') or 'Lithium Iron Phosphate (LFP / Blade Battery)'
        battery_kwh = raw_specs.get('battery_capacity_kwh') or c.get('battery_capacity_kwh')
        range_km = raw_specs.get('electric_range_km') or c.get('electric_range_km') or c.get('range_nedc_km') or c.get('range_wltp_km') or c.get('range_cltc_km')
        
        v2l_watts = c.get('v2l_max_power_watts') or raw_specs.get('v2l_watts')
        v2l_supp = raw_specs.get('v2l_support') or (f"Ya ({v2l_watts} Watt)" if v2l_watts else "Ya, Mendukung V2L") if c.get('v2l_supported') else "Ya"
        
        cockpit = c.get('cockpit_instrument_cluster') or raw_specs.get('cluster_display') or 'Full Digital TFT Instrument Cluster'
        infotainment = c.get('head_unit_infotainment') or raw_specs.get('audio_display') or 'Touchscreen Central Display with Apple CarPlay & Android Auto'
        
        airbags = c.get('airbag_count') or raw_specs.get('airbags') or 6
        adas_pkg = c.get('adas_package_name') or raw_specs.get('adas_name') or 'Full Level 2 Intelligent ADAS'
        adas_feats = c.get('adas_features') or raw_specs.get('adas_features')
        if isinstance(adas_feats, list):
            adas_str = f"{adas_pkg} ({', '.join(adas_feats[:4])})"
        else:
            adas_str = adas_pkg

        pkb_val = c.get('estimated_pkb_annual_idr') or raw_specs.get('annual_tax_estimate') or 0
        pkb_formatted = f"Rp {int(pkb_val):,}/tahun".replace(',', '.') if pkb_val else "Rp 0 - 350.000 / tahun"
        
        v_warr_yr = c.get('vehicle_warranty_years') or 5
        v_warr_km = c.get('vehicle_warranty_km') or 150000
        b_warr_yr = c.get('battery_warranty_years') or 8
        b_warr_km = c.get('battery_warranty_km') or 160000
        
        fallback_veh = f"{v_warr_yr} Tahun / {v_warr_km} km" if isinstance(v_warr_km, str) else f"{v_warr_yr} Tahun / {int(v_warr_km):,} km".replace(',', '.')
        fallback_bat = f"{b_warr_yr} Tahun / {b_warr_km} km" if isinstance(b_warr_km, str) else f"{b_warr_yr} Tahun / {int(b_warr_km):,} km".replace(',', '.')

        warranty_veh = raw_specs.get('warranty_vehicle') or fallback_veh
        warranty_bat = raw_specs.get('warranty_battery') or fallback_bat
        assembly = raw_specs.get('assembly_status') or c.get('assembly_status') or 'CKD / CBU Resmi'

        specs = {
            'length_mm': length_mm,
            'width_mm': width_mm,
            'height_mm': height_mm,
            'wheelbase_mm': wheelbase_mm,
            'ground_clearance_mm': ground_clearance_mm,
            'seating_capacity': seating_capacity,
            'trunk_volume_liters': trunk_volume,
            'fuel_tank_liters': raw_specs.get('fuel_tank_liters'),
            'engine_name': motor_type,
            'engine_capacity_cc': raw_specs.get('engine_capacity_cc'),
            'fuel_consumption_kmpl': raw_specs.get('fuel_consumption_kmpl'),
            'battery_type': battery_type,
            'battery_capacity_kwh': battery_kwh,
            'electric_range_km': range_km,
            'range_standard': raw_specs.get('range_standard') or 'WLTP',
            'horsepower': raw_specs.get('horsepower'),
            'torque_nm': raw_specs.get('torque_nm'),
            'acceleration_0_100': raw_specs.get('acceleration_0_100'),
            'v2l_support': v2l_supp,
            'cockpit_instrument_cluster': cockpit,
            'head_unit_infotainment': infotainment,
            'airbag_count': airbags,
            'abs_ebd': raw_specs.get('abs_ebd', False),
            'esc': raw_specs.get('esc', False),
            'adas': raw_specs.get('adas', False),
            'adas_name': adas_pkg,
            'safety_adas_full': adas_str,
            'wall_charger_info': raw_specs.get('wall_charger_info'),
            'annual_tax_estimate': pkb_formatted,
            'warranty_vehicle': warranty_veh,
            'warranty_battery': warranty_bat,
            'assembly_status': assembly,
            'top_speed_kmh': c.get('top_speed_kph') or raw_specs.get('top_speed_kmh') or 160,
            'transmission': c.get('transmission') or raw_specs.get('transmission') or 'Single-Speed Reduction Gear',
            'drivetrain': raw_specs.get('drivetrain') or 'FWD / RWD'
        }

        p_start = c.get('price_start') or 0
        p_end = c.get('price_end') or p_start
        
        hp_val = raw_specs.get('horsepower') or c.get('horsepower') or c.get('max_power_hp')
        hp = f'{hp_val} HP' if hp_val else 'Spesifikasi Resmi'
        
        tq_val = raw_specs.get('torque_nm') or c.get('torque_nm') or c.get('max_torque_nm')
        torque = f'{tq_val} Nm' if tq_val else 'Spesifikasi Resmi'
        
        acc_val = raw_specs.get('acceleration_0_100') or c.get('acceleration_0_100')
        acc = f'{acc_val}s' if acc_val else '-'
        
        if range_km:
            consumption = f"{range_km} km WLTP"
        elif raw_specs.get('fuel_consumption_kmpl'):
            consumption = f"{raw_specs.get('fuel_consumption_kmpl')} km/L"
        else:
            consumption = 'Sesuai Standar Uji'

        # Resolve image URL
        img_url = c.get('image_url')
        if not img_url:
            clean_slug = c_slug.lower().replace('_', '-').replace(' ', '-')
            slug_alphanum = re.sub(r'[^a-z0-9]', '', clean_slug)
            
            img_url = (
                local_car_images.get(clean_slug) or
                local_car_images.get(slug_alphanum)
            )
            if not img_url:
                for k_stem, v_path in local_car_images.items():
                    if k_stem in clean_slug or clean_slug in k_stem or k_stem in slug_alphanum:
                        img_url = v_path
                        break
            if not img_url:
                img_url = default_img

        # Process and normalize all variants
        variants = []
        raw_variants = c.get('variants') or []
        
        for v_idx, v in enumerate(raw_variants, 1):
            raw_v_name = (
                v.get('variant_name') or 
                v.get('name') or 
                v.get('trim_name') or 
                (c.get('available_trims', [])[v_idx-1] if len(c.get('available_trims', [])) >= v_idx else f"{c_name} Varian {v_idx}")
            )

            if len(raw_v_name.split()) <= 2 and not any(part.lower() in raw_v_name.lower() for part in c_name.split()[:2]):
                v_name = f"{c_name} {raw_v_name}"
            else:
                v_name = raw_v_name
            v_name = re.sub(r'\s*CKD\b', '', v_name, flags=re.I).strip()
            
            v_price = (
                v.get('price_otr_jakarta') or 
                v.get('price') or 
                v.get('price_idr') or 
                (p_start if p_start > 0 else 0)
            )
            
            if v_price and v_price > 0:
                v_price_label = f"Rp {int(v_price):,}".replace(',', '.')
            else:
                v_price_label = "Hubungi APM / OTR Jakarta"

            # Power normalization
            if v.get('power_output'):
                v_power = v.get('power_output')
            elif v.get('max_power_hp') and v.get('max_torque_nm'):
                v_power = f"{v.get('max_power_hp')} HP / {v.get('max_torque_nm')} Nm"
            elif v.get('horsepower'):
                v_power = f"{v.get('horsepower')} HP / {v.get('torque_nm', 200)} Nm"
            else:
                v_power = hp

            # Battery / Range normalization
            if v.get('battery_range'):
                v_range = v.get('battery_range')
            elif v.get('battery_capacity_kwh'):
                range_dist = v.get('range_nedc_km') or v.get('range_wltp_km') or v.get('range_cltc_km') or range_km or '400+'
                v_range = f"{v.get('battery_capacity_kwh')} kWh (Jarak {range_dist} km)"
            else:
                v_range = consumption

            # ADAS normalization
            if v.get('safety_adas'):
                v_adas = v.get('safety_adas')
            elif v.get('adas_package_name'):
                v_adas = v.get('adas_package_name')
            else:
                v_adas = adas_pkg

            # Wheel & Interior
            v_wheel = v.get('wheel_spec') or v.get('wheels') or 'Alloy Wheels'
            v_interior = v.get('interior_spec') or v.get('seat_upholstery') or 'Synthetic Leather / Fabric Seats'
            v_audio = v.get('audio_display') or v.get('audio_system') or v.get('infotainment') or infotainment
            v_roof = v.get('sunroof') or v.get('roof_type') or 'Solid Hardtop Roof'
            v_v2l = v.get('v2l_support') or v2l_supp

            # Variant Gallery Parsing
            v_gallery = []
            if v.get('gallery_json'):
                try:
                    v_gallery = json.loads(v['gallery_json']) if isinstance(v['gallery_json'], str) else v['gallery_json']
                except Exception:
                    v_gallery = []

            variants.append({
                'name': v_name,
                'price': v_price,
                'priceLabel': v_price_label,
                'highlights': v.get('highlights') or v.get('description') or f"Tenaga {v_power}, Kapasitas {v_range}",
                'power_output': v_power,
                'battery_range': v_range,
                'battery_type': v.get('battery_type') or battery_type,
                'v2l_support': v_v2l,
                'charging_time': v.get('charging_time') or (f"DC {v.get('max_dc_charging_power_kw', '')} kW / AC {v.get('max_ac_charging_power_kw', '')} kW" if v.get('max_dc_charging_power_kw') else 'DC Fast Charging 30 Menit'),
                'wall_charger_info': v.get('wall_charger_info') or c.get('home_charger_package') or 'Termasuk Gratis 7 kW Wallbox Charger',
                'wheel_spec': v_wheel,
                'interior_spec': v_interior,
                'seating_layout': v.get('seating_layout') or f"{seating_capacity}-Seater",
                'cluster_display': v.get('cluster_display') or cockpit,
                'audio_display': v_audio,
                'tailgate_feature': v.get('tailgate_feature') or 'Standard Tailgate',
                'sunroof': v_roof,
                'telematics_feature': v.get('telematics_feature') or 'Connected Smartphone App (DiLink/MyBMW)',
                'camera_vision': v.get('camera_vision') or v.get('camera_system') or '360 HD Panoramic Camera',
                'lighting_spec': v.get('lighting_spec') or v.get('headlights') or 'LED Projector Headlamps + DRL',
                'safety_adas': v_adas,
                'annual_tax': v.get('annual_tax') or pkb_formatted,
                'gallery': v_gallery
            })

        # Recalculate price range and clean metrics across variants
        if variants:
            var_prices = [v['price'] for v in variants if v['price'] > 0]
            if var_prices:
                p_start = min(var_prices)
                p_end = max(var_prices)

        price_str = format_price_display(p_start, p_end)
        hp = format_power_metrics(raw_specs, variants, hp)
        consumption = format_range_metrics(raw_specs, variants, consumption)
        acc = format_acc_metrics(raw_specs, variants, acc)

        # Match brochure URL
        db_brochure = c.get('brochure_url')
        brochure_url = None
        if db_brochure:
            brochure_url = db_brochure
        elif available_brochures:
            c_name_clean = re.sub(r'[^a-z0-9]', '', c_name.lower())
            c_slug_clean = re.sub(r'[^a-z0-9]', '', c_slug.lower())
            cand_keys = [
                f"{c_name.lower()}.pdf",
                f"{c_slug.lower()}.pdf",
                c_name_clean,
                c_slug_clean
            ]
            for ck in cand_keys:
                if ck in available_brochures:
                    brochure_url = f"/brosur/{available_brochures[ck]}"
                    break
            if not brochure_url:
                for bf_key, bf_orig in available_brochures.items():
                    if len(c_name_clean) >= 4 and (c_name_clean in bf_key or bf_key in c_name_clean):
                        brochure_url = f"/brosur/{bf_orig}"
                        break

        # Car Photo Gallery Parsing (Interior, Eksterior, Fitur)
        car_gallery = []
        if c.get('gallery_json'):
            try:
                car_gallery = json.loads(c['gallery_json']) if isinstance(c['gallery_json'], str) else c['gallery_json']
            except Exception:
                car_gallery = []

        f_car = {
            'id': idx,
            'slug': c_slug,
            'name': c_name,
            'brand': bname,
            'bodyType': c.get('body_type_slug', 'suv'),
            'engineType': eslug,
            'engineLabel': elabel,
            'price': price_str,
            'priceVal': round(p_start / 1000000) if p_start else 0,
            'img': img_url,
            'brochureUrl': brochure_url,
            'hp': hp,
            'torque': torque,
            'acc': acc,
            'consumption': consumption,
            'badge': badge,
            'tagline': c.get('tagline', ''),
            'description': c.get('description', '') or c.get('market_position', ''),
            'status': c.get('status', 'active'),
            'specs': specs,
            'variants': variants,
            'gallery': car_gallery,
            'gallery_json': c.get('gallery_json'),
            'affiliates': c.get('affiliates', [])
        }
        frontend_cars.append(f_car)

    target_dir = os.path.join(backend_dir, '..', 'src', 'data')
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, 'electrified-cars.json')

    with open(target_path, 'w', encoding='utf-8') as tf:
        json.dump(frontend_cars, tf, indent=2, ensure_ascii=False)

    print(f'Successfully exported {len(frontend_cars)} cars to {target_path}')

    # Also export fuel and electricity prices to src/data/fuel-prices.json
    try:
        from app.models.fuel_price import FuelPrice
        prices = db.query(FuelPrice).all()
        prices_data = [
            {
                "id": p.id,
                "fuel_type": p.fuel_type,
                "price_per_unit": p.price_per_unit,
                "unit": p.unit,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            }
            for p in prices
        ]
        prices_path = os.path.join(target_dir, 'fuel-prices.json')
        with open(prices_path, 'w', encoding='utf-8') as pf:
            json.dump(prices_data, pf, indent=2, ensure_ascii=False)
        print(f'Successfully exported {len(prices_data)} fuel prices to {prices_path}')
    except Exception:
        pass

if __name__ == '__main__':
    export_cars()
