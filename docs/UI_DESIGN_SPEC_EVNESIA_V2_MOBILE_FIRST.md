# 📱 UI DESIGN SPEC V2 — EVnesia "Console Glass" (Mobile-First)

> **Revisi dari V1.** Fokus: **mobile dulu**, ringkas, tidak "kepanjangan ke bawah", **khusus mobil**.
> **Gaya:** PS5 (panggung gelap, fokus tegas) × iOS 26 Liquid Glass (kaca, kapsul, sheet)
> **Stack:** Astro.js · Tailwind + Custom CSS · TypeScript
> **Versi:** 2.0 · 2026-10-06

---

## 📌 DAFTAR ISI
1. [Apa yang Berubah dari V1](#1-apa-yang-berubah-dari-v1)
2. [Aturan Emas Mobile](#2-aturan-emas-mobile)
3. [Skala Ukuran Mobile vs Desktop](#3-skala-ukuran-mobile-vs-desktop)
4. [Fokus Mobil Saja (Pembersihan Motor)](#4-fokus-mobil-saja)
5. [Beranda: Kalkulator EV di Paling Atas](#5-beranda-kalkulator-ev-di-paling-atas)
6. [Lineup Per Merek (Bukan Kartu Biasa)](#6-lineup-per-merek)
7. [Detail Mobil: Trim & Spesifikasi Modern](#7-detail-mobil-trim--spesifikasi-modern)
8. [Interaksi: Rekomendasi, Berita Terkait, Bandingkan](#8-interaksi)
9. [Navigasi Mobile](#9-navigasi-mobile)
10. [Desktop (Adaptasi)](#10-desktop-adaptasi)
11. [Performa & Aksesibilitas](#11-performa--aksesibilitas)
12. [Token CSS Versi Ringkas](#12-token-css-versi-ringkas)
13. [Pemetaan ke Proyek & Roadmap](#13-pemetaan-ke-proyek--roadmap)
14. [Checklist QA Mobile](#14-checklist-qa-mobile)

---

## 1. Apa yang Berubah dari V1

| Masalah di desain lama / V1 | Perbaikan di V2 |
| :--- | :--- |
| Elemen terlalu besar di mobile (display 88px, header 64px, kartu 220–320px) | Skala **mobile terpisah** & lebih kecil (lihat bagian 3). |
| Halaman memanjang ke bawah | **Anggaran tinggi halaman**, banyak konten dipindah ke **rail horizontal, tab, accordion, bottom sheet**. |
| Kartu mobil seragam | Lineup berbentuk **Spotlight + Peta Harga×Jarak + Rail ringkas** (bagian 6). |
| Spesifikasi berupa bar/tabel | **Gauge, kurva pengisian, siluet bersensor, "diff chips"** (bagian 7). |
| Kalkulator di bagian tengah | **Kalkulator = hero beranda**, tepat di bawah navbar (bagian 5). |
| Ada sub-tema motor | **Dihapus**; web hanya mobil (bagian 4). |

---

## 2. Aturan Emas Mobile

Acuan layar: **390×844** (iPhone umum) dan **360×800** (Android menengah yang paling umum di Indonesia). Jika pas di 360×800, aman di semua.

1. **Anggaran tinggi:** Beranda ≤ **5 layar** (≈ 4.200px). Detail mobil ≤ **7 layar** (dengan tab, bukan satu scroll panjang).
2. **Satu section ≤ 1 layar.** Lebih dari itu → pecah jadi rail/tab/sheet.
3. **Tidak ada elemen > 55% tinggi layar**, kecuali panggung foto (maks **40svh**).
4. **Horizontal > vertikal.** Daftar panjang jadi rail yang bisa digeser; "peek" kartu berikutnya 12–16% agar jelas bisa digeser.
5. **Detail disembunyikan, bukan dihapus:** tampilkan 3 angka kunci, sisanya di "Lihat semua" (bottom sheet).
6. **Satu tangan:** aksi penting di **separuh bawah** layar (dock, sheet, tombol).
7. **Target sentuh ≥ 44px**, jarak antar target ≥ 8px.
8. **Konten pertama terlihat < 1 detik:** kalkulator & hero harus muncul tanpa menunggu gambar berat.
9. **Efek berat (blur) maksimal 3 elemen** di satu layar.
10. **Jangan skala hanya dengan `vw` mentah.** Gunakan `clamp()` dengan batas atas rendah dan **container queries** untuk komponen.

---

## 3. Skala Ukuran Mobile vs Desktop

### 3.1 Ukuran komponen

| Elemen | Mobile (≤ 767px) | Desktop (≥ 1024px) |
| :--- | :--- | :--- |
| Header kapsul | tinggi **48px**, margin 8px | 60px |
| Dock bawah | tinggi **56px** + safe-area | tidak ada (diganti header) |
| Padding halaman (gutter) | **16px** | 32–48px |
| Jarak antar section | **24–32px** | 64px |
| Radius kartu / panel | **20px** | 24px |
| Radius elemen dalam | 12px | 16px |
| Tombol | tinggi **44px** | 44–48px |
| Chip filter | tinggi **32px** | 36px |
| Foto kartu rail | lebar **72% layar** (maks 280px), rasio **4:3** | 280–320px, rasio 16:10 |
| Panggung foto detail | **36–40svh** | 60vh |
| Bottom sheet | tinggi 50% / 85% layar | modal 560px / panel samping |

### 3.2 Tipografi fluid (lebih kecil di mobile)

| Peran | Mobile | Desktop | CSS |
| :--- | :--- | :--- | :--- |
| `display` (hero) | 30px | 64px | `clamp(1.875rem, 1.2rem + 3vw, 4rem)` |
| `title-1` | 24px | 36px | `clamp(1.5rem, 1.2rem + 1.2vw, 2.25rem)` |
| `title-2` (judul section) | 18px | 24px | `clamp(1.125rem, 1rem + .5vw, 1.5rem)` |
| `body` | 15px | 16px | `clamp(.9375rem, .9rem + .2vw, 1rem)` |
| `caption` | 12px | 13px | — |
| `metric` (angka besar) | 28px | 48px | `clamp(1.75rem, 1.2rem + 2.2vw, 3rem)` |

> Batas atas sengaja rendah. Inilah yang mencegah elemen "membengkak" saat layar berubah.

---

## 4. Fokus Mobil Saja

- Hapus: `src/themes/motor-listrik/`, `katalog-motor.astro`, menu/filter/tab "Motor", kategori berita "Motor Listrik", sub-tema warna motor.
- Alihkan URL lama (`/katalog-motor`) dengan **301** ke `/katalog-mobil` agar SEO tidak rusak.
- Cakupan jenis penggerak tetap: **BEV · PHEV · HEV** (semuanya mobil).
- Brand Hub, filter, pencarian, dan schema.org cukup memakai `Car` / `Vehicle`.
- Hasilnya navigasi lebih pendek: **Beranda · Katalog · Bandingkan · Berita · Tools**.

---

## 5. Beranda: Kalkulator EV di Paling Atas

### 5.1 Urutan beranda (mobile)

```
┌─ Header kapsul 48px ──────────────────┐
│ ① KALKULATOR EV  (hero, ±440px)       │  ← selling point, langsung di bawah navbar
│ ② Rekomendasi cepat (chip + rail)     │
│ ③ Jelajahi Merek (strip logo bulat)   │
│ ④ Mobil Terbaru (rail)                │
│ ⑤ Berita Pilihan (rail 1 baris)       │
│ ⑥ Tools lain (4 ubin kecil)           │
│ Footer ringkas                        │
└─ Dock bawah 56px ─────────────────────┘
```
Total ≈ 4 layar. Tidak ada hero foto besar sebelum kalkulator.

### 5.2 Komponen Kalkulator Hero ("Hitung Hemat Kamu")

**Wireframe mobile (360–390px):**
```
┌──────────────────────────────────┐
│ ⚡ Hitung hemat pakai mobil listrik│  ← title-2
│                                  │
│ Mobil EV   [🚗 BYD Atto 3   ▾]   │  ← selector + thumbnail kecil
│                                  │
│ Jarak harian                     │
│ ●━━━━━━○────────  40 km          │  ← slider kaca, label mengikuti jempol
│                                  │
│ Isi daya   (Rumah | SPKLU | Campur)│ ← segmented 3 pilihan
│                                  │
│ ┌──────────────────────────────┐ │
│ │ HEMAT / TAHUN                │ │
│ │ Rp 14,2 jt        ▁▂▃▅▆▇     │ │  ← metric besar + sparkline break-even
│ │ Rp 1,18 jt/bln · balik modal │ │
│ │ 6,4 th · CO₂ −1,9 ton        │ │
│ └──────────────────────────────┘ │
│ [ Atur lebih detail ▾ ]  [Cari mobil cocok →]│
└──────────────────────────────────┘
```
Tinggi target **≤ 440px** (± setengah layar). Hasil **selalu terlihat tanpa scroll di dalam widget**.

**Aturan interaksi:**
- Hasil **menghitung langsung** saat slider digeser (tanpa tombol "Hitung"). Angka memakai count-up 250ms.
- **"Atur lebih detail"** membuka accordion (bukan halaman baru): mobil BBM pembanding, jenis BBM, konsumsi km/L, tarif listrik rumah/SPKLU, harga mobil, jangka waktu.
- Nilai default cerdas (40 km/hari, isi daya rumah) agar hasil langsung bermakna.
- **Tarif & harga BBM disimpan di satu berkas konfigurasi** (`src/data/energy-rates.ts`) supaya mudah diperbarui; tampilkan label "Diperbarui: tanggal".
- Tombol **"Cari mobil cocok →"** membawa hasil ke Rekomendasi (bagian 5.3) dengan filter otomatis (budget & jarak harian).
- Tampilkan disklaimer satu baris kecil: *"Estimasi, bukan penawaran."*
- Pilihan mobil memakai **bottom sheet pencarian** (daftar bergambar kecil + pencarian), bukan dropdown bawaan browser.
- Latar widget: kaca (L2) di atas gradasi ambient biru; angka hasil memakai warna `--energy` (hijau).

**Desktop:** dua kolom — kiri input, kanan hasil besar + grafik break-even penuh. Tinggi tetap ≈ 420px.

### 5.3 Rekomendasi Cepat (tepat di bawah kalkulator)

- Baris **chip** (kapsul 32px): `Hemat` · `Keluarga` · `Jarak Jauh` · `Di bawah 300 jt` · `Fast Charging`.
- Memilih chip → **rail di bawahnya berganti** dengan animasi geser halus (tanpa pindah halaman).
- Setelah memakai kalkulator, chip pertama otomatis menjadi **"Cocok untuk 40 km/hari"** dan rail menampilkan **% kecocokan** + **estimasi hemat per mobil** (angka hijau kecil).

---

## 6. Lineup Per Merek

Halaman `/merek/[brand]` (atau `/katalog-mobil?brand=`). Tujuan: tahu **jenis-jenis mobil dari merek itu** dengan cepat, dalam **≤ 2 layar**.

### 6.1 Struktur halaman (mobile)

```
┌ Header ───────────────────────────────┐
│ [logo] BYD            12 model · mulai Rp 235 jt │  ← 56px, bukan hero besar
│ (Semua | SUV | Sedan | MPV | Hatchback)          │  ← chip tipe bodi, sticky
│ Tampilan:  ◉ Spotlight   ○ Peta   ○ Daftar       │  ← segmented kaca
│                                       │
│  [ VIEW AKTIF — lihat 6.2 / 6.3 / 6.4 ] │
└───────────────────────────────────────┘
```

### 6.2 Mode 1 — **Spotlight** (default, paling visual)

Satu mobil jadi "tokoh utama", sisanya mengintip di kiri/kanan (ala *coverflow* / Apple TV).

```
        ┌─────┐  ┌───────────────┐  ┌─────┐
        │ ‹   │  │  [ FOTO MOBIL │  │   › │   ← mobil tengah besar,
        │ kecil│  │   BEBAS-BG ]  │  │kecil│     tetangga 70% & redup
        └─────┘  └───────────────┘  └─────┘
                    Sealion 7
                    SUV · BEV · 5 kursi
        ─────────────────────────────────
        Rp 719 jt │ ⚡ 502 km │ 230 kW │ 18 mnt   ← strip statistik 1 baris, berganti saat swipe
        ─────────────────────────────────
        [ Lihat Detail ]   [ + Bandingkan ]
```
- Tinggi total ≈ **60% layar**.
- Memakai **foto tanpa latar** (cut-out) bila ada; bila tidak, foto studio dengan *mask* gradasi agar menyatu ke panggung gelap.
- **Swipe** mengganti mobil; strip statistik **bertransisi per angka** (count-up), sehingga terasa "hidup" tanpa kartu tambahan.
- Titik indikator berbentuk kapsul kaca di bawah; geser cepat memakai *scroll-snap*.
- Mobil non-fokus: `scale(.82)`, `opacity .55` (efek fokus ala PS5, tanpa hover).

### 6.3 Mode 2 — **Peta Harga × Jarak** (paling informatif)

Setiap model = **satu titik bergambar** pada sumbu **Harga (X)** dan **Jarak tempuh (Y)**. Cepat melihat mana yang paling murah, terjauh, atau paling seimbang.

```
 Jarak ↑
 600 │            ◉ Seal
 500 │      ◉ Sealion 7     
 400 │  ◉ Atto 3
 300 │ ◉ Dolphin
     └───────────────────────→ Harga
       250jt   500jt   800jt
```
- Titik berupa **thumbnail bulat 36px** (logo/foto mobil) yang membesar saat disentuh; muncul **tooltip kaca** berisi nama + harga + jarak + tombol "Detail".
- Warna titik mengikuti tipe bodi (SUV, Sedan, dst.), dengan legenda berupa chip yang bisa di-toggle.
- **Zona "sweet spot"**: area kaca transparan di kanan-atas-kiri (murah & jauh) bisa disorot dengan label "Paling worth it".
- Tinggi grafik **≈ 300px**. Pinch/drag untuk zoom ringan; tombol "Reset".
- Bisa diaktifkan juga di halaman Katalog untuk **semua merek** dengan warna berbeda per merek.

### 6.4 Mode 3 — **Daftar Ringkas ("Lineup Ribbon")**

Alternatif untuk pengguna yang ingin melihat banyak sekaligus, tapi **bukan kartu kotak**.

```
 ─────────────────────────────────────────
  Sealion 7        SUV          [foto ke kanan,
  ⚡502 km · 230kW              keluar tepi layar]
  Rp 719 jt ›
 ─────────────────────────────────────────
  Atto 3           SUV
  …
```
- Setiap baris tinggi **84px**, tanpa kotak/border; hanya garis pemisah tipis.
- **Foto mobil keluar dari tepi kanan** (bleed, di-crop), memberi kesan dinamis dan hemat ruang.
- Ikon kecil tipe bodi + chip BEV/PHEV/HEV.
- **Swipe baris ke kiri** memunculkan aksi: `Bandingkan` · `Simpan`.
- Tekan-tahan → *peek sheet* (lihat 8.3).

### 6.5 Katalog semua merek
- Pilihan merek memakai **strip logo bulat 44px** (bisa digeser), bukan popover 3 baris.
- Filter memakai **bottom sheet**: harga (slider rentang), tipe bodi, penggerak, jarak tempuh minimum, jumlah kursi. Hitungan hasil dinamis pada tombol *"Tampilkan 23 mobil"*.
- Pilihan tampilan sama: **Spotlight / Peta / Daftar**.

---

## 7. Detail Mobil: Trim & Spesifikasi Modern

### 7.1 Kerangka halaman (mobile) — memakai tab agar tidak panjang

```
┌ Panggung (foto, 38svh, swipe galeri) ┐
│ BYD · SUV · BEV          ♡   ⤴       │
│ Sealion 7                            │  ← title-1
│ (Standard | ●Premium | Performance)  │  ← pemilih trim (7.2)
│ Rp 719 jt  · PPN 1% · [+Rp 60 jt]    │
├──────────────────────────────────────┤
│ Ringkas · Performa · Baterai · Dimensi · Keselamatan · Garansi │ ← tab sticky, geser horizontal
├──────────────────────────────────────┤
│ [ konten tab aktif ≤ 1 layar ]       │
└──────────────────────────────────────┘
 Dock: [Brosur PDF] [Simulasi Kredit] [Test Drive]
```
- **Ringkas** menampilkan 4 angka utama + "Apa yang berbeda di trim ini".
- Konten per tab maksimal satu layar; sisanya "Lihat semua spek" → bottom sheet setinggi 85%.
- Desktop: panggung kiri *sticky* (55%), konten kanan.

### 7.2 Pemilih Trim — **"Trim Ladder"**

Bukan dropdown, bukan tabel harga.

```
  Standard ──── ● Premium ──── Performance AWD
  Rp 659 jt     Rp 719 jt      Rp 799 jt
                  ↑ +Rp 60 jt dari Standard
```
- Tiga/empat titik pada **tangga horizontal**; titik terpilih menyala (aksen), garis penghubung terisi sampai titik aktif.
- Di bawahnya, **"Diff Chips"**: hanya fitur **yang berubah dari trim sebelumnya**
  `＋ Atap panoramik` `＋ ADAS Level 2` `＋ Pendingin kursi` `↑ Daya 150 → 230 kW`
- Saat ganti trim: angka di halaman **beranimasi** (count-up), dan nilai yang berubah **berkedip hijau sebentar** (highlight 600ms). Pengguna langsung paham apa dampaknya.
- Tombol **"Bandingkan trim"** membuka *split sheet*: dua trim berdampingan, hanya baris yang **berbeda** yang ditampilkan (sakelar "Tampilkan semua").

### 7.3 Spesifikasi — pengganti bar & tabel

| Data | Visual modern | Catatan mobile |
| :--- | :--- | :--- |
| **Jarak tempuh** | **Gauge busur 240°** (seperti panel instrumen) dengan angka besar di tengah; label standar (CLTC/NEDC/WLTP) sebagai chip. | Diameter ±140px |
| **Daya & torsi** | **Dua busur konsentris** (kW luar, Nm dalam) + chip PS. | Satu widget, bukan dua bar |
| **0–100 km/jam** | **Lintasan balap mini**: titik melaju sepanjang garis, durasi dihitung sungguhan saat tab terlihat; titik pembanding (Avanza/rata-rata kelas) opsional. | Tinggi 56px |
| **Baterai** | **Ilustrasi sel baterai** terisi sesuai kWh relatif terhadap rentang kelas; chip kimia (LFP/NMC). | |
| **Pengisian cepat** | **Kurva pengisian** (sparkline) 0–100%: sumbu waktu, area gradasi hijau, **penanda 10–80%** dan label "18 menit". Geser jari di kurva → menampilkan % & menit di titik itu. | Tinggi 120px |
| **Isi daya di rumah** | **Selektor sumber daya** (2,2 kW · 7 kW · 22 kW · DC 150 kW) berupa segmented; **cincin waktu** di sebelahnya berubah. | Menggantikan estimator terpisah |
| **Dimensi** | **Siluet samping + atas** dengan titik penunjuk (P × L × T, wheelbase, ground clearance); ketuk titik → angka muncul. Garis neon biru tipis di panggung gelap. | Satu layar penuh |
| **Bagasi & kursi** | **Ikon ruang** (denah kursi 5/6/7) + angka liter; frunk ditandai ikon depan. | |
| **Garansi** | **Linimasa horizontal** (baterai 8 th/160.000 km, kendaraan, dst.) berupa pita berlabel. | |
| **Harga & paket** | **Chip paket** (Wallbox 7 kW, V2L, Portable Charger) yang bisa dicentang untuk melihat nilai bonus. | |

**Susunan tab "Performa/Baterai" (contoh satu layar mobile):**
```
 ┌─────────────┐ ┌─────────────┐
 │  GAUGE 502  │ │ BUSUR DAYA  │   ← 2 widget sejajar, masing-masing ±165px
 │   km CLTC   │ │ 230kW 380Nm │
 └─────────────┘ └─────────────┘
 ┌───────────────────────────────┐
 │ Kurva pengisian 10–80% · 18 mnt │
 └───────────────────────────────┘
 [ Lihat semua spesifikasi › ]
```

### 7.4 Keselamatan (ADAS) — pengganti matriks tabel

- **Siluet mobil dari atas** dengan **zona sensor** (kerucut kamera 360°, radar depan, ultrasonik, blind-spot) yang **menyala** saat fitur dipilih.
- Di bawahnya **chip fitur** (ACC, Lane Keep, Blind Spot, AEB, 360° Cam, …) berstatus:
  - ✓ **Ada di trim ini** (hijau)
  - 🔒 **Tersedia di trim lebih tinggi** (abu + label "Premium+") — ketuk untuk pindah ke trim itu
  - — Tidak tersedia
- **Lencana tingkat bantuan** (L1/L2) dan **skor ringkas** "9 dari 12 fitur".
- Ketuk chip → *popover kaca* berisi penjelasan singkat 1–2 kalimat (edukasi untuk pembaca awam).

### 7.5 Tombol & dock aksi
- Dock berubah konteks di halaman mobil: **Brosur · Kredit · Test Drive** (+ ikon bandingkan).
- Saat sheet terbuka, dock **menghilang halus** agar tidak menumpuk.

---

## 8. Interaksi

### 8.1 Rekomendasi Mobil — **"Cari yang Cocok" (Finder)**

Dibuka dari tombol di kalkulator, dari dock, atau dari chip rekomendasi. Berupa **bottom sheet 85%**, 3 langkah ringan, bukan formulir panjang.

```
 Langkah 1/3  Budget       ━━●━━━━━   Rp 250 – 500 jt
 Langkah 2/3  Kebutuhan    [Harian] [Keluarga] [Jarak jauh] [Gaya]
 Langkah 3/3  Isi daya     [Ada charger rumah] [Hanya SPKLU]
 ─────────────────────────────────────
 Hasil (urut kecocokan)
 ① Atto 3        ●●●●○  92% cocok   hemat ±Rp 12 jt/th
 ② Dolphin       ●●●●○  88% cocok
 ③ …
```
- Hasil berupa **deret Spotlight kecil** (swipe), bukan kartu seragam; **persentase cocok** disertai **alasan** dalam satu kalimat ("Jarak 410 km cukup untuk 2 hari pemakaian").
- Skor transparan: sebutkan faktor (harga, jarak, kursi, pengisian), bukan angka rahasia.
- Hasil terakhir disimpan lokal (localStorage) → beranda menampilkan "Lanjutkan pilihanmu".

### 8.2 "Mirip Dengan Ini" di halaman detail
- Rail **"Alternatif"** berisi 4–6 mobil: setiap item menampilkan **selisih** dari mobil saat ini (`−Rp 80 jt` hijau, `+38 km` hijau, `−2 kursi` merah) — bukan sekadar daftar.
- Ketuk selisih → langsung buka *split sheet* perbandingan dua mobil.

### 8.3 Peek Sheet (pratinjau tanpa pindah halaman)
Dipicu **tekan-tahan** pada mobil mana pun (rail, lineup, artikel):
- Muncul sheet 50%: foto, 4 angka kunci, trim termurah, tombol `Detail` `Bandingkan` `Simpan`.
- Haptic ringan hanya bila perangkat mendukung dan pengguna belum mematikan.

### 8.4 Berita Terkait — **kontekstual, bukan daftar**

**Di halaman mobil:** bagian **"Sedang Dibicarakan"** berupa rail satu baris (tinggi ±96px) berisi berita yang menyebut model itu, urut tanggal, dengan chip jenis: `Review` · `Harga` · `Peluncuran` · `Insentif`. Ada filter chip di atasnya.

**Di halaman artikel (interaksi unggulan):**
- Nama model dalam teks menjadi **"Car Chip"** (kapsul kecil dengan thumbnail). Ketuk → **Peek Sheet** (8.3) tanpa meninggalkan artikel. Ini menghubungkan konten redaksi dengan database kendaraan, dan keunggulan unik situs Anda.
- **Bilah progres baca** tipis di bawah header.
- Di akhir artikel: **"Lanjut Baca"** sebagai tumpukan 3 kartu bertingkat (efek Wallet iOS) yang bisa digeser ke samping, ditambah "Mobil yang disebut di artikel ini" (rail Car Chip).
- Pada artikel review: panel **"Ringkasan spek"** mengambang yang bisa dilipat, memperlihatkan 4 angka utama saat pembaca scroll.

### 8.5 Bandingkan — **Tray Mengambang**
- Menekan `+ Bandingkan` memunculkan **kapsul kaca** di atas dock: `2 dipilih · Bandingkan →` dengan thumbnail bertumpuk (maks 3).
- Halaman perbandingan: **tampilan "Diff-first"** — secara default hanya menampilkan baris yang **berbeda**; nilai terbaik per baris bertanda ★ hijau; sakelar "Tampilkan semua".
- Header kolom (foto + nama) **sticky**; di mobile kolom bisa digeser horizontal dengan *snap* per mobil.

### 8.6 Garasi Saya (opsional, ringan)
- Ikon ♡ menyimpan mobil ke localStorage; tab "Tersimpan" ada di menu Katalog. Tanpa akun, tanpa beban server.

### 8.7 Gerak yang dipakai
| Interaksi | Durasi | Catatan |
| :--- | :--- | :--- |
| Ganti trim / mobil (count-up) | 250–300ms | hanya angka yang berubah |
| Sheet naik | 320ms spring | dari bawah, dengan *grabber* |
| Spotlight swipe | scroll-snap native | + skala/opasitas via `animation-timeline: scroll()` jika didukung |
| Rail mengganti isi (chip rekomendasi) | 220ms | geser + fade |
| Tekan elemen | 90ms `scale(.97)` | pengganti hover |

Semua dimatikan/diminimalkan pada `prefers-reduced-motion`.

---

## 9. Navigasi Mobile

**Header kapsul (48px):** logo kiri · pencarian (ikon) · menu (ikon). Menyusut saat scroll turun, kembali saat naik.

**Dock bawah (56px, kapsul kaca):**
`Beranda · Katalog · Bandingkan · Berita · Tools`
- *Tools* membuka sheet kecil: Kalkulator · SPKLU · Komparasi · Finder.
- Badge angka kecil pada *Bandingkan* bila ada mobil di tray.
- Dock **tidak muncul** bersamaan dengan keyboard virtual / saat input difokuskan.

**Pencarian:** ketuk ikon → **sheet penuh** dengan input otomatis fokus, hasil per kategori (Mobil · Merek · Berita), dan riwayat pencarian terakhir.

**Menu merek:** strip logo bulat (bagian 6.5), bukan popover berlapis.

---

## 10. Desktop (Adaptasi)

| Bagian | Mobile | Desktop |
| :--- | :--- | :--- |
| Kalkulator | 1 kolom, ±440px | 2 kolom (input / hasil+grafik), ±420px |
| Navigasi | Header + dock | Header kapsul lebar dengan tab (Beranda, Katalog, Bandingkan, Berita, Tools) |
| Lineup | Spotlight/Peta/Daftar bergantian | Spotlight lebar + **Peta di sebelah kanan** secara bersamaan |
| Detail mobil | Tab satu layar | Panggung kiri *sticky*, konten kanan, tab tetap |
| Sheet | Bottom sheet | Modal tengah / panel samping 420px |
| Rail | Peek 12–16% | Panah kaca di tepi, tampil 4–5 item |
| Hover | Tidak ada (press state) | Focus-card: scale 1.04 + ring + redup yang lain |
| Navigasi keyboard | — | Panah antar item rail, `Esc` tutup sheet, roving tabindex |

> **Prinsip:** komponen sama, **hanya tata letak yang berubah** lewat container query — bukan dua desain terpisah.

---

## 11. Performa & Aksesibilitas

### Performa (Android menengah sebagai patokan)
- **Blur hanya pada:** header, dock, sheet aktif. Kartu/rail memakai isi semi-solid (`rgba` + highlight tepi atas), **tanpa** `backdrop-filter`.
- Blur mobile **12–16px** (bukan 24px).
- Gauge, kurva, dan siluet memakai **SVG inline** (ringan, tajam di semua layar); animasi memakai `transform`/`stroke-dashoffset`.
- **Peta Harga×Jarak:** SVG + `<img>` thumbnail 36px WebP; tanpa library grafik berat.
- Gambar: `srcset` + `sizes` per breakpoint; cut-out dalam WebP/AVIF; kartu rail ≤ 40KB per gambar.
- `content-visibility: auto` untuk section di bawah lipatan; hydrate komponen interaktif dengan `client:visible` / `client:idle`.
- Kalkulator harus bisa dipakai **sebelum** sisa halaman selesai dimuat (render statis + hidrasi `client:load` ringan).
- Target: LCP < 2,5 dtk di 4G, INP < 200ms, CLS < 0,1.

### Aksesibilitas
- Setiap visual data punya **teks setara** (mis. gauge → `aria-label="Jarak tempuh 502 km menurut CLTC"`; kurva → ringkasan teks).
- Slider memakai elemen native `input[type=range]` yang distilkan, agar dapat diakses keyboard & pembaca layar.
- Sheet: *focus trap*, `Esc`/tombol tutup, `aria-modal`, fokus kembali ke pemicu.
- Status tidak hanya warna: ✓ / 🔒 / — selalu disertai ikon/teks.
- `prefers-reduced-motion`, `prefers-reduced-transparency`, `prefers-contrast` didukung.
- Kontras teks ≥ 4,5:1; teks di atas foto selalu memakai scrim.
- Zoom teks sistem hingga 200% tidak boleh memecah tata letak (hindari tinggi tetap pada teks).

---

## 12. Token CSS Versi Ringkas

```css
:root {
  /* warna (sama seperti V1) */
  --bg-void:#04060c; --bg-deep:#0a1020; --bg-raise:#111a30;
  --accent:#2e9bff; --accent-deep:#0070d1; --energy:#34e0a1;
  --warn:#ffb340; --danger:#ff5a5f;
  --label-1:#f5f7fa; --label-2:rgba(235,240,255,.62); --label-3:rgba(235,240,255,.34);

  /* kaca (mobile lebih ringan) */
  --glass-fill:rgba(255,255,255,.08);
  --glass-stroke:rgba(255,255,255,.16);
  --glass-highlight:rgba(255,255,255,.36);
  --glass-blur:14px;

  /* ukuran mobile-first */
  --gutter:16px;
  --header-h:48px;
  --dock-h:56px;
  --r-card:20px; --r-inner:12px; --r-pill:999px;
  --tap:44px;
  --stage-h:38svh;

  /* tipografi fluid */
  --fs-display:clamp(1.875rem,1.2rem + 3vw,4rem);
  --fs-title1:clamp(1.5rem,1.2rem + 1.2vw,2.25rem);
  --fs-title2:clamp(1.125rem,1rem + .5vw,1.5rem);
  --fs-body:clamp(.9375rem,.9rem + .2vw,1rem);
  --fs-metric:clamp(1.75rem,1.2rem + 2.2vw,3rem);

  --ease-spring:linear(0,.18 6%,.62 16%,.92 28%,1.04 40%,1.02 55%,1);
  --ease-out:cubic-bezier(.2,.8,.2,1);
}

@media (min-width:768px){
  :root{ --gutter:32px; --header-h:60px; --r-card:24px; --r-inner:16px; --glass-blur:22px; --stage-h:60vh; }
}
@media (min-width:1024px){ :root{ --gutter:48px; } }

/* padding aman untuk dock & notch */
body{ padding-bottom:calc(var(--dock-h) + env(safe-area-inset-bottom,0px)); }
@media (min-width:1024px){ body{ padding-bottom:0; } }

/* rail dengan peek */
.rail{
  display:flex; gap:12px; overflow-x:auto; scroll-snap-type:x proximity;
  padding-inline:var(--gutter); scroll-padding-inline:var(--gutter);
  scrollbar-width:none;
}
.rail > *{ flex:0 0 min(72%,280px); scroll-snap-align:start; }
```

---

## 13. Pemetaan ke Proyek & Roadmap

### Komponen baru / diubah

| Komponen | Lokasi disarankan |
| :--- | :--- |
| Kalkulator hero + sheet pemilih mobil | `src/components/calculator/EvCalculator.astro` (+ island TS) · `src/data/energy-rates.ts` |
| Rekomendasi chip + Finder sheet | `src/components/finder/` |
| Lineup: Spotlight / Peta / Ribbon | `src/components/lineup/` |
| Trim Ladder + Diff Chips | `src/components/car/TrimLadder.astro` |
| Gauge, Kurva pengisian, Siluet dimensi, Siluet ADAS | `src/components/car/viz/` (SVG) |
| Peek Sheet, Bottom Sheet, Compare Tray | `src/components/ui/` |
| Car Chip dalam artikel | `src/components/news/CarChip.astro` (+ transform pada konten artikel) |
| Dock & header | `src/components/Header.astro`, `MobileDock.astro` |

### Urutan kerja yang disarankan

| Fase | Isi | Hasil |
| :--- | :--- | :--- |
| **1** | Token mobile + skala + header 48px + dock; **perbaiki tinggi & ukuran** komponen lama | Masalah "terlalu besar/panjang" langsung teratasi |
| **2** | Kalkulator hero di beranda + chip rekomendasi + rail ringkas | Selling point tampil di atas |
| **3** | Lineup Spotlight + Peta + Ribbon; strip merek; sheet filter | Menu merek/jenis mobil baru |
| **4** | Detail mobil: tab, Trim Ladder, gauge, kurva, siluet dimensi & ADAS | Trim & spek modern |
| **5** | Finder, Peek Sheet, Compare Tray, Car Chip di artikel, rail "Sedang Dibicarakan" | Interaksi unggulan |
| **6** | Pembersihan motor, redirect 301, audit performa (Android 360×800) & A11y | Siap rilis |

> Fase 1 sebaiknya dikerjakan **lebih dulu dan dirilis sendiri**, karena langsung memperbaiki keluhan utama.

---

## 14. Checklist QA Mobile

- [ ] Diuji di **360×800**, **390×844**, **430×932**, tablet 768 dan desktop 1280+.
- [ ] Beranda ≤ 5 layar; detail mobil tiap tab ≤ 1 layar.
- [ ] Kalkulator terlihat penuh (input + hasil) pada layar 360×800 **tanpa scroll di dalam widget**.
- [ ] Tidak ada elemen > 55% tinggi layar selain panggung foto (≤ 40svh).
- [ ] Semua target sentuh ≥ 44px; tidak ada teks < 12px.
- [ ] Rail menunjukkan "peek" kartu berikutnya.
- [ ] Maksimal 3 elemen berblur dalam satu layar; FPS mulus di Android menengah.
- [ ] Setiap gauge/kurva/siluet punya teks alternatif.
- [ ] Sheet bisa ditutup dengan swipe, tombol, dan `Esc`; fokus kembali ke pemicu.
- [ ] Dock tidak menutupi konten (padding bawah benar) dan tidak tampil saat keyboard muncul.
- [ ] Mode `reduce motion` / `reduce transparency` / kontras tinggi diuji.
- [ ] Tidak ada lagi referensi "motor" di navigasi, filter, sitemap, RSS, dan schema.
- [ ] Lighthouse mobile: Performance ≥ 90, Accessibility ≥ 95.

---

### 🧭 Catatan
- Jika foto cut-out (tanpa latar) belum tersedia untuk semua model, Spotlight tetap bisa berjalan dengan foto studio + *mask* gradasi; cut-out bisa disiapkan bertahap mulai dari merek terlaris.
- Angka ukuran di dokumen adalah titik awal. Setelah Fase 1, **ukur langsung di ponsel nyata** dan setel ulang sebelum lanjut ke fase berikutnya.
- Dokumen V1 tetap valid untuk token warna, bahasa kaca, dan prinsip dasar; V2 menggantikan bagian ukuran, tata letak mobile, dan komponen yang disebutkan di atas.
