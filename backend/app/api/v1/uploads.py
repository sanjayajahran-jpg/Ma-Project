import io
import os
import re
import shutil
import json
from pathlib import Path
from uuid import uuid4
from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Form
from sqlalchemy.orm import Session
from PIL import Image

from app.api import deps
from app.core.config import settings
from app.database import get_db
from app.models.user import User
from app.models.car import Car, CarVariant
from app.models.car_media import CarMedia, MediaCategory
from app.models.brand import Brand
from app.services.s3_service import upload_to_storage, delete_from_storage, is_s3_configured

router = APIRouter()

# Resolve absolute upload directory path relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
UPLOAD_DIR_PATH = BASE_DIR / settings.UPLOAD_DIR
CARS_DIR_PATH = UPLOAD_DIR_PATH / "cars"
BRANDS_DIR_PATH = UPLOAD_DIR_PATH / "brands"
VARIANTS_DIR_PATH = UPLOAD_DIR_PATH / "variants"

# Ensure all subdirectories exist
UPLOAD_DIR_PATH.mkdir(parents=True, exist_ok=True)
CARS_DIR_PATH.mkdir(parents=True, exist_ok=True)
BRANDS_DIR_PATH.mkdir(parents=True, exist_ok=True)
VARIANTS_DIR_PATH.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(name: str, prefix: str = "", force_ext: Optional[str] = None) -> str:
    """Clean filename and keep only alphanumeric, dashes, and underscores."""
    stem = Path(name).stem
    clean_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', stem)[:40]
    ext = force_ext if force_ext else Path(name).suffix.lower()
    prefix_str = f"{prefix}_" if prefix else ""
    return f"{prefix_str}{uuid4().hex[:8]}_{clean_stem}{ext}"


def _convert_to_webp(file_obj, quality: int = 85) -> Tuple[io.BytesIO, str]:
    """
    Konversi gambar otomatis (PNG/JPG/JPEG/dll) menjadi WebP teroptimasi secara in-memory.
    """
    image = Image.open(file_obj)
    output = io.BytesIO()
    # Jika mode RGBA / LA / transparan
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image.save(output, format="WEBP", quality=quality, method=6)
    else:
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(output, format="WEBP", quality=quality, method=6)
    output.seek(0)
    return output, "image/webp"


def _validate_image_file(file: UploadFile):
    """Validate uploaded image MIME type and extension."""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipe file '{file.content_type}' tidak diizinkan. Tipe yang didukung: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )


@router.post("/", summary="Upload gambar umum (Admin)")
async def upload_single_image(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload file gambar ke folder root uploads.
    """
    _validate_image_file(file)

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ukuran file terlalu besar ({round(file_size / (1024*1024), 2)} MB). Maksimal {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    safe_name = _sanitize_filename(file.filename or "image.webp")
    public_url, storage_key = upload_to_storage(file.file, f"general/{safe_name}", file.content_type)

    return {
        "url": public_url,
        "filename": safe_name,
        "original_name": file.filename,
        "size_bytes": file_size,
        "content_type": file.content_type,
        "message": "Gambar berhasil diunggah ke storage cloud"
    }


@router.post("/cars", summary="Upload foto mobil dengan konversi otomatis ke WebP")
async def upload_car_image(
    file: UploadFile = File(...),
    car_id: Optional[int] = Form(None),
    car_slug: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload foto mobil langsung ke Neon Object Storage (car-assets/cars/).
    Otomatis dikonversi ke WebP untuk performa maksimal dan ukuran minimal.
    Opsional: jika car_id atau car_slug diberikan, otomatis memperbarui image_url mobil di database.
    """
    _validate_image_file(file)

    # Otomatis konversi file gambar ke WebP teroptimasi
    try:
        webp_stream, c_type = _convert_to_webp(file.file, quality=85)
        safe_name = _sanitize_filename(file.filename or "car.png", prefix="car", force_ext=".webp")
        upload_stream = webp_stream
    except Exception as e:
        # Fallback jika konversi gagal
        file.file.seek(0)
        safe_name = _sanitize_filename(file.filename or "car.png", prefix="car")
        c_type = file.content_type
        upload_stream = file.file

    public_url, storage_key = upload_to_storage(upload_stream, f"cars/{safe_name}", c_type)

    # Auto-update Car in DB if ID or Slug provided
    car_updated = False
    if car_id:
        car = db.query(Car).filter(Car.id == car_id).first()
        if car:
            car.image_url = public_url
            car.thumbnail_url = public_url
            db.commit()
            car_updated = True
    elif car_slug:
        car = db.query(Car).filter(Car.slug == car_slug).first()
        if car:
            car.image_url = public_url
            car.thumbnail_url = public_url
            db.commit()
            car_updated = True

    if car_updated:
        try:
            from app.api.v1.cars import trigger_frontend_export
            trigger_frontend_export()
        except Exception:
            pass

    return {
        "url": public_url,
        "filename": safe_name,
        "original_name": file.filename,
        "format": "webp",
        "car_updated": car_updated,
        "message": "Foto mobil berhasil dikonversi ke WebP dan diunggah ke Neon Object Storage!"
    }


@router.post("/brochures", summary="Upload brosur PDF mobil ke Neon Storage")
async def upload_car_brochure(
    file: UploadFile = File(...),
    car_id: Optional[int] = Form(None),
    car_slug: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload brosur mobil PDF langsung ke Neon Object Storage (car-assets/brochures/).
    Opsional: jika car_id atau car_slug diberikan, otomatis memperbarui brochure_url mobil di database.
    """
    if not (file.filename and file.filename.lower().endswith(".pdf")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hanya file berekstensi .pdf yang diperbolehkan untuk brosur mobil."
        )

    safe_name = _sanitize_filename(file.filename, prefix="brochure", force_ext=".pdf")
    public_url, storage_key = upload_to_storage(file.file, f"brochures/{safe_name}", "application/pdf")

    # Auto-update Car in DB if ID or Slug provided
    car_updated = False
    if car_id:
        car = db.query(Car).filter(Car.id == car_id).first()
        if car:
            car.brochure_url = public_url
            db.commit()
            car_updated = True
    elif car_slug:
        car = db.query(Car).filter(Car.slug == car_slug).first()
        if car:
            car.brochure_url = public_url
            db.commit()
            car_updated = True

    if car_updated:
        try:
            from app.api.v1.cars import trigger_frontend_export
            trigger_frontend_export()
        except Exception:
            pass

    return {
        "url": public_url,
        "filename": safe_name,
        "original_name": file.filename,
        "car_updated": car_updated,
        "message": "Brosur PDF berhasil diunggah ke Neon Object Storage!"
    }


@router.post("/brands", summary="Upload logo merek kendaraan")
async def upload_brand_logo(
    file: UploadFile = File(...),
    brand_id: Optional[int] = Form(None),
    brand_slug: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload logo merek resmi (SVG / PNG / WebP) langsung ke Supabase Storage.
    Opsional: jika brand_id atau brand_slug diberikan, otomatis memperbarui logo_url merek di database.
    """
    _validate_image_file(file)

    safe_name = _sanitize_filename(file.filename or "brand.png", prefix="brand")
    public_url, storage_key = upload_to_storage(file.file, f"brands/{safe_name}", file.content_type)

    # Auto-update Brand in DB if ID or Slug provided
    brand_updated = False
    if brand_id:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if brand:
            brand.logo_url = public_url
            db.commit()
            brand_updated = True
    elif brand_slug:
        brand = db.query(Brand).filter(Brand.slug == brand_slug).first()
        if brand:
            brand.logo_url = public_url
            db.commit()
            brand_updated = True

    return {
        "url": public_url,
        "filename": safe_name,
        "original_name": file.filename,
        "brand_updated": brand_updated,
        "message": "Logo merek resmi berhasil diunggah ke Supabase Storage"
    }


@router.post("/variants/{variant_id}/gallery", summary="Upload galeri foto varian trim")
async def upload_variant_gallery(
    variant_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload beberapa foto spesifik untuk varian trim tertentu dan simpan ke gallery_json varian.
    """
    variant = db.query(CarVariant).filter(CarVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Varian trim dengan ID {variant_id} tidak ditemukan"
        )

    existing_gallery = []
    if variant.gallery_json:
        try:
            existing_gallery = json.loads(variant.gallery_json)
        except Exception:
            existing_gallery = []

    uploaded_urls = []
    for file in files:
        _validate_image_file(file)
        safe_name = _sanitize_filename(file.filename or "variant.webp", prefix=f"v{variant_id}")
        destination = VARIANTS_DIR_PATH / safe_name

        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pub_url = f"/static/uploads/variants/{safe_name}"
        uploaded_urls.append(pub_url)
        existing_gallery.append(pub_url)

    variant.gallery_json = json.dumps(existing_gallery)
    db.commit()

    return {
        "variant_id": variant_id,
        "new_uploads": uploaded_urls,
        "total_gallery_count": len(existing_gallery),
        "gallery": existing_gallery,
        "message": f"Berhasil menambahkan {len(uploaded_urls)} foto ke galeri varian"
    }


# =====================================================================
# HIERARCHICAL STORAGE API (Brand -> Car -> Photos & Brochure)
# =====================================================================

@router.post("/brand/{brand_slug}/logo", summary="Upload logo merek ke folder uploads/{brand_slug}/")
async def upload_hierarchical_brand_logo(
    brand_slug: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Menyimpan logo resmi merek ke folder berjenjang: uploads/{brand_slug}/logo.<ext>
    dan otomatis mengupdate field logo_url di database merek.
    """
    _validate_image_file(file)

    clean_brand = re.sub(r'[^a-zA-Z0-9_\-]', '', brand_slug).lower()
    brand_folder = UPLOAD_DIR_PATH / clean_brand
    brand_folder.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "logo.png").suffix.lower()
    filename = f"logo{ext}"
    dest = brand_folder / filename

    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    public_url = f"/static/uploads/{clean_brand}/{filename}"

    brand = db.query(Brand).filter(Brand.slug == clean_brand).first()
    if brand:
        brand.logo_url = public_url
        db.commit()

    return {
        "url": public_url,
        "brand_slug": clean_brand,
        "filename": filename,
        "message": f"Logo merek '{clean_brand}' berhasil disimpan ke folder uploads/{clean_brand}/"
    }


@router.post("/car/{brand_slug}/{car_slug}/photo", summary="Upload foto mobil ke folder uploads/{brand_slug}/{car_slug}/")
async def upload_hierarchical_car_photo(
    brand_slug: str,
    car_slug: str,
    file: UploadFile = File(...),
    is_cover: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Menyimpan foto mobil ke folder terstruktur rapi: uploads/{brand_slug}/{car_slug}/
    Jika is_cover=True, otomatis memperbarui image_url mobil di database.
    """
    _validate_image_file(file)

    clean_brand = re.sub(r'[^a-zA-Z0-9_\-]', '', brand_slug).lower()
    clean_car = re.sub(r'[^a-zA-Z0-9_\-]', '', car_slug).lower()
    car_folder = UPLOAD_DIR_PATH / clean_brand / clean_car
    car_folder.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "car.webp").suffix.lower()
    if is_cover:
        filename = f"cover{ext}"
    else:
        filename = _sanitize_filename(file.filename or "photo.webp")

    dest = car_folder / filename
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    public_url = f"/static/uploads/{clean_brand}/{clean_car}/{filename}"

    car = db.query(Car).filter(Car.slug == clean_car).first()
    if car and is_cover:
        car.image_url = public_url
        db.commit()

    return {
        "url": public_url,
        "brand_slug": clean_brand,
        "car_slug": clean_car,
        "filename": filename,
        "is_cover": is_cover,
        "message": f"Foto mobil '{clean_car}' berhasil disimpan di folder uploads/{clean_brand}/{clean_car}/"
    }


@router.post("/car/{brand_slug}/{car_slug}/brochure", summary="Upload brosur PDF ke folder uploads/{brand_slug}/{car_slug}/")
async def upload_hierarchical_car_brochure(
    brand_slug: str,
    car_slug: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Menyimpan file brosur PDF resmi mobil ke folder: uploads/{brand_slug}/{car_slug}/brochure.pdf
    dan otomatis mengupdate field brochure_url mobil di database.
    """
    ext = Path(file.filename or "brochure.pdf").suffix.lower()
    if ext != ".pdf" and "pdf" not in (file.content_type or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File yang diunggah harus berformat PDF (.pdf)"
        )

    clean_brand = re.sub(r'[^a-zA-Z0-9_\-]', '', brand_slug).lower()
    clean_car = re.sub(r'[^a-zA-Z0-9_\-]', '', car_slug).lower()
    car_folder = UPLOAD_DIR_PATH / clean_brand / clean_car
    car_folder.mkdir(parents=True, exist_ok=True)

    filename = "brochure.pdf"
    dest = car_folder / filename
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    public_url = f"/static/uploads/{clean_brand}/{clean_car}/{filename}"

    # Update database
    car = db.query(Car).filter(Car.slug == clean_car).first()
    if car:
        car.brochure_url = public_url
        db.commit()

        # Copy to legacy brosur folder as fallback
        brosur_dir = BASE_DIR / "brosur"
        brosur_dir.mkdir(parents=True, exist_ok=True)
        legacy_dest = brosur_dir / f"{car.name}.pdf"
        try:
            shutil.copyfile(dest, legacy_dest)
        except Exception:
            pass

        try:
            from app.api.v1.cars import trigger_frontend_export
            trigger_frontend_export()
        except Exception:
            pass

    return {
        "url": public_url,
        "brand_slug": clean_brand,
        "car_slug": clean_car,
        "filename": filename,
        "message": f"Brosur resmi PDF berhasil disimpan di folder uploads/{clean_brand}/{clean_car}/"
    }


@router.get("/tree", summary="Lihat struktur folder penyimpanan merek & mobil")
def get_storage_tree():
    """
    Menampilkan pohon hierarki folder media: Merek -> Mobil -> Foto & Brosur
    """
    tree = []
    if not UPLOAD_DIR_PATH.exists():
        return {"tree": []}

    for brand_item in sorted(UPLOAD_DIR_PATH.iterdir()):
        if not brand_item.is_dir() or brand_item.name in ("cars", "brands", "variants"):
            continue

        brand_data = {
            "brand_slug": brand_item.name,
            "has_logo": any(brand_item.glob("logo.*")),
            "cars": []
        }

        for car_item in sorted(brand_item.iterdir()):
            if car_item.is_dir():
                photos = [f.name for f in car_item.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.svg')]
                has_brochure = any(car_item.glob("*.pdf"))
                brand_data["cars"].append({
                    "car_slug": car_item.name,
                    "photos_count": len(photos),
                    "photos": photos,
                    "has_brochure": has_brochure,
                    "folder_path": f"/static/uploads/{brand_item.name}/{car_item.name}/"
                })

        tree.append(brand_data)

    return {"total_brands": len(tree), "tree": tree}


# =====================================================================
# S3 CAR MEDIA MANAGEMENT (Integrated with car_media table)
# =====================================================================

@router.post("/cars/{car_id}/media", summary="Upload media mobil ke S3 dan catat di tabel car_media")
async def upload_car_media_s3(
    car_id: int,
    file: UploadFile = File(...),
    category: str = Form("exterior"),
    variant_id: Optional[int] = Form(None),
    caption: Optional[str] = Form(None),
    sort_order: int = Form(1),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Unggah foto/brosur ke cloud S3 (atau penyimpanan terstruktur lokal)
    dan catat record baru ke tabel 'car_media'.
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mobil dengan ID {car_id} tidak ditemukan"
        )

    # Validasi kategori
    valid_categories = ["hero", "exterior", "interior", "feature", "brochure"]
    cat_lower = category.lower().strip()
    if cat_lower not in valid_categories:
        cat_lower = "exterior"

    # Validasi tipe file
    _validate_image_file(file)

    # Tentukan ukuran file
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    # Sanitasi nama file dan susun S3 Key sesuai hierarki
    brand_slug = car.brand.slug if car.brand else "general"
    clean_car = car.slug
    ext = Path(file.filename or "media.webp").suffix.lower()
    clean_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(file.filename or "media").stem)[:30]
    unique_filename = f"{uuid4().hex[:8]}_{clean_stem}{ext}"

    # Hierarki S3 Key: cars/{brand_slug}/{car_slug}/{category}/{filename}
    s3_key = f"cars/{brand_slug}/{clean_car}/{cat_lower}/{unique_filename}"

    # Unggah via S3 Service
    content_type = file.content_type or "image/webp"
    public_url, actual_s3_key = upload_to_storage(
        file_obj=file.file,
        storage_key=s3_key,
        content_type=content_type
    )

    # Simpan ke tabel car_media
    media_entry = CarMedia(
        car_id=car.id,
        variant_id=variant_id,
        category=MediaCategory(cat_lower),
        file_url=public_url,
        s3_key=actual_s3_key,
        file_name=file.filename or unique_filename,
        mime_type=content_type,
        file_size_bytes=file_size,
        caption=caption,
        sort_order=sort_order,
        is_active=True
    )
    db.add(media_entry)

    # Jika kategori hero, update car.image_url
    if cat_lower == "hero":
        car.image_url = public_url

    # Jika kategori brochure, update car.brochure_url
    if cat_lower == "brochure":
        car.brochure_url = public_url

    # Sinkronisasi ke legacy gallery_json agar kompatibel 100%
    try:
        current_gallery = json.loads(car.gallery_json) if car.gallery_json else []
    except Exception:
        current_gallery = []

    if public_url not in current_gallery and cat_lower != "brochure":
        current_gallery.append(public_url)
        car.gallery_json = json.dumps(current_gallery)

    db.commit()
    db.refresh(media_entry)

    # Trigger export frontend agar Astro langsung sinkron
    try:
        from app.api.v1.cars import trigger_frontend_export
        trigger_frontend_export()
    except Exception:
        pass

    return {
        "id": media_entry.id,
        "car_id": media_entry.car_id,
        "variant_id": media_entry.variant_id,
        "category": media_entry.category.value,
        "file_url": media_entry.file_url,
        "s3_key": media_entry.s3_key,
        "file_name": media_entry.file_name,
        "file_size_bytes": media_entry.file_size_bytes,
        "caption": media_entry.caption,
        "sort_order": media_entry.sort_order,
        "is_s3": is_s3_configured(),
        "message": f"Media kategori '{cat_lower}' berhasil disimpan ke penyimpanan dan tabel car_media"
    }


@router.get("/cars/{car_id}/media", summary="Ambil semua media & galeri mobil dari tabel car_media")
def get_car_media_list(car_id: int, db: Session = Depends(get_db)):
    """
    Mengambil seluruh daftar foto & berkas S3 untuk satu mobil,
    dikelompokkan berdasarkan kategori (hero, exterior, interior, feature, brochure).
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mobil dengan ID {car_id} tidak ditemukan"
        )

    media_items = db.query(CarMedia).filter(
        CarMedia.car_id == car_id,
        CarMedia.is_active == True
    ).order_by(CarMedia.sort_order.asc(), CarMedia.id.asc()).all()

    grouped = {
        "hero": [],
        "exterior": [],
        "interior": [],
        "feature": [],
        "brochure": []
    }

    raw_items = []
    for item in media_items:
        data = {
            "id": item.id,
            "category": item.category.value,
            "file_url": item.file_url,
            "s3_key": item.s3_key,
            "file_name": item.file_name,
            "file_size_bytes": item.file_size_bytes,
            "caption": item.caption,
            "sort_order": item.sort_order,
            "variant_id": item.variant_id
        }
        raw_items.append(data)
        if item.category.value in grouped:
            grouped[item.category.value].append(data)

    return {
        "car_id": car_id,
        "car_name": car.name,
        "total_media": len(media_items),
        "grouped": grouped,
        "items": raw_items
    }


@router.delete("/media/{media_id}", summary="Hapus media dari S3 dan tabel car_media")
def delete_car_media_item(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Menghapus berkas dari cloud S3 / lokal dan menghapus baris data dari tabel car_media.
    """
    media_item = db.query(CarMedia).filter(CarMedia.id == media_id).first()
    if not media_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media dengan ID {media_id} tidak ditemukan"
        )

    # 1. Hapus dari S3 / storage disk
    if media_item.s3_key:
        delete_from_storage(media_item.s3_key)

    # 2. Hapus dari database
    car_id = media_item.car_id
    db.delete(media_item)
    db.commit()

    return {
        "media_id": media_id,
        "car_id": car_id,
        "message": "Berkas media berhasil dihapus dari storage dan database"
    }

