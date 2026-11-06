# CMS Media — Frontend Publik

Frontend publik multi-portal berbasis Astro 7 dan Tailwind v4. Tampilan dan
identitas portal diambil dari CMS API berdasarkan domain request, sehingga
repository ini dapat dipakai sebagai dasar untuk customisasi tampilan portal.

## Menjalankan

```bash
pnpm install
pnpm dev       # http://localhost:4321
pnpm build     # build SSR ke dist/
pnpm preview   # pratinjau hasil build
```

Untuk menjalankan portal tertentu, salin `.env.example` menjadi `.env` lalu
isi domain dan endpoint API:

```bash
PUBLIC_PORTAL_DOMAIN=evnesia.id
PUBLIC_SITE_URL=https://evnesia.id
PUBLIC_API_URL=https://api-cms.bukin.id/api/v1
SERVER_API_URL=https://api-cms.bukin.id/api/v1
PUBLIC_USE_FALLBACK_DATA=true
PUBLIC_THEME=Automotive
```

`SERVER_API_URL` dipakai oleh rendering SSR, sedangkan `PUBLIC_API_URL` dipakai
oleh browser. Jangan masukkan token atau kredensial ke environment frontend.

Untuk mengembangkan tema tertentu secara lokal, isi `PUBLIC_THEME` di `.env`,
misalnya `PUBLIC_THEME=Automotive`. Resolver akan memakai tema dari `src/themes/`
tersebut dan mengabaikan template yang dipilih CMS. API tetap dipakai untuk
mengambil artikel, identitas portal, brand, dan konfigurasi konten lainnya.
Restart server setelah mengubah `.env`.

## Struktur

```
src/
├── data/          # MOCK DATA — pengganti API (articles, categories, authors, tags)
├── components/     # ArticleCard, Header, Footer, ShareButtons, TOC, dll.
├── layouts/        # BaseLayout (head/SEO/JSON-LD), PageLayout (halaman statis)
├── pages/          # rute: beranda, [kategori]/[slug], kategori/, tag/, penulis/, cari, statis, rss.xml
├── lib/format.ts   # util tanggal/angka, ekstrak TOC
├── site.ts         # konfigurasi situs + navigasi
└── styles/global.css  # design token (@theme) + base + prose
```

## Halaman

- `/` — beranda (hero, terbaru, trending, blok kategori, konten kerjasama)
- `/[kategori]/[slug]` — artikel (byline, TOC, share, terkait, prev/next, label bersponsor)
- `/kategori/[slug]`, `/tag/[slug]`, `/penulis/[slug]` — arsip
- `/cari` — pencarian klien (progressive enhancement)
- `/tentang`, `/redaksi`, `/kontak`, `/pasang-iklan`, `/privasi`, `/disclosure`
- `/rss.xml`, `/sitemap-index.xml`, `/404`

## Customisasi tampilan

- Tema berada di `src/themes/`.
- Resolver tema berada di `src/lib/theme-resolver.ts`.
- Komponen global, API client, dan tipe berada di `src/lib/`, `src/components/`,
  dan `src/types.ts`.
- Tema aktif ditentukan oleh konfigurasi template portal di CMS; perubahan
  desain dapat dikembangkan dan diuji tanpa mengubah backend.
