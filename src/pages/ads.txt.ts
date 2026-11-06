import type { APIContext } from "astro";
import { resolveApiUrl, portalDomainFromScope } from "@/lib/api";

export async function GET(context: APIContext) {
  const portalDomain = portalDomainFromScope(context.request);
  const base = resolveApiUrl(context.request).replace(/\/$/, "");
  const url = new URL(`${base}/ads-txt`);
  url.searchParams.set("portal_domain", portalDomain);
  url.searchParams.set("domain", portalDomain);

  try {
    const resp = await fetch(url, {
      headers: { "x-portal-domain": portalDomain },
    });
    if (resp.ok) {
      const text = await resp.text();
      return new Response(text, {
        headers: {
          "content-type": "text/plain; charset=utf-8",
          "cache-control": "public, max-age=300",
        },
      });
    }
  } catch {
    // fall through to empty default
  }

  return new Response("", {
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "public, max-age=60",
    },
  });
}
