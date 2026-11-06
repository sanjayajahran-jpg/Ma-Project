// brand-utils.ts — Official brand logos and metadata for EVHub.id
import ELECTRIFIED_CARS_DATA from "@/data/electrified-cars.json";

export function getBrandLogo(brand: string): string {
  if (!brand) return "/images/brands/byd-logo.svg";
  const clean = brand.toLowerCase()
    .replace(/ë/g, "e")
    .replace(/\s*\(.*?\)/g, "")
    .trim();

  if (clean.includes("mercedes")) return "/images/brands/mercedes-benz-logo.svg";
  if (clean.includes("gac") || clean.includes("aion")) return "/images/brands/gac-logo.svg";
  if (clean.includes("icar")) return "/images/brands/icar-seeklogo.svg";
  if (clean.includes("gwm") || clean.includes("great wall")) return "/images/brands/gwm-logo.svg";
  if (clean.includes("mg") || clean.includes("morris")) return "/images/brands/mg-logo.svg";
  if (clean.includes("citroen")) return "/images/brands/citroen-logo.svg";

  const slug = clean.replace(/[^a-z0-9]/g, "");
  return `/images/brands/${slug}-logo.svg`;
}

export interface BrandMetadata {
  name: string;
  slug: string;
  logo: string;
  count: number;
}

export function getOfficialBrands(): BrandMetadata[] {
  const brandCounts = new Map<string, number>();
  ELECTRIFIED_CARS_DATA.forEach((car: any) => {
    const b = (car.brand || "").trim();
    if (b) {
      brandCounts.set(b, (brandCounts.get(b) || 0) + 1);
    }
  });

  const result: BrandMetadata[] = [];
  for (const [realBrand, count] of brandCounts.entries()) {
    result.push({
      name: realBrand.replace(/\s*\(.*?\)/g, "").trim(),
      slug: realBrand.toLowerCase().replace(/[^a-z0-9]/g, "-"),
      logo: getBrandLogo(realBrand),
      count,
    });
  }

  // Sort strictly alphabetically from A to Z
  result.sort((a, b) => a.name.localeCompare(b.name, "id", { sensitivity: "base" }));

  return result;
}

/**
 * Mengoptimalkan path gambar mobil dari PNG ke WebP (hemat hingga 85% file size)
 */
export function getOptimizedCarImg(imgUrl: string | undefined): string {
  if (!imgUrl) return "/images/cars/default-car.webp";
  if (imgUrl.toLowerCase().endsWith(".png")) {
    return imgUrl.slice(0, -4) + ".webp";
  }
  return imgUrl;
}

