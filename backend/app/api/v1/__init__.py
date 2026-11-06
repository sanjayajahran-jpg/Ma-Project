from fastapi import APIRouter
from app.api.v1 import auth, brands, cars, compare, calculator, fuel_prices, uploads, affiliates, articles, cms_sync

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(brands.router, prefix="/brands", tags=["Brands"])
api_router.include_router(cars.router, prefix="/cars", tags=["Cars & Catalog"])
api_router.include_router(articles.router, prefix="/articles", tags=["Articles & News (Neon)"])
api_router.include_router(cms_sync.router, prefix="/cms", tags=["CMS Open API Sync"])
api_router.include_router(compare.router, prefix="/compare", tags=["Car Comparison"])
api_router.include_router(calculator.router, prefix="/calculator", tags=["Calculators"])
api_router.include_router(fuel_prices.router, prefix="/fuel-prices", tags=["Fuel & Energy Prices"])
api_router.include_router(affiliates.router, prefix="/affiliates", tags=["Car Affiliates & Accessories"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["File Uploads"])
api_router.include_router(uploads.router, prefix="/upload", tags=["File Uploads (Legacy)"])



