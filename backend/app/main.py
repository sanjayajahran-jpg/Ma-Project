import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api.v1 import api_router
from app.database import engine, Base, check_db_connection

# Import all models to ensure they are registered with Base metadata
import app.models  # noqa: F401

# Create tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend REST API resmi untuk portal media dan pusat data kendaraan elektrifikasi EVnesia PRO.",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Static Directories & Mounts
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR_PATH = BASE_DIR / settings.UPLOAD_DIR
UPLOAD_DIR_PATH.mkdir(parents=True, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR_PATH), name="uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR_PATH), name="uploads_alias")

# Static Images Directory (Serving all frontend car & brand images in backend)
PUBLIC_DIR = BASE_DIR.parent / "public"
PUBLIC_IMAGES_DIR = PUBLIC_DIR / "images"
if PUBLIC_IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=PUBLIC_IMAGES_DIR), name="images")
    app.mount("/static/images", StaticFiles(directory=PUBLIC_IMAGES_DIR), name="static_images")
if PUBLIC_DIR.exists():
    app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public_dir")

# Static Brochure PDFs Directory
BROSUR_DIR_PATH = BASE_DIR / "brosur"
BROSUR_DIR_PATH.mkdir(parents=True, exist_ok=True)
app.mount("/static/brosur", StaticFiles(directory=BROSUR_DIR_PATH), name="brosur")
app.mount("/brosur", StaticFiles(directory=BROSUR_DIR_PATH), name="brosur_alias")

app.include_router(api_router, prefix=settings.API_V1_STR)

TEMPLATE_PATH = Path(__file__).parent / "templates" / "index.html"


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
@app.get("/admin", response_class=HTMLResponse, tags=["Dashboard"])
def admin_dashboard():
    """Serve visual EVnesia Admin and REST API Dashboard"""
    if TEMPLATE_PATH.exists():
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>EVnesia PRO API</h1><p><a href='/docs'>Swagger Docs</a></p>")


@app.get("/health", tags=["Health"])
def health_check():
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "app": settings.PROJECT_NAME,
        "database_connected": db_ok,
        "uploads_active": UPLOAD_DIR_PATH.exists()
    }


