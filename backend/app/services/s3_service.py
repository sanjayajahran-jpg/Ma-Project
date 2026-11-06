import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOCAL_UPLOAD_PATH = BASE_DIR / settings.UPLOAD_DIR


def is_s3_configured() -> bool:
    """Periksa apakah kredensial Neon Object Storage (S3) sudah diisi di .env"""
    return bool(
        settings.S3_BUCKET_NAME and
        settings.S3_ACCESS_KEY_ID and
        settings.S3_SECRET_ACCESS_KEY
    )


def get_s3_client():
    """Inisialisasi klien boto3 S3 / Cloudflare R2"""
    if not is_s3_configured():
        return None

    client_kwargs = {
        "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
        "region_name": settings.S3_REGION_NAME or "ap-southeast-1"
    }

    if settings.S3_ENDPOINT_URL:
        client_kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL

    return boto3.client("s3", **client_kwargs)


def upload_to_storage(
    file_obj,
    storage_key: str,
    content_type: str = "image/webp"
) -> Tuple[str, str]:
    """
    Unggah berkas:
    1. Prioritas Utama: Neon Object Storage (S3-compatible) / AWS S3
    2. Fallback: Folder uploads/ lokal
    
    Returns:
        Tuple[str, str]: (public_url, storage_key)
    """
    storage_key = storage_key.lstrip("/")

    # 1. Neon Object Storage / S3
    if is_s3_configured():
        try:
            client = get_s3_client()
            extra_args = {"ContentType": content_type}

            file_obj.seek(0)
            client.upload_fileobj(
                file_obj,
                settings.S3_BUCKET_NAME,
                storage_key,
                ExtraArgs=extra_args
            )

            if settings.S3_PUBLIC_DOMAIN:
                public_url = f"{settings.S3_PUBLIC_DOMAIN.rstrip('/')}/{storage_key}"
            else:
                public_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.S3_REGION_NAME}.amazonaws.com/{storage_key}"

            logger.info(f"File berhasil diunggah ke S3: {public_url}")
            return public_url, storage_key
        except ClientError as e:
            logger.error(f"Gagal mengunggah ke S3: {e}. Mengalihkan ke penyimpanan lokal...")

    # 3. Fallback Penyimpanan Lokal Terstruktur
    local_file_dest = LOCAL_UPLOAD_PATH / storage_key
    local_file_dest.parent.mkdir(parents=True, exist_ok=True)

    file_obj.seek(0)
    with open(local_file_dest, "wb") as buffer:
        shutil.copyfileobj(file_obj, buffer)

    frontend_dest = BASE_DIR.parent / "public" / "static" / "uploads" / storage_key
    frontend_dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(local_file_dest, frontend_dest)
    except Exception:
        pass

    public_url = f"/static/uploads/{storage_key}"
    return public_url, storage_key


def delete_from_storage(storage_key: str) -> bool:
    """
    Hapus berkas dari Supabase Storage, S3, dan/atau lokal.
    """
    storage_key = storage_key.lstrip("/")
    deleted = False

    # 1. Neon Object Storage (S3)
    if is_s3_configured():
        try:
            client = get_s3_client()
            client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=storage_key
            )
            deleted = True
        except Exception as e:
            logger.error(f"Error saat menghapus dari S3: {e}")

    # 3. Disk lokal jika ada
    local_path = LOCAL_UPLOAD_PATH / storage_key
    if local_path.exists():
        try:
            local_path.unlink()
            deleted = True
        except Exception:
            pass

    return deleted
