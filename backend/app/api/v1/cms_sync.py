from typing import Any, Dict
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.api import deps
from app.models.article import CMSSyncCheckpoint
from app.schemas.article import SyncStatusResponse, TriggerSyncRequest
from app.services.cms_client import InovaCMSClient, CMSClientError
from app.services.cms_sync_service import cms_sync_service
from app.database import SessionLocal

router = APIRouter()


class ExtractUrlRequest(BaseModel):
    url: str


def run_background_sync(portal_id: str, force_full: bool, limit: int, pages: int):
    """Background task worker untuk sinkronisasi tanpa memblokir request HTTP."""
    db = SessionLocal()
    try:
        cms_sync_service.sync_articles(
            db=db,
            portal_id=portal_id,
            force_full_sync=force_full,
            limit_per_page=limit,
            max_pages=pages
        )
    finally:
        db.close()


@router.get("/health")
def cms_health_check():
    """
    Menguji koneksi HMAC-SHA256 ke Inova CMS Open API (Grup Indosatu).
    """
    client = InovaCMSClient()
    if not client.is_configured:
        return {
            "ok": False,
            "configured": False,
            "message": "Kredensial belum dikonfigurasi. Harap isi CMS_ACCESS_KEY dan CMS_SECRET di file .env."
        }

    try:
        res = client.health()
        return {
            "ok": True,
            "configured": True,
            "cms_response": res
        }
    except CMSClientError as e:
        return {
            "ok": False,
            "configured": True,
            "code": e.code,
            "message": str(e),
            "requestId": e.request_id,
            "status_code": e.status_code
        }


@router.get("/status", response_model=SyncStatusResponse)
def get_sync_status(
    portal_id: str = Query(..., description="UUID Portal"),
    db: Session = Depends(deps.get_db)
):
    """
    Mengecek status dan checkpoint sinkronisasi terakhir untuk portal.
    """
    checkpoint = db.query(CMSSyncCheckpoint).filter(
        CMSSyncCheckpoint.portal_id == portal_id
    ).first()

    if not checkpoint:
        return {
            "portal_id": portal_id,
            "sync_status": "idle",
            "total_synced_articles": 0,
            "last_synced_at": None,
            "last_checkpoint_timestamp": None,
            "last_error": None
        }

    return checkpoint


@router.post("/trigger")
def trigger_sync(
    payload: TriggerSyncRequest,
    background_tasks: BackgroundTasks,
    run_async: bool = Query(True, description="Jalankan di background task (rekomendasi)"),
    db: Session = Depends(deps.get_db)
):
    """
    Memicu proses sinkronisasi artikel dari Inova CMS Open API ke database Supabase.
    """
    client = InovaCMSClient()
    target_portal = payload.portal_id or client.portal_id
    if not target_portal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Portal ID harus disediakan via payload atau CMS_PORTAL_ID di environment."
        )

    if not client.is_configured:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kredensial CMS_ACCESS_KEY dan CMS_SECRET belum diisi di .env."
        )

    if run_async:
        background_tasks.add_task(
            run_background_sync,
            target_portal,
            payload.force_full_sync,
            payload.limit_per_page,
            payload.max_pages
        )
        return {
            "ok": True,
            "mode": "background",
            "message": f"Sinkronisasi artikel portal '{target_portal}' telah dimulai di background.",
            "portal_id": target_portal
        }
    else:
        result = cms_sync_service.sync_articles(
            db=db,
            portal_id=target_portal,
            force_full_sync=payload.force_full_sync,
            limit_per_page=payload.limit_per_page,
            max_pages=payload.max_pages
        )
        return result


@router.post("/extract")
def extract_article(payload: ExtractUrlRequest):
    """
    Mengekstrak judul, konten, dan cover berita dari URL eksternal via CMS Open API.
    """
    client = InovaCMSClient()
    if not client.is_configured:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kredensial CMS_ACCESS_KEY dan CMS_SECRET belum diisi di .env."
        )

    try:
        return client.extract_article(payload.url)
    except CMSClientError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.code}: {str(e)}"
        )
