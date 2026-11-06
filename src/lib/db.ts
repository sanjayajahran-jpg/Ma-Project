import mysql from 'mysql2/promise';

let pool: mysql.Pool | null = null;

/**
 * Get or create a MySQL connection pool.
 * Reads connection config from environment variables.
 */
export function getPool(): mysql.Pool {
  if (pool) return pool;

  pool = mysql.createPool({
    host: import.meta.env.DB_HOST ?? process.env.DB_HOST ?? 'localhost',
    port: Number(import.meta.env.DB_PORT ?? process.env.DB_PORT ?? 3306),
    user: import.meta.env.DB_USER ?? process.env.DB_USER ?? 'root',
    password: import.meta.env.DB_PASSWORD ?? process.env.DB_PASSWORD ?? '',
    database: import.meta.env.DB_NAME ?? process.env.DB_NAME ?? 'autodrive',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
    // Return plain objects instead of RowDataPacket
    typeCast: true,
  });

  return pool;
}

/**
 * Execute a query and return typed results.
 */
export async function query<T = any>(sql: string, params: any[] = []): Promise<T[]> {
  const db = getPool();
  const [rows] = await db.execute(sql, params);
  return rows as T[];
}

/**
 * Execute a single-row query.
 */
export async function queryOne<T = any>(sql: string, params: any[] = []): Promise<T | null> {
  const results = await query<T>(sql, params);
  return results[0] ?? null;
}

/**
 * Execute an INSERT/UPDATE/DELETE and return result info.
 */
export async function execute(sql: string, params: any[] = []) {
  const db = getPool();
  const [result] = await db.execute(sql, params);
  return result as mysql.ResultSetHeader;
}

/**
 * Test the database connection.
 */
export async function testConnection(): Promise<boolean> {
  try {
    const db = getPool();
    await db.query('SELECT 1');
    return true;
  } catch (error) {
    console.error('[DB] Connection test failed:', error);
    return false;
  }
}
