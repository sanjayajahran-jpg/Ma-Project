import type { APIRoute } from 'astro';
import { query } from '@/lib/db';
import type { Brand } from '@/lib/automotive-types';

/**
 * GET /api/brands
 *
 * Returns all car brands with optional car count.
 * Query params:
 *   with_count — include number of active cars per brand (e.g. ?with_count=1)
 */
export const GET: APIRoute = async ({ url }) => {
  try {
    const withCount = url.searchParams.get('with_count') === '1';

    let sql: string;
    if (withCount) {
      sql = `
        SELECT b.*, COUNT(c.id) AS car_count
        FROM brands b
        LEFT JOIN cars c ON c.brand_id = b.id AND c.status = 'active'
        GROUP BY b.id
        HAVING car_count > 0
        ORDER BY b.name ASC
      `;
    } else {
      sql = 'SELECT * FROM brands ORDER BY name ASC';
    }

    const brands = await query<Brand & { car_count?: number }>(sql);

    return new Response(JSON.stringify({ items: brands }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error: any) {
    try {
      const ELECTRIFIED_CARS_DATA = (await import('@/data/electrified-cars.json')).default;
      const brandCounts: Record<string, number> = {};
      ELECTRIFIED_CARS_DATA.forEach((c: any) => {
        brandCounts[c.brand] = (brandCounts[c.brand] || 0) + 1;
      });

      const items = Object.keys(brandCounts).sort().map((brandName, idx) => ({
        id: idx + 1,
        name: brandName,
        slug: brandName.toLowerCase().replace(/[^a-z0-9]/g, ''),
        car_count: brandCounts[brandName],
      }));

      return new Response(JSON.stringify({ items }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    } catch (fallbackError: any) {
      console.error('[API /api/brands] Error:', error.message);
      return new Response(JSON.stringify({
        error: 'Database error',
        message: error.message,
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  }
};
