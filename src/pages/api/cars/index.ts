import type { APIRoute } from 'astro';
import { query } from '@/lib/db';
import type { Car } from '@/lib/automotive-types';

/**
 * GET /api/cars
 *
 * Query params:
 *   brand    — filter by brand slug (e.g. ?brand=toyota)
 *   engine   — filter by engine type slug (e.g. ?engine=ev)
 *   body     — filter by body type slug (e.g. ?body=suv)
 *   year     — filter by year (e.g. ?year=2026)
 *   featured — show featured only (e.g. ?featured=1)
 *   search   — search by name (e.g. ?search=ioniq)
 *   sort     — sort field: price_asc, price_desc, name, newest (default: newest)
 *   limit    — max results (default: 50)
 *   page     — pagination page (default: 1)
 */
export const GET: APIRoute = async ({ url }) => {
  try {
    const brand = url.searchParams.get('brand');
    const engine = url.searchParams.get('engine');
    const body = url.searchParams.get('body');
    const year = url.searchParams.get('year');
    const featured = url.searchParams.get('featured');
    const search = url.searchParams.get('search');
    const sort = url.searchParams.get('sort') ?? 'newest';
    const limit = Math.min(Number(url.searchParams.get('limit') ?? 50), 100);
    const page = Math.max(Number(url.searchParams.get('page') ?? 1), 1);
    const offset = (page - 1) * limit;

    const conditions: string[] = ["c.status = 'active'"];
    const params: any[] = [];

    if (brand) {
      conditions.push('b.slug = ?');
      params.push(brand);
    }
    if (engine) {
      conditions.push('et.slug = ?');
      params.push(engine);
    }
    if (body) {
      conditions.push('bt.slug = ?');
      params.push(body);
    }
    if (year) {
      conditions.push('c.year = ?');
      params.push(Number(year));
    }
    if (featured === '1') {
      conditions.push('c.is_featured = 1');
    }
    if (search) {
      conditions.push('c.name LIKE ?');
      params.push(`%${search}%`);
    }

    const whereClause = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

    let orderClause = 'ORDER BY c.is_featured DESC, c.created_at DESC';
    switch (sort) {
      case 'price_asc': orderClause = 'ORDER BY c.price_start ASC'; break;
      case 'price_desc': orderClause = 'ORDER BY c.price_start DESC'; break;
      case 'name': orderClause = 'ORDER BY c.name ASC'; break;
      case 'newest': orderClause = 'ORDER BY c.year DESC, c.created_at DESC'; break;
    }

    // Count total
    const countSql = `
      SELECT COUNT(*) as total
      FROM cars c
      JOIN brands b ON c.brand_id = b.id
      JOIN engine_types et ON c.engine_type_id = et.id
      LEFT JOIN body_types bt ON c.body_type_id = bt.id
      ${whereClause}
    `;
    const [countRow] = await query<{ total: number }>(countSql, params);
    const total = countRow?.total ?? 0;

    // Fetch cars
    const sql = `
      SELECT
        c.*,
        b.name AS brand_name, b.slug AS brand_slug,
        et.name AS engine_type_name, et.slug AS engine_type_slug,
        bt.name AS body_type_name, bt.slug AS body_type_slug
      FROM cars c
      JOIN brands b ON c.brand_id = b.id
      JOIN engine_types et ON c.engine_type_id = et.id
      LEFT JOIN body_types bt ON c.body_type_id = bt.id
      ${whereClause}
      ${orderClause}
      LIMIT ? OFFSET ?
    `;
    const cars = await query<Car>(sql, [...params, limit, offset]);

    return new Response(JSON.stringify({
      items: cars,
      total,
      page,
      page_size: limit,
      total_pages: Math.ceil(total / limit),
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error: any) {
    // Graceful fallback to JSON dataset if MySQL is not running
    try {
      const ELECTRIFIED_CARS_DATA = (await import('@/data/electrified-cars.json')).default;
      const brand = url.searchParams.get('brand')?.toLowerCase();
      const engine = url.searchParams.get('engine')?.toLowerCase();
      const search = url.searchParams.get('search')?.toLowerCase();
      const limit = Math.min(Number(url.searchParams.get('limit') ?? 50), 100);
      const page = Math.max(Number(url.searchParams.get('page') ?? 1), 1);

      let filtered = (ELECTRIFIED_CARS_DATA as any[]).map((c: any, index: number) => ({
        id: index + 1,
        slug: c.slug,
        name: c.name,
        brand_name: c.brand,
        brand_slug: (c.brand || '').toLowerCase().replace(/[^a-z0-9]/g, ''),
        price_start: c.priceVal ? c.priceVal * 1000000 : 0,
        price_end: c.priceVal ? c.priceVal * 1000000 : 0,
        price_display: c.price,
        engine_type_slug: c.engineType?.toLowerCase() || 'ev',
        engine_type_name: c.engineType || 'BEV',
        body_type_name: c.bodyType || 'SUV',
        image_url: c.img,
        specs: c.specs,
      }));

      if (brand) {
        filtered = filtered.filter(c => c.brand_slug.includes(brand) || c.brand_name.toLowerCase().includes(brand));
      }
      if (engine) {
        filtered = filtered.filter(c => c.engine_type_slug.includes(engine));
      }
      if (search) {
        filtered = filtered.filter(c => c.name.toLowerCase().includes(search) || c.brand_name.toLowerCase().includes(search));
      }

      const total = filtered.length;
      const offset = (page - 1) * limit;
      const items = filtered.slice(offset, offset + limit);

      return new Response(JSON.stringify({
        items,
        total,
        page,
        page_size: limit,
        total_pages: Math.ceil(total / limit),
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    } catch (fallbackError: any) {
      console.error('[API /api/cars] Error:', error.message);
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
