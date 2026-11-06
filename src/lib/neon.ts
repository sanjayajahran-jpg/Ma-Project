import { Pool, neon } from "@neondatabase/serverless";

// Connection string from environment variables
const getDatabaseUrl = () => {
  if (typeof process !== "undefined" && process.env?.DATABASE_URL) {
    return process.env.DATABASE_URL;
  }
  return import.meta.env.DATABASE_URL || "";
};

const databaseUrl = getDatabaseUrl();

/**
 * Neon SQL client for tagged template queries.
 * Example:
 *   const rows = await sql`SELECT * FROM cars WHERE status = 'active'`;
 */
export const sql = databaseUrl ? neon(databaseUrl) : null;

/**
 * Neon connection pool.
 */
export const pool = databaseUrl ? new Pool({ connectionString: databaseUrl }) : null;

/**
 * Helper to check connection to Neon Lakebase Postgres.
 */
export async function checkNeonPostgres(): Promise<{ ok: boolean; message: string; version?: string }> {
  if (!sql) {
    return { ok: false, message: "DATABASE_URL is not configured." };
  }
  try {
    const result = await sql`SELECT version(), current_database() as db`;
    return {
      ok: true,
      message: `Connected to database '${result[0]?.db}' on Neon Lakebase Postgres`,
      version: String(result[0]?.version)
    };
  } catch (error: any) {
    return { ok: false, message: error?.message || String(error) };
  }
}
