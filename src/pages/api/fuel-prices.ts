import type { APIRoute } from 'astro';
import { query } from '@/lib/db';
import type { FuelPrice } from '@/lib/automotive-types';

/**
 * GET /api/fuel-prices
 *
 * Returns current fuel & electricity prices in Indonesia.
 */
export const GET: APIRoute = async () => {
  try {
    const prices = await query<FuelPrice>(
      'SELECT * FROM fuel_prices ORDER BY fuel_type ASC'
    );

    return new Response(JSON.stringify({ items: prices }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error: any) {
    const defaultPrices = [
      { id: 1, fuel_type: 'ron90', name: 'Pertalite (RON 90)', price_per_unit: 10000, unit: 'liter', updated_at: '2026-03-01' },
      { id: 2, fuel_type: 'ron92', name: 'Pertamax (RON 92)', price_per_unit: 12950, unit: 'liter', updated_at: '2026-03-01' },
      { id: 3, fuel_type: 'ron98', name: 'Pertamax Turbo (RON 98)', price_per_unit: 14400, unit: 'liter', updated_at: '2026-03-01' },
      { id: 4, fuel_type: 'diesel', name: 'Dexlite (CN 51)', price_per_unit: 13900, unit: 'liter', updated_at: '2026-03-01' },
      { id: 5, fuel_type: 'electricity_home', name: 'Listrik Rumah (1.300+ VA)', price_per_unit: 1699.53, unit: 'kWh', updated_at: '2026-03-01' },
      { id: 6, fuel_type: 'electricity_spklu', name: 'Listrik SPKLU Fast Charging (PLN)', price_per_unit: 2466, unit: 'kWh', updated_at: '2026-03-01' },
    ];
    return new Response(JSON.stringify({ items: defaultPrices }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
