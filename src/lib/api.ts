import { articles as fallbackArticles } from "@/data/articles";
import type { Article, Author, Category, LinkedArticle, Tag } from "@/types";

interface ApiLinkedArticle {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  cover_url: string | null;
  category_slug: string;
  category_name: string;
  published_at: string | null;
}

interface ApiArticle {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  body_html: string;
  cover_url?: string | null;
  cover_thumb_url?: string | null;
  cover_mobile_url?: string | null;
  cover_image_url?: string | null;
  image_url?: string | null;
  thumbnail_url?: string | null;
  featured_image_url?: string | null;
  cover_alt?: string | null;
  cover_caption?: string | null;
  type: Article["type"];
  reading_time_min: number;
  view_count?: number;
  published_at?: string | null;
  author: { id: string; slug: string; name: string; bio?: string | null; avatar_url?: string | null };
  category: { id: string; slug: string; name: string; description?: string | null };
  tags: Array<{ slug: string; name: string }>;
  baca_juga?: ApiLinkedArticle[];
  berita_terkait?: ApiLinkedArticle[];
  generated_by_agent_id?: string | null;
  generated_by_agent_name?: string | null;
}

interface ApiListResponse {
  items: ApiArticle[];
  total?: number;
  page?: number;
  page_size?: number;
  next_cursor?: string | null;
}

interface ApiSlotArticleSummary {
  id: string;
  slug: string;
  title: string;
  excerpt: string | null;
  category_slug: string | null;
  category_name: string | null;
  cover_url: string | null;
  published_at: string | null;
}

export interface ApiHomepageSlot {
  id: string;
  slot_key: string;
  article_id: string | null;
  headline_title: string | null;
  short_title: string | null;
  kicker: string | null;
  label: string | null;
  position: number;
  article?: ApiSlotArticleSummary | null;
}

export interface ApiHomepageResponse {
  slots: ApiHomepageSlot[];
  template: {
    portal?: ApiPortal;
    template: {
      key: string;
      name: string;
    };
    config: Record<string, unknown>;
  };
}

export interface ApiPortal {
  id: string;
  name: string;
  slug: string;
  domain: string;
  public_site_url: string;
  socials?: PortalSocialLink[];
  /** Key/value dari System > Settings (mis. default_meta_title, alamat, phone). */
  settings?: Record<string, string>;
}

export interface PortalSocialLink {
  id: string;
  title: string;
  url: string;
  icon?: string;
}

export type HomepageSourceKind = "latest" | "popular" | "category" | "tag" | "manual";

export interface HomepageSectionSource {
  kind: HomepageSourceKind;
  slug?: string;
}

export type HomepageSectionType =
  | "ticker"
  | "hero"
  | "grid"
  | "latest"
  | "spotlight"
  | "video"
  | "popular";

export type HomepageSectionLayout =
  | "ticker"
  | "slider"
  | "cards"
  | "feed"
  | "dark"
  | "ranked";

export interface HomepageSectionConfig {
  id: string;
  type: HomepageSectionType;
  title: string;
  enabled: boolean;
  source: HomepageSectionSource;
  limit: number;
  layout: HomepageSectionLayout;
}

export interface ProfessionalNewsHomepageConfig {
  version: 1;
  sections: HomepageSectionConfig[];
}

export interface ApiSiteConfigResponse {
  portal_id: string;
  portal?: ApiPortal;
  template: {
    key: string;
    name: string;
  };
  config: {
    site_title?: string | null;
    tagline?: string | null;
    brand?: {
      primary_color?: string;
      accent_color?: string;
      density?: string;
      logo_url?: string | null;
      logo_dark_url?: string | null;
      default_image_url?: string | null;
      favicon_url?: string | null;
    };
    ad_mode?: string;
    homepage?: ProfessionalNewsHomepageConfig;
  };
  analytics?: {
    ga_measurement_id?: string;
  } | null;
}

export interface ApiStaticPage {
  title: string;
  slug: string;
  excerpt: string | null;
  body_html: string;
  seo_title: string | null;
  seo_description: string | null;
}

export type BannerPlacement = string;
export interface ApiBannerAd { id: string; name: string; target_url: string; ad_type: "image" | "html"; html_code: string | null; hide_effect: "fade" | "slide_top" | "slide_bottom" | "slide_left" | "slide_right"; functions_enabled: boolean; display_duration_ms: number; transition_duration_ms: number; desktop_image_url: string | null; mobile_image_url: string | null; placements: BannerPlacement[]; }

const publicApiUrl = import.meta.env.PUBLIC_API_URL ?? "https://api.groovetimes.com/api/v1";
const serverApiUrl = import.meta.env.SERVER_API_URL ?? publicApiUrl;
export type PortalScope = Request | string | null | undefined;
export const PORTAL_DOMAIN = import.meta.env.PUBLIC_PORTAL_DOMAIN ?? "evhub.id";
const useFallbackData = import.meta.env.PUBLIC_USE_FALLBACK_DATA !== "false";

// Per-portal cache control.
// PUBLIC_CACHE_DOMAINS = comma-separated list of domains where TTL cache is ENABLED.
// Domains NOT in this list always fetch fresh (debug mode).
// Example: PUBLIC_CACHE_DOMAINS=sewaktu.id
// Read at runtime (process.env) so it can be changed without rebuild.
function getCacheEnabledDomains(): Set<string> {
  const raw = (typeof process !== "undefined" && process.env?.PUBLIC_CACHE_DOMAINS)
    || import.meta.env.PUBLIC_CACHE_DOMAINS
    || "";
  return new Set(
    raw.split(",").map((d: string) => d.trim().toLowerCase().replace(/^www\./, "")).filter(Boolean),
  );
}
// PUBLIC_DEBUG_MODE = global override: if explicitly "false", enable cache for ALL domains
const globalCacheEnabled = import.meta.env.PUBLIC_DEBUG_MODE === "false";

// Selalu aktifkan cache in-memory agar TTFB respons server instan (< 15ms)
function isCacheEnabled(_scope?: PortalScope): boolean {
  return true;
}

// --- Request-scoped dedup (always active) ---
const inflight = new Map<string, Promise<unknown>>();
function dedupe<T>(key: string, fn: () => Promise<T>): Promise<T> {
  const existing = inflight.get(key);
  if (existing) return existing as Promise<T>;
  const p = fn().finally(() => inflight.delete(key));
  inflight.set(key, p);
  return p;
}

// --- In-memory TTL cache (active when isCacheEnabled(scope) = true) ---
const ttlCache = new Map<string, { data: unknown; expires: number }>();
const CACHE_TTL = {
  siteConfig: 5 * 60_000,
  categories: 5 * 60_000,
  menus: 5 * 60_000,
  homepage: 30_000,
  tags: 5 * 60_000,
} as const;

function getCached<T>(key: string): T | undefined {
  const entry = ttlCache.get(key);
  if (entry && entry.expires > Date.now()) return entry.data as T;
  ttlCache.delete(key);
  return undefined;
}
function setCached<T>(key: string, data: T, ttl: number) {
  ttlCache.set(key, { data, expires: Date.now() + ttl });
}
function withCache<T>(key: string, ttl: number, fn: () => Promise<T>, scope?: PortalScope): Promise<T> {
  if (!isCacheEnabled(scope)) return dedupe(key, fn);
  const cached = getCached<T>(key);
  if (cached !== undefined) return Promise.resolve(cached);
  return dedupe(key, fn).then((data) => { setCached(key, data, ttl); return data; });
}

export function isFallbackDataEnabled() {
  return useFallbackData;
}

let currentActivePortalDomain: string | null = null;

export function setActivePortalDomain(domain: string) {
  currentActivePortalDomain = domain;
}

export function getActivePortalDomain(): string {
  return currentActivePortalDomain || PORTAL_DOMAIN;
}

function parseCookieHeader(cookieHeader: string | null, name: string): string | null {
  if (!cookieHeader) return null;
  const matches = cookieHeader.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return matches ? decodeURIComponent(matches[1]) : null;
}

function domainForThemeKey(themeKey: string): string | null {
  switch (themeKey.toLowerCase()) {
    case "automotive":
    case "evnesia-v2":
      return PORTAL_DOMAIN || "evhub.id";
    case "gaming-arena":
      return "gamingnews.id";
    case "minimal-daily":
      return "faishion.id";
    case "magazine-feature":
      return "naranta.id";
    case "breaking-wire":
      return "awasi.id";
    case "berdaya":
      return "berdayanews.com";
    case "photo-story":
      return "photostory.id";
    case "video-first":
      return "videofirst.id";
    case "corporate-media":
      return "corporatemedia.id";
    case "promedia":
      return "promedia.id";
    case "regional-network":
      return "regionalnetwork.id";
    case "professional-news":
      return "berdayanews.com";
    default:
      return null;
  }
}

export function portalDomainFromScope(scope?: PortalScope) {
  if (typeof scope === "string") {
    const domain = normalizePortalDomain(scope) ?? PORTAL_DOMAIN;
    setActivePortalDomain(domain);
    return domain;
  }

  if (scope && typeof scope === "object" && "url" in scope) {
    try {
      const url = new URL(scope.url);
      const themeParam = url.searchParams.get("theme_preview")?.trim();
      const cookieTheme = parseCookieHeader(scope.headers.get("cookie"), "theme_preview");
      const themeKey = (themeParam && themeParam !== "reset" && themeParam !== "clear")
        ? themeParam
        : (cookieTheme && cookieTheme !== "reset" && cookieTheme !== "clear")
        ? cookieTheme
        : null;

      if (themeKey) {
        const themeDomain = domainForThemeKey(themeKey);
        if (themeDomain) {
          setActivePortalDomain(themeDomain);
          return themeDomain;
        }
      }
    } catch {}
  }

  const headerDomain =
    scope?.headers.get("x-forwarded-host") ??
    scope?.headers.get("x-portal-domain") ??
    scope?.headers.get("host") ??
    "";

  const domain = normalizePortalDomain(headerDomain) ?? PORTAL_DOMAIN;
  setActivePortalDomain(domain);
  return domain;
}

export function siteUrlFromScope(scope?: PortalScope) {
  const domain = portalDomainFromScope(scope);
  if (typeof scope === "string" || !scope) return `https://${domain}`;
  const proto = scope.headers.get("x-forwarded-proto") ?? new URL(scope.url).protocol.replace(":", "");
  return `${proto || "https"}://${domain}`;
}

function normalizePortalDomain(value: string) {
  const raw = value.trim().toLowerCase();
  if (!raw) return null;

  const withoutScheme = raw.replace(/^https?:\/\//, "");
  const host = withoutScheme.split("/")[0]?.split(",")[0]?.trim();
  if (!host) return null;

  const withoutPort = host.replace(/:\d+$/, "");
  const clean = withoutPort.replace(/^www\./, "");
  if (clean === "localhost" || clean === "127.0.0.1" || clean.endsWith(".local")) {
    return null;
  }
  return clean;
}

export function resolveApiUrl(scope?: PortalScope): string {
  if (typeof window === 'undefined') {
    const runtime = typeof process !== "undefined" ? process.env?.SERVER_API_URL : undefined;
    if (runtime) return runtime;
    if (serverApiUrl) return serverApiUrl;
  }
  return publicApiUrl;
}

function scopedUrl(path: string, params: Record<string, string | number> = {}, scope?: PortalScope) {
  const portalDomain = portalDomainFromScope(scope);
  const url = new URL(`${resolveApiUrl(scope).replace(/\/$/, "")}${path}`);
  url.searchParams.set("portal_domain", portalDomain);
  url.searchParams.set("domain", portalDomain);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, String(value)));
  return url;
}

function scopedHeaders(scope?: PortalScope) {
  return {
    accept: "application/json",
    "x-portal-domain": portalDomainFromScope(scope),
  };
}

export async function fetchArticlesFromApi(
  params: Record<string, string | number> = {},
  scope?: PortalScope,
) {
  try {
    const url = scopedUrl("/articles", params, scope);
    const [fallbackImage, response] = await Promise.all([
      defaultArticleImage(scope),
      fetch(url, {
        headers: scopedHeaders(scope),
        signal: AbortSignal.timeout(2500),
      }),
    ]);

    if (!response.ok) return [];
    const data = (await response.json()) as ApiListResponse;
    return data.items.map((article) => mapApiArticle(article, fallbackImage));
  } catch {
    return [];
  }
}

export async function fetchAllArticlesFromApi(limit = 100, scope?: PortalScope) {
  const domain = portalDomainFromScope(scope);
  return dedupe(`articles-all:${domain}:${limit}`, async () => {
    const items = await fetchArticlesFromApi({ limit }, scope);
    return items.length || !useFallbackData ? items : [...fallbackArticles];
  });
}

export async function fetchArticlesPaginated(
  params: Record<string, string | number> = {},
  scope?: PortalScope,
): Promise<{ items: Article[]; total: number; page: number; pageSize: number }> {
  try {
    const url = scopedUrl("/articles", params, scope);
    const [fallbackImage, response] = await Promise.all([
      defaultArticleImage(scope),
      fetch(url, {
        headers: scopedHeaders(scope),
        signal: AbortSignal.timeout(5000),
      }),
    ]);

    if (!response.ok) {
      return { items: [], total: 0, page: 1, pageSize: 24 };
    }
    const data = (await response.json()) as ApiListResponse;
    const items = data.items.map((article) => mapApiArticle(article, fallbackImage));
    return {
      items: items.length || !useFallbackData ? items : [...fallbackArticles],
      total: data.total ?? items.length,
      page: data.page ?? 1,
      pageSize: data.page_size ?? 24,
    };
  } catch {
    return { items: [], total: 0, page: 1, pageSize: 24 };
  }
}

export async function fetchHomepageFromApi(scope?: PortalScope) {
  const domain = portalDomainFromScope(scope);
  return withCache(`homepage:${domain}`, CACHE_TTL.homepage, async () => {
    try {
      const response = await fetch(scopedUrl("/homepage", {}, scope), {
        headers: scopedHeaders(scope),
        signal: AbortSignal.timeout(2500),
      });

      if (!response.ok) return null;
      return (await response.json()) as ApiHomepageResponse;
    } catch {
      return null;
    }
  }, scope);
}

export async function fetchBannersFromApi(placement: BannerPlacement, scope?: PortalScope): Promise<ApiBannerAd[]> {
  try {
    const response = await fetch(scopedUrl("/banners", { placement }, scope), { headers: scopedHeaders(scope), signal: AbortSignal.timeout(2000) });
    if (!response.ok) return [];
    return ((await response.json()) as { items?: ApiBannerAd[] }).items ?? [];
  } catch { return []; }
}

export async function fetchSiteConfigFromApi(scope?: PortalScope) {
  const domain = portalDomainFromScope(scope);
  return withCache(`site-config:${domain}`, CACHE_TTL.siteConfig, async () => {
    try {
      const response = await fetch(scopedUrl("/site-config", {}, scope), {
        headers: scopedHeaders(scope),
        signal: AbortSignal.timeout(2500),
      });

      if (!response.ok) return null;
      return (await response.json()) as ApiSiteConfigResponse;
    } catch {
      return null;
    }
  }, scope);
}

export async function fetchPageBySlugFromApi(slug: string, scope?: PortalScope): Promise<ApiStaticPage | null> {
  const domain = portalDomainFromScope(scope);
  return withCache(`page:${slug}:${domain}`, CACHE_TTL.siteConfig, async () => {
    try {
      const response = await fetch(scopedUrl(`/pages/${encodeURIComponent(slug)}`, {}, scope), {
        headers: scopedHeaders(scope),
        signal: AbortSignal.timeout(2500),
      });
      if (!response.ok) return null;
      return (await response.json()) as ApiStaticPage;
    } catch {
      return null;
    }
  }, scope);
}

/**
 * Menu location key. Built-in presets are "main", "footer", "mobile", but
 * admins can define arbitrary custom locations (e.g. "header_top",
 * "sidebar_menu") — those are also valid here.
 */
export type MenuLocation = string;

export interface ApiMenuItem {
  id: string;
  portal_id: string | null;
  location: string | null;
  label: string;
  url: string;
  target: string;
  icon?: string | null;
  sort_order: number;
  parent_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

interface ApiMenuListResponse {
  items: ApiMenuItem[];
}

export interface MenuNode {
  id: string;
  label: string;
  href: string;
  target: string;
  icon?: string | null;
  sortOrder: number;
  children: MenuNode[];
}

/**
 * Fetch menu items for a given location, already nested into a tree.
 * Returns an empty array on any error so callers can fall back to defaults.
 */
export async function fetchMenusFromApi(
  location: MenuLocation,
  scope?: PortalScope,
): Promise<MenuNode[]> {
  const domain = portalDomainFromScope(scope);
  return withCache(`menus:${domain}:${location}`, CACHE_TTL.menus, async () => {
    try {
      const response = await fetch(scopedUrl(`/menus/${location}`, {}, scope), {
        headers: scopedHeaders(scope),
        signal: AbortSignal.timeout(2000),
      });
      if (!response.ok) return [];
      const data = (await response.json()) as ApiMenuListResponse;
      return nestMenuItems(data.items ?? []);
    } catch {
      return [];
    }
  }, scope);
}

function nestMenuItems(items: ApiMenuItem[]): MenuNode[] {
  const sorted = [...items].sort(
    (a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0),
  );
  const nodes = new Map<string, MenuNode>();
  const roots: MenuNode[] = [];

  // First pass: create all nodes.
  for (const item of sorted) {
    nodes.set(item.id, {
      id: item.id,
      label: item.label,
      href: item.url,
      target: item.target || "_self",
      icon: item.icon ?? null,
      sortOrder: item.sort_order ?? 0,
      children: [],
    });
  }

  // Second pass: link children to parents.
  for (const item of sorted) {
    const node = nodes.get(item.id)!;
    const parentId = item.parent_id ?? null;
    if (parentId && nodes.has(parentId)) {
      nodes.get(parentId)!.children.push(node);
    } else {
      roots.push(node);
    }
  }

  return roots;
}

export function siteConfigToCssVars(config: ApiSiteConfigResponse | null) {
  const brand = config?.config?.brand ?? {};
  const template = config?.template?.key ?? "professional-news";
  const templateRaw = template.toLowerCase();
  const isRegional = templateRaw === "regional-network";
  const isAutomotive = templateRaw === "automotive" || templateRaw.includes("automotive");

  const density = brand.density === "compact" ? "compact" : "comfortable";
  const radius = templateRaw.includes("minimal") || templateRaw.includes("breaking") || density === "compact" ? "0.25rem" : "0.5rem";
  const sectionGap = density === "compact" ? "2.5rem" : "3.5rem";

  if (isAutomotive) {
    return [
      `--color-primary: #0284c7`,
      `--color-accent: #06b6d4`,
      `--radius-card: ${radius}`,
      `--section-gap: ${sectionGap}`,
    ].join("; ");
  }

  const defaultPrimary = isRegional ? "#065f46" : "#17211d";
  const defaultAccent =
    isRegional ? "#065f46" :
    templateRaw === "corporate-media" ? "#1e40af" :
    templateRaw === "berdaya" ? "#1f6f54" :
    "#0284c7";

  const accent = isRegional ? "#065f46" : (safeHex(brand.accent_color) ?? defaultAccent);
  const primary = isRegional ? "#065f46" : (safeHex(brand.primary_color) ?? defaultPrimary);

  const primaryLum = luminance(primary);
  const ink = isRegional ? "#0f1c15" : primaryLum > 0.55 ? "#15171a" : primary;
  const onPrimary = primaryLum > 0.55 ? "#15171a" : "#ffffff";
  const terracotta = "#c2410c";

  return [
    `--color-ink: ${ink}`,
    `--color-soft: ${mix(ink, "#ffffff", 0.16)}`,
    `--color-primary: ${primary}`,
    `--color-on-primary: ${onPrimary}`,
    `--color-brand: ${accent}`,
    `--color-brand-dark: #044734`,
    `--color-terracotta: ${terracotta}`,
    `--color-gold: ${isRegional ? terracotta : accent}`,
    `--color-gold-soft: ${mix(accent, "#ffffff", 0.88)}`,
    `--radius-card: ${radius}`,
    `--section-gap: ${sectionGap}`,
  ].join("; ");
}

export async function fetchArticleBySlugFromApi(slug: string, scope?: PortalScope) {
  try {
    const [fallbackImage, response] = await Promise.all([
      defaultArticleImage(scope),
      fetch(scopedUrl(`/articles/${slug}`, {}, scope), {
        headers: scopedHeaders(scope),
        signal: AbortSignal.timeout(2500),
      }),
    ]);

    if (!response.ok) return useFallbackData ? fallbackArticles.find((article) => article.slug === slug) : undefined;
    return mapApiArticle((await response.json()) as ApiArticle, fallbackImage);
  } catch {
    return useFallbackData ? fallbackArticles.find((article) => article.slug === slug) : undefined;
  }
}

export async function fetchCategoriesFromApi(scope?: PortalScope) {
  return fetchCategoriesListFromApi(scope);
}

async function fetchCategoriesListFromApi(
  scope?: PortalScope,
): Promise<{ slug: string; name: string; description?: string }[]> {
  const domain = portalDomainFromScope(scope);
  return withCache(`categories:${domain}`, CACHE_TTL.categories, async () => {
    try {
      const response = await fetch(scopedUrl("/categories", {}, scope), {
        headers: scopedHeaders(scope),
        signal: AbortSignal.timeout(2000),
      });
      if (!response.ok) return [];
      const data = await response.json();
      return Array.isArray(data) ? data : [];
    } catch {
      return [];
    }
  }, scope);
}

export async function fetchTagsFromApi(scope?: PortalScope) {
  const domain = portalDomainFromScope(scope);
  return withCache(`tags:${domain}`, CACHE_TTL.tags, async () => {
    const articles = await fetchAllArticlesFromApi(100, scope);
    return uniqueBy(articles.flatMap((article) => article.tags), (tag) => tag.slug);
  }, scope);
}

export async function fetchAuthorsFromApi(scope?: PortalScope) {
  const articles = await fetchAllArticlesFromApi(100, scope);
  return uniqueBy(articles.map((article) => article.author), (author) => author.slug);
}

export function getRelatedFromList(articles: Article[], article: Article, n = 3) {
  return articles
    .filter((item) => item.id !== article.id)
    .map((item) => {
      let score = item.category.slug === article.category.slug ? 3 : 0;
      score += item.tags.filter((tag) =>
        article.tags.some((currentTag) => currentTag.slug === tag.slug),
      ).length;
      return { article: item, score };
    })
    .filter((item) => item.score > 0)
    .sort(
      (left, right) =>
        right.score - left.score ||
        +new Date(right.article.publishedAt) - +new Date(left.article.publishedAt),
    )
    .slice(0, n)
    .map((item) => item.article);
}

export function getAdjacentFromList(articles: Article[], article: Article) {
  const sorted = [...articles].sort(
    (left, right) => +new Date(right.publishedAt) - +new Date(left.publishedAt),
  );
  const index = sorted.findIndex((item) => item.id === article.id);
  return {
    newer: index > 0 ? sorted[index - 1] : undefined,
    older: index >= 0 && index < sorted.length - 1 ? sorted[index + 1] : undefined,
  };
}

function uniqueBy<T>(items: T[], getKey: (item: T) => string) {
  return [...new Map(items.map((item) => [getKey(item), item])).values()];
}

export function brandConfig(config: ApiSiteConfigResponse | null) {
  return config?.config?.brand ?? {};
}

export function socialLinksFromConfig(config: ApiSiteConfigResponse | null): PortalSocialLink[] {
  const links = config?.portal?.socials;
  if (!Array.isArray(links)) return [];

  return links.flatMap((link) => {
    if (!link || typeof link !== "object") return [];
    const title = typeof link.title === "string" ? link.title.trim() : "";
    const url = typeof link.url === "string" ? link.url.trim() : "";
    if (!title || !isSafeSocialUrl(url)) return [];
    return [{
      id: typeof link.id === "string" && link.id.trim() ? link.id.trim() : `${title}:${url}`,
      title,
      url,
      icon: typeof link.icon === "string" ? link.icon.trim() : undefined,
    }];
  });
}

function isSafeSocialUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}

export function siteTitleFromConfig(config: ApiSiteConfigResponse | null, fallback = "") {
  const title = config?.config?.site_title?.trim();
  if (title) return title;
  const portalName = config?.portal?.name?.trim();
  return portalName || fallback;
}

export function siteTaglineFromConfig(config: ApiSiteConfigResponse | null, fallback = "") {
  const tagline = config?.config?.tagline?.trim();
  return tagline || fallback;
}

/** Ambil nilai key/value System > Settings (mis. default_meta_title, alamat, phone). */
export function portalSettingFromConfig(config: ApiSiteConfigResponse | null, key: string) {
  const value = config?.portal?.settings?.[key];
  return typeof value === "string" ? value.trim() : "";
}

export function brandAsset(value: string | null | undefined, fallback = "") {
  if (!value || typeof value !== "string") return fallback;
  const trimmed = value.trim();
  return rewriteBerdayaBrandAsset(trimmed) || fallback;
}

const berdayaSpacesBase = "https://groovetimes.sgp1.digitaloceanspaces.com/media/";
const berdayaBrandAssets = new Set([
  "f3035df0-9f61-4d37-9051-c0b5ed2a328d-berdaya-news.png",
  "d96b0b1e-a231-4668-80d6-5f6be8b6358e-berdaya-bg.jpg",
  "5c358def-0f85-4d75-a55b-4da3232b466c-berdaya-favicon.png",
]);

function rewriteBerdayaBrandAsset(value: string) {
  const filename = value.split("?")[0]?.split("#")[0]?.split("/").pop();
  if (!filename || !berdayaBrandAssets.has(filename)) return value;
  return `${berdayaSpacesBase}${filename}`;
}

async function defaultArticleImage(scope?: PortalScope) {
  const config = await fetchSiteConfigFromApi(scope);
  return brandAsset(brandConfig(config).default_image_url, "/og-default.svg");
}

export function mapApiArticle(article: ApiArticle, fallbackImage = "/og-default.svg"): Article {
  const cover = articleCoverImage(article, fallbackImage);
  return {
    id: article.id,
    slug: article.slug,
    title: article.title,
    dek: article.excerpt,
    bodyHtml: article.body_html,
    cover,
    coverThumb: firstNonEmpty(article.cover_thumb_url) ? brandAsset(article.cover_thumb_url!, fallbackImage) : undefined,
    coverMobile: firstNonEmpty(article.cover_mobile_url) ? brandAsset(article.cover_mobile_url!, fallbackImage) : undefined,
    coverAlt: article.cover_alt?.trim() || article.title,
    coverCaption: article.cover_caption?.trim() || undefined,
    author: {
      id: article.author.id,
      slug: article.author.slug,
      name: article.author.name,
      role: "Penulis",
      avatar: article.author.avatar_url ?? "/favicon.svg",
      bio: article.author.bio ?? "",
    },
    category: {
      id: article.category.id,
      slug: article.category.slug,
      name: article.category.name,
      description: article.category.description ?? "",
      color: article.category.slug,
    },
    type: article.type,
    tags: article.tags,
    publishedAt: article.published_at ?? new Date().toISOString(),
    readingTime: article.reading_time_min,
    viewCount: article.view_count ?? 0,
    bacaJuga: (article.baca_juga ?? []).map((a) => mapLinkedArticle(a, fallbackImage)),
    beritaTerkait: (article.berita_terkait ?? []).map((a) => mapLinkedArticle(a, fallbackImage)),
    generated_by_agent_id: article.generated_by_agent_id ?? null,
    generated_by_agent_name: article.generated_by_agent_name ?? null,
  };
}

function mapLinkedArticle(article: ApiLinkedArticle, fallbackImage = "/og-default.svg"): LinkedArticle {
  return {
    id: article.id,
    slug: article.slug,
    title: article.title,
    excerpt: article.excerpt,
    cover: article.cover_url ? brandAsset(article.cover_url, fallbackImage) : fallbackImage,
    categorySlug: article.category_slug,
    categoryName: article.category_name,
    publishedAt: article.published_at ?? new Date().toISOString(),
  };
}

export function mapSlotArticleSummary(article: ApiSlotArticleSummary, fallbackImage = "/og-default.svg"): Article {
  const cover = firstNonEmpty(article.cover_url)
    ? brandAsset(article.cover_url!, fallbackImage)
    : article.slug
      ? `/article-image/${encodeURIComponent(article.slug)}.svg`
      : fallbackImage;
  return {
    id: article.id,
    slug: article.slug,
    title: article.title,
    dek: article.excerpt ?? "",
    bodyHtml: "",
    cover,
    coverAlt: article.title,
    author: {
      id: "unknown",
      slug: "unknown",
      name: "Redaksi",
      role: "Penulis",
      avatar: "/favicon.svg",
      bio: "",
    },
    category: {
      id: article.category_slug ?? "umum",
      slug: article.category_slug ?? "umum",
      name: article.category_name ?? "Umum",
      description: "",
      color: article.category_slug ?? "umum",
    },
    type: "standard",
    tags: [],
    publishedAt: article.published_at ?? new Date().toISOString(),
    readingTime: 3,
    viewCount: 0,
    bacaJuga: [],
    beritaTerkait: [],
  };
}

function articleCoverImage(article: ApiArticle, fallbackImage = "/og-default.svg") {
  const apiCover =
    firstNonEmpty(
      article.cover_url,
      article.cover_image_url,
      article.featured_image_url,
      article.image_url,
      article.thumbnail_url,
    ) ?? firstImageFromHtml(article.body_html);

  if (apiCover) return brandAsset(apiCover, fallbackImage);
  if (article.slug) return `/article-image/${encodeURIComponent(article.slug)}.svg`;
  return fallbackImage;
}

function firstNonEmpty(...values: Array<string | null | undefined>) {
  return values.find((value) => typeof value === "string" && value.trim().length > 0)?.trim();
}

function firstImageFromHtml(html: string | null | undefined) {
  if (!html) return undefined;
  const match = html.match(/<img[^>]+src=["']([^"']+)["']/i);
  return match?.[1]?.trim();
}

function safeHex(value: string | undefined) {
  if (!value) return null;
  return /^#[0-9a-f]{6}$/i.test(value) ? value : null;
}

function mix(hexA: string, hexB: string, weightB: number) {
  const a = hexToRgb(hexA);
  const b = hexToRgb(hexB);
  if (!a || !b) return hexA;
  const weightA = 1 - weightB;
  const channel = (left: number, right: number) =>
    Math.round(left * weightA + right * weightB)
      .toString(16)
      .padStart(2, "0");
  return `#${channel(a.r, b.r)}${channel(a.g, b.g)}${channel(a.b, b.b)}`;
}

function luminance(hex: string): number {
  const rgb = hexToRgb(hex);
  if (!rgb) return 0;
  return (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
}

function hexToRgb(value: string) {
  const match = value.match(/^#([0-9a-f]{6})$/i);
  if (!match) return null;
  const int = Number.parseInt(match[1], 16);
  return {
    r: (int >> 16) & 255,
    g: (int >> 8) & 255,
    b: int & 255,
  };
}

// ----------------------------------------------------
// EVnesia Automotive API Fetching Helpers
// ----------------------------------------------------
const CAR_API_BASE = import.meta.env.PUBLIC_CAR_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchCarsFromApi(pageSize = 100, request?: Request): Promise<any[]> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${CAR_API_BASE}/cars?page_size=${pageSize}`, {
      signal: controller.signal,
      headers: { "Accept": "application/json" }
    });
    clearTimeout(timeoutId);
    if (!res.ok) return [];
    const data = await res.json();
    return data.items || [];
  } catch (err) {
    return [];
  }
}

export async function fetchCarDetailFromApi(idOrSlug: string, request?: Request): Promise<any | null> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${CAR_API_BASE}/cars/${idOrSlug}`, {
      signal: controller.signal,
      headers: { "Accept": "application/json" }
    });
    clearTimeout(timeoutId);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchBrandsFromApi(request?: Request): Promise<any[]> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${CAR_API_BASE}/brands?with_count=true`, {
      signal: controller.signal,
      headers: { "Accept": "application/json" }
    });
    clearTimeout(timeoutId);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    return [];
  }
}

export type { Author, Category, LinkedArticle, Tag };
