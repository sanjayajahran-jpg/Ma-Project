-- ============================================================
-- AutoDrive PRO — Database Schema
-- Portal Otomotif: Katalog, Spesifikasi, Komparasi, Kalkulator
-- ============================================================

CREATE DATABASE IF NOT EXISTS autodrive
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE autodrive;

-- ------------------------------------------------------------
-- 1. Brands (Merek Mobil)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS brands (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) NOT NULL UNIQUE,
  country VARCHAR(80) DEFAULT NULL,
  logo_url VARCHAR(500) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. Engine Types (Jenis Mesin)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS engine_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,          -- e.g. 'EV (Listrik)', 'Hybrid', 'Bensin', 'Diesel'
  slug VARCHAR(50) NOT NULL UNIQUE,   -- e.g. 'ev', 'hybrid', 'bensin', 'diesel'
  icon_url VARCHAR(500) DEFAULT NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. Body Types (Tipe Bodi)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS body_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,          -- e.g. 'SUV', 'Sedan', 'Hatchback', 'MPV', 'Pickup'
  slug VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. Cars (Katalog Mobil Utama)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cars (
  id INT AUTO_INCREMENT PRIMARY KEY,
  brand_id INT NOT NULL,
  engine_type_id INT NOT NULL,
  body_type_id INT DEFAULT NULL,
  name VARCHAR(200) NOT NULL,
  slug VARCHAR(200) NOT NULL UNIQUE,
  year INT NOT NULL,
  price_start BIGINT DEFAULT NULL,       -- Harga OTR mulai dari (dalam Rupiah)
  price_end BIGINT DEFAULT NULL,         -- Harga OTR tertinggi
  tagline VARCHAR(300) DEFAULT NULL,
  description TEXT DEFAULT NULL,
  image_url VARCHAR(500) DEFAULT NULL,
  thumbnail_url VARCHAR(500) DEFAULT NULL,
  is_featured TINYINT(1) DEFAULT 0,
  is_new TINYINT(1) DEFAULT 1,
  status ENUM('active','draft','discontinued') DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE,
  FOREIGN KEY (engine_type_id) REFERENCES engine_types(id),
  FOREIGN KEY (body_type_id) REFERENCES body_types(id),
  INDEX idx_brand (brand_id),
  INDEX idx_engine (engine_type_id),
  INDEX idx_year (year),
  INDEX idx_status (status)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 5. Car Specs (Spesifikasi Teknis Detail)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS car_specs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  car_id INT NOT NULL UNIQUE,
  -- Mesin
  engine_capacity_cc INT DEFAULT NULL,        -- Kapasitas mesin (cc)
  engine_name VARCHAR(200) DEFAULT NULL,      -- Nama mesin (e.g. '2.0L Skyactiv-G')
  horsepower INT DEFAULT NULL,                -- Tenaga (HP)
  torque_nm INT DEFAULT NULL,                 -- Torsi (Nm)
  transmission VARCHAR(100) DEFAULT NULL,     -- e.g. 'CVT', '6AT', 'Manual 6-speed'
  drivetrain VARCHAR(50) DEFAULT NULL,        -- e.g. 'FWD', 'AWD', '4WD', 'RWD'
  -- Performa
  acceleration_0_100 DECIMAL(4,1) DEFAULT NULL,  -- 0-100 km/j (detik)
  top_speed_kmh INT DEFAULT NULL,
  -- Konsumsi & Jarak Tempuh
  fuel_consumption_kmpl DECIMAL(5,1) DEFAULT NULL,  -- Konsumsi BBM (km/L)
  battery_capacity_kwh DECIMAL(5,1) DEFAULT NULL,   -- Kapasitas baterai (kWh) — untuk EV/Hybrid
  electric_range_km INT DEFAULT NULL,                -- Jarak tempuh listrik (km)
  -- Dimensi
  length_mm INT DEFAULT NULL,
  width_mm INT DEFAULT NULL,
  height_mm INT DEFAULT NULL,
  wheelbase_mm INT DEFAULT NULL,
  ground_clearance_mm INT DEFAULT NULL,
  curb_weight_kg INT DEFAULT NULL,
  -- Kapasitas
  seating_capacity INT DEFAULT NULL,
  trunk_volume_liters INT DEFAULT NULL,
  fuel_tank_liters INT DEFAULT NULL,
  -- Fitur Keamanan
  airbags INT DEFAULT NULL,
  abs_ebd TINYINT(1) DEFAULT 0,
  esc TINYINT(1) DEFAULT 0,
  adas TINYINT(1) DEFAULT 0,                -- Advanced Driver Assistance Systems
  -- Rating
  safety_rating DECIMAL(2,1) DEFAULT NULL,   -- 0.0 - 5.0
  comfort_rating DECIMAL(2,1) DEFAULT NULL,
  performance_rating DECIMAL(2,1) DEFAULT NULL,
  value_rating DECIMAL(2,1) DEFAULT NULL,
  FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 6. Car Variants (Varian per Model)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS car_variants (
  id INT AUTO_INCREMENT PRIMARY KEY,
  car_id INT NOT NULL,
  name VARCHAR(200) NOT NULL,            -- e.g. 'CX-5 Elite', 'CX-5 Kuro Edition'
  price BIGINT NOT NULL,                 -- Harga OTR (Rupiah)
  highlights TEXT DEFAULT NULL,          -- Fitur unggulan varian
  FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE,
  INDEX idx_car (car_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 7. Fuel Prices (Harga BBM & Listrik)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fuel_prices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  fuel_type VARCHAR(50) NOT NULL UNIQUE,   -- e.g. 'Pertalite', 'Pertamax', 'Pertamax Turbo', 'Solar', 'SPKLU'
  price_per_unit DECIMAL(12,2) NOT NULL,   -- Rp per Liter / per kWh
  unit VARCHAR(20) NOT NULL DEFAULT 'L',   -- 'L' (liter) atau 'kWh'
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- SEED DATA
-- ============================================================

-- Brands
INSERT INTO brands (name, slug, country) VALUES
  ('Toyota', 'toyota', 'Jepang'),
  ('Honda', 'honda', 'Jepang'),
  ('Mazda', 'mazda', 'Jepang'),
  ('Hyundai', 'hyundai', 'Korea Selatan'),
  ('Wuling', 'wuling', 'Tiongkok'),
  ('BYD', 'byd', 'Tiongkok'),
  ('Mitsubishi', 'mitsubishi', 'Jepang'),
  ('Suzuki', 'suzuki', 'Jepang'),
  ('Daihatsu', 'daihatsu', 'Jepang'),
  ('BMW', 'bmw', 'Jerman'),
  ('Mercedes-Benz', 'mercedes-benz', 'Jerman'),
  ('Tesla', 'tesla', 'Amerika Serikat'),
  ('Ford', 'ford', 'Amerika Serikat'),
  ('Nissan', 'nissan', 'Jepang'),
  ('Porsche', 'porsche', 'Jerman');

-- Engine Types
INSERT INTO engine_types (name, slug) VALUES
  ('EV (Listrik)', 'ev'),
  ('Hybrid (HEV & PHEV)', 'hybrid'),
  ('Bensin (ICE)', 'bensin'),
  ('Diesel & Turbo', 'diesel');

-- Body Types
INSERT INTO body_types (name, slug) VALUES
  ('SUV', 'suv'),
  ('Sedan', 'sedan'),
  ('Hatchback', 'hatchback'),
  ('MPV', 'mpv'),
  ('Pickup', 'pickup'),
  ('Crossover', 'crossover'),
  ('Coupe', 'coupe'),
  ('Wagon', 'wagon');

-- Cars (20 Mobil Populer Indonesia 2026)
INSERT INTO cars (brand_id, engine_type_id, body_type_id, name, slug, year, price_start, price_end, tagline, is_featured, is_new) VALUES
  -- Toyota
  (1, 2, 1, 'Toyota Innova Zenix', 'toyota-innova-zenix', 2026, 419000000, 560000000, 'MPV Premium Hybrid Pertama di Kelasnya', 1, 1),
  (1, 3, 1, 'Toyota Avanza', 'toyota-avanza', 2026, 237000000, 295000000, 'Keluarga Indonesia Sejak 2003', 0, 0),
  (1, 2, 1, 'Toyota Yaris Cross', 'toyota-yaris-cross', 2026, 310000000, 395000000, 'Compact SUV Hybrid Stylish', 1, 1),

  -- Honda
  (2, 2, 1, 'Honda CR-V RS e:HEV', 'honda-crv-rs-ehev', 2026, 739000000, 799000000, 'SUV Hybrid Berperforma Tinggi', 1, 1),
  (2, 3, 2, 'Honda Civic RS', 'honda-civic-rs', 2026, 567000000, 599000000, 'Sedan Sport Paling Dinamis', 0, 1),

  -- Mazda
  (3, 3, 1, 'Mazda CX-5 2026', 'mazda-cx5-2026', 2026, 560000000, 650000000, 'Driving Matters — Desain Kodo & i-Activ AWD', 1, 1),
  (3, 3, 6, 'Mazda CX-30', 'mazda-cx30', 2026, 469000000, 530000000, 'Crossover Premium dengan Skyactiv-X', 0, 1),

  -- Hyundai
  (4, 1, 1, 'Hyundai Ioniq 5', 'hyundai-ioniq-5', 2026, 748000000, 829000000, 'EV Futuristik Platform E-GMP', 1, 1),
  (4, 1, 2, 'Hyundai Ioniq 6', 'hyundai-ioniq-6', 2026, 850000000, 950000000, 'Sedan Elektrik Streamliner', 0, 1),
  (4, 3, 1, 'Hyundai Creta', 'hyundai-creta', 2026, 291000000, 399000000, 'Compact SUV Fitur Canggih', 0, 1),

  -- Wuling
  (5, 1, 3, 'Wuling Binguo EV', 'wuling-binguo-ev', 2026, 199000000, 289000000, 'City Car Listrik Terjangkau', 1, 1),
  (5, 1, 1, 'Wuling Cloud EV', 'wuling-cloud-ev', 2026, 379000000, 449000000, 'SUV Listrik Keluarga', 0, 1),

  -- BYD
  (6, 1, 2, 'BYD Seal', 'byd-seal', 2026, 559000000, 699000000, 'Sedan Elektrik Blade Battery', 1, 1),
  (6, 1, 1, 'BYD Atto 3', 'byd-atto-3', 2026, 399000000, 489000000, 'Compact EV SUV Serbaguna', 0, 1),

  -- Mitsubishi
  (7, 3, 1, 'Mitsubishi Xpander', 'mitsubishi-xpander', 2026, 269000000, 319000000, 'MPV Crossover Terlaris Indonesia', 0, 0),
  (7, 4, 1, 'Mitsubishi Pajero Sport', 'mitsubishi-pajero-sport', 2026, 539000000, 685000000, 'SUV Diesel Tangguh Off-Road', 1, 1),

  -- Tesla
  (12, 1, 2, 'Tesla Model 3', 'tesla-model-3', 2026, 750000000, 950000000, 'Sedan Listrik Performa Terbaik', 1, 1),
  (12, 1, 1, 'Tesla Model Y', 'tesla-model-y', 2026, 850000000, 1100000000, 'SUV Listrik Paling Populer Dunia', 0, 1),

  -- Porsche
  (15, 1, 2, 'Porsche Taycan Turbo GT', 'porsche-taycan-turbo-gt', 2026, 3500000000, 4200000000, 'Electric Supercar 1.092 HP — Rekor Nürburgring', 1, 1),

  -- Suzuki
  (8, 3, 4, 'Suzuki Ertiga', 'suzuki-ertiga', 2026, 237000000, 289000000, 'MPV Irit 7-Seater', 0, 0);

-- Car Specs (contoh 5 mobil)
INSERT INTO car_specs (car_id, engine_name, engine_capacity_cc, horsepower, torque_nm, transmission, drivetrain, acceleration_0_100, top_speed_kmh, fuel_consumption_kmpl, battery_capacity_kwh, electric_range_km, length_mm, width_mm, height_mm, wheelbase_mm, seating_capacity, airbags, abs_ebd, esc, adas, safety_rating, comfort_rating, performance_rating, value_rating) VALUES
  -- Toyota Innova Zenix Hybrid
  (1, '2.0L Dynamic Force Hybrid', 1987, 152, 188, 'e-CVT', 'FWD', 10.5, 180, 18.4, NULL, NULL, 4755, 1850, 1795, 2850, 7, 6, 1, 1, 1, 5.0, 4.5, 4.0, 4.5),

  -- Honda CR-V RS e:HEV
  (4, '2.0L i-VTEC Hybrid e:HEV', 1993, 204, 335, 'e-CVT', 'AWD', 8.6, 190, 20.1, NULL, NULL, 4694, 1866, 1680, 2700, 5, 6, 1, 1, 1, 5.0, 4.8, 4.5, 4.0),

  -- Hyundai Ioniq 5
  (8, 'Dual Electric Motor (E-GMP)', NULL, 320, 605, 'Single-Speed Reduction', 'AWD', 5.1, 185, NULL, 77.4, 481, 4635, 1890, 1605, 3000, 5, 6, 1, 1, 1, 5.0, 4.8, 4.7, 4.2),

  -- BYD Seal
  (13, 'Dual Motor AWD (Blade Battery)', NULL, 523, 670, 'Single-Speed Reduction', 'AWD', 3.8, 200, NULL, 82.5, 570, 4800, 1875, 1460, 2920, 5, 8, 1, 1, 1, 5.0, 4.6, 4.9, 4.5),

  -- Porsche Taycan Turbo GT
  (19, 'Dual-Motor Overboost Attack Mode', NULL, 1092, 1340, 'Single-Speed Reduction + 2-speed rear', 'AWD', 2.2, 305, NULL, 105.0, 555, 4963, 1966, 1378, 2900, 4, 10, 1, 1, 1, 5.0, 4.5, 5.0, 3.5);

-- Car Variants
INSERT INTO car_variants (car_id, name, price) VALUES
  (1, 'Innova Zenix G CVT', 419000000),
  (1, 'Innova Zenix V CVT', 479000000),
  (1, 'Innova Zenix Q HEV CVT', 540000000),
  (1, 'Innova Zenix Q HEV CVT TSS', 560000000),
  (8, 'Ioniq 5 Standard Range', 748000000),
  (8, 'Ioniq 5 Long Range 2WD', 789000000),
  (8, 'Ioniq 5 Long Range AWD', 829000000),
  (19, 'Taycan Turbo GT', 3500000000),
  (19, 'Taycan Turbo GT with Weissach Package', 4200000000);

-- Fuel Prices (Harga BBM & Listrik Indonesia 2026)
INSERT INTO fuel_prices (fuel_type, price_per_unit, unit) VALUES
  ('Pertalite', 10000.00, 'L'),
  ('Pertamax', 13700.00, 'L'),
  ('Pertamax Turbo', 15200.00, 'L'),
  ('Solar (Subsidi)', 6800.00, 'L'),
  ('Dexlite', 14500.00, 'L'),
  ('Pertamina Dex', 15800.00, 'L'),
  ('SPKLU (Listrik)', 2466.00, 'kWh');
