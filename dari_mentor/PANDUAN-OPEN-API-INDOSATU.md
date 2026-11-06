# Panduan Open API — Grup Indosatu

Grup ini menaungi portal: sewaktu.id, narasi.biz.id, pojokbogor.id, gamingnews.id, pojoksulsel.id,
insight.pojoksatu.id, esensico.com, sentul24jam.com, naranta.id, jabar.pojoksatu.id,
pepo.id, dipojokin.id, infosentulcity.id, kutaudayawangsa.id, dan portal Indosatu lainnya.

Dokumen ini untuk developer yang ingin menghubungkan **sistem sendiri** (website
custom, aplikasi mobile backend, CMS lain, data pipeline) ke CMS — tanpa memakai
plugin WordPress. Plugin WordPress *Inova CMS Sync* memakai API yang sama persis;
semua yang bisa dilakukan plugin bisa dilakukan sistem Anda lewat API ini.

File pendamping:

| File | Isi |
| --- | --- |
| `inova-cms-openapi-indosatu.postman_collection.json` | Koleksi Postman siap pakai — signature HMAC dihitung otomatis |

---

## 1. Ringkasan

| Hal | Nilai |
| --- | --- |
| Protokol | HTTPS, JSON (UTF-8) |
| Prefix path | `/openapi/v1` |
| Autentikasi | HMAC-SHA256 per request (access key + secret) |
| Pemanggilan | **Server-to-server saja** — tidak ada CORS, jangan panggil dari browser |
| Timeout server | 60 detik per request |
| Gaya penamaan | Query parameter **snake_case** (`portal_id`), field JSON response **camelCase** (`portalId`) |

### Base URL

```
https://api-cms.bukin.id/openapi/v1
```

Contoh URL lengkap: `https://api-cms.bukin.id/openapi/v1/health`.

---

## 2. Mendapatkan kredensial

Kredensial dibuat oleh admin CMS lewat **Superadmin → Portals → Edit Portal →
tab Integrasi → Buat Key Baru**. Anda akan menerima:

| Kredensial | Format | Keterangan |
| --- | --- | --- |
| Access Key | `oak_` + 32 hex | Dikirim di setiap request (header) |
| Secret | `osk_` + 48 hex | **Rahasia.** Hanya dipakai untuk menghitung signature, tidak pernah dikirim. Ditampilkan sekali saja saat dibuat |
| Portal ID | UUID | Portal tempat key terikat |

Simpan secret di server (environment variable / secret manager), jangan di
kode front-end atau repository.

### Scope

Setiap key hanya bisa memanggil endpoint sesuai scope yang diberikan. Minta
admin CMS mengaktifkan scope yang Anda butuhkan saja:

| Scope | Membuka endpoint |
| --- | --- |
| `media:read` | `GET /portals`, `GET /media`, `GET /media/{id}` |
| `media:content` | `GET /media/{id}/content` |
| `articles:read` | `GET /articles`, `GET /articles/{id}`, `POST /articles/extract` |
| `agents:read` | `GET /agents` |
| `ai:generate` | `POST /ai/articles/generate`, `GET /ai/generate-jobs/{id}` |
| `credits:read` | `GET /credits` |
| `credits:topup` | `GET /billing/payment-methods`, `POST /billing/topup` |

`GET /health` bisa dipanggil dengan scope apa pun.

### Cakupan data

Access key terikat ke **satu portal**, tetapi **artikel dan media** di-scope ke
level **perusahaan media** (media company) pemilik portal itu. Artinya
`GET /articles` dan `GET /media` tanpa filter mengembalikan data dari **semua
portal** dalam perusahaan yang sama.

> Jika sistem Anda hanya untuk satu portal, **selalu kirim `portal_id`** di
> `GET /articles` dan `GET /media`. Tanpa filter itu, artikel portal lain dalam
> grup yang sama ikut terambil.

Agen AI, kredit, job AI, dan top-up selalu milik portal tempat key terikat.

---

## 3. Autentikasi (HMAC signing)

Setiap request wajib membawa 5 header:

| Header | Isi |
| --- | --- |
| `X-AIV-Access-Key` | Access key (`oak_...`) |
| `X-AIV-Timestamp` | Waktu UTC RFC3339 **tanpa milidetik**, mis. `2026-10-16T08:30:00Z` |
| `X-AIV-Nonce` | String unik per request — pakai UUID v4 |
| `X-AIV-Content-SHA256` | Hex SHA-256 dari body request persis seperti dikirim. Tanpa body (GET) = SHA-256 string kosong: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `X-AIV-Signature` | Hex `HMAC-SHA256(key = secret, message = canonical string)` |

Untuk request ber-body (POST) tambahkan `Content-Type: application/json`.

### Canonical string

Enam baris digabung dengan `\n` (LF, tanpa newline di akhir):

```
METHOD
PATH
CANONICAL_QUERY
TIMESTAMP
NONCE
CONTENT_SHA256
```

| Baris | Aturan |
| --- | --- |
| `METHOD` | Huruf besar: `GET`, `POST` |
| `PATH` | Path **lengkap** termasuk prefix, mis. `/openapi/v1/articles`. Tanpa domain, tanpa `?query` |
| `CANONICAL_QUERY` | Lihat di bawah. String kosong bila tidak ada query |
| `TIMESTAMP`, `NONCE`, `CONTENT_SHA256` | Sama persis dengan nilai header |

**Canonical query** — server mendekode query string, lalu menyusunnya ulang:

1. Urutkan pasangan `key=value` berdasarkan **key**, lalu berdasarkan **value**
   (perbandingan byte, case-sensitive).
2. Encode key dan value dengan aturan `application/x-www-form-urlencoded`:
   - `A–Z a–z 0–9` dan `* - . _` tidak diubah
   - spasi menjadi `+`
   - byte lain (UTF-8) menjadi `%XX` dengan hex **huruf besar** (`~` → `%7E`)
3. Gabungkan dengan `&`.

Contoh: query `?query=bank jateng&limit=5&portal_id=abc` →
canonical `limit=5&portal_id=abc&query=bank+jateng`.

Di JavaScript, `new URLSearchParams(pasanganTerurut).toString()` menghasilkan
encoding yang tepat. Di bahasa lain, pakai fungsi encode di contoh kode bagian 6
— `urlencode`/`quote_plus` bawaan PHP/Python **berbeda** untuk karakter `*` dan
`~`.

> Yang ditandatangani adalah hasil susunan ulang, bukan urutan query di URL.
> Query di URL boleh dalam urutan apa pun, asal isinya sama.

### Contoh canonical string

`GET https://api-cms.bukin.id/openapi/v1/articles?limit=5&portal_id=3840d668-69ba-4e0f-b54c-7157b3bbbefb`

```
GET
/openapi/v1/articles
limit=5&portal_id=3840d668-69ba-4e0f-b54c-7157b3bbbefb
2026-10-16T08:30:00Z
6f1c2a8e-5b7d-4e2a-9c1f-0d3b8a7e6c55
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### Aturan verifikasi server

- Timestamp harus dalam **±5 menit** dari jam server → pastikan jam server
  Anda tersinkron NTP.
- Nonce **tidak boleh dipakai ulang** dalam 15 menit untuk access key yang
  sama. Retry = nonce baru + signature baru.
- Hash body dihitung dari **byte yang benar-benar dikirim**. Serialisasi JSON
  sekali, hash string itu, kirim string yang sama.

---

## 4. Endpoint

Semua contoh di bawah relatif terhadap base URL (`.../openapi/v1`). Setiap
response sukses maupun error menyertakan `requestId` — sertakan nilai ini saat
melapor masalah ke tim CMS.

### 4.1 Health — `GET /health`

Cek koneksi dan validitas kredensial. Panggil ini pertama kali saat setup.

```json
{
  "ok": true,
  "service": "insight-cms",
  "site": { "id": "3840d668-69ba-4e0f-b54c-7157b3bbbefb", "name": "Sewaktu" },
  "scopes": ["articles:read", "media:read"],
  "requestId": "req_c7a3714f46084a09b6517684e7c6a09c"
}
```

### 4.2 Daftar portal — `GET /portals`

Scope `media:read`. Semua portal aktif dalam perusahaan media yang sama.

```json
{
  "items": [
    { "id": "3840d668-...", "name": "Sewaktu", "slug": "sewaktu", "domain": "sewaktu.id" }
  ],
  "requestId": "req_..."
}
```

### 4.3 Daftar artikel — `GET /articles`

Scope `articles:read`. Hanya artikel berstatus **published**.

| Parameter | Tipe | Default | Keterangan |
| --- | --- | --- | --- |
| `portal_id` | UUID | — | Filter satu portal. **Sangat disarankan** (lihat Cakupan data) |
| `query` | string | — | Cari di judul dan isi (substring, tidak peka huruf besar/kecil) |
| `limit` | int | 10 | 1–100 |
| `cursor` | string | — | `page.nextCursor` dari response sebelumnya |
| `order_by` | string | `published_at` | `updated_at` untuk urut berdasarkan waktu update |
| `updated_after` | RFC3339 | — | Hanya artikel dengan `updatedAt >=` nilai ini |
| `include` | string | — | `contentHtml` untuk ikut mengirim isi HTML lengkap |

Urutan selalu terbaru dulu. Response:

```json
{
  "items": [
    {
      "id": "9b0c...",
      "title": "Judul Artikel",
      "excerpt": "Ringkasan singkat...",
      "content": "Isi artikel versi teks polos (maks. 12.000 karakter)...",
      "contentHtml": "<p>Isi lengkap HTML...</p>",
      "url": "https://sewaktu.id/ekonomi/judul-artikel",
      "category": { "slug": "ekonomi", "name": "Ekonomi" },
      "author": { "name": "Tim Redaksi" },
      "portal": { "id": "3840d668-...", "name": "Sewaktu", "slug": "sewaktu", "domain": "sewaktu.id" },
      "featuredMedia": {
        "id": "67d9...", "fileName": "cover.jpg", "mimeType": "image/jpeg", "size": 184233,
        "width": 1200, "height": 675, "alt": "Keterangan gambar", "caption": null,
        "url": "https://cdn.../cover.jpg",
        "createdAt": "2026-10-15T03:00:00+00:00", "updatedAt": "2026-10-15T03:00:00+00:00"
      },
      "tags": [ { "id": "…", "slug": "bank-jateng", "name": "Bank Jateng" } ],
      "publishedAt": "2026-10-15T03:10:00+00:00",
      "updatedAt": "2026-10-15T04:22:11+00:00"
    }
  ],
  "page": { "nextCursor": "MTc2MDQ5...", "hasMore": true },
  "requestId": "req_..."
}
```

Catatan field:

- `contentHtml` hanya ada bila `include=contentHtml`. `content` (teks polos,
  terpotong 12.000 karakter) selalu ada — pakai `contentHtml` untuk
  menampilkan artikel utuh.
- `author`, `featuredMedia`, `featuredMedia.alt/caption/width/height`,
  `publishedAt` bisa `null`.

### 4.4 Detail artikel — `GET /articles/{articleId}`

Scope `articles:read`. Parameter opsional `include=contentHtml`. Bentuk
response = satu item dari daftar artikel (tanpa `page`/`requestId`).

Endpoint ini **tidak** memfilter status published — dipakai juga untuk
mengambil hasil AI generate yang masih draft (lihat 4.9). Error `404
ARTICLE_NOT_FOUND` bila ID tidak ada atau milik perusahaan lain.

### 4.5 Ekstrak artikel dari URL — `POST /articles/extract`

Scope `articles:read`. Mengambil judul, isi, dan gambar utama dari halaman berita
publik. Rate limit **10 request/menit per access key**.

```json
{ "url": "https://contoh-media.com/berita/judul-berita" }
```

Response:

```json
{
  "title": "Judul Berita",
  "content": "Isi berita teks polos (maks. 12.000 karakter)...",
  "imageUrl": "https://contoh-media.com/img/cover.jpg",
  "sourceUrl": "https://contoh-media.com/berita/judul-berita",
  "author": null,
  "publishedAt": null,
  "requestId": "req_..."
}
```

Error khusus: `400 BLOCKED_URL` (alamat internal/privat), `502
EXTRACTION_FAILED` (halaman tidak bisa diambil/diurai), `429 RATE_LIMITED`.

### 4.6 Daftar media — `GET /media`

Scope `media:read`. Hanya gambar `image/jpeg`, `image/png`, `image/webp`.

| Parameter | Tipe | Default | Keterangan |
| --- | --- | --- | --- |
| `portal_id` | UUID | — | Filter satu portal |
| `query` | string | — | Cari di nama file, alt, caption (substring) |
| `limit` | int | 30 | 1–100 |
| `cursor` | string | — | `page.nextCursor` dari response sebelumnya |
| `mime_type` | string | — | `image/jpeg`, `image/png`, atau `image/webp` |
| `updated_after` | RFC3339 | — | Hanya media yang **dibuat** sejak waktu ini (edit alt/caption tidak terhitung) |

```json
{
  "items": [
    {
      "id": "67d95171-e6e7-4a01-8926-5c7f632e3119",
      "fileName": "d98fd93a8b7ce6b32fe011cb0e8580dd.jpeg",
      "mimeType": "image/jpeg",
      "size": 184233,
      "width": 1200,
      "height": 675,
      "alt": "Ilustrasi rapat Bawaslu",
      "caption": null,
      "credit": null,
      "article": null,
      "portal": { "id": "cf503552-...", "name": "Sewaktu", "slug": "sewaktu" },
      "createdAt": "2026-07-16T22:55:11.004335+00:00",
      "updatedAt": "2026-07-16T22:55:11.004335+00:00"
    }
  ],
  "page": { "nextCursor": null, "hasMore": false },
  "requestId": "req_..."
}
```

`portal` bisa `null` untuk media lama. Response media tidak berisi URL file —
ambil file lewat endpoint berikut.

### 4.7 Detail media — `GET /media/{mediaId}`

Scope `media:read`. Response = satu item media. `404 MEDIA_NOT_FOUND` bila
tidak ada.

### 4.8 File media — `GET /media/{mediaId}/content`

Scope `media:content`. Response `302 Found` dengan header `Location` ke URL file
di CDN. Ikuti redirect untuk mengunduh. **Jangan simpan URL redirect secara
permanen** — simpan `mediaId`, lalu unduh/salin file ke storage Anda sendiri bila
perlu dipakai jangka panjang.

> Signature dihitung untuk request ke `/openapi/v1/media/{id}/content`. Request
> ke URL CDN tujuan redirect tidak perlu (dan tidak boleh) membawa header
> `X-AIV-*`.

### 4.9 AI Writer

Membuat artikel dengan agen AI yang dikonfigurasi di CMS. Prosesnya
**asinkron**: kirim permintaan → dapat `jobId` → polling status → ambil artikel.

#### Daftar agen — `GET /agents` (scope `agents:read`)

```json
{
  "items": [
    { "id": "a1b2...", "name": "Redaktur Ekonomi", "model": "…", "providerLabel": "…", "isDefault": true }
  ],
  "requestId": "req_..."
}
```

#### Saldo kredit — `GET /credits` (scope `credits:read`)

```json
{ "balance": 250000, "currency": "IDR", "requestId": "req_..." }
```

#### Buat artikel — `POST /ai/articles/generate` (scope `ai:generate`)

Field body memakai **snake_case**:

| Field | Wajib | Keterangan |
| --- | --- | --- |
| `title` | ya | Judul / topik artikel |
| `agent_id` | — | UUID dari `GET /agents`. Kosong = agen default portal |
| `angle` | — | Sudut pandang |
| `keywords` | — | Kata kunci, dipisah koma |
| `tone` | — | Gaya bahasa |
| `content_type` | — | Jenis konten |
| `instructions` | — | Instruksi tambahan untuk AI |
| `source_url` | — | URL sumber rujukan |
| `source_content` | — | Teks sumber rujukan (mis. hasil `POST /articles/extract`) |

```json
{
  "title": "Bank Jateng salurkan KUR Rp 2 triliun",
  "keywords": "bank jateng, kur, umkm",
  "instructions": "Tulis 600 kata, sertakan konteks penyaluran tahun lalu."
}
```

Response `200`:

```json
{ "jobId": "5e7f...", "articleId": "9c1d...", "status": "queued", "requestId": "req_..." }
```

`402 INSUFFICIENT_CREDITS` bila saldo habis. Setiap generate memotong saldo
kredit portal.

#### Status job — `GET /ai/generate-jobs/{jobId}` (scope `ai:generate`)

```json
{
  "id": "5e7f...",
  "status": "running",
  "articleId": "9c1d...",
  "errorMessage": null,
  "agentName": "Redaktur Ekonomi",
  "createdAt": "2026-10-16T08:30:01+00:00",
  "completedAt": null,
  "requestId": "req_..."
}
```

`status`: `queued` → `running` → `succeeded` atau `failed` (lihat
`errorMessage`). Polling tiap 3–5 detik; umumnya selesai dalam 5–60 detik
tergantung antrean. Hentikan polling setelah ±5 menit.

#### Ambil hasil

Setelah `succeeded`, panggil `GET /articles/{articleId}?include=contentHtml`.
Artikel hasil AI tersimpan di CMS sebagai **draft** — tidak tampil di
`GET /articles` dan tidak terbit di portal sampai diterbitkan editor.

### 4.10 Top-up kredit (scope `credits:topup`)

#### Metode pembayaran — `GET /billing/payment-methods?amount=100000`

`amount` minimal 10.000 (default 100.000), dipakai untuk menghitung biaya.

```json
{
  "items": [
    { "paymentMethod": "BC", "paymentName": "BCA Virtual Account", "paymentImage": "https://…", "totalFee": 4000 }
  ],
  "requestId": "req_..."
}
```

#### Buat tagihan — `POST /billing/topup`

Field body memakai **camelCase**:

```json
{ "amount": 100000, "paymentMethod": "BC", "customerEmail": "finance@contoh.com" }
```

Response:

```json
{ "topupId": "…", "orderId": "TOP-ISM-1760603400000", "paymentUrl": "https://…", "status": "pending", "requestId": "req_..." }
```

Arahkan pengguna ke `paymentUrl`. Saldo bertambah otomatis setelah pembayaran
terkonfirmasi; cek lewat `GET /credits`.

Riwayat transaksi dan invoice bisa dilihat di halaman Billing CMS:
https://editor.indosatumedia.com/billing

---

## 5. Pagination & sinkronisasi

List `GET /articles` dan `GET /media` memakai **cursor**:

```
page.hasMore == true  →  kirim ulang request yang sama + cursor=page.nextCursor
page.hasMore == false →  selesai
```

Cursor bersifat opaque — kirim apa adanya, jangan diurai. Saat paginasi, kirim
parameter lain (`portal_id`, `order_by`, dst.) tetap sama.

**Pola sinkronisasi artikel berkala** (yang dipakai plugin WordPress):

1. Request `GET /articles?portal_id=…&order_by=updated_at&updated_after=<checkpoint>&include=contentHtml&limit=50`.
2. Habiskan semua halaman lewat cursor.
3. Upsert ke database Anda dengan kunci `id` (artikel bisa muncul lagi bila
   diedit — perlakukan sebagai update, bukan artikel baru).
4. Simpan `updatedAt` terbesar yang diterima sebagai `<checkpoint>` berikutnya.
5. Ulangi tiap 5–15 menit. Hindari interval < 1 menit.

Karena `updated_after` inklusif (`>=`), artikel terakhir akan terambil lagi di
putaran berikutnya — upsert berdasarkan `id` membuatnya aman.

---

## 6. Contoh kode

Semua contoh memakai env var `CMS_BASE_URL` (mis. `https://api-cms.bukin.id/openapi/v1`),
`CMS_ACCESS_KEY`, `CMS_SECRET`.

### Node.js (18+)

```js
import crypto from 'node:crypto';

const BASE = process.env.CMS_BASE_URL;          // https://api-cms.bukin.id/openapi/v1
const ACCESS_KEY = process.env.CMS_ACCESS_KEY;
const SECRET = process.env.CMS_SECRET;

export async function cms(method, path, { query = {}, body } = {}) {
  const url = new URL(BASE + path);
  const pairs = Object.entries(query)
    .filter(([, v]) => v !== undefined && v !== null)
    .map(([k, v]) => [k, String(v)])
    .sort((a, b) => (a[0] === b[0] ? (a[1] < b[1] ? -1 : 1) : a[0] < b[0] ? -1 : 1));
  const canonicalQuery = new URLSearchParams(pairs).toString();

  const bodyStr = body === undefined ? '' : JSON.stringify(body);
  const contentSha = crypto.createHash('sha256').update(bodyStr).digest('hex');
  const timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  const nonce = crypto.randomUUID();

  const canonical = [method, url.pathname, canonicalQuery, timestamp, nonce, contentSha].join('\n');
  const signature = crypto.createHmac('sha256', SECRET).update(canonical).digest('hex');

  const res = await fetch(url.href + (canonicalQuery ? '?' + canonicalQuery : ''), {
    method,
    headers: {
      'X-AIV-Access-Key': ACCESS_KEY,
      'X-AIV-Timestamp': timestamp,
      'X-AIV-Nonce': nonce,
      'X-AIV-Content-SHA256': contentSha,
      'X-AIV-Signature': signature,
      Accept: 'application/json',
      ...(bodyStr ? { 'Content-Type': 'application/json' } : {}),
    },
    body: bodyStr || undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(`${data.error?.code}: ${data.error?.message} (${data.requestId})`);
  return data;
}

// Contoh
console.log(await cms('GET', '/health'));
const { items } = await cms('GET', '/articles', {
  query: { portal_id: process.env.CMS_PORTAL_ID, limit: 5, include: 'contentHtml' },
});
```

### Python 3 (requests)

```python
import hashlib, hmac, json, os, uuid
from datetime import datetime, timezone
from urllib.parse import urlsplit
import requests

BASE = os.environ["CMS_BASE_URL"]          # https://api-cms.bukin.id/openapi/v1
ACCESS_KEY = os.environ["CMS_ACCESS_KEY"]
SECRET = os.environ["CMS_SECRET"].encode()

_SAFE = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789*-._")

def form_encode(s: str) -> str:
    out = []
    for b in s.encode("utf-8"):
        if b in _SAFE:
            out.append(chr(b))
        elif b == 0x20:
            out.append("+")
        else:
            out.append("%%%02X" % b)
    return "".join(out)

def cms(method, path, query=None, body=None):
    pairs = sorted((str(k), str(v)) for k, v in (query or {}).items() if v is not None)
    canonical_query = "&".join(f"{form_encode(k)}={form_encode(v)}" for k, v in pairs)

    body_str = "" if body is None else json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    body_bytes = body_str.encode("utf-8")
    content_sha = hashlib.sha256(body_bytes).hexdigest()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    nonce = str(uuid.uuid4())

    url = BASE + path
    canonical = "\n".join([method, urlsplit(url).path, canonical_query, timestamp, nonce, content_sha])
    signature = hmac.new(SECRET, canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    headers = {
        "X-AIV-Access-Key": ACCESS_KEY,
        "X-AIV-Timestamp": timestamp,
        "X-AIV-Nonce": nonce,
        "X-AIV-Content-SHA256": content_sha,
        "X-AIV-Signature": signature,
        "Accept": "application/json",
    }
    if body_bytes:
        headers["Content-Type"] = "application/json"
    if canonical_query:
        url += "?" + canonical_query
    res = requests.request(method, url, headers=headers, data=body_bytes or None, timeout=60)
    data = res.json()
    if not res.ok:
        raise RuntimeError(f"{data['error']['code']}: {data['error']['message']} ({data['requestId']})")
    return data

print(cms("GET", "/health"))
```

### PHP 7.4+ (cURL)

```php
<?php
function cms_form_encode(string $s): string {
    // urlencode() menyandikan '*' sebagai %2A; server membiarkan '*'.
    return str_replace('%2A', '*', urlencode($s));
}

function cms(string $method, string $path, array $query = [], ?array $body = null): array {
    $base = getenv('CMS_BASE_URL');           // https://api-cms.bukin.id/openapi/v1
    $secret = getenv('CMS_SECRET');

    $pairs = [];
    foreach ($query as $k => $v) {
        if ($v !== null) $pairs[] = [(string) $k, (string) $v];
    }
    usort($pairs, fn($a, $b) => $a[0] === $b[0] ? strcmp($a[1], $b[1]) : strcmp($a[0], $b[0]));
    $canonicalQuery = implode('&', array_map(
        fn($p) => cms_form_encode($p[0]) . '=' . cms_form_encode($p[1]), $pairs));

    $bodyStr = $body === null ? '' : json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    $contentSha = hash('sha256', $bodyStr);
    $timestamp = gmdate('Y-m-d\TH:i:s\Z');
    $nonce = bin2hex(random_bytes(16));

    $url = $base . $path;
    $canonical = implode("\n", [$method, parse_url($url, PHP_URL_PATH), $canonicalQuery, $timestamp, $nonce, $contentSha]);
    $signature = hash_hmac('sha256', $canonical, $secret);

    $headers = [
        'X-AIV-Access-Key: ' . getenv('CMS_ACCESS_KEY'),
        'X-AIV-Timestamp: ' . $timestamp,
        'X-AIV-Nonce: ' . $nonce,
        'X-AIV-Content-SHA256: ' . $contentSha,
        'X-AIV-Signature: ' . $signature,
        'Accept: application/json',
    ];
    if ($bodyStr !== '') $headers[] = 'Content-Type: application/json';

    $ch = curl_init($url . ($canonicalQuery !== '' ? '?' . $canonicalQuery : ''));
    curl_setopt_array($ch, [
        CURLOPT_CUSTOMREQUEST => $method,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 60,
    ]);
    if ($bodyStr !== '') curl_setopt($ch, CURLOPT_POSTFIELDS, $bodyStr);
    $raw = curl_exec($ch);
    $status = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);

    $data = json_decode($raw, true);
    if ($status >= 400) {
        throw new RuntimeException("{$data['error']['code']}: {$data['error']['message']} ({$data['requestId']})");
    }
    return $data;
}

print_r(cms('GET', '/health'));
```

### Bash (curl + openssl)

```bash
#!/usr/bin/env bash
set -euo pipefail
BASE="https://api-cms.bukin.id"            # tanpa /openapi/v1
PATHNAME="/openapi/v1/articles"
QUERY="limit=5&portal_id=${CMS_PORTAL_ID}"   # sudah terurut & ter-encode

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
NONCE=$(uuidgen | tr 'A-Z' 'a-z')
CONTENT_SHA=$(printf '' | openssl dgst -sha256 -hex | awk '{print $NF}')

SIGNATURE=$(printf '%s\n%s\n%s\n%s\n%s\n%s' \
  GET "$PATHNAME" "$QUERY" "$TIMESTAMP" "$NONCE" "$CONTENT_SHA" \
  | openssl dgst -sha256 -hmac "$CMS_SECRET" -hex | awk '{print $NF}')

curl -s "${BASE}${PATHNAME}?${QUERY}" \
  -H "X-AIV-Access-Key: ${CMS_ACCESS_KEY}" \
  -H "X-AIV-Timestamp: ${TIMESTAMP}" \
  -H "X-AIV-Nonce: ${NONCE}" \
  -H "X-AIV-Content-SHA256: ${CONTENT_SHA}" \
  -H "X-AIV-Signature: ${SIGNATURE}"
```

---

## 7. Memakai koleksi Postman

1. Postman → **Import** → pilih `inova-cms-openapi-indosatu.postman_collection.json`.
2. Buka koleksi → tab **Variables**, isi:

   | Variable | Contoh |
   | --- | --- |
   | `base_url` | `https://api-cms.bukin.id/openapi/v1` |
   | `access_key` | `oak_...` |
   | `secret` | `osk_...` |
   | `portal_id` | UUID portal Anda |

3. Jalankan **Health** dulu. Pre-request script koleksi menghitung timestamp,
   nonce, hash body, dan signature otomatis untuk setiap request.
4. Request yang butuh ID (`article_id`, `media_id`, `job_id`) memakai variabel
   koleksi. Request **List Articles**, **List Media**, dan **AI Generate**
   mengisi variabel itu otomatis dari response, jadi bisa dijalankan berurutan.

Jangan bagikan koleksi yang sudah berisi `secret` — kosongkan nilainya sebelum
export, atau simpan secret di Postman Environment dengan tipe *secret*.

---

## 8. Error

Format semua error:

```json
{ "error": { "code": "INVALID_SIGNATURE", "message": "Signature does not match" }, "requestId": "req_..." }
```

| HTTP | Code | Penyebab | Yang perlu dicek |
| --- | --- | --- | --- |
| 400 | `INVALID_REQUEST` / `VALIDATION_ERROR` / `INVALID_BODY` | Body/parameter tidak valid | JSON body, field wajib |
| 400 | `BLOCKED_URL` | URL extract mengarah ke alamat internal | Pakai URL publik |
| 401 | `INVALID_ACCESS_KEY` | Key tidak dikenal, nonaktif, dicabut, atau kedaluwarsa | Hubungi admin CMS |
| 401 | `INVALID_SIGNATURE` | Header hilang atau signature tidak cocok | Lihat daftar di bawah |
| 401 | `STALE_REQUEST` | Timestamp di luar ±5 menit atau format salah | Sinkronkan jam (NTP), format tanpa milidetik |
| 402 | `INSUFFICIENT_CREDITS` | Saldo kredit AI habis | Top-up |
| 403 | `INSUFFICIENT_SCOPE` | Key tidak punya scope endpoint ini | Minta scope ke admin CMS |
| 404 | `ARTICLE_NOT_FOUND` / `MEDIA_NOT_FOUND` / `NOT_FOUND` | ID tidak ada atau bukan milik Anda | |
| 409 | `NONCE_REPLAYED` | Nonce sudah dipakai | Nonce baru tiap request, termasuk retry |
| 429 | `RATE_LIMITED` | > 10 extract/menit | Tunggu, lalu ulangi |
| 502 | `EXTRACTION_FAILED` / `PAYMENT_METHODS_FAILED` / `TOPUP_FAILED` | Layanan pihak ketiga gagal | Ulangi beberapa saat lagi |
| 503 | `BILLING_NOT_CONFIGURED` | Billing belum aktif di grup ini | Hubungi admin CMS |
| 500 | `INTERNAL_ERROR` | Kesalahan server | Laporkan dengan `requestId` |

**Debug `INVALID_SIGNATURE`** — penyebab yang paling sering:

1. `PATH` tanpa prefix `/openapi/v1`.
2. Query di canonical tidak diurutkan, atau encoding beda (spasi harus `+`,
   bukan `%20`).
3. Body yang di-hash berbeda dari body yang dikirim (JSON diserialisasi dua kali,
   atau library HTTP menambah/mengubah spasi).
4. Ada newline di akhir canonical string, atau memakai `\r\n`.
5. HMAC memakai access key, bukan secret — atau secret tersalin dengan spasi.
6. Signature dikirim dalam base64; harus hex huruf kecil/besar.

Cara cepat: cetak canonical string Anda dan bandingkan baris per baris dengan
aturan di bagian 3.
