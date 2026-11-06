=== Inova CMS Sync ===
Contributors: inova
Tags: cms, sync, ai, articles, import
Requires at least: 6.0
Tested up to: 7.0
Requires PHP: 7.4
Stable tag: 1.1.4
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Sinkronisasi artikel dari Inova CMS ke WordPress + AI Writer dari editor post.

== Description ==

Plugin ini menghubungkan situs WordPress Anda dengan Inova CMS:

**F1 — Sinkronisasi Artikel (CMS → WP):**
Tarik artikel yang sudah ditulis di CMS menjadi post WordPress secara otomatis.
Featured image, kategori, dan tag ikut tersinkron.

**F2 — Inova AI Writer (WP → CMS → WP):**
Tombol "Inova AI" di editor post WordPress untuk generate artikel
menggunakan AI dari CMS. Hasil tersimpan sebagai draft di CMS dan
langsung mengisi editor WordPress.

== Installation ==

1. Upload folder `inova-cms-sync` ke `/wp-content/plugins/`
2. Aktifkan plugin di menu Plugins
3. Buka menu **Inova CMS → Pengaturan**
4. Isi API Base URL, Access Key, dan Secret dari halaman Open API CMS
5. Klik **Tes Koneksi** untuk verifikasi
6. Atur sinkronisasi dan kategori sesuai kebutuhan
7. Untuk sinkron otomatis, disarankan setup real cron:
   `*/15 * * * * curl -s https://situs/wp-cron.php?doing_wp_cron > /dev/null`

== Frequently Asked Questions ==

= Apakah plugin ini butuh koneksi internet? =
Ya, plugin berkomunikasi dengan server CMS via Open API.

= Apakah data WordPress saya aman? =
Plugin hanya membuat post baru dari data CMS. Tidak menghapus data existing.
Uninstall plugin tidak menghapus post yang sudah dibuat.

== Changelog ==

= 1.1.4 =
* **KRITIS**: perbaiki "Plugin tidak dapat diaktifkan karena terpicu
  kesalahan fatal." — `class-ics-settings.php` kehilangan tanda kurung
  kurawal penutup pada `save_all()` (fatal PHP parse error, plugin gagal
  di-bootstrap sama sekali). Diperkenalkan di 1.1.3 saat menambahkan fitur
  pemetaan kategori; **1.1.3 rusak total dan tidak boleh dipasang**.
* Perbaiki fitur pemetaan kategori itu sendiri: nilai baris
  `category_map_keys`/`category_map_vals` dari form dibaca dari sumber yang
  salah (`$all`, bukan `$data` yang dikirim form) sehingga tidak pernah
  benar-benar tersimpan meski tanpa crash sekalipun.

= 1.1.2 =
* **KRITIS**: perbaiki "Telah terjadi eror kritis pada situs web ini" saat
  menyimpan Pengaturan. Callback sanitasi Settings API memanggil
  `update_option()` sendiri, padahal `update_option()` selalu memicu ulang
  callback yang sama — menyebabkan rekursi tak berhenti sampai memori PHP
  habis. Terjadi pada SETIAP penyimpanan Pengaturan lewat form wp-admin,
  tanpa kecuali, sejak rilis pertama.

= 1.1.1 =
* **PENTING**: perbaiki tanda tangan HMAC — server memvalidasi terhadap path
  lengkap (`/openapi/v1/...`), plugin menandatangani path relatif. Semua
  permintaan sebelumnya ditolak `INVALID_SIGNATURE`.
* **PENTING**: perbaiki sinkronisasi artikel — kirim `portal_id` yang sudah
  diisi di Pengaturan. Tanpa ini, artikel dari SEMUA portal milik media
  company yang sama ikut ter-import (kebocoran lintas-portal).
* Perbaiki pembacaan respons `/articles`: field yang benar adalah `items`,
  bukan `articles` — sinkronisasi sebelumnya selalu mengimpor 0 artikel.

= 1.1.0 =
* Rebrand ke Inova CMS, dukungan inova.id

= 1.0.0 =
* Rilis awal
* Fitur F1: Sinkronisasi artikel CMS → WordPress
* HMAC-signed HTTP client
* Admin UI: Pengaturan, Riwayat, Status
