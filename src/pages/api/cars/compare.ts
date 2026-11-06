import type { APIRoute } from 'astro';
import { query, queryOne } from '@/lib/db';
import type { Car, CarSpec, CarVariant } from '@/lib/automotive-types';

/**
 * POST /api/cars/compare
 *
 * Body: { "ids": [1, 8, 13] } or { "slugs": ["hyundai-ioniq-5", "byd-seal"] }
 * Returns full detail + specs for 2-4 cars side by side.
 */
export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const ids: number[] = body.ids ?? [];
    const slugs: string[] = body.slugs ?? [];

    if (ids.length === 0 && slugs.length === 0) {
      return new Response(JSON.stringify({ error: 'Provide "ids" or "slugs" array (2-4 items)' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const lookupValues = ids.length > 0 ? ids : slugs;
    if (lookupValues.length < 2 || lookupValues.length > 4) {
      return new Response(JSON.stringify({ error: 'Compare requires 2-4 cars' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const isById = ids.length > 0;
    const placeholders = lookupValues.map(() => '?').join(',');
    const carsSql = `
      SELECT
        c.*,
        b.name AS brand_name, b.slug AS brand_slug,
        et.name AS engine_type_name, et.slug AS engine_type_slug,
        bt.name AS body_type_name, bt.slug AS body_type_slug
      FROM cars c
      JOIN brands b ON c.brand_id = b.id
      JOIN engine_types et ON c.engine_type_id = et.id
      LEFT JOIN body_types bt ON c.body_type_id = bt.id
      WHERE ${isById ? `c.id IN (${placeholders})` : `c.slug IN (${placeholders})`}
    `;
    const cars = await query<Car>(carsSql, lookupValues);

    if (cars.length < 2) {
      return new Response(JSON.stringify({ error: 'Not enough valid cars found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Fetch specs & variants for each car
    const carIds = cars.map(c => c.id);
    const specPlaceholders = carIds.map(() => '?').join(',');

    const allSpecs = await query<CarSpec>(
      `SELECT * FROM car_specs WHERE car_id IN (${specPlaceholders})`,
      carIds
    );
    const allVariants = await query<CarVariant>(
      `SELECT * FROM car_variants WHERE car_id IN (${specPlaceholders}) ORDER BY price ASC`,
      carIds
    );

    const comparison = cars.map(car => ({
      ...car,
      specs: allSpecs.find(s => s.car_id === car.id) ?? null,
      variants: allVariants.filter(v => v.car_id === car.id),
    }));

    return new Response(JSON.stringify({ cars: comparison }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error: any) {
    console.error('[API /api/cars/compare] Error:', error.message);
    return new Response(JSON.stringify({
      error: 'Database error',
      message: error.message,
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
