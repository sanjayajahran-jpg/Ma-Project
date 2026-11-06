/** Util format lokal Indonesia. */

const DATE_FMT = new Intl.DateTimeFormat("id-ID", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "Asia/Jakarta",
});

const TIME_FMT = new Intl.DateTimeFormat("en-GB", {
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
  timeZone: "Asia/Jakarta",
});

export function formatDate(iso: string): string {
  return DATE_FMT.format(new Date(iso));
}

/**
 * Format waktu publikasi untuk tampilan artikel.
 *
 * Artikel berumur kurang dari 12 jam menampilkan waktu relatif. Setelah itu,
 * tampilkan tanggal dan jam publikasi agar pembaca mendapat waktu yang pasti.
 */
export function formatPublicationTime(iso: string, now: Date = new Date()): string {
  const publishedAt = new Date(iso);
  if (Number.isNaN(publishedAt.getTime())) return iso;

  const date = formatDate(iso);
  const diffMs = now.getTime() - publishedAt.getTime();
  const twelveHoursMs = 12 * 60 * 60 * 1000;

  if (diffMs >= 0 && diffMs < twelveHoursMs) {
    const minutes = Math.floor(diffMs / (60 * 1000));
    if (minutes < 60) return `${date} ${Math.max(1, minutes)} menit lalu`;
    return `${date} ${Math.floor(minutes / 60)} jam lalu`;
  }

  return `${date} ${TIME_FMT.format(publishedAt)}`;
}

/** "3 jam lalu", "2 hari lalu", atau tanggal jika lama. */
export function timeAgo(iso: string, now: Date = new Date()): string {
  const d = new Date(iso);
  const diff = Math.round((now.getTime() - d.getTime()) / 1000);
  const min = Math.round(diff / 60);
  const hr = Math.round(diff / 3600);
  const day = Math.round(diff / 86400);
  if (diff < 60) return "baru saja";
  if (min < 60) return `${min} menit lalu`;
  if (hr < 24) return `${hr} jam lalu`;
  if (day < 7) return `${day} hari lalu`;
  return formatDate(iso);
}

/** 1234 -> "1,2 rb", 1200000 -> "1,2 jt" */
export function formatViews(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(".", ",")} jt`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1).replace(".", ",")} rb`;
  return String(n);
}

/** ISO -> "2026-06-29" (untuk <time datetime>) */
export function isoDate(iso: string): string {
  return new Date(iso).toISOString().slice(0, 10);
}

/** Ekstrak daftar isi dari heading <h2 id="..">..</h2> pada body HTML. */
export function extractToc(html: string): { id: string; text: string }[] {
  const out: { id: string; text: string }[] = [];
  const re = /<h2[^>]*\bid="([^"]+)"[^>]*>(.*?)<\/h2>/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html)) !== null) {
    out.push({ id: m[1], text: m[2].replace(/<[^>]+>/g, "").trim() });
  }
  return out;
}

interface BacaJugaItem {
  slug: string;
  title: string;
  categorySlug: string;
}

function bacaJugaHtml(items: BacaJugaItem[]): string {
  const links = items
    .map(
      (a) =>
        `<li><a href="/${a.categorySlug}/${a.slug}" class="font-semibold text-ink hover:text-brand">${a.title}</a></li>`,
    )
    .join("");
  return `<aside class="my-6 rounded-card border border-line bg-cream p-5 not-prose"><h2 class="kicker text-faint">Baca Juga</h2><ul class="mt-2 space-y-2">${links}</ul></aside>`;
}

/**
 * Sisipkan blok "Baca Juga" ke dalam body HTML artikel:
 * - Setelah paragraf ke-2: 1 link
 * - Setelah paragraf ke-4: 2 link
 * Sisa link (jika ada) tetap dirender di posisi awal.
 */
export function injectBacaJuga(
  bodyHtml: string,
  items: BacaJugaItem[],
): { html: string; remaining: BacaJugaItem[] } {
  if (!items.length) return { html: bodyHtml, remaining: [] };

  const parts = bodyHtml.split("</p>");
  if (parts.length < 3) return { html: bodyHtml, remaining: items };

  let idx = 0;

  // Batch 1: 1 item setelah paragraf 2
  const batch1 = items[idx] ? [items[idx++]] : [];

  // Batch 2: 2 item setelah paragraf 4
  const batch2 = items.slice(idx, idx + 2);
  idx += batch2.length;

  const remaining = items.slice(idx);

  const firstChunk = parts.slice(0, 2).join("</p>") + "</p>";
  const inject1 = batch1.length ? bacaJugaHtml(batch1) : "";

  let result: string;

  if (parts.length >= 5) {
    const midChunk = parts.slice(2, 4).join("</p>") + "</p>";
    const inject2 = batch2.length ? bacaJugaHtml(batch2) : "";
    const tail = parts.slice(4).join("</p>");
    result = firstChunk + inject1 + midChunk + inject2 + tail;
  } else {
    const tail = parts.slice(2).join("</p>");
    result = firstChunk + inject1 + tail;
  }

  return { html: result, remaining };
}
