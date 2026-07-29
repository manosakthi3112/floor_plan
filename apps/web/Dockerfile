FROM node:20-alpine AS base
WORKDIR /app

# 1. Install dependencies
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web/package.json ./apps/web/
COPY packages/shared-types ./packages/shared-types

RUN corepack enable && pnpm install

# 2. Copy source code & build
COPY . .
RUN corepack enable && pnpm --filter @plancraft3d/web build

EXPOSE 3000
CMD ["pnpm", "--filter", "@plancraft3d/web", "start"]
