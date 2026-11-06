/** Tipe domain — mengikuti model DB di docs/planing.md Bagian 5. */

export type ArticleType = "premium" | "kerjasama" | "standard";

export interface Author {
  id: string;
  slug: string;
  name: string;
  role: string;
  avatar: string;
  bio: string;
  socials?: { twitter?: string; instagram?: string };
}

export interface Category {
  id: string;
  slug: string;
  name: string;
  description: string;
  /** nama token warna di global.css: --color-cat-<slug> */
  color: string;
}

export interface Tag {
  slug: string;
  name: string;
}

export interface Sponsor {
  name: string;
  logo?: string;
  website?: string;
}

export interface LinkedArticle {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  cover: string;
  categorySlug: string;
  categoryName: string;
  publishedAt: string;
}

export interface Article {
  id: string;
  slug: string;
  title: string;
  dek: string;
  bodyHtml: string;
  cover: string;
  coverThumb?: string;
  coverMobile?: string;
  coverAlt: string;
  coverCaption?: string;
  author: Author;
  category: Category;
  type: ArticleType;
  tags: Tag[];
  /** ISO 8601 */
  publishedAt: string;
  updatedAt?: string;
  readingTime: number;
  viewCount: number;
  isFeatured?: boolean;
  isPinned?: boolean;
  sponsor?: Sponsor;
  seoTitle?: string;
  seoDescription?: string;
  bacaJuga?: LinkedArticle[];
  beritaTerkait?: LinkedArticle[];
  generated_by_agent_id?: string | null;
  generated_by_agent_name?: string | null;
}

/** URL kanonik artikel: /[kategori]/[slug] */
export function articleUrl(a: Article): string {
  return `/${a.category.slug}/${a.slug}`;
}
