# Inova CMS Sync — WordPress Plugin

Plugin WordPress untuk sinkronisasi artikel dari Inova CMS + AI Writer.

## Struktur

```
inova-cms-sync/
├── inova-cms-sync.php          # Main file + plugin header
├── uninstall.php                 # Cleanup on uninstall
├── readme.txt                    # WordPress.org format
├── includes/
│   ├── class-ics-plugin.php      # Singleton bootstrap
│   ├── class-ics-client.php      # HMAC-signed HTTP client (GET + POST)
│   ├── class-ics-settings.php    # Settings store (wp_options)
│   ├── class-ics-importer.php    # F1: article sync CMS → WP
│   ├── class-ics-media.php       # F1: featured + inline image import
│   ├── class-ics-mapping.php     # Remote ID ↔ WP post ID mapping
│   ├── class-ics-cron.php        # WP-Cron scheduling
│   ├── class-ics-logger.php      # Log table CRUD
│   └── class-ics-activator.php   # DB tables + cron registration
├── admin/
│   ├── class-ics-admin.php       # Menu + settings + handlers
│   ├── views/
│   │   ├── settings.php          # Connection + sync config
│   │   ├── logs.php              # Sync/AI history
│   │   └── status.php            # Stats + manual sync
│   ├── css/ics-admin.css
│   └── js/ics-admin.js
└── languages/
```

## Status Implementasi

| Phase | Fitur | Status |
|---|---|---|
| 6 | Plugin skeleton | ✅ Done |
| 7 | Core (client, settings, activator, logger) | ✅ Done |
| 7 | HTTP client dengan HMAC signing | ✅ Done |
| 8 | F1: Importer (article sync) | ✅ Done |
| 8 | F1: Media (featured + inline) | ✅ Done |
| 8 | F1: Cron scheduling | ✅ Done |
| 14 | Admin UI (settings, logs, status) | ✅ Done |
| 1-5 | Open API improvements (backend) | ⬜ Pending |
| 9-13 | F2: AI Writer (editor integration) | ⬜ Pending |
| 18 | Auto-update plugin | ⬜ Pending |

## Auth Protocol

Lihat `docs/integrasi/aiv/aiv.md` untuk detail lengkap HMAC signing.

Header wajib:
- `X-AIV-Access-Key`: `oak_...`
- `X-AIV-Timestamp`: RFC3339 tanpa milliseconds
- `X-AIV-Nonce`: UUID v4
- `X-AIV-Content-SHA256`: SHA-256 hex dari body (GET = empty SHA)
- `X-AIV-Signature`: hex(HMAC-SHA256(secret, canonical))

## Konfigurasi

1. Buka **Inova CMS → Pengaturan** di wp-admin
2. Isi koneksi: API Base URL, Access Key, Secret, Portal ID
3. Tes koneksi
4. Set status post default, penulis, kategori
5. Aktifkan sinkronisasi + pilih interval
