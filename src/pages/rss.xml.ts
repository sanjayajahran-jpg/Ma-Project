import rss from "@astrojs/rss";
import type { APIContext } from "astro";
import { SITE, portalIdentityForDomain } from "@/site";
import { allArticles } from "@/data";
import { articleUrl } from "@/types";
import {
  fetchAllArticlesFromApi,
  fetchSiteConfigFromApi,
  isFallbackDataEnabled,
  portalDomainFromScope,
  siteUrlFromScope,
} from "@/lib/api";

export async function GET(context: APIContext) {
  const siteConfig = await fetchSiteConfigFromApi(context.request);
  const identity = portalIdentityForDomain(portalDomainFromScope(context.request), siteConfig?.portal?.name);
  const articles = await fetchAllArticlesFromApi(100, context.request);
  const items = articles.length ? articles : isFallbackDataEnabled() ? allArticles : [];
  return rss({
    title: `${identity.name} — ${SITE.tagline}`,
    description: identity.description,
    site: siteUrlFromScope(context.request),
    items: items.map((a) => ({
      title: a.title,
      description: a.dek,
      pubDate: new Date(a.publishedAt),
      link: articleUrl(a),
      categories: [a.category.name, ...a.tags.map((t) => t.name)],
      author: a.author.name,
    })),
    customData: `<language>id-ID</language>`,
  });
}
