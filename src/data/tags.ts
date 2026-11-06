import type { Tag } from "@/types";

export const tags: Record<string, Tag> = {
  pemilu: { slug: "pemilu", name: "Pemilu" },
  kebijakan: { slug: "kebijakan", name: "Kebijakan Publik" },
  apbn: { slug: "apbn", name: "APBN" },
  startup: { slug: "startup", name: "Startup" },
  ai: { slug: "ai", name: "Kecerdasan Buatan" },
  umkm: { slug: "umkm", name: "UMKM" },
  fintech: { slug: "fintech", name: "Fintech" },
  inflasi: { slug: "inflasi", name: "Inflasi" },
  esg: { slug: "esg", name: "ESG" },
  energi: { slug: "energi", name: "Transisi Energi" },
  kesehatan: { slug: "kesehatan", name: "Kesehatan" },
  kota: { slug: "kota", name: "Urban" },
  sepakbola: { slug: "sepakbola", name: "Sepak Bola" },
  timnas: { slug: "timnas", name: "Timnas" },
  gawai: { slug: "gawai", name: "Gawai" },
  etika: { slug: "etika", name: "Etika" },
  ev: { slug: "ev", name: "Mobil Listrik" },
  baterai: { slug: "baterai", name: "Baterai & Pengisian" },
  spklu: { slug: "spklu", name: "SPKLU" },
  otomotif: { slug: "otomotif", name: "Otomotif" },
};

export const tagBySlug = (slug: string): Tag | undefined => tags[slug];
