import type { APIRoute } from 'astro';
import { query, queryOne } from '@/lib/db';
import type { Car, CarSpec, CarVariant, CarDetail } from '@/lib/automotive-types';

/**
 * GET /api/cars/[id]
 *
 * Returns full car detail including specs and variants.
 * Accepts either numeric ID or slug.
 */
export const GET: APIRoute = async ({ params }) => {
  try {
    const idOrSlug = params.id;
    if (!idOrSlug) {
      return new Response(JSON.stringify({ error: 'Car ID or slug is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Determine if lookup is by ID or slug
    const isNumeric = /^\d+$/.test(idOrSlug);
    const carSql = `
      SELECT
        c.*,
        b.name AS brand_name, b.slug AS brand_slug,
        et.name AS engine_type_name, et.slug AS engine_type_slug,
        bt.name AS body_type_name, bt.slug AS body_type_slug
      FROM cars c
      JOIN brands b ON c.brand_id = b.id
      JOIN engine_types et ON c.engine_type_id = et.id
      LEFT JOIN body_types bt ON c.body_type_id = bt.id
      WHERE ${isNumeric ? 'c.id = ?' : 'c.slug = ?'}
      LIMIT 1
    `;
    const car = await queryOne<Car>(carSql, [isNumeric ? Number(idOrSlug) : idOrSlug]);

    if (!car) {
      return new Response(JSON.stringify({ error: 'Car not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Fetch specs
    const specs = await queryOne<CarSpec>(
      'SELECT * FROM car_specs WHERE car_id = ?',
      [car.id]
    );

    // Fetch variants
    const variants = await query<CarVariant>(
      'SELECT * FROM car_variants WHERE car_id = ? ORDER BY price ASC',
      [car.id]
    );

    const detail: CarDetail = {
      ...car,
      specs,
      variants,
    };

    return new Response(JSON.stringify(detail), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error: any) {
    try {
      const idOrSlug = params.id;
      const ELECTRIFIED_CARS_DATA = (await import('@/data/electrified-cars.json')).default;
      const found = ELECTRIFIED_CARS_DATA.find((c: any) => c.slug === idOrSlug || c.name.toLowerCase().includes(idOrSlug?.toLowerCase() || ''));

      if (!found) {
        return new Response(JSON.stringify({ error: 'Car not found' }), {
          status: 404,
          headers: { 'Content-Type': 'application/json' },
        });
      }

      const carData: any = found;
      const detail = {
        id: 1,
        slug: carData.slug,
        name: carData.name,
        brand_name: carData.brand,
        price_start: carData.priceVal ? carData.priceVal * 1000000 : 0,
        price_display: carData.price,
        engine_type_slug: carData.engineType?.toLowerCase() || 'ev',
        image_url: carData.img,
        specs: carData.specs,
        variants: carData.variants || [],
      };

      return new Response(JSON.stringify(detail), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    } catch (fallbackError: any) {
      console.error('[API /api/cars/:id] Error:', error.message);
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
