import sys
from app.database import SessionLocal
from app.models.fuel_price import FuelPrice
from export_frontend_cars import export_cars

db = SessionLocal()

STANDARD_PRICES = [
    {"fuel_type": "Pertamax (RON 92)", "price": 13700.0, "unit": "L"},
    {"fuel_type": "Pertalite (Subsidi)", "price": 10000.0, "unit": "L"},
    {"fuel_type": "PLN Rumah Reguler (7 kW)", "price": 1699.0, "unit": "kWh"},
    {"fuel_type": "PLN Diskon Malam (22.00-05.00)", "price": 1189.0, "unit": "kWh"},
    {"fuel_type": "SPKLU Fast Charging (DC 50 kW)", "price": 2466.0, "unit": "kWh"},
    {"fuel_type": "SPKLU Ultra Fast (DC 150-200 kW)", "price": 2900.0, "unit": "kWh"},
]

for item in STANDARD_PRICES:
    # Check by fuel_type keyword
    name = item["fuel_type"]
    existing = None
    for p in db.query(FuelPrice).all():
        if item["unit"] == "L" and ("pertamax" in name.lower() and "pertamax" in p.fuel_type.lower() and "turbo" not in p.fuel_type.lower()):
            existing = p
            break
        elif item["unit"] == "L" and ("pertalite" in name.lower() and "pertalite" in p.fuel_type.lower()):
            existing = p
            break
        elif "malam" in name.lower() and "malam" in p.fuel_type.lower():
            existing = p
            break
        elif "ultra" in name.lower() and "ultra" in p.fuel_type.lower():
            existing = p
            break
        elif "fast" in name.lower() and "fast" in p.fuel_type.lower() and "ultra" not in p.fuel_type.lower():
            existing = p
            break
        elif "reguler" in name.lower() and ("reguler" in p.fuel_type.lower() or "rumah" in p.fuel_type.lower()):
            existing = p
            break

    if existing:
        existing.fuel_type = name
        existing.price_per_unit = item["price"]
        existing.unit = item["unit"]
        print(f"Updated: {existing.id} -> {name}: {item['price']}")
    else:
        new_p = FuelPrice(fuel_type=name, price_per_unit=item["price"], unit=item["unit"])
        db.add(new_p)
        print(f"Created: {name}: {item['price']}")

db.commit()

# Re-export frontend JSON
export_cars()
print("Successfully synced fuel prices to database and frontend JSON!")
