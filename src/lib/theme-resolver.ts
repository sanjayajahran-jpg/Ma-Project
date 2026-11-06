import { fetchSiteConfigFromApi, portalDomainFromScope } from "./api";
import type { ApiSiteConfigResponse } from "./api";
import { normalizeProfessionalNewsConfig } from "./homepage-customization";
import { defaultThemeForDomain } from "@/site";

const themePages = import.meta.glob("../themes/*/pages/*.astro");
const localThemeKey = import.meta.env.PUBLIC_THEME?.trim();

export interface ThemePageProps {
  request: Request;
  params: Record<string, string | undefined>;
  url: URL;
  siteConfig: ApiSiteConfigResponse | null;
}

function parseCookie(cookieHeader: string | null, name: string): string | null {
  if (!cookieHeader) return null;
  const matches = cookieHeader.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return matches ? decodeURIComponent(matches[1]) : null;
}

function normalizeTemplateKey(key: string | null | undefined): string | null {
  if (!key) return null;
  const trimmed = key.trim();
  const lower = trimmed.toLowerCase();
  for (const pagePath of Object.keys(themePages)) {
    const match = pagePath.match(/^\.\.\/themes\/([^/]+)\/pages\//);
    if (match && match[1].toLowerCase() === lower) {
      return match[1];
    }
  }
  return trimmed;
}

function findThemePageLoader(themeKey: string | null | undefined, pageName: string) {
  if (!themeKey) return null;
  const normalizedKey = normalizeTemplateKey(themeKey) ?? themeKey;
  const directKey = `../themes/${normalizedKey}/pages/${pageName}.astro`;
  if (themePages[directKey]) return themePages[directKey];

  const targetLower = `../themes/${themeKey.toLowerCase()}/pages/${pageName.toLowerCase()}.astro`;
  for (const [k, loader] of Object.entries(themePages)) {
    if (k.toLowerCase() === targetLower) {
      return loader;
    }
  }
  return null;
}

export async function resolveThemePage(
  request: Request,
  pageName: string,
): Promise<{ default: any; siteConfig: ApiSiteConfigResponse | null }> {
  const siteConfig = await fetchSiteConfigFromApi(request);
  const url = new URL(request.url);
  const hostDomain = portalDomainFromScope(request);
  const defaultTheme = defaultThemeForDomain(hostDomain);
  const rawActiveTemplateKey = siteConfig?.template?.key ?? localThemeKey ?? defaultTheme;
  const activeTemplateKey = normalizeTemplateKey(rawActiveTemplateKey) ?? "Automotive";
  
  const paramTheme = (url.searchParams.get("theme_preview") || url.searchParams.get("theme"))?.trim();
  const cookieTheme = parseCookie(request.headers.get("cookie"), "theme_preview") || parseCookie(request.headers.get("cookie"), "theme");
  const referer = request.headers.get("referer");
  let refererTheme: string | null = null;
  if (referer) {
    try {
      const refUrl = new URL(referer);
      refererTheme = normalizeTemplateKey(refUrl.searchParams.get("theme_preview") || refUrl.searchParams.get("theme"));
    } catch {}
  }

  let requestedTemplateKey: string | null = null;
  if (paramTheme === "reset" || paramTheme === "clear") {
    requestedTemplateKey = null;
  } else if (paramTheme) {
    requestedTemplateKey = normalizeTemplateKey(paramTheme);
  } else if (cookieTheme && cookieTheme !== "reset" && cookieTheme !== "clear") {
    requestedTemplateKey = normalizeTemplateKey(cookieTheme);
  } else if (refererTheme && refererTheme !== "reset" && refererTheme !== "clear") {
    requestedTemplateKey = refererTheme;
  }

  const configuredTemplateKey = requestedTemplateKey || activeTemplateKey;
  const templateKey = findThemePageLoader(configuredTemplateKey, pageName)
    ? configuredTemplateKey
    : activeTemplateKey;

  const previewHomepage = templateKey.toLowerCase() === "professional-news"
    ? decodePreviewHomepage(url.searchParams.get("preview_config"))
    : null;
  const resolvedSiteConfig = previewHomepage && siteConfig
    ? {
        ...siteConfig,
        template: { ...siteConfig.template, key: templateKey },
        config: { ...siteConfig.config, homepage: previewHomepage },
      }
    : siteConfig && templateKey !== activeTemplateKey
      ? { ...siteConfig, template: { ...siteConfig.template, key: templateKey } }
      : siteConfig;

  const loader =
    findThemePageLoader(templateKey, pageName) ??
    findThemePageLoader("Automotive", pageName) ??
    findThemePageLoader("evnesia-v2", pageName);

  if (!loader) throw new Error(`Theme page not found: ${pageName}`);

  const module = await loader() as { default: any };
  return { default: module.default, siteConfig: resolvedSiteConfig };
}

function decodePreviewHomepage(value: string | null) {
  if (!value || value.length > 24_000) return null;
  try {
    const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
    const bytes = Uint8Array.from(atob(padded), (char) => char.charCodeAt(0));
    const parsed = JSON.parse(new TextDecoder().decode(bytes)) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
    return normalizeProfessionalNewsConfig(parsed);
  } catch {
    return null;
  }
}
