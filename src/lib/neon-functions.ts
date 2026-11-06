const getEnv = (key: string): string => {
  if (typeof process !== "undefined" && process.env?.[key]) {
    return process.env[key] as string;
  }
  return (import.meta.env as any)?.[key] || "";
};

const helloBaseUrl = getEnv("NEON_FUNCTION_HELLO_BASE_URL");

/**
 * Call the deployed Neon Function "hello".
 */
export async function callNeonHelloFunction(): Promise<{ ok: boolean; status: number; text: string }> {
  const url = helloBaseUrl || "https://br-withered-thunder-azpp43y4-hello.compute.c-3.ap-southeast-1.aws.neon.tech";
  try {
    const res = await fetch(url);
    const text = await res.text();
    return {
      ok: res.ok,
      status: res.status,
      text,
    };
  } catch (error: any) {
    return {
      ok: false,
      status: 500,
      text: error?.message || String(error),
    };
  }
}
