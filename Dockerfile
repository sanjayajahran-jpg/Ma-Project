FROM node:22-bookworm-slim AS builder
WORKDIR /app
RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json tsconfig.base.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/shared-types/package.json packages/shared-types/package.json
COPY packages/ui/package.json packages/ui/package.json
RUN pnpm install --frozen-lockfile

COPY apps/web apps/web
COPY packages/shared-types packages/shared-types
COPY packages/ui packages/ui
RUN pnpm --filter @insight/web build

FROM node:22-bookworm-slim AS runtime
WORKDIR /app
ENV HOST=0.0.0.0
ENV PORT=4321
ENV NODE_ENV=production
COPY --from=builder /app/apps/web/dist ./dist
EXPOSE 4321
CMD ["node", "./dist/server/entry.mjs"]
