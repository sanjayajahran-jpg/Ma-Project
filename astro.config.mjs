// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import node from '@astrojs/node';

// Local web preview consumes the Groovetimes production API by default.
export default defineConfig({
  site: process.env.PUBLIC_SITE_URL ?? 'https://groovetimes.com',
  server: {
    host: true,
    port: 4321,
  },
  output: 'server',
  adapter: node({
    mode: 'standalone',
  }),
  prefetch: {
    prefetchAll: false,
    defaultStrategy: 'hover',
  },
  integrations: [sitemap()],
  image: {
    // Izinkan optimasi gambar remote (mock pakai picsum/pravatar/unsplash).
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https' }
    ],
  },
  vite: {
    server: {
      allowedHosts: true,
    },
    plugins: [tailwindcss()],
    build: {
      cssCodeSplit: true,
      minify: 'esbuild',
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules/@fontsource')) {
              return 'vendor-fonts';
            }
          },
        },
      },
    },
  },
});

