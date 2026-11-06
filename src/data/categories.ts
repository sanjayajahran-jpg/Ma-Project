import type { Category } from "@/types";

export const categories: Category[] = [
  {
    id: "ct-1",
    slug: "politik",
    name: "Politik",
    description:
      "Liputan dan analisis kekuasaan, kebijakan, dan dinamika pemerintahan.",
    color: "politik",
  },
  {
    id: "ct-2",
    slug: "ekonomi",
    name: "Ekonomi",
    description:
      "Makroekonomi, pasar, bisnis, dan denyut keuangan rumah tangga.",
    color: "ekonomi",
  },
  {
    id: "ct-3",
    slug: "teknologi",
    name: "Teknologi",
    description: "Startup, kecerdasan buatan, gawai, dan masa depan digital.",
    color: "teknologi",
  },
  {
    id: "ct-4",
    slug: "gaya-hidup",
    name: "Gaya Hidup",
    description: "Kota, kesehatan, budaya, dan cara hidup masa kini.",
    color: "gaya-hidup",
  },
  {
    id: "ct-5",
    slug: "olahraga",
    name: "Olahraga",
    description: "Taktik, prestasi, dan kisah di balik lapangan.",
    color: "olahraga",
  },
  {
    id: "ct-6",
    slug: "opini",
    name: "Opini",
    description: "Gagasan dan argumen dari para penulis media ini.",
    color: "opini",
  },
  {
    id: "ct-7",
    slug: "ulasan",
    name: "Ulasan & Test Drive",
    description: "Review mendalam, pengujian konsumsi baterai, performa motor, dan kenyamanan mobil listrik.",
    color: "ulasan",
  },
  {
    id: "ct-8",
    slug: "ulasan-test-drive",
    name: "Ulasan Test Drive",
    description: "Pengujian jalan raya, efisiensi konsumsi daya, dan perbandingan varian trim mobil listrik.",
    color: "ulasan",
  },
  {
    id: "ct-9",
    slug: "spklu",
    name: "Ekosistem & SPKLU",
    description: "Jaringan stasiun pengisian kendaraan listrik umum, tarif daya, dan panduan home charging.",
    color: "spklu",
  },
  {
    id: "ct-10",
    slug: "berita",
    name: "Berita Otomotif",
    description: "Kabar terkini seputar industri kendaraan listrik dan otomotif nasional.",
    color: "berita",
  },
  {
    id: "ct-11",
    slug: "panduan",
    name: "Panduan Pembeli",
    description: "Tips memilih mobil listrik, perbandingan biaya kepemilikan, dan insentif pemerintah.",
    color: "panduan",
  },
];

export const categoryBySlug = (slug: string) =>
  categories.find((c) => c.slug === slug);
