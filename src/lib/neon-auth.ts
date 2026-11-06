const getEnv = (key: string): string => {
  if (typeof process !== "undefined" && process.env?.[key]) {
    return process.env[key] as string;
  }
  return (import.meta.env as any)?.[key] || "";
};

export const NEON_AUTH_BASE_URL = getEnv("NEON_AUTH_BASE_URL");
export const NEON_AUTH_JWKS_URL = getEnv("NEON_AUTH_JWKS_URL");

/**
 * Check whether Neon Auth endpoint is reachable and responsive.
 */
export async function checkNeonAuthStatus(): Promise<{ ok: boolean; status: number; message: string }> {
  if (!NEON_AUTH_JWKS_URL) {
    return { ok: false, status: 400, message: "NEON_AUTH_JWKS_URL is not set" };
  }
  try {
    const res = await fetch(NEON_AUTH_JWKS_URL);
    return {
      ok: res.ok,
      status: res.status,
      message: res.ok ? "Neon Auth JWKS endpoint reachable" : `HTTP ${res.status}`,
    };
  } catch (error: any) {
    return {
      ok: false,
      status: 500,
      message: error?.message || String(error),
    };
  }
}
