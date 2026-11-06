import type { APIContext } from "astro";
import { allArticles, authors, categories, tags } from "@/data";
import { articleUrl } from "@/types";
import { isFallbackDataEnabled, portalDomainFromScope, siteUrlFromScope } from "@/lib/api";
import ELECTRIFIED_CARS_DATA from "@/data/electrified-cars.json";

const apiUrl = import.meta.env.PUBLIC_API_URL ?? "https://api.groovetimes.com/api/v1";

export async function GET(context: APIContext) {
  const urls = await sitemapUrls(context.request);
  return new Response(renderSitemap(urls), {
    headers: {
      "content-type": "application/xml; charset=utf-8",
      "cache-control": "public, max-age=300",
    },
  });
}

async function sitemapUrls(request: Request) {
  const portalDomain = portalDomainFromScope(request);
  const siteUrl = siteUrlFromScope(request);

  // Automotive Catalog & Car Detail URLs
  const carUrls = [
    `${siteUrl}/katalog-mobil`,
    ...ELECTRIFIED_CARS_DATA.map((car: any) => `${siteUrl}/mobil/${car.slug}`)
  ];

  try {
    const url = new URL(`${apiUrl.replace(/\/$/, "")}/sitemap-data`);
    url.searchParams.set("portal_domain", portalDomain);
    url.searchParams.set("domain", portalDomain);
    const response = await fetch(url, {
      headers: { accept: "application/json", "x-portal-domain": portalDomain },
      signal: AbortSignal.timeout(2500),
    });
    if (!response.ok) throw new Error("sitemap-data unavailable");
    const data = (await response.json()) as {
      articles?: string[];
      categories?: string[];
      tags?: string[];
      authors?: string[];
    };
    return [
      siteUrl,
      ...carUrls,
      ...(data.articles ?? []).map((slug) => `${siteUrl}/${slug}`),
      ...(data.categories ?? []).map((slug) => `${siteUrl}/kategori/${slug}`),
      ...(data.tags ?? []).map((slug) => `${siteUrl}/tag/${slug}`),
      ...(data.authors ?? []).map((slug) => `${siteUrl}/penulis/${slug}`),
    ];
  } catch {
    if (!isFallbackDataEnabled()) return [siteUrl, ...carUrls];

    return [
      siteUrl,
      ...carUrls,
      ...allArticles.map((article) => `${siteUrl}${articleUrl(article)}`),
      ...categories.map((category) => `${siteUrl}/kategori/${category.slug}`),
      ...Object.keys(tags).map((slug) => `${siteUrl}/tag/${slug}`),
      ...authors.map((author) => `${siteUrl}/penulis/${author.slug}`),
    ];
  }
}

function renderSitemap(urls: string[]) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${[...new Set(urls)].map((url) => `  <url><loc>${escapeXml(url)}</loc></url>`).join("\n")}
</urlset>`;
}

function escapeXml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
