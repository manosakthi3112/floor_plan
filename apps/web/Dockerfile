FROM node:20-alpine AS base
WORKDIR /app

# Enable corepack first
RUN corepack enable

# 1. Install dependencies - copy workspace files first
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web/package.json ./apps/web/
COPY packages/shared-types ./packages/shared-types

RUN pnpm install

# 2. Copy source code & build
COPY . .
RUN pnpm --filter @plancraft3d/web build

EXPOSE 3000
CMD ["pnpm", "--filter", "@plancraft3d/web", "start"]
