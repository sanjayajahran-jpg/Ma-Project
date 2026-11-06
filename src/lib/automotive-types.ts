/**
 * AutoDrive PRO — Automotive-specific type definitions.
 * These types represent database entities for the car catalog system.
 */

export interface Brand {
  id: number;
  name: string;
  slug: string;
  country: string | null;
  logo_url: string | null;
}

export interface EngineType {
  id: number;
  name: string;
  slug: string;
  icon_url: string | null;
}

export interface BodyType {
  id: number;
  name: string;
  slug: string;
}

export interface Car {
  id: number;
  brand_id: number;
  engine_type_id: number;
  body_type_id: number | null;
  name: string;
  slug: string;
  year: number;
  price_start: number | null;
  price_end: number | null;
  tagline: string | null;
  description: string | null;
  image_url: string | null;
  thumbnail_url: string | null;
  is_featured: boolean;
  is_new: boolean;
  status: 'active' | 'draft' | 'discontinued';
  // Joined fields
  brand_name?: string;
  brand_slug?: string;
  engine_type_name?: string;
  engine_type_slug?: string;
  body_type_name?: string;
  body_type_slug?: string;
}

export interface CarSpec {
  id: number;
  car_id: number;
  engine_name: string | null;
  engine_capacity_cc: number | null;
  horsepower: number | null;
  torque_nm: number | null;
  transmission: string | null;
  drivetrain: string | null;
  acceleration_0_100: number | null;
  top_speed_kmh: number | null;
  fuel_consumption_kmpl: number | null;
  battery_capacity_kwh: number | null;
  electric_range_km: number | null;
  length_mm: number | null;
  width_mm: number | null;
  height_mm: number | null;
  wheelbase_mm: number | null;
  ground_clearance_mm: number | null;
  curb_weight_kg: number | null;
  seating_capacity: number | null;
  seating_capacity_text?: string | null;
  trunk_volume_liters: number | null;
  fuel_tank_liters: number | null;
  airbags: number | null;
  abs_ebd: boolean;
  esc: boolean;
  adas: boolean;
  safety_rating: number | null;
  comfort_rating: number | null;
  performance_rating: number | null;
  value_rating: number | null;
}

export interface CarVariant {
  id: number;
  car_id: number;
  name: string;
  price: number;
  highlights: string | null;
}

export interface FuelPrice {
  id: number;
  fuel_type: string;
  price_per_unit: number;
  unit: string;
  updated_at: string;
}

/** Full car detail with specs, variants, and brand info */
export interface CarDetail extends Car {
  specs: CarSpec | null;
  variants: CarVariant[];
}

/** Fuel cost calculation request */
export interface FuelCostRequest {
  distance_km: number;           // Jarak tempuh per bulan (km)
  fuel_type: string;             // e.g. 'Pertamax', 'SPKLU (Listrik)'
  consumption: number;           // km/L atau km/kWh
}

/** Fuel cost calculation result */
export interface FuelCostResult {
  fuel_type: string;
  price_per_unit: number;
  unit: string;
  consumption: number;
  distance_km: number;
  fuel_needed: number;
  monthly_cost: number;
  yearly_cost: number;
}
