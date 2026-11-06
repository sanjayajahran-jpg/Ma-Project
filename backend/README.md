# AutoDrive PRO — Automotive Backend API (FastAPI)

Backend REST API resmi untuk tema otomotif **AutoDrive PRO**, dibangun menggunakan **Python 3.10+** dan framework modern **FastAPI** dengan **SQLAlchemy ORM** dan **Pydantic v2**.

---

## 🌟 Fitur Utama

1. **Autentikasi Admin (JWT)**
   - Login menggunakan OAuth2 Password Bearer / JSON body.
   - Endpoint terproteksi untuk operasi CRUD data mobil, brand, dan harga BBM.

2. **Katalog Mobil & Brand (CRUD)**
   - List mobil dengan filter dinamis (`brand`, `engine`, `body`, `year`, `price`, `search`).
   - Detail spesifikasi lengkap mobil (`horsepower`, `torque`, `battery_kwh`, `range_km`, `dimensi`, dll).
   - Manajemen varian tipe & harga OTR per mobil.

3. **Komparasi Mobil (Side-by-Side Specs)**
   - Bandingkan 2–4 mobil sekaligus berdasarkan ID atau Slug.

4. **Kalkulator Biaya Energi (BBM vs Listrik SPKLU)**
   - Kalkulasi estimasi biaya bulanan dan tahunan.
   - Perbandingan penghematan mobil listrik (EV) vs bensin/diesel.

5. **Interactive Swagger Documentation**
   - OpenAPI Swagger UI interaktif di `http://localhost:8000/docs`.

---

## 🚀 Cara Menjalankan Backend

### 1. Masuk ke folder backend & Aktifkan Virtual Environment

**Windows (PowerShell / Command Prompt):**
```bash
cd backend
.\venv\Scripts\activate
```

### 2. Unified CLI Management (`manage.py`)
Gunakan script CLI terpadu `manage.py` untuk mengelola seluruh aspek backend:
```bash
python manage.py status        # Cek status koneksi SQLite, dataset, & spek
python manage.py run           # Jalankan server FastAPI (port 8000)
python manage.py seed          # Seed database dari data referensi
python manage.py audit         # Audit kelengkapan 184 model mobil & varian
python manage.py list-scripts  # Tampilkan daftar script pembantu di scripts/
```

### 3. Jalankan Server FastAPI Manual
```bash
python run.py
```
Server akan berjalan di `http://localhost:8000`.

---

## 📁 Struktur Script & Utilitas Terorganisasi (`backend/scripts/`)

Semua script pembantu ad-hoc (seperti scraper Google Drive, migrasi data, dan alat audit) kini dikelompokkan rapi ke dalam:
- `scripts/data_tools/`: Script migrasi data spesifikasi, CSV importer, dan batch updater.
- `scripts/diagnostics/`: Script inspeksi database, tes pembaca PDF, dan verifikasi parameter teknis.
- `scripts/drive_tools/`: Script otomatisasi download brosur APM dari Google Drive.
- `data/`: File dump referensi (`compiled_cars.json`, `all_parsed_cars.json`, dll).

---

## 📚 Akses Dokumentasi API (Swagger UI)

Buka browser dan kunjungi:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

Anda bisa langsung login dan menguji semua endpoint API secara visual!

---

## 🗄️ Konfigurasi Database (.env)

Default menggunakan **SQLite** (`autodrive.db`) agar bisa langsung dijalankan tanpa perlu setup database server:
```env
DATABASE_URL="sqlite:///./autodrive.db"
```

Jika ingin menggunakan **MySQL di Laragon / XAMPP**:
```env
DATABASE_URL="mysql+pymysql://root:@localhost:3306/autodrive?charset=utf8mb4"
```

---

## 📡 Daftar Endpoint API (Ringkasan)

| Method | Endpoint | Deskripsi | Akses |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Login admin & dapatkan token JWT | Publik |
| `POST` | `/api/v1/auth/register` | Daftarkan user baru | Publik |
| `GET` | `/api/v1/auth/me` | Profil admin yang sedang login | Bearer Token |
| `GET` | `/api/v1/brands` | Daftar merek mobil (`?with_count=true`) | Publik |
| `POST` | `/api/v1/brands` | Tambah merek mobil baru | Admin |
| `GET` | `/api/v1/cars` | Katalog mobil + filter + pagination | Publik |
| `GET` | `/api/v1/cars/{id_or_slug}` | Detail spesifikasi mobil lengkap | Publik |
| `POST` | `/api/v1/cars` | Tambah mobil + spesifikasi + varian | Admin |
| `PUT` | `/api/v1/cars/{id}` | Update data mobil | Admin |
| `DELETE` | `/api/v1/cars/{id}` | Hapus mobil | Admin |
| `POST` | `/api/v1/compare` | Komparasi spesifikasi 2–4 mobil | Publik |
| `GET` | `/api/v1/fuel-prices` | Daftar harga BBM & listrik terkini | Publik |
| `POST` | `/api/v1/calculator/fuel-cost` | Kalkulasi biaya BBM vs SPKLU | Publik |
