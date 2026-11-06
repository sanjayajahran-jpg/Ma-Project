import type { Article } from "@/types";
import { articles as baseArticles } from "./articles";

export interface RegionCorridor {
  slug: string;
  name: string;
  shortName: string;
  provinces: string[];
}

export const REGION_CORRIDORS: RegionCorridor[] = [
  { slug: "semua", name: "Semua Nusantara", shortName: "Semua", provinces: [] },
  { slug: "sumatra", name: "Sumatra", shortName: "Sumatra", provinces: ["Aceh", "Sumut", "Sumbar", "Riau", "Kepri", "Jambi", "Sumsel", "Babel", "Bengkulu", "Lampung"] },
  { slug: "jawa-bali", name: "Jawa & Bali", shortName: "Jawa-Bali", provinces: ["DKI Jakarta", "Jabar", "Banten", "Jateng", "DIY", "Jatim", "Bali"] },
  { slug: "kalimantan", name: "Kalimantan", shortName: "Kalimantan", provinces: ["Kalbar", "Kalteng", "Kalsel", "Kaltim", "Kaltara"] },
  { slug: "sulawesi", name: "Sulawesi", shortName: "Sulawesi", provinces: ["Sulut", "Gorontalo", "Sulteng", "Sulbar", "Sulsel", "Sultra"] },
  { slug: "maluku-nusa-tenggara", name: "Maluku & Nusa Tenggara", shortName: "Maluku-Nusa", provinces: ["NTB", "NTT", "Maluku", "Malut"] },
  { slug: "papua", name: "Papua", shortName: "Papua", provinces: ["Papua", "Papua Barat", "Papua Selatan", "Papua Tengah", "Papua Pegunungan"] },
];

export interface CommodityPrice {
  name: string;
  unit: string;
  nationalAvg: number;
  changePercent: number; // positive = up, negative = down, 0 = stable
  topRegion: string;
  topPrice: number;
}

export const COMMODITY_PRICES: CommodityPrice[] = [
  { name: "Beras Medium", unit: "kg", nationalAvg: 13500, changePercent: -0.8, topRegion: "Sumatra Barat", topPrice: 14200 },
  { name: "Cabai Merah Keriting", unit: "kg", nationalAvg: 42000, changePercent: 3.5, topRegion: "Jawa Tengah", topPrice: 45000 },
  { name: "Minyak Goreng Curah", unit: "liter", nationalAvg: 15800, changePercent: 0.0, topRegion: "Sulawesi Selatan", topPrice: 16000 },
  { name: "Daging Sapi Segar", unit: "kg", nationalAvg: 138000, changePercent: 1.2, topRegion: "DKI Jakarta", topPrice: 145000 },
];

export interface CitizenReport {
  id: string;
  title: string;
  location: string;
  regionSlug: string;
  category: "Jalan & Infrastruktur" | "Pelayanan Publik" | "Fasilitas Kesehatan" | "Air & Energi";
  status: "Diproses Pemda" | "Selesai Ditindaklanjuti" | "Verifikasi Redaksi";
  date: string;
  upvotes: number;
}

export const CITIZEN_REPORTS: CitizenReport[] = [
  {
    id: "cr-01",
    title: "Perbaikan Jembatan Penghubung Antar-Desa di Kab. Lahat Mulai Direalisasikan",
    location: "Lahat, Sumatera Selatan",
    regionSlug: "sumatra",
    category: "Jalan & Infrastruktur",
    status: "Selesai Ditindaklanjuti",
    date: "10 Agt 2026",
    upvotes: 248,
  },
  {
    id: "cr-02",
    title: "Layanan Puskesmas Pembantu di Pesisir Bone Butuh Peremajaan Alat Medis",
    location: "Bone, Sulawesi Selatan",
    regionSlug: "sulawesi",
    category: "Fasilitas Kesehatan",
    status: "Diproses Pemda",
    date: "09 Agt 2026",
    upvotes: 189,
  },
  {
    id: "cr-03",
    title: "Aspirasi Warga: Penambahan Penerangan Jalan Umum di Jalur Trans Kalimantan",
    location: "Palangkaraya, Kalimantan Tengah",
    regionSlug: "kalimantan",
    category: "Jalan & Infrastruktur",
    status: "Verifikasi Redaksi",
    date: "08 Agt 2026",
    upvotes: 142,
  },
];

/** Regional news articles mapped to specific island corridors */
export const REGIONAL_ARTICLES: (Article & { regionSlug: string; regionName: string; locationName: string })[] = [
  {
    ...baseArticles[0],
    id: "reg-01",
    slug: "tol-trans-sumatra-seksi-baru-diresmikan",
    title: "Seksi Baru Tol Trans-Sumatra Diresmikan: Waktu Tempuh Medan-Tebing Tinggi Kian Ringkas",
    dek: "Pemerintah daerah optimis konektivitas anyar ini mempercepat distribusi komoditas unggulan perkebunan dan kelautan.",
    cover: "https://picsum.photos/seed/sumatra-highway/1280/720",
    coverAlt: "Jalan tol baru membentang di Sumatra",
    regionSlug: "sumatra",
    regionName: "Sumatra",
    locationName: "Medan, Sumut",
    publishedAt: "2026-08-11T08:00:00+07:00",
  },
  {
    ...baseArticles[1],
    id: "reg-02",
    slug: "inovasi-pemda-banyuwangi-digitalisasi-pelayanan-publik",
    title: "Inovasi Pemda Banyuwangi: Mal Pelayanan Publik Digital Jangkau Desa Terpencil",
    dek: "Pengurusan dokumen kependudukan kini dapat tuntas di kantor desa dalam kurun waktu kurang dari 15 menit.",
    cover: "https://picsum.photos/seed/banyuwangi-service/1280/720",
    coverAlt: "Warga mengurus administrasi di pusat pelayanan publik",
    regionSlug: "jawa-bali",
    regionName: "Jawa & Bali",
    locationName: "Banyuwangi, Jatim",
    publishedAt: "2026-08-10T14:30:00+07:00",
  },
  {
    ...baseArticles[4],
    id: "reg-03",
    slug: "local-heroes-perajin-tenun-ikot-sikka-tembus-pasar-eropa",
    title: "Local Heroes: Perajin Tenun Ikat Sikka Menggoyahkan Pasar Kriya Eropa",
    dek: "Sentuhan pewarna alami kelor dan indigo menjadikan kriya lokal NTT diburu desainer internasional.",
    cover: "https://picsum.photos/seed/tenun-sikka/1280/720",
    coverAlt: "Perajin kain tenun ikat tradisional",
    regionSlug: "maluku-nusa-tenggara",
    regionName: "Maluku & Nusa Tenggara",
    locationName: "Maumere, NTT",
    publishedAt: "2026-08-10T11:15:00+07:00",
  },
  {
    ...baseArticles[3],
    id: "reg-04",
    slug: "pelabuhan-semayang-balikpapan-digenjot-jadi-hub-logistik-ikn",
    title: "Pelabuhan Semayang Balikpapan Digenjot Jadi Hub Logistik Utama Kalimantan",
    dek: "Peningkatan kapasitas dermaga dan integrasi sistem bea cukai memperlancar arus barang pendukung kawasan ekonomi.",
    cover: "https://picsum.photos/seed/balikpapan-port/1280/720",
    coverAlt: "Aktivitas bongkar muat kontainer pelabuhan",
    regionSlug: "kalimantan",
    regionName: "Kalimantan",
    locationName: "Balikpapan, Kaltim",
    publishedAt: "2026-08-09T16:45:00+07:00",
  },
  {
    ...baseArticles[2],
    id: "reg-05",
    slug: "komoditas-kakao-sulsel-raih-sertifikasi-organik-global",
    title: "Komoditas Kakao Petani Luwu Utara Raih Sertifikasi Organik Standar Global",
    dek: "Pendampingan kemitraan mendorong nilai tambah ekspor biji cokelat lokal hingga naik 40 persen.",
    cover: "https://picsum.photos/seed/sulawesi-cocoa/1280/720",
    coverAlt: "Petani memanen buah kakao segar",
    regionSlug: "sulawesi",
    regionName: "Sulawesi",
    locationName: "Luwu Utara, Sulsel",
    publishedAt: "2026-08-09T09:20:00+07:00",
  },
  {
    ...baseArticles[6],
    id: "reg-06",
    slug: "pemberdayaan-energi-surya-mandiri-di-keerom-papua",
    title: "Kemandirian Energi: Pembangkit Listrik Surya Komunitas Terang di Keerom Papua",
    dek: "Inisiatif pemuda lokal memanfaatkan potensi sinar matahari untuk menerangi fasilitas umum dan sekolah desa.",
    cover: "https://picsum.photos/seed/papua-solar/1280/720",
    coverAlt: "Panel surya terpasang di desa perbatasan",
    regionSlug: "papua",
    regionName: "Papua",
    locationName: "Keerom, Papua",
    publishedAt: "2026-08-08T13:10:00+07:00",
  },
];
