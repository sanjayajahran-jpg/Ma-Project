import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

_SAFE_URL_CHARS = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789*-._")


def form_encode(s: str) -> str:
    """
    Encoding form-urlencoded sesuai spesifikasi HMAC Inova CMS Open API:
    - Byte A-Z, a-z, 0-9, *, -, ., _ dibiarkan
    - Spasi (0x20) menjadi '+'
    - Byte lain menjadi %XX uppercase
    """
    out = []
    for b in str(s).encode("utf-8"):
        if b in _SAFE_URL_CHARS:
            out.append(chr(b))
        elif b == 0x20:
            out.append("+")
        else:
            out.append("%%%02X" % b)
    return "".join(out)


class CMSClientError(Exception):
    def __init__(self, message: str, code: Optional[str] = None, request_id: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.code = code
        self.request_id = request_id
        self.status_code = status_code


class InovaCMSClient:
    """
    Client resmi untuk Inova CMS Open API (Grup Indosatu).
    Mengimplementasikan autentikasi HMAC-SHA256 sesuai PANDUAN-OPEN-API-INDOSATU.md.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret: Optional[str] = None,
        portal_id: Optional[str] = None,
        timeout: int = 45
    ):
        raw_base = (base_url or settings.CMS_BASE_URL or "https://api-cms.bukin.id/openapi/v1").rstrip("/")
        if not raw_base.endswith("/openapi/v1"):
            if "/api/v" in raw_base:
                raw_base = raw_base.split("/api/v")[0] + "/openapi/v1"
            else:
                raw_base += "/openapi/v1"
        self.base_url = raw_base
        self.access_key = access_key or settings.CMS_ACCESS_KEY
        self.secret = secret or settings.CMS_SECRET
        self.portal_id = portal_id or settings.CMS_PORTAL_ID
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        """Mengecek apakah kredensial API sudah terisi di konfigurasi."""
        return bool(self.access_key and self.secret)

    def _build_canonical_query(self, query: Optional[Dict[str, Any]] = None) -> str:
        if not query:
            return ""
        pairs = sorted((str(k), str(v)) for k, v in query.items() if v is not None)
        return "&".join(f"{form_encode(k)}={form_encode(v)}" for k, v in pairs)

    def request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Kirim request berautentikasi HMAC-SHA256 ke Inova CMS Open API.
        """
        if not self.is_configured:
            raise CMSClientError(
                "Kredensial CMS_ACCESS_KEY dan CMS_SECRET belum dikonfigurasi di environment.",
                code="NOT_CONFIGURED"
            )

        clean_path = "/" + path.lstrip("/")
        full_url = self.base_url + clean_path
        parsed_url = urlsplit(full_url)
        signed_path = parsed_url.path  # Termasuk prefix /openapi/v1/...

        canonical_query = self._build_canonical_query(query)

        body_bytes = b""
        if method.upper() in ("POST", "PUT", "PATCH") and body is not None:
            body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
            body_bytes = body_str.encode("utf-8")

        content_sha = hashlib.sha256(body_bytes).hexdigest()
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        nonce = str(uuid.uuid4())

        canonical = "\n".join([
            method.upper(),
            signed_path,
            canonical_query,
            timestamp,
            nonce,
            content_sha
        ])

        signature = hmac.new(
            self.secret.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "X-AIV-Access-Key": self.access_key,
            "X-AIV-Timestamp": timestamp,
            "X-AIV-Nonce": nonce,
            "X-AIV-Content-SHA256": content_sha,
            "X-AIV-Signature": signature,
            "Accept": "application/json",
        }
        if body_bytes:
            headers["Content-Type"] = "application/json"

        target_url = full_url + ("?" + canonical_query if canonical_query else "")

        try:
            res = requests.request(
                method.upper(),
                target_url,
                headers=headers,
                data=body_bytes or None,
                timeout=self.timeout
            )
            data = res.json()
        except requests.RequestException as e:
            logger.error("Gagal melakukan HTTP request ke CMS: %s", str(e))
            raise CMSClientError(f"HTTP request error: {str(e)}", code="NETWORK_ERROR")
        except ValueError:
            logger.error("Respons dari CMS bukan JSON valid: %s", res.text[:200])
            raise CMSClientError("Respons CMS bukan format JSON yang valid", code="INVALID_JSON")

        if not res.ok:
            err_data = data.get("error", {})
            err_code = err_data.get("code", "UNKNOWN_ERROR")
            err_msg = err_data.get("message", res.text)
            req_id = data.get("requestId")
            raise CMSClientError(
                f"{err_code}: {err_msg} (Request ID: {req_id})",
                code=err_code,
                request_id=req_id,
                status_code=res.status_code
            )

        return data

    # -------------------------------------------------------------
    # Endpoint Helpers
    # -------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """Cek koneksi dan validitas kredensial (GET /health)."""
        return self.request("GET", "/health")

    def get_portals(self) -> List[Dict[str, Any]]:
        """Mengambil daftar semua portal di bawah grup media (GET /portals)."""
        res = self.request("GET", "/portals")
        return res.get("items", [])

    def get_articles(
        self,
        portal_id: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50,
        cursor: Optional[str] = None,
        order_by: str = "updated_at",
        updated_after: Optional[str] = None,
        include: str = "contentHtml"
    ) -> Dict[str, Any]:
        """
        Mengambil daftar artikel (published) dengan paginasi kursor (GET /articles).
        """
        target_portal = portal_id or self.portal_id
        q_params: Dict[str, Any] = {
            "limit": limit,
            "order_by": order_by,
        }
        if target_portal:
            q_params["portal_id"] = target_portal
        if query:
            q_params["query"] = query
        if cursor:
            q_params["cursor"] = cursor
        if updated_after:
            q_params["updated_after"] = updated_after
        if include:
            q_params["include"] = include

        return self.request("GET", "/articles", query=q_params)

    def get_article(self, article_id: str, include: str = "contentHtml") -> Dict[str, Any]:
        """Mengambil detail satu artikel lengkap (GET /articles/{id})."""
        q_params = {"include": include} if include else None
        return self.request("GET", f"/articles/{article_id}", query=q_params)

    def extract_article(self, source_url: str) -> Dict[str, Any]:
        """Ekstrak judul, isi, dan cover dari URL publik (POST /articles/extract)."""
        return self.request("POST", "/articles/extract", body={"url": source_url})

    def get_media(
        self,
        portal_id: Optional[str] = None,
        limit: int = 30,
        cursor: Optional[str] = None,
        mime_type: Optional[str] = None,
        updated_after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mengambil daftar gambar media (GET /media)."""
        target_portal = portal_id or self.portal_id
        q_params: Dict[str, Any] = {"limit": limit}
        if target_portal:
            q_params["portal_id"] = target_portal
        if cursor:
            q_params["cursor"] = cursor
        if mime_type:
            q_params["mime_type"] = mime_type
        if updated_after:
            q_params["updated_after"] = updated_after

        return self.request("GET", "/media", query=q_params)
