import type { APIRoute } from 'astro';
import { query } from '@/lib/db';
import type { FuelPrice, FuelCostRequest, FuelCostResult } from '@/lib/automotive-types';

/**
 * POST /api/calculator/fuel-cost
 *
 * Body: {
 *   "distance_km": 1500,
 *   "comparisons": [
 *     { "fuel_type": "Pertamax", "consumption_kmpl": 12 },
 *     { "fuel_type": "SPKLU (Listrik)", "consumption_kmpl": 6.5 }
 *   ]
 * }
 *
 * Returns monthly/yearly cost comparison between fuel types.
 */
export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const distanceKm: number = body.distance_km ?? 1500;
    const comparisons: Array<{ fuel_type: string; consumption_kmpl: number }> =
      body.comparisons ?? [];

    if (!comparisons.length) {
      return new Response(JSON.stringify({
        error: 'Provide "comparisons" array with fuel_type and consumption_kmpl'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Fetch all current fuel prices
    const prices = await query<FuelPrice>('SELECT * FROM fuel_prices');
    const priceMap = new Map(prices.map(p => [p.fuel_type, p]));

    const results: FuelCostResult[] = comparisons.map(comp => {
      const priceInfo = priceMap.get(comp.fuel_type);
      const pricePerUnit = priceInfo?.price_per_unit ?? 0;
      const unit = priceInfo?.unit ?? 'L';

      const fuelNeeded = distanceKm / comp.consumption_kmpl;
      const monthlyCost = fuelNeeded * pricePerUnit;
      const yearlyCost = monthlyCost * 12;

      return {
        fuel_type: comp.fuel_type,
        price_per_unit: pricePerUnit,
        unit,
        consumption: comp.consumption_kmpl,
        distance_km: distanceKm,
        fuel_needed: Math.round(fuelNeeded * 100) / 100,
        monthly_cost: Math.round(monthlyCost),
        yearly_cost: Math.round(yearlyCost),
      };
    });

    // Calculate savings (cheapest vs most expensive)
    const sorted = [...results].sort((a, b) => a.monthly_cost - b.monthly_cost);
    const cheapest = sorted[0];
    const mostExpensive = sorted[sorted.length - 1];
    const monthlySaving = mostExpensive.monthly_cost - cheapest.monthly_cost;
    const yearlySaving = mostExpensive.yearly_cost - cheapest.yearly_cost;

    return new Response(JSON.stringify({
      distance_km: distanceKm,
      results,
      summary: {
        cheapest: cheapest.fuel_type,
        most_expensive: mostExpensive.fuel_type,
        monthly_saving: monthlySaving,
        yearly_saving: yearlySaving,
      },
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error: any) {
    console.error('[API /api/calculator/fuel-cost] Error:', error.message);
    return new Response(JSON.stringify({
      error: 'Calculation error',
      message: error.message,
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
