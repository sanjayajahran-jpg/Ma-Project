import { defineMiddleware } from "astro:middleware";

function shouldCache(request: Request): boolean {
  const domain =
    request.headers.get("x-forwarded-host") ??
    request.headers.get("x-portal-domain") ??
    request.headers.get("host") ??
    "";
  const clean = domain.replace(/^www\./, "").toLowerCase();

  if (import.meta.env.PUBLIC_DEBUG_MODE === "false") return true;

  const raw =
    (typeof process !== "undefined" && process.env?.PUBLIC_CACHE_DOMAINS) ||
    import.meta.env.PUBLIC_CACHE_DOMAINS ||
    "";
  const domains = new Set(
    raw
      .split(",")
      .map((d: string) => d.trim().toLowerCase().replace(/^www\./, ""))
      .filter(Boolean),
  );
  return domains.has(clean);
}

export const onRequest = defineMiddleware(async (context, next) => {
  const themeParam = context.url.searchParams.get("theme_preview")?.trim();
  if (themeParam === "reset" || themeParam === "clear") {
    context.cookies.delete("theme_preview", { path: "/" });
  } else if (themeParam) {
    context.cookies.set("theme_preview", themeParam, { path: "/", maxAge: 60 * 60 * 24 });
  }

  const response = await next();

  if (
    response.status === 200 &&
    !response.headers.has("Cache-Control") &&
    shouldCache(context.request)
  ) {
    response.headers.set(
      "Cache-Control",
      "public, max-age=0, s-maxage=60, stale-while-revalidate=30",
    );
  }

  return response;
});
