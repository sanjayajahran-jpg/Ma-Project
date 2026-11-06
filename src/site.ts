import { getActivePortalDomain } from "@/lib/api";

const defaultEnvSiteName = import.meta.env.PUBLIC_SITE_NAME;
const siteName = defaultEnvSiteName ?? "Portal Media";
const sitePublisher = import.meta.env.PUBLIC_SITE_PUBLISHER ?? siteName;
const siteDomain = import.meta.env.PUBLIC_PORTAL_DOMAIN ?? "berdayanews.com";
const siteUrl = import.meta.env.PUBLIC_SITE_URL ?? `https://${siteDomain}`;

interface PortalProfile {
  email?: string;
  tagline?: string;
  description?: string;
  address?: { street: string; city: string; mapUrl?: string };
  social?: { twitter: string; instagram: string; youtube: string };
  defaultTheme?: string;
}

const PORTAL_PROFILES: Record<string, PortalProfile> = {
  "faishion.id": {
    email: "onetyrr@gmail.com",
    tagline: "Inspirasimu tampil stylish tanpa ribet",
    description: "Faishion hadir sebagai ruang inspirasi bagi siapa saja yang ingin tampil stylish tanpa ribet.",
    address: { street: "Jalan Raya Pajajaran No. 40, Baranangsiang", city: "Bogor" },
    social: { twitter: "#", instagram: "https://instagram.com/faishion.id", youtube: "#" },
    defaultTheme: "minimal-daily",
  },
  "pearlskin.id": {
    email: "afraadnanath@gmail.com",
    tagline: "Know Your Skin, Know Your Glow",
    description: "Pearlskin.id adalah portal beauty & skincare yang fokus pada edukasi skincare routine.",
    address: { street: "Jalan Cinangka Raya, Kelurahan Serua", city: "Depok" },
    social: { twitter: "#", instagram: "https://instagram.com/pearskinid", youtube: "#" },
    defaultTheme: "minimal-daily",
  },
  "naranta.id": {
    email: "dickyilhamnudin29@gmail.com",
    tagline: "Portal berita politik, film, dan musik",
    description: "Naranta.id adalah portal berita digital Indonesia yang berfokus pada pemberitaan politik serta industri hiburan.",
    address: { street: "Kp. Cinangka RT. 05/RW. 02", city: "Bogor" },
    social: { twitter: "#", instagram: "#", youtube: "#" },
    defaultTheme: "magazine-feature",
  },
  "dipojokin.id": {
    email: "redaksi@dipojokin.id",
    tagline: "Media santai untuk keresahan sehari-hari",
    description: "Dipojokin.id memakai gaya jurnalisme alternatif berbasis esai, opini personal, dan satire.",
    address: { street: "Jl. RE. Martadinata No.25", city: "Bogor" },
    social: { twitter: "#", instagram: "#", youtube: "#" },
    defaultTheme: "magazine-feature",
  },
  "gamingnews.id": {
    email: "redaksi@gamingnews.id",
    tagline: "Informasi gaming terkini dan terupdate",
    description: "Gamingnews.id menyajikan informasi gaming terkini dan terupdate, serta informasi teknologi game.",
    address: { street: "Jl. RE. Martadinata No.25", city: "Bogor" },
    social: { twitter: "#", instagram: "#", youtube: "#" },
    defaultTheme: "gaming-arena",
  },
  "awasi.id": {
    email: "redaksi@awasi.id",
    tagline: "Informasi cepat, tajam, dan tepercaya",
    description: "Awasi.id menyajikan berita utama terkini dengan liputan kilat dan analisis mendalam.",
    address: { street: "Jakarta, Indonesia", city: "Jakarta" },
    social: { twitter: "https://x.com/awasiid", instagram: "https://instagram.com/awasi.id", youtube: "#" },
    defaultTheme: "breaking-wire",
  },
  "berdayanews.com": {
    email: "redaksi@berdayanews.com",
    tagline: "Media pemberdayaan masyarakat & ekonomi kreatif",
    description: "Berdaya News menyajikan kisah inspiratif, pemberdayaan UMKM, dan informasi sosial relevan.",
    address: { street: "Bandung, Jawa Barat", city: "Bandung" },
    social: { twitter: "#", instagram: "https://instagram.com/berdayanews", youtube: "#" },
    defaultTheme: "berdaya",
  },
  "photostory.id": {
    email: "redaksi@photostory.id",
    tagline: "Cerita dunia dalam setiap bingkai foto",
    description: "PhotoStory.id adalah portal jurnalisme foto visual yang mengedepankan narasi gambar.",
    address: { street: "Yogyakarta, Indonesia", city: "Yogyakarta" },
    social: { twitter: "#", instagram: "#", youtube: "#" },
    defaultTheme: "photo-story",
  },
  "videofirst.id": {
    email: "redaksi@videofirst.id",
    tagline: "Kabar terkini dalam sajian tayangan video",
    description: "VideoFirst.id menghadirkan tayangan liputan eksklusif dan berita multimedia.",
    address: { street: "Jakarta, Indonesia", city: "Jakarta" },
    social: { twitter: "#", instagram: "#", youtube: "#" },
    defaultTheme: "video-first",
  },
  "corporatemedia.id": {
    email: "redaksi@corporatemedia.id",
    tagline: "Analisis bisnis, finansial, dan korporasi",
    description: "Corporate Media menyajikan wawasan ekonomi profesional dan tren pasar.",
    address: { street: "Jakarta, Indonesia", city: "Jakarta" },
    social: { twitter: "#", instagram: "#", youtube: "#" },
    defaultTheme: "corporate-media",
  },
  "promedia.id": {
    email: "redaksi@promedia.id",
    tagline: "Jaringan portal berita terdepan nusantara",
    description: "Promedia.id menghubungkan berbagai liputan berita tanah air.",
    address: { street: "Surabaya, Jawa Timur", city: "Surabaya" },
    social: { twitter: "#", instagram: "#", youtube: "#" },
    defaultTheme: "promedia",
  },
  "motorlistrik.com": {
    email: "redaksi@evnesia.id",
    tagline: "Portal Berita, Panduan, Spesifikasi & Komparasi Kendaraan Listrik Indonesia",
    description: "EVnesia — Portal Informasi Terdepan Seputar Kendaraan Listrik di Indonesia.",
    address: { street: "Jl. Elektrifikasi Hijau No. 88", city: "Jakarta Selatan" },
    social: { twitter: "https://x.com/evnesia", instagram: "https://instagram.com/evnesia.id", youtube: "https://youtube.com/@evnesia" },
    defaultTheme: "automotive",
  },
  "motorlistrik.id": {
    email: "redaksi@evnesia.id",
    tagline: "Portal Berita, Panduan, Spesifikasi & Komparasi Kendaraan Listrik Indonesia",
    description: "EVnesia — Portal Informasi Terdepan Seputar Kendaraan Listrik di Indonesia.",
    address: { street: "Jl. Elektrifikasi Hijau No. 88", city: "Jakarta Selatan" },
    social: { twitter: "https://x.com/evnesia", instagram: "https://instagram.com/evnesia.id", youtube: "https://youtube.com/@evnesia" },
    defaultTheme: "automotive",
  },
  "evhub.id": {
    email: "redaksi@evhub.id",
    tagline: "Media Informasi, Panduan & Komparasi Mobil Listrik & Hybrid Indonesia",
    description: "EVHub — Portal Media & Pusat Data Kendaraan Elektrifikasi (BEV, PHEV, HEV) di Indonesia. Ulasan pengujian jalan riil, katalog spesifikasi teknis brosur, komparasi trim varian, dan kalkulator kehematan SPKLU.",
    address: { street: "Jl. Elektrifikasi Hijau No. 88", city: "Jakarta Selatan" },
    social: { twitter: "https://x.com/evhub_id", instagram: "https://instagram.com/evhub.id", youtube: "https://youtube.com/@evhub" },
    defaultTheme: "automotive",
  },
  "evnesia.id": {
    email: "redaksi@evnesia.id",
    tagline: "Media Informasi, Panduan & Komparasi Mobil Listrik & Hybrid Indonesia",
    description: "EVnesia — Portal Media & Pusat Data Kendaraan Elektrifikasi (BEV, PHEV, HEV, FCEV) di Indonesia. Ulasan pengujian jalan riil, katalog spesifikasi teknis brosur, komparasi trim varian, dan kalkulator kehematan SPKLU.",
    address: { street: "Jl. Elektrifikasi Hijau No. 88", city: "Jakarta Selatan" },
    social: { twitter: "https://x.com/evnesia", instagram: "https://instagram.com/evnesia.id", youtube: "https://youtube.com/@evnesia" },
    defaultTheme: "automotive",
  },
  "evnesia.com": {
    email: "redaksi@evnesia.com",
    tagline: "Media Informasi, Panduan & Komparasi Mobil Listrik & Hybrid Indonesia",
    description: "EVnesia — Portal Media & Pusat Data Kendaraan Elektrifikasi (BEV, PHEV, HEV, FCEV) di Indonesia.",
    address: { street: "Jl. Elektrifikasi Hijau No. 88", city: "Jakarta Selatan" },
    social: { twitter: "https://x.com/evnesia", instagram: "https://instagram.com/evnesia.id", youtube: "https://youtube.com/@evnesia" },
    defaultTheme: "automotive",
  },
  "autodrive.id": {
    email: "redaksi@evnesia.id",
    tagline: "Media Informasi, Panduan & Komparasi Mobil Listrik & Hybrid Indonesia",
    description: "EVnesia (AutoDrive) — Portal Media & Pusat Data Kendaraan Elektrifikasi di Indonesia.",
    address: { street: "Jl. Elektrifikasi Hijau No. 88", city: "Jakarta Selatan" },
    social: { twitter: "#", instagram: "https://instagram.com/evnesia.id", youtube: "#" },
    defaultTheme: "automotive",
  },
  "autodrive.com": {
    email: "redaksi@evnesia.com",
    tagline: "Media Informasi, Panduan & Komparasi Mobil Listrik & Hybrid Indonesia",
    description: "EVnesia — Portal Media & Pusat Data Kendaraan Elektrifikasi di Indonesia.",
    address: { street: "Jl. Elektrifikasi Hijau No. 88", city: "Jakarta Selatan" },
    social: { twitter: "#", instagram: "https://instagram.com/evnesia.id", youtube: "#" },
    defaultTheme: "automotive",
  },
  "regionalnetwork.id": {
    email: "redaksi@regionalnetwork.id",
    tagline: "Suara daerah untuk pembaca Indonesia",
    description: "Regional Network menyajikan kabar daerah dan pembangunan kawasan nusantara.",
    address: { street: "Semarang, Jawa Tengah", city: "Semarang" },
    social: { twitter: "#", instagram: "#", youtube: "#" },
    defaultTheme: "regional-network",
  },
};

export function defaultThemeForDomain(domain: string): string {
  const clean = domain.trim().toLowerCase().replace(/^www\./, "");
  if (PORTAL_PROFILES[clean]?.defaultTheme) {
    return PORTAL_PROFILES[clean].defaultTheme!;
  }
  if (clean === "awasi.id") return "breaking-wire";
  if (clean === "berdayanews.com") return "berdaya";
  if (clean.includes("evnesia") || clean.includes("auto") || clean.includes("mobil") || clean.includes("motor") || clean.includes("otomotif") || clean.includes("drive") || clean.includes("listrik")) return "automotive";
  if (clean.includes("gaming")) return "gaming-arena";
  if (clean.includes("faishion") || clean.includes("pearlskin")) return "minimal-daily";
  if (clean.includes("naranta") || clean.includes("dipojokin")) return "magazine-feature";
  return "automotive";
}

export function portalIdentityForDomain(domain: string, name?: string | null) {
  const clean = domain.trim().toLowerCase().replace(/^www\./, "") || siteDomain;
  const profile = PORTAL_PROFILES[clean];
  const derivedName = name?.trim() ||
    (defaultEnvSiteName && clean === siteDomain ? defaultEnvSiteName : null) ||
    (clean === "awasi.id" ? "AWASI.ID" : clean === "berdayanews.com" ? "Berdaya News" : siteNameFromDomain(clean));

  const email = siteEmailForDomain(clean);
  const partnershipEmail =
    clean === "awasi.id" ? "kerjasama@awasi.id" : clean === "berdayanews.com" ? "kerjasama@berdayanews.com" : email;

  return {
    name: derivedName,
    publisher: derivedName,
    domain: clean,
    email,
    partnershipEmail,
    social: siteSocialForDomain(clean),
    tagline: profile?.tagline ?? "Media profesional, cepat, dan relevan.",
    description: profile?.description ?? `${derivedName} menyajikan berita, analisis, dan liputan profesional yang relevan untuk pembaca Indonesia.`,
    address: profile?.address ?? { street: "Indonesia", city: "" },
  };
}

export function siteEmailForDomain(domain: string) {
  const clean = domain.trim().toLowerCase().replace(/^www\./, "") || siteDomain;
  const profile = PORTAL_PROFILES[clean];
  if (profile?.email) return profile.email;
  if (clean === "awasi.id") return "redaksi@awasi.id";
  if (clean === "berdayanews.com") return "redaksi@berdayanews.com";
  return `redaksi@${clean}`;
}

export function siteSocialForDomain(domain: string) {
  const clean = domain.trim().toLowerCase().replace(/^www\./, "");
  const profile = PORTAL_PROFILES[clean];
  if (profile?.social) return profile.social;
  if (clean === "awasi.id") {
    return {
      twitter: "https://x.com/awasiid",
      instagram: "https://instagram.com/awasi.id",
      youtube: "https://youtube.com/@awasiid",
    };
  }
  if (clean === "berdayanews.com") {
    return {
      twitter: "https://x.com/berdayanews",
      instagram: "https://instagram.com/berdayanews",
      youtube: "https://youtube.com/@berdayanews",
    };
  }
  return {
    twitter: "#",
    instagram: "#",
    youtube: "#",
  };
}

export function portalAddressForDomain(domain: string) {
  const clean = domain.trim().toLowerCase().replace(/^www\./, "") || siteDomain;
  return PORTAL_PROFILES[clean]?.address ?? null;
}

function siteNameFromDomain(domain: string) {
  return domain
    .split(".")[0]
    ?.split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ") || siteName;
}

export const SITE = new Proxy({} as any, {
  get(_target, prop) {
    const activeDomain = getActivePortalDomain();
    const identity = portalIdentityForDomain(activeDomain);
    if (prop === "name") return identity.name;
    if (prop === "publisher") return identity.publisher;
    if (prop === "domain") return identity.domain;
    if (prop === "email") return identity.email;
    if (prop === "tagline") return identity.tagline;
    if (prop === "description") return identity.description;
    if (prop === "social") return identity.social;
    if (prop === "address") return identity.address;
    if (prop === "url") return `https://${identity.domain}`;
    if (prop === "locale") return "id-ID";
    return (identity as any)[prop];
  }
});

/** Item navigasi utama (slug merujuk ke kategori). */
export const NAV = [
  { label: "Politik", href: "/kategori/politik" },
  { label: "Ekonomi", href: "/kategori/ekonomi" },
  { label: "Teknologi", href: "/kategori/teknologi" },
  { label: "Gaya Hidup", href: "/kategori/gaya-hidup" },
  { label: "Olahraga", href: "/kategori/olahraga" },
  { label: "Opini", href: "/kategori/opini" },
];

export const FOOTER_LINKS = [
  {
    title: "Informasi",
    links: [
      { label: "Tentang Kami", href: "/tentang" },
      { label: "Redaksi", href: "/redaksi" },
      { label: "Kontak", href: "/kontak" },
    ],
  },
  {
    title: "Kerja Sama",
    links: [
      { label: "Pasang Iklan", href: "/pasang-iklan" },
      { label: "Pedoman Konten Bersponsor", href: "/disclosure" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Kebijakan Privasi", href: "/privasi" },
      { label: "Pedoman Media Siber", href: "/pedoman-pemberitaan" },
      { label: "Pedoman AI", href: "/pedoman-ai" },
    ],
  },
];
