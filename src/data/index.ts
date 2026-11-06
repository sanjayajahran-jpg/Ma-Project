/**
 * Lapisan query mock — meniru endpoint API di docs/planing.md Bagian 6.
 * Produksi: ganti isi fungsi ini dengan fetch ke https://api.narasi.biz.id.
 */
import type { Article, Category } from "@/types";
import { articles } from "./articles";
import { categories } from "./categories";
import { authors } from "./authors";
import { tags } from "./tags";

export { categories, authors, tags };

/** Semua artikel terbit, terbaru dulu. */
export const allArticles: Article[] = [...articles].sort(
  (x, y) => +new Date(y.publishedAt) - +new Date(x.publishedAt)
);

export const getArticleBySlug = (slug: string) =>
  allArticles.find((a) => a.slug === slug);

export const getByCategory = (catSlug: string) =>
  allArticles.filter((a) => a.category.slug === catSlug);

export const getByTag = (tagSlug: string) =>
  allArticles.filter((a) => a.tags.some((t) => t.slug === tagSlug));

export const getByAuthor = (authorSlug: string) =>
  allArticles.filter((a) => a.author.slug === authorSlug);

export const getFeatured = (n = 5) =>
  allArticles.filter((a) => a.isFeatured).slice(0, n);

export const getPinned = () => allArticles.find((a) => a.isPinned);

export const getLatest = (n = 8, exclude: string[] = []) =>
  allArticles.filter((a) => !exclude.includes(a.id)).slice(0, n);

export const getTrending = (n = 5) =>
  [...allArticles].sort((x, y) => y.viewCount - x.viewCount).slice(0, n);

export const getSponsored = (n = 3) =>
  allArticles.filter((a) => a.type === "kerjasama").slice(0, n);

/** Artikel terkait: kategori sama dulu, lalu berbagi tag. */
export function getRelated(article: Article, n = 3): Article[] {
  const scored = allArticles
    .filter((a) => a.id !== article.id)
    .map((a) => {
      let score = 0;
      if (a.category.slug === article.category.slug) score += 3;
      score += a.tags.filter((t) =>
        article.tags.some((t2) => t2.slug === t.slug)
      ).length;
      return { a, score };
    })
    .filter((x) => x.score > 0)
    .sort((x, y) => y.score - x.score || +new Date(y.a.publishedAt) - +new Date(x.a.publishedAt));
  return scored.slice(0, n).map((x) => x.a);
}

/** Navigasi prev/next berdasar urutan kronologis. */
export function getAdjacent(article: Article) {
  const idx = allArticles.findIndex((a) => a.id === article.id);
  return {
    newer: idx > 0 ? allArticles[idx - 1] : undefined,
    older: idx < allArticles.length - 1 ? allArticles[idx + 1] : undefined,
  };
}

/** Beberapa artikel teratas per kategori (untuk blok beranda). */
export function getCategorySection(cat: Category, n = 4) {
  return getByCategory(cat.slug).slice(0, n);
}

/** Pencarian sederhana (judul + dek + tag + kategori + penulis). */
export function searchArticles(q: string): Article[] {
  const term = q.trim().toLowerCase();
  if (!term) return [];
  return allArticles.filter((a) => {
    const hay = [
      a.title,
      a.dek,
      a.category.name,
      a.author.name,
      ...a.tags.map((t) => t.name),
    ]
      .join(" ")
      .toLowerCase();
    return hay.includes(term);
  });
}

/** Hitung jumlah artikel per kategori. */
export const categoryCount = (catSlug: string) => getByCategory(catSlug).length;
