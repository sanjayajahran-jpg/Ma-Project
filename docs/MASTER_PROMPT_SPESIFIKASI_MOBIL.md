# 📋 MASTER PROMPT RISET SPESIFIKASI MOBIL ELEKTRIFIKASI INDONESIA

Dokumen ini berisi 2 versi Master Prompt terstandarisasi untuk mengekstrak spesifikasi mobil elektrifikasi (BEV, PHEV, HEV) resmi APM Indonesia.

---

## ⚡ VERSI 1: MURNI KODE PYTHON (SINGLE-BLOCK — PALING CEPAT & LANGSUNG KE DATABASE)
> **Gunakan versi ini** jika Anda ingin AI langsung menghasilkan 1 blok kode Python dictionary terstruktur yang siap disalin langsung ke database tanpa teks bertele-tele.

```text
Anda adalah Automotive Database Engineer dan Technical Analyst spesialis data spesifikasi kendaraan elektrifikasi Indonesia (EV, PHEV, HEV).

TUGAS ANDA:
Ekstrak dan susun data spesifikasi resmi brosur APM Indonesia (harga OTR Jakarta) untuk mobil:
[MASUKKAN NAMA MOBIL DI SINI, contoh: Chery Tiggo 8 Pro e+ / Kia EV9 GT-Line / MG4 EV / Neta V-II / Denza D9 / BYD M6 / Hyundai Ioniq 5 / Honda CR-V e:HEV / Wuling Cloud EV / Geely EX2]

ATURAN WAJIB (STRICT RULES):
1. Output HANYA dalam 1 blok kode Python Dictionary terstruktur sesuai template di bawah ini tanpa teks pengantar atau penutup apapun di luar blok kode.
2. Semua nilai teknis wajib to-the-point, ringkas, dan akurat sesuai data resmi APM Indonesia.
3. Wajib mencantumkan SELURUH trim atau varian yang dijual resmi di Indonesia ke dalam list "variants". Jika mobil memiliki 2, 3, 4, atau lebih trim, buatkan objek kamus untuk SEMUA trim tersebut lengkap dengan 16 parameter pembeda.
4. Paket Home Wall Charger (termasuk gratis atau bayar, berapa kW, dan biaya instalasi) wajib dicantumkan.
5. Abaikan pencarian URL foto/gambar (fokus pada spesifikasi teknis).

FORMAT OUTPUT WAJIB:

```python
{
    # 1. IDENTITAS, PASAR DAN DAFTAR TRIM RESMI
    "slug": "nama-model-slug",                          # contoh: "geely-ex2"
    "name": "Nama Resmi Model Mobil",                  # contoh: "Geely EX2"
    "brand_name": "Merek",                             # contoh: "Geely"
    "engine_type_slug": "bev",                          # 'bev' / 'phev' / 'hev' / 'fcev'
    "body_type_slug": "hatchback",                      # 'suv' / 'mpv' / 'sedan' / 'hatchback' / 'crossover'
    "year": 2026,
    "price_start": 250000000,                          # Integer harga OTR terendah
    "price_end": 320000000,                            # Integer harga OTR tertinggi
    "available_trims": ["Trim 1 (Standard)", "Trim 2 (Long Range / Premium)"], # List semua trim resmi
    "tagline": "Slogan resmi singkat APM (1 kalimat padat)",
    "description": "Ringkasan posisi pasar mobil ini di Indonesia (maksimal 2 kalimat).",
    "image_url": None,                                 # Foto dicari manual
    "is_featured": True,

    # 2. SPESIFIKASI TEKNIS UMUM (BROSUR RESMI)
    "specs": {
        # Status Perakitan, Baterai dan V2L
        "assembly_status": "CKD (Rakit Lokal Indonesia - TKDN 40%)", # CKD / CBU
        "battery_type": "LFP (Lithium Iron Phosphate / Short Blade Battery)", # LFP / NMC / NiMH
        "battery_capacity_kwh": 39.4,                  # Kapasitas baterai kWh (float)
        "electric_range_km": 405,                      # Jarak tempuh EV murni km (integer)
        "v2l_support": "Ya, Daya 3300 Watt (3.3 kW) V2L Adapter", # Ya, Daya 3.3 kW / Tidak Didukung
        "energy_consumption": "11.8 kWh/100 km (8.5 km/kWh)", # Konsumsi energi baku ringkas

        # Powertrain dan Performa
        "engine_name": "Single Permanent Magnet Synchronous Motor",
        "engine_capacity_cc": None,                    # Integer cc (isi None jika BEV murni)
        "horsepower": 114,                             # Total kombinasi Horsepower (HP)
        "torque_nm": 150,                              # Total kombinasi Torsi (Nm)
        "transmission": "Single Reduction Gear",
        "drivetrain": "RWD",                           # FWD / RWD / AWD / 4WD
        "acceleration_0_100": 9.8,                     # Angka detik (float)
        "top_speed_kmh": 140,                          # Angka km/jam (integer)
        "fuel_consumption_kmpl": None,                 # Angka km/L jika hybrid, None jika BEV

        # Dimensi, Sasis dan Kapasitas
        "length_mm": 4135,                             # Panjang mm
        "width_mm": 1805,                              # Lebar mm
        "height_mm": 1570,                             # Tinggi mm
        "wheelbase_mm": 2650,                          # Sumbu roda mm
        "ground_clearance_mm": 165,                    # Ground clearance mm
        "curb_weight_kg": 1285,                        # Bobot kosong kg
        "seating_capacity": 5,                         # Jumlah kursi
        "trunk_volume_liters": 375,                    # Volume bagasi Liter
        "fuel_tank_liters": None,                      # Tangki BBM Liter (None jika BEV)

        # Kokpit, Layar dan Warna
        "cluster_display": "8.8 inch Full Digital TFT Meter Cluster + HUD",
        "colors_json": '["Crystal White", "Urban Gray", "Ocean Blue", "Aurora Green"]',

        # Keselamatan dan ADAS
        "airbags": 6,                                  # Jumlah airbags
        "abs_ebd": True,
        "esc": True,
        "adas": True,
        "adas_name": "Geely Smart Pilot Level 2",
        "adas_features_json": '["Adaptive Cruise Control (ACC) with Stop and Go", "Autonomous Emergency Braking (AEB)", "Lane Keeping Assist (LKA)", "Lane Following Assist (LFA)", "Blind Spot Detection (BSD)", "Rear Cross Traffic Alert (RCTA)", "Kamera 540 Panoramic View with Transparent Chassis", "High Beam Assist (HBA)"]',
        "safety_rating": 5.0,
        "comfort_rating": 4.7,
        "performance_rating": 4.5,
        "value_rating": 4.9,

        # Pajak, Garansi dan Paket Home Wall Charger
        "annual_tax_estimate": 0,                      # Estimasi PKB Jakarta (Rp, integer. BEV = 0)
        "warranty_vehicle": "5 Tahun / 150000 km",
        "warranty_battery": "8 Tahun / 160000 km (Garansi Seumur Hidup)",
        "wall_charger_info": "Termasuk Gratis 7 kW Wallbox + Gratis Jasa Pasang dan Tambah Daya PLN"
    },

    # 3. MATRIKS 16 PARAMETER LENGKAP SEMUA TRIM (BUAT OBJEK UNTUK SEMUA TRIM YANG ADA)
    "variants": [
        {
            "name": "Nama Trim 1 (Standard Range 300 km)",
            "price": 250000000,                        # Integer harga OTR
            "highlights": "Pembeda ringkas trim ini dalam 1 baris",
            "power_output": "94 HP / 130 Nm (Single Motor RWD)",
            "battery_range": "30.0 kWh LFP (Jarak 300 km NEDC)",
            "battery_type": "LFP Battery",
            "v2l_support": "Ya, 3.3 kW",
            "charging_time": "DC 50 kW (30 mnt 30-80%) / AC 6.6 kW",
            "wall_charger_info": "Termasuk Gratis Portable Charger 2.2 kW (Wallbox 7 kW Opsional Rp 8 Juta)",
            "wheel_spec": "15 inch Steel Wheels with Aero Cover (195/65 R15)",
            "interior_spec": "Fabric Seats + 6-Way Manual Driver Adjuster",
            "seating_layout": "5-Seater Standard Bench",
            "cluster_display": "5 inch TFT Digital Instrument Cluster",
            "audio_display": "10.1 inch Touchscreen + 4 Speakers",
            "tailgate_feature": "Manual Tailgate",
            "sunroof": "Standard Solid Roof",
            "telematics_feature": "Standard Bluetooth dan Wired CarPlay",
            "camera_vision": "Rear View Camera with Parking Sensors",
            "lighting_spec": "LED Reflector Headlamps Standar",
            "climate_air": "Single-Zone Auto Climate Control",
            "convenience_extras": "Standard USB Type-A Charging Ports",
            "styling_kit": "Standard Exterior Styling",
            "safety_adas": "Basic Safety (Dual Airbags, ABS, ESC, Rear Camera)",
            "annual_tax": 0,
            "gallery_json": None
        },
        {
            "name": "Nama Trim 2 (Long Range 405 km / Flagship)",
            "price": 320000000,                        # Integer harga OTR
            "highlights": "Pembeda ringkas trim flagship ini dalam 1 baris",
            "power_output": "114 HP / 150 Nm (Single Motor RWD, 0-100 9.8s)",
            "battery_range": "39.4 kWh LFP (Jarak 405 km NEDC)",
            "battery_type": "Short Blade LFP Battery",
            "v2l_support": "Ya, 3.3 kW",
            "charging_time": "DC 70 kW (28 mnt 30-80%) / AC 6.6 kW",
            "wall_charger_info": "Termasuk Gratis 7 kW Wallbox + Gratis Jasa Pasang dan Tambah Daya PLN",
            "wheel_spec": "16 inch Two-Tone Alloy Wheels (205/55 R16)",
            "interior_spec": "Leatherette Dual-Tone Seats + 6-Way Power Driver Adjuster",
            "seating_layout": "5-Seater Premium Seat",
            "cluster_display": "8.8 inch Full Digital TFT Meter Cluster",
            "audio_display": "14.6 inch HD Touchscreen with Flyme Auto + 6 Speakers",
            "tailgate_feature": "Power Tailgate Standar",
            "sunroof": "Panoramic Glass Roof with Electric Power Sunshade",
            "telematics_feature": "Geely Connected App (Remote Engine Start, AC, Lock, GPS Tracker)",
            "camera_vision": "Kamera 540 Panoramic View with Transparent Chassis",
            "lighting_spec": "Full LED Projector Headlamps + Auto High Beam + DRL",
            "climate_air": "Single-Zone Auto Climate Control + PM2.5 Air Filter",
            "convenience_extras": "Qi Wireless Smartphone Charger 15W + USB-C 45W Fast Charging",
            "styling_kit": "Two-Tone Roof Exterior Styling + Gloss Black Spoiler",
            "safety_adas": "Full Geely Smart Pilot Level 2 ADAS (ACC with Stop and Go, AEB, LKA, BSD)",
            "annual_tax": 0,
            "gallery_json": None
        }
    ]
}
```
```

---

## 📑 VERSI 2: DUAL FORMAT (TABEL MARKDOWN PREVIEW + KODE PYTHON)
> **Gunakan versi ini** jika Anda ingin melihat tabel perbandingan dalam format teks sebelum menyalin kode Python.

```text
Anda adalah Senior Automotive Database Engineer dan Technical Analyst spesialis data spesifikasi kendaraan elektrifikasi Indonesia (EV, PHEV, HEV).

TUGAS ANDA:
Ekstrak dan susun data spesifikasi resmi brosur APM Indonesia secara ringkas, to-the-point, akurat, dan seragam untuk mobil:
[MASUKKAN NAMA MOBIL DI SINI, contoh: Chery Tiggo 8 Pro e+ / Kia EV9 GT-Line / MG4 EV / Neta V-II / Denza D9 / BYD M6 / Hyundai Ioniq 5 / Honda CR-V e:HEV / Wuling Cloud EV / Geely EX2]

ATURAN WAJIB (STRICT RULES):
1. Dilarang membuat kalimat narasi panjang pada parameter teknis. Semua nilai wajib to-the-point dan ringkas.
2. Gunakan data resmi APM Indonesia (harga OTR Jakarta).
3. Wajib mencantumkan dan membandingkan SELURUH trim atau varian yang dijual resmi di Indonesia. Jika mobil memiliki 2, 3, 4, atau lebih trim, buatkan kolom perbandingan dan objek varian untuk SEMUA trim tersebut tanpa ada yang dipotong.
4. Paket Home Wall Charger (termasuk gratis atau bayar, berapa kW, dan biaya instalasi) wajib dicantumkan.
5. Abaikan pencarian URL foto/gambar (fokus pada spesifikasi teknis).
6. Sajikan jawaban langsung dalam 2 bagian di bawah ini:

======================================================================
1. TABEL RINGKASAN BROSUR RESMI (MARKDOWN PREVIEW)
======================================================================

1. IDENTITAS, PASAR DAN DAFTAR TRIM:
- Model dan Merek: [Nama Mobil] | [Merek]
- Tipe Bodi dan Powertrain: [SUV / MPV / Sedan / Hatchback / Crossover] | [BEV / PHEV / HEV / FCEV]
- Status Perakitan: [CKD (Rakit Lokal Indonesia - TKDN XX%) / CBU (Impor Utuh)]
- Tahun Model: [2025 / 2026]
- Daftar Lengkap Trim yang Tersedia: [Sebutkan semua nama trim yang dijual, contoh: 1. Trim A, 2. Trim B, 3. Trim C]
- Rentang Harga OTR Jakarta: Rp [Harga Terendah] - Rp [Harga Tertinggi]
- Pilihan Warna Resmi APM: [Daftar seluruh pilihan warna resmi brosur]
- Slogan Resmi APM: [1 kalimat slogan resmi brosur]
- Posisi Pasar: [1-2 kalimat ringkas mengenai posisi mobil ini di pasar Indonesia]

2. POWERTRAIN DAN PERFORMA:
- Arsitektur Mesin / Motor Listrik: [Nama Rangkaian Motor / Mesin]
- Kapasitas Mesin (cc): [Isi angka cc jika PHEV/HEV, '-' jika BEV murni]
- Tenaga Maksimum: [Angka HP / kW]
- Torsi Maksimum: [Angka Nm]
- Transmisi dan Sistem Penggerak: [Single Reduction Gear / e-CVT / DHT] | [FWD / RWD / AWD / 4WD]
- Akselerasi 0-100 km/jam: [Angka detik]
- Kecepatan Puncak (Top Speed): [Angka km/jam]

3. BATERAI, JANGKAUAN, PENGISIAN DAN V2L:
- Kapasitas dan Jenis Kimia Baterai: [Kapasitas kWh] | [LFP (Blade Battery) / Ternary Lithium NMC / NiMH]
- Jarak Tempuh EV Murni: [Angka km (Standar NEDC / WLTP)]
- Konsumsi Energi / BBM Baku: [Angka kWh/100 km (km/kWh) untuk BEV] / [Angka km/L untuk Hybrid]
- Pengisian Cepat DC: [Daya Maks kW (durasi menit 10%–80%)]
- Pengisian Normal AC: [Daya Maks kW (durasi jam 0%–100%)]
- Fitur V2L (Vehicle-to-Load): [Ya, Daya 3300 Watt (3.3 kW) Soket Luar dan Kabin / Tidak Didukung]
- Paket Home Wall Charger: [Contoh: Termasuk Gratis Wallbox 7 kW + Gratis Jasa Pasang dan Tambah Daya PLN / Beli Terpisah Opsional Rp 10.000.000 / Portable Charger Saja]

4. DIMENSI, SASIS DAN KAPASITAS:
- Dimensi Eksterior (P x L x T): [Panjang] x [Lebar] x [Tinggi] mm
- Jarak Sumbu Roda (Wheelbase): [Angka] mm
- Ground Clearance dan Bobot: [Angka] mm | Bobot Kosong: [Angka] kg
- Kapasitas Kursi: [5 / 6 / 7 Penumpang]
- Volume Bagasi: [Volume Standar] Liter / [Volume Kursi Terlipat] Liter
- Kapasitas Tangki BBM: [Volume] Liter (khusus PHEV/HEV)

5. KOKPIT, LAYAR DAN AUDIO:
- Layar Speedometer (Instrument Cluster): [Ukuran dan Tipe MID, contoh: 12.3 inch Full Digital TFT + Head-Up Display (HUD)]
- Layar Head Unit Multimedia: [Ukuran Layar Sentuh + Konektivitas Apple CarPlay dan Android Auto]
- Sistem Audio: [Brand Audio Premium, contoh: BOSE / Dynaudio / Sony / Harman Kardon + Jumlah Speaker]

6. KESELAMATAN DAN ADAS:
- Jumlah Airbags: [Jumlah Airbags]
- Fitur Rem dan Stabilitas: [ABS, EBD, BA, ESC, Hill Start Assist, Auto Hold]
- Paket ADAS Aktif: [Nama Resmi Paket ADAS, contoh: Toyota Safety Sense 3.0 / Hyundai SmartSense / Honda SENSING] (Level 2 / Level 2+)
- Daftar Lengkap Fitur ADAS: [ACC with Stop and Go, AEB, LKA, LFA, BSM, BVM, RCTA, TSR, HBA, Kamera 360 / 540 derajat, Remote Parking]

7. PAJAK DAN GARANSI RESMI:
- Estimasi Pajak Tahunan (PKB Jakarta): Rp [Nominal PKB Tahunan] (BEV = Rp 0 insentif / SWDKLLJ Rp 143.000)
- Garansi Kendaraan: [Angka Tahun / km]
- Garansi Baterai: [Angka Tahun / km / Garansi Seumur Hidup]

8. MATRIKS 16 PARAMETER LENGKAP PERBEDAAN SELURUH TRIM:
| No | Parameter Pembeda | Trim 1 ([Nama Trim 1]) | Trim 2 ([Nama Trim 2]) | Trim 3 ([Nama Trim 3 jika ada]) | Trim 4 ([Nama Trim 4 jika ada]) |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Harga OTR Resmi | Rp [Harga] | Rp [Harga] | Rp [Harga] | Rp [Harga] |
| 2 | Motor, Tenaga dan Torsi | [Motor, FWD/RWD/AWD, HP / Nm] | [Motor, FWD/RWD/AWD, HP / Nm] | [Motor, FWD/RWD/AWD, HP / Nm] | [Motor, FWD/RWD/AWD, HP / Nm] |
| 3 | Akselerasi 0-100 km/jam | [Angka detik] | [Angka detik] | [Angka detik] | [Angka detik] |
| 4 | Baterai, Kimia dan Jarak | [Kapasitas kWh (LFP/NMC) - Jarak km] | [Kapasitas kWh (LFP/NMC) - Jarak km] | [Kapasitas kWh (LFP/NMC) - Jarak km] | [Kapasitas kWh (LFP/NMC) - Jarak km] |
| 5 | Daya Charging dan V2L | [DC kW / AC kW / V2L kW] | [DC kW / AC kW / V2L kW] | [DC kW / AC kW / V2L kW] | [DC kW / AC kW / V2L kW] |
| 6 | Paket Wall Charger Rumah | [Termasuk 7 kW Gratis / Opsional Rp 10 Juta] | [Termasuk 7 kW / 11 kW Gratis + Pasang] | [Paket Wall Charger Trim 3] | [Paket Wall Charger Trim 4] |
| 7 | Velg dan Profil Ban | [Ukuran Ring dan Ukuran Ban] | [Ukuran Ring dan Ukuran Ban] | [Ukuran Ring dan Ukuran Ban] | [Ukuran Ring dan Ukuran Ban] |
| 8 | Bahan, Fitur dan Arah Kursi | [Bahan Jok + 6-Way Manual / 8-Way Power Driver] | [Nappa Leather + 8-Way Power Memory + Lumbar + Ottoman] | [Detail Kursi Trim 3] | [Detail Kursi Trim 4] |
| 9 | Konfigurasi Tempat Duduk | [7-Seater Standard Bench] | [6-Seater Captain Seats + Ottoman / 7-Seater] | [Layout Kursi Trim 3] | [Layout Kursi Trim 4] |
| 10 | Speedometer dan Audio | [Cluster inch + Head Unit inch + Jumlah Spk] | [Cluster inch + Head Unit inch + Brand Spk] | [Cluster/Audio Trim 3] | [Cluster/Audio Trim 4] |
| 11 | Fitur Pintu Bagasi | [Manual / Power Tailgate Standar] | [Hands-free Kick Sensor + Walk-Away Close] | [Fitur Bagasi Trim 3] | [Fitur Bagasi Trim 4] |
| 12 | Tipe Atap (Roof) | [Solid Roof / Sunroof Standar] | [Panoramic Glass Roof + Power Sunshade] | [Atap Trim 3] | [Atap Trim 4] |
| 13 | Konektivitas Telematika | [Standar Bluetooth dan Wired CarPlay] | [Honda CONNECT / Bluelink / T-Intouch (App HP)] | [Telematika Trim 3] | [Telematika Trim 4] |
| 14 | Kamera Parkir dan Pandangan | [Rear Multi-Angle Camera] | [Kamera 360 Surround View + LaneWatch] | [Kamera Trim 3] | [Kamera Trim 4] |
| 15 | Lampu dan Pencahayaan | [Full LED Headlamp Standar] | [Adaptive Driving Beam + Active Cornering Light] | [Lampu Trim 3] | [Lampu Trim 4] |
| 16 | Fitur Kenyamanan Ekstra | [USB Port Standar] | [Qi Wireless Charger 15W + Nanoe-X Purifier] | [Fitur Ekstra Trim 3] | [Fitur Ekstra Trim 4] |
| 17 | Kelengkapan ADAS dan Styling | [Basic Safety / Standard ADAS] | [Full ADAS Level 2+ + RS / Modellista Styling Kit] | [ADAS dan Styling Trim 3] | [ADAS dan Styling Trim 4] |

======================================================================
2. PYTHON DICTIONARY TERSTRUKTUR (DATABASE SEED FORMAT)
======================================================================
* Buat objek dalam list variants untuk SEMUA trim yang ada tanpa terkecuali:

```python
{
    # 1. IDENTITAS DAN PASAR
    "slug": "nama-model-slug",
    "name": "Nama Resmi Model Mobil",
    "brand_name": "Merek",
    "engine_type_slug": "bev",                          # 'bev' / 'phev' / 'hev' / 'fcev'
    "body_type_slug": "suv",                           # 'suv' / 'mpv' / 'sedan' / 'hatchback' / 'crossover'
    "year": 2026,
    "price_start": 500000000,                          # Integer harga OTR terendah
    "price_end": 650000000,                            # Integer harga OTR tertinggi
    "tagline": "Slogan resmi singkat APM (1 kalimat padat)",
    "description": "Ringkasan ulasan posisi pasar mobil ini di Indonesia (maksimal 2 kalimat).",
    "image_url": None,                                 # Foto dicari manual
    "is_featured": True,

    "specs": {
        # 2. STATUS PERAKITAN, BATERAI DAN V2L
        "assembly_status": "CKD (Rakit Lokal Indonesia - TKDN 40%)", # CKD / CBU
        "battery_type": "LFP (Lithium Iron Phosphate / Blade Battery)", # LFP / NMC / NiMH
        "battery_capacity_kwh": 61.0,                  # Kapasitas baterai kWh (float)
        "electric_range_km": 430,                      # Jarak tempuh EV murni km (integer)
        "v2l_support": "Ya, Daya 3300 Watt (3.3 kW) V2L Adapter Luar dan Kabin",
        "energy_consumption": "14.2 kWh/100 km (7.0 km/kWh)", # Konsumsi energi baku

        # 3. POWERTRAIN DAN PERFORMA
        "engine_name": "Nama Arsitektur Motor/Mesin",
        "engine_capacity_cc": None,                    # Integer cc (isi None jika BEV murni)
        "horsepower": 204,                             # Total Horsepower (HP)
        "torque_nm": 340,                              # Total Torsi (Nm)
        "transmission": "Single Reduction Gear",       # Single Reduction Gear / e-CVT / DHT
        "drivetrain": "FWD",                           # FWD / RWD / AWD / 4WD
        "acceleration_0_100": 7.2,                     # Angka detik (float)
        "top_speed_kmh": 180,                          # Angka km/jam (integer)
        "fuel_consumption_kmpl": None,                 # Angka km/L jika hybrid, None jika BEV

        # 4. DIMENSI, SASIS DAN KAPASITAS
        "length_mm": 4424,                             # Panjang mm
        "width_mm": 1830,                              # Lebar mm
        "height_mm": 1588,                             # Tinggi mm
        "wheelbase_mm": 2630,                          # Sumbu roda mm
        "ground_clearance_mm": 190,                    # Ground clearance mm
        "curb_weight_kg": 1780,                        # Bobot kosong kg
        "seating_capacity": 5,                         # Jumlah kursi
        "trunk_volume_liters": 360,                    # Volume bagasi Liter
        "fuel_tank_liters": None,                      # Tangki BBM Liter (None jika BEV)

        # 5. KOKPIT, LAYAR DAN WARNA
        "cluster_display": "10.25 inch Full Digital TFT Meter Cluster + Head-Up Display (HUD)",
        "colors_json": '["Warna 1", "Warna 2", "Warna 3", "Warna 4"]',

        # 6. KESELAMATAN DAN ADAS
        "airbags": 6,                                  # Jumlah airbags
        "abs_ebd": True,
        "esc": True,
        "adas": True,
        "adas_name": "Nama Paket ADAS (contoh: Toyota Safety Sense 3.0 / Hyundai SmartSense)",
        "adas_features_json": '["Adaptive Cruise Control (ACC) with Stop and Go", "Autonomous Emergency Braking (AEB)", "Lane Keeping Assist (LKA)", "Lane Following Assist (LFA)", "Blind Spot Monitoring (BSM)", "Rear Cross Traffic Alert (RCTA)", "Kamera 360 Surround View", "High Beam Assist (HBA)"]',
        "safety_rating": 5.0,
        "comfort_rating": 4.7,
        "performance_rating": 4.6,
        "value_rating": 4.8,

        # 7. PAJAK, GARANSI DAN PAKET WALL CHARGER
        "annual_tax_estimate": 0,                      # Estimasi PKB Jakarta (Rp, integer. BEV = 0)
        "warranty_vehicle": "5 Tahun / 150000 km",
        "warranty_battery": "8 Tahun / 160000 km (Garansi Seumur Hidup)",
        "wall_charger_info": "Termasuk Gratis Wallbox 7.4 kW + Gratis Pemasangan Kabel dan Tambah Daya PLN"
    },

    # 8. MATRIKS 16 PARAMETER LENGKAP SEMUA TRIM
    "variants": [
        {
            "name": "Nama Trim 1 (Standard / Varian Bawah)",
            "price": 500000000,                        # Integer harga OTR
            "highlights": "Pembeda ringkas trim ini dalam 1 baris",
            "power_output": "170 HP / 310 Nm (Single Motor, 0-100 8.5s)",
            "battery_range": "50.0 kWh (Jarak 350 km NEDC)",
            "battery_type": "LFP Battery",
            "v2l_support": "Ya, 3.3 kW",
            "charging_time": "DC 70 kW (35 mnt 10-80%) / AC 6.6 kW",
            "wall_charger_info": "Gratis Portable Charger 2.2 kW (Wallbox 7 kW Opsional Rp 10 Juta)",
            "wheel_spec": "18 inch Alloy Wheels (215/55 R18)",
            "interior_spec": "Fabric Seats + 6-Way Manual Driver Adjuster",
            "seating_layout": "7-Seater Standard Bench",
            "cluster_display": "7 inch TFT Digital Instrument Cluster",
            "audio_display": "10.25 inch Touchscreen + 6 Speakers",
            "tailgate_feature": "Manual Tailgate",
            "sunroof": "Standard Solid Roof",
            "telematics_feature": "Standard Bluetooth dan Wired CarPlay",
            "camera_vision": "Rear Multi-Angle Camera",
            "lighting_spec": "Full LED Headlamp Standar",
            "climate_air": "Single-Zone Auto Climate Control",
            "convenience_extras": "Standard USB Charging Ports",
            "styling_kit": "Standard Exterior Styling",
            "safety_adas": "Basic ADAS (ACC, AEB, LDW, Rear Camera)",
            "annual_tax": 0,
            "gallery_json": None
        },
        {
            "name": "Nama Trim 2 (Flagship / Varian Tertinggi)",
            "price": 650000000,                        # Integer harga OTR
            "highlights": "Pembeda ringkas trim flagship ini dalam 1 baris",
            "power_output": "204 HP / 340 Nm (Dual Motor AWD, 0-100 5.1s)",
            "battery_range": "65.0 kWh (Jarak 480 km WLTP)",
            "battery_type": "Blade LFP Battery",
            "v2l_support": "Ya, 3.3 kW",
            "charging_time": "DC 150 kW (28 mnt 10-80%) / AC 11 kW",
            "wall_charger_info": "Gratis Wallbox 7.4 kW + Gratis Pemasangan Kabel dan Tambah Daya PLN",
            "wheel_spec": "19 inch Two-Tone Diamond Cut Alloy Wheels (235/50 R19)",
            "interior_spec": "Premium Nappa Leather + 8-Way Power Memory + 4-Way Lumbar + Ventilated dan Heated + Ottoman Relaxation",
            "seating_layout": "6-Seater Captain Seats + Ottoman / 7-Seater Premium",
            "cluster_display": "12.3 inch Full Digital TFT Curved Cluster + Head-Up Display (HUD)",
            "audio_display": "15.6 inch Rotating Screen + BOSE / Dynaudio 12-Speaker Premium Audio",
            "tailgate_feature": "Hands-free Kick Sensor Power Tailgate + Walk-Away Auto Close",
            "sunroof": "Panoramic Glass Roof with Electric Power Sunshade",
            "telematics_feature": "Full App Connected Services (Remote Engine dan AC, Digital Key, GPS)",
            "camera_vision": "Kamera 360 Multi-Angle Surround View + Blind Spot View Monitor",
            "lighting_spec": "Adaptive Driving Beam (Matrix LED) + Active Cornering Light",
            "climate_air": "Tri-Zone Auto Climate Control + Nanoe-X Air Purifier",
            "convenience_extras": "Dual Qi Wireless Fast Charger 50W + USB-C 45W All Rows",
            "styling_kit": "RS / Modellista Aero Body Kit + Dark Chrome Grille + Roof Rail",
            "safety_adas": "Full Level 2+ ADAS (ACC Stop and Go, LKA, LFA, BVM, RCTA, Kamera 540, Remote Parking)",
            "annual_tax": 0,
            "gallery_json": None
        }
    ]
}
```
```
