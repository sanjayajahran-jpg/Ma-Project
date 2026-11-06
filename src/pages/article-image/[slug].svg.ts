import type { APIContext } from "astro";
import {
  fetchArticleBySlugFromApi,
  fetchSiteConfigFromApi,
  portalDomainFromScope,
} from "@/lib/api";
import { portalIdentityForDomain } from "@/site";

export async function GET(context: APIContext) {
  const slug = context.params.slug ?? "";
  const [article, siteConfig] = await Promise.all([
    fetchArticleBySlugFromApi(slug, context.request),
    fetchSiteConfigFromApi(context.request),
  ]);
  const identity = portalIdentityForDomain(portalDomainFromScope(context.request), siteConfig?.portal?.name);
  const title = article?.title ?? readableSlug(slug);
  const category = article?.category?.name ?? identity.name;
  const palette = paletteFrom(`${identity.domain}:${slug}`);
  const svg = renderArticleSvg({
    brand: identity.name,
    title,
    category,
    ...palette,
  });

  return new Response(svg, {
    headers: {
      "content-type": "image/svg+xml; charset=utf-8",
      "cache-control": "public, max-age=86400, stale-while-revalidate=604800",
    },
  });
}

function renderArticleSvg({
  brand,
  title,
  category,
  primary,
  secondary,
  accent,
}: {
  brand: string;
  title: string;
  category: string;
  primary: string;
  secondary: string;
  accent: string;
}) {
  const lines = wrap(title, 42).slice(0, 4);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="${escapeXml(title)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${primary}"/>
      <stop offset="58%" stop-color="${secondary}"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <radialGradient id="glow" cx="78%" cy="18%" r="70%">
      <stop offset="0%" stop-color="${accent}" stop-opacity=".55"/>
      <stop offset="55%" stop-color="${accent}" stop-opacity=".12"/>
      <stop offset="100%" stop-color="${accent}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M48 0H0V48" fill="none" stroke="#fff" stroke-opacity=".08" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="1280" height="720" fill="url(#bg)"/>
  <rect width="1280" height="720" fill="url(#glow)"/>
  <rect width="1280" height="720" fill="url(#grid)"/>
  <circle cx="1080" cy="80" r="210" fill="#fff" opacity=".08"/>
  <circle cx="1160" cy="560" r="280" fill="${accent}" opacity=".18"/>
  <path d="M0 590 C230 500 430 650 665 570 C875 500 1010 445 1280 500 L1280 720 L0 720 Z" fill="#020617" opacity=".22"/>
  <rect x="82" y="84" width="1116" height="552" rx="42" fill="#ffffff" opacity=".10" stroke="#ffffff" stroke-opacity=".22"/>
  <text x="122" y="145" font-family="Inter, Arial, sans-serif" font-size="26" font-weight="800" letter-spacing="3" fill="#ffffff" opacity=".84">${escapeXml(category.toUpperCase())}</text>
  <g font-family="Source Serif 4, Georgia, serif" font-weight="800" font-size="64" fill="#ffffff">
    ${lines.map((line, index) => `<text x="122" y="${250 + index * 76}">${escapeXml(line)}</text>`).join("\n    ")}
  </g>
  <text x="122" y="584" font-family="Inter, Arial, sans-serif" font-size="30" font-weight="800" fill="#ffffff" opacity=".92">${escapeXml(brand)}</text>
  <rect x="122" y="604" width="260" height="8" rx="4" fill="${accent}"/>
</svg>`;
}

function paletteFrom(seed: string) {
  const palettes = [
    { primary: "#172554", secondary: "#1e3a8a", accent: "#ef4444" },
    { primary: "#111827", secondary: "#334155", accent: "#f97316" },
    { primary: "#14532d", secondary: "#166534", accent: "#eab308" },
    { primary: "#581c87", secondary: "#6d28d9", accent: "#fb7185" },
    { primary: "#0f172a", secondary: "#0f766e", accent: "#38bdf8" },
    { primary: "#7f1d1d", secondary: "#991b1b", accent: "#facc15" },
  ];
  return palettes[hash(seed) % palettes.length];
}

function hash(value: string) {
  let result = 0;
  for (let index = 0; index < value.length; index += 1) {
    result = (result * 31 + value.charCodeAt(index)) >>> 0;
  }
  return result;
}

function wrap(value: string, max = 42) {
  const words = value.replace(/\s+/g, " ").trim().split(" ");
  const lines: string[] = [];
  let line = "";
  for (const word of words) {
    const next = line ? `${line} ${word}` : word;
    if (next.length > max && line) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines.length ? lines : ["Artikel"];
}

function readableSlug(slug: string) {
  return decodeURIComponent(slug || "artikel").replace(/-/g, " ");
}

function escapeXml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
