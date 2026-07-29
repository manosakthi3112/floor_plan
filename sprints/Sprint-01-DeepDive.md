# Sprint 1 — Foundation & Auth (Days 1–5)

## Goal
Monorepo scaffold, FastAPI backend foundation, Next.js frontend foundation, auth system.

---

## Task List

### 1.1 Monorepo scaffold
- [ ] Init root `package.json` with workspaces (`apps/web`, `packages/*`)
- [ ] Create `docker-compose.yml` with postgres + redis + api + web services
- [ ] Create `.env.example` with all env vars
- [ ] Create `turbo.json` or `nx.json` for task orchestration
- [ ] **Files:** `package.json`, `docker-compose.yml`, `.env.example`, `turbo.json`

### 1.2 FastAPI foundation
- [ ] Scaffold `apps/api/` with `main.py`, `config.py` (pydantic-settings), health check
- [ ] Add CORS middleware, error handlers, logging
- [ ] Initialize Alembic with SQLAlchemy async support
- [ ] Create `dependencies.py` with DI for db sessions
- [ ] **Files:** `apps/api/app/main.py`, `config.py`, `dependencies.py`, `core/exceptions.py`, `alembic/env.py`

### 1.3 Auth system (backend)
- [ ] Create `models/user.py` — SQLAlchemy User model
- [ ] Create `schemas/user.py` — Pydantic request/response schemas
- [ ] Create `core/security.py` — JWT encode/decode, password hashing (bcrypt)
- [ ] Create `services/auth_service.py` — register, login, refresh logic
- [ ] Create `routers/auth.py` — POST `/auth/register`, `/auth/login`, `/auth/refresh`, GET `/auth/me`
- [ ] **Files:** `models/user.py`, `schemas/user.py`, `core/security.py`, `services/auth_service.py`, `routers/auth.py`

### 1.4 Next.js scaffold
- [ ] Init `apps/web/` with Next.js App Router + TypeScript strict
- [ ] Add TailwindCSS, shadcn/ui or custom UI primitives
- [ ] Create layout shell: `AppShell.tsx`, `TopBar.tsx`, `Sidebar.tsx`
- [ ] Create auth pages (login, register) under `app/(marketing)`
- [ ] Create auth guard layout under `app/(app)/layout.tsx`
- [ ] **Files:** `apps/web/src/app/(marketing)/page.tsx`, `app/(app)/layout.tsx`, `components/layout/*`

### 1.5 API client
- [ ] Create `services/apiClient.ts` — Axios instance with JWT interceptor
- [ ] Create `services/projectService.ts` — CRUD functions
- [ ] Create `hooks/useAuth.ts` — login/register/logout/session state
- [ ] **Files:** `services/apiClient.ts`, `services/projectService.ts`, `hooks/useAuth.ts`

### 1.6 Zustand store shape
- [ ] Define TypeScript types in `types/floorPlan.ts`, `types/project.ts`, `types/design.ts`
- [ ] Create `stores/floorPlanStore.ts` with initial state + all mutation stubs
- [ ] Create `stores/projectStore.ts` — project list, current project
- [ ] Create `stores/uiStore.ts` — panel visibility, active tool
- [ ] **Files:** `types/*.ts`, `stores/*.ts`

### 1.7 User + Project CRUD (backend)
- [ ] Create `models/project.py` — Project model with JSONB fields
- [ ] Create `schemas/project.py` — Pydantic schemas
- [ ] Create `services/project_service.py` — CRUD logic
- [ ] Create `routers/projects.py` — GET/POST/PUT/DELETE project endpoints
- [ ] **Files:** `models/project.py`, `schemas/project.py`, `services/project_service.py`, `routers/projects.py`

### 1.8 DB migrations
- [ ] Generate initial Alembic migration for users + projects tables
- [ ] Test migration up/down
- [ ] **Files:** `alembic/versions/001_initial.py`

---

## Notes / Design Decisions

- **JWT with refresh tokens**: Access token = 15min, refresh = 7d. Refresh rotates (old one invalidated).
- **DB driver**: `asyncpg` for async PostgreSQL. SQLAlchemy 2.0 async sessions.
- **Next.js**: Use `next/dynamic` for all 3D components from day 1 to avoid SSR issues later.
- **Zustand**: Use `temporal` middleware for undo/redo from the start — easier than retrofitting.
- **API versioning**: `/api/v1/` prefix on all routes.

## Acceptance Criteria
- [ ] `docker compose up` starts postgres, redis, api (port 8000), web (port 3000)
- [ ] `GET /api/v1/health` returns `{"status": "ok"}`
- [ ] Register a user → returns JWT
- [ ] Login with credentials → returns JWT
- [ ] Create/list/get/update/delete projects via API (authenticated)
- [ ] Login page renders at `/login`, register at `/register`
- [ ] Authenticated routes redirect to login if no JWT
