import type { Author } from "@/types";

export const authors: Author[] = [
  {
    id: "au-1",
    slug: "rangga-pratama",
    name: "Rangga Pratama",
    role: "Redaktur Pelaksana",
    avatar: "https://i.pravatar.cc/240?img=12",
    bio: "Memimpin meja redaksi media ini. Menulis isu politik dan kebijakan publik lebih dari satu dekade.",
    socials: { twitter: "https://twitter.com/" },
  },
  {
    id: "au-2",
    slug: "sari-wulandari",
    name: "Sari Wulandari",
    role: "Jurnalis Ekonomi",
    avatar: "https://i.pravatar.cc/240?img=45",
    bio: "Meliput makroekonomi, pasar, dan UMKM. Percaya data yang jujur mengalahkan opini yang nyaring.",
    socials: { twitter: "https://twitter.com/" },
  },
  {
    id: "au-3",
    slug: "dimas-nugroho",
    name: "Dimas Nugroho",
    role: "Editor Teknologi",
    avatar: "https://i.pravatar.cc/240?img=33",
    bio: "Mengulas startup, kecerdasan buatan, dan dampak teknologi pada keseharian.",
    socials: { instagram: "https://instagram.com/" },
  },
  {
    id: "au-4",
    slug: "ayu-lestari",
    name: "Ayu Lestari",
    role: "Kontributor Gaya Hidup",
    avatar: "https://i.pravatar.cc/240?img=47",
    bio: "Menulis tentang kota, kesehatan, dan cara hidup yang lebih berkelanjutan.",
    socials: { instagram: "https://instagram.com/" },
  },
  {
    id: "au-5",
    slug: "budi-santoso",
    name: "Budi Santoso",
    role: "Lead Automotive Journalist",
    avatar: "https://i.pravatar.cc/240?img=60",
    bio: "Spesialis pengujian kendaraan listrik, efisiensi konsumsi baterai, dan infrastruktur mobilitas hijau Indonesia.",
    socials: { twitter: "https://twitter.com/" },
  },
];

export const authorBySlug = (slug: string) =>
  authors.find((a) => a.slug === slug);
