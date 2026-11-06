import {
  fetchArticlesFromApi,
  mapSlotArticleSummary,
  type ApiHomepageResponse,
  type HomepageSectionConfig,
  type HomepageSectionLayout,
  type HomepageSectionSource,
  type HomepageSectionType,
  type PortalScope,
  type ProfessionalNewsHomepageConfig,
} from "./api";
import type { Article } from "@/types";

const SECTION_TYPES = new Set<HomepageSectionType>([
  "ticker",
  "hero",
  "grid",
  "latest",
  "spotlight",
  "video",
  "popular",
]);

const SECTION_LAYOUTS = new Set<HomepageSectionLayout>([
  "ticker",
  "slider",
  "cards",
  "feed",
  "dark",
  "ranked",
]);

const SOURCE_KINDS = new Set(["latest", "popular", "category", "tag", "manual"]);

export const PROFESSIONAL_NEWS_DEFAULT_SECTIONS: HomepageSectionConfig[] = [
  {
    id: "headline-ticker",
    type: "ticker",
    title: "Headline",
    enabled: true,
    source: { kind: "latest" },
    limit: 6,
    layout: "ticker",
  },
  {
    id: "hero-slider",
    type: "hero",
    title: "Headline",
    enabled: true,
    source: { kind: "manual" },
    limit: 5,
    layout: "slider",
  },
  {
    id: "editor-grid",
    type: "grid",
    title: "Pilihan Redaksi",
    enabled: true,
    source: { kind: "latest" },
    limit: 4,
    layout: "cards",
  },
  {
    id: "latest-feed",
    type: "latest",
    title: "Terkini",
    enabled: true,
    source: { kind: "latest" },
    limit: 8,
    layout: "feed",
  },
  {
    id: "spotlight",
    type: "spotlight",
    title: "Sorotan",
    enabled: true,
    source: { kind: "popular" },
    limit: 3,
    layout: "dark",
  },
  {
    id: "video",
    type: "video",
    title: "Video",
    enabled: true,
    source: { kind: "latest" },
    limit: 3,
    layout: "cards",
  },
  {
    id: "popular",
    type: "popular",
    title: "Terpopuler",
    enabled: true,
    source: { kind: "popular" },
    limit: 5,
    layout: "ranked",
  },
];

export const PROFESSIONAL_NEWS_DEFAULT_CONFIG: ProfessionalNewsHomepageConfig = {
  version: 1,
  sections: PROFESSIONAL_NEWS_DEFAULT_SECTIONS,
};

export interface ResolvedHomepageSection extends HomepageSectionConfig {
  articles: Article[];
}

export function normalizeProfessionalNewsConfig(value: unknown): ProfessionalNewsHomepageConfig {
  if (!isRecord(value) || value.version !== 1 || !Array.isArray(value.sections)) {
    return cloneDefaultConfig();
  }

  const ids = new Set<string>();
  const sections = value.sections
    .map((section, index) => normalizeSection(section, index))
    .filter((section): section is HomepageSectionConfig => {
      if (!section || ids.has(section.id)) return false;
      ids.add(section.id);
      return true;
    })
    .slice(0, 8);

  return sections.length ? { version: 1, sections } : cloneDefaultConfig();
}

export async function resolveProfessionalNewsSections(
  config: ProfessionalNewsHomepageConfig,
  fallbackArticles: Article[],
  homepage: ApiHomepageResponse | null,
  scope?: PortalScope,
): Promise<ResolvedHomepageSection[]> {
  const enabled = config.sections.filter((section) => section.enabled);
  const pools = new Map<string, Promise<Article[]>>();

  const poolFor = (section: HomepageSectionConfig) => {
    const key = sourceKey(section.source);
    if (!pools.has(key)) {
      pools.set(key, fetchSourcePool(section.source, fallbackArticles, scope));
    }
    return pools.get(key)!;
  };

  return Promise.all(
    enabled.map(async (section) => {
      const manual = manualArticles(section, fallbackArticles, homepage);
      const pool = section.source.kind === "manual" ? manual : await poolFor(section);
      const articles = [...new Map(sortForSource(pool, section.source).map((article) => [article.id, article])).values()]
        .slice(0, section.limit);
      return { ...section, articles };
    }),
  );
}

async function fetchSourcePool(
  source: HomepageSectionSource,
  fallbackArticles: Article[],
  scope?: PortalScope,
) {
  if (source.kind === "latest" || source.kind === "popular") return fallbackArticles;
  if ((source.kind === "category" || source.kind === "tag") && source.slug) {
    const fetched = await fetchArticlesFromApi({ [source.kind]: source.slug, limit: 12 }, scope);
    if (fetched.length) return fetched;
  }
  return filterForSource(fallbackArticles, source);
}

function manualArticles(
  section: HomepageSectionConfig,
  articles: Article[],
  homepage: ApiHomepageResponse | null,
) {
  const keys = section.type === "hero"
    ? new Set(["main", "secondary", "editor_pick"])
    : section.type === "ticker"
      ? new Set(["breaking"])
      : new Set([section.id]);
  const slots = (homepage?.slots ?? [])
    .filter((slot) => keys.has(slot.slot_key) && slot.article_id)
    .sort((left, right) =>
      manualSlotRank(section.type, left.slot_key) - manualSlotRank(section.type, right.slot_key)
      || left.position - right.position,
    );
  const byId = new Map(articles.map((article) => [article.id, article]));
  const selected = slots
    .map((slot) => {
      const article = byId.get(slot.article_id!) ?? (slot.article ? mapSlotArticleSummary(slot.article) : undefined);
      if (!article) return undefined;
      return slot.headline_title ? { ...article, title: slot.headline_title } : article;
    })
    .filter((article): article is Article => Boolean(article));
  const unique = [...new Map(selected.map((article) => [article.id, article])).values()];
  return unique.length ? unique : articles;
}

function manualSlotRank(type: HomepageSectionType, slotKey: string) {
  if (type !== "hero") return 0;
  return { main: 0, secondary: 1, editor_pick: 2 }[slotKey] ?? 3;
}

function filterForSource(articles: Article[], source: HomepageSectionSource) {
  if (source.kind === "category" && source.slug) {
    return articles.filter((article) => article.category.slug === source.slug);
  }
  if (source.kind === "tag" && source.slug) {
    return articles.filter((article) => article.tags.some((tag) => tag.slug === source.slug));
  }
  return articles;
}

function sortForSource(articles: Article[], source: HomepageSectionSource) {
  const copy = [...filterForSource(articles, source)];
  if (source.kind === "manual") return copy;
  if (source.kind === "popular") {
    return copy.sort(
      (left, right) =>
        right.viewCount - left.viewCount ||
        +new Date(right.publishedAt) - +new Date(left.publishedAt),
    );
  }
  return copy.sort(
    (left, right) => +new Date(right.publishedAt) - +new Date(left.publishedAt),
  );
}

function normalizeSection(value: unknown, index: number): HomepageSectionConfig | null {
  if (!isRecord(value)) return null;
  const type = SECTION_TYPES.has(value.type as HomepageSectionType)
    ? (value.type as HomepageSectionType)
    : null;
  const layout = SECTION_LAYOUTS.has(value.layout as HomepageSectionLayout)
    ? (value.layout as HomepageSectionLayout)
    : null;
  if (!type || !layout) return null;

  const id = typeof value.id === "string" ? value.id.trim() : "";
  if (id && !/^[a-z0-9][a-z0-9-]{0,63}$/.test(id)) return null;

  const sourceValue = isRecord(value.source) ? value.source : {};
  const kind = SOURCE_KINDS.has(sourceValue.kind as string)
    ? (sourceValue.kind as HomepageSectionSource["kind"])
    : "latest";
  const rawSlug = typeof sourceValue.slug === "string" ? sourceValue.slug.trim() : undefined;
  const slug = rawSlug && /^[a-z0-9][a-z0-9-]{0,99}$/.test(rawSlug) ? rawSlug : undefined;
  const source: HomepageSectionSource = {
    kind: (kind === "category" || kind === "tag") && !slug ? "latest" : kind,
    ...(slug ? { slug } : {}),
  };

  return {
    id: id || `${type}-${index + 1}`,
    type,
    title: typeof value.title === "string" && value.title.trim()
      ? value.title.trim().slice(0, 80)
      : defaultTitle(type),
    enabled: value.enabled !== false,
    source,
    limit: clampLimit(value.limit),
    layout,
  };
}

function defaultTitle(type: HomepageSectionType) {
  return PROFESSIONAL_NEWS_DEFAULT_SECTIONS.find((section) => section.type === type)?.title ?? "Berita";
}

function clampLimit(value: unknown) {
  const parsed = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(parsed)) return 4;
  return Math.max(1, Math.min(12, Math.round(parsed)));
}

function sourceKey(source: HomepageSectionSource) {
  return `${source.kind}:${source.slug ?? ""}`;
}

function cloneDefaultConfig(): ProfessionalNewsHomepageConfig {
  return {
    version: 1,
    sections: PROFESSIONAL_NEWS_DEFAULT_SECTIONS.map((section) => ({
      ...section,
      source: { ...section.source },
    })),
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
