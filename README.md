# PlanCraft3D — Deep Dive README

> Turns a 2D floor plan image into an editable 3D model, lets users design layouts from scratch, customize walls/floors/ceilings, and apply design presets.

**Status**: MVP Complete (6 sprints, ~140 files) | **Architecture**: [architecture doc](floorplan-3d-webapp-architecture.md) | **Plan**: [implementation plan](deep-dive-implementation-plan.md)

---

## Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [What Was Built vs Planned](#what-was-built-vs-planned)
- [Core Data Flow](#core-data-flow)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Frontend Component Map](#frontend-component-map)
- [State Management](#state-management)
- [Testing Strategy](#testing-strategy)
- [Deployment](#deployment)
- [Known Gaps & Limitations](#known-gaps--limitations)
- [Roadmap Post-MVP](#roadmap-post-mvp)
- [File Inventory](#file-inventory)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT (Browser)                             │
│  Next.js 14 + React 18 + Three.js (react-three-fiber)           │
│  - 2D Floor Plan Editor (Konva.js)                              │
│  - 3D Viewer/Editor (Three.js + react-three-fiber + drei)       │
│  - Material/Color panel, Room list, Design preset gallery       │
│  - Zustand state management (floorPlan + ui stores)             │
└───────────────┬───────────────────────────────────┬─────────────┘
                │ REST/GraphQL + WebSocket           │
┌───────────────▼───────────────────────────────────▼─────────────┐
│                  APPLICATION API (FastAPI)                        │
│  - Auth (JWT, register/login/refresh)                            │
│  - Projects CRUD (Postgres, JSONB fields)                        │
│  - Parsing orchestration (upload -> queue -> parse)              │
│  - Design presets (built-in + user CRUD)                         │
│  - Export (GLTF/PNG)                                             │
└──────┬───────────────┬───────────────┬───────────────┬──────────┘
       │               │               │               │
┌──────▼─────┐  ┌──────▼───────┐ ┌────▼───────┐ ┌──────▼────────┐
│ Floor Plan │  │  Redis Queue  │ │  Storage    │ │  PostgreSQL   │
│ Parsing    │  │  (job queue + │ │  (S3/local) │ │  (users,      │
│ Service    │  │   pub/sub)    │ │  - uploads  │ │   projects,   │
│ (YOLOv8,   │  └──────────────┘ │  - exports  │ │   presets)    │
│ Tesseract) │                   └─────────────┘ └───────────────┘
└────────────┘
```

### Layers

| Layer | Tech | Directory | Files |
|-------|------|-----------|-------|
| Frontend | Next.js 14 + React 18 | `apps/web/` | 42 source files |
| API | FastAPI + SQLAlchemy 2.0 | `apps/api/` | 30 files |
| Parsing | FastAPI + Ultralytics YOLOv8 | `services/parsing/` | 13 files |
| Shared | TypeScript interfaces | `packages/shared-types/` | 4 files |
| Ops | Docker Compose, CI/CD | root | 5 files |

---

## Project Structure

```
E:\Jung-Floor\
├── apps/
│   ├── web/                              # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── (marketing)/           # Landing page
│   │   │   │   ├── (app)/                 # Authenticated routes
│   │   │   │   │   ├── dashboard/         # Project list
│   │   │   │   │   └── project/
│   │   │   │   │       ├── [projectId]/   # Editor (2D + 3D)
│   │   │   │   │       └── new/           # New project
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── components/
│   │   │   │   ├── editor-2d/             # 2D Konva.js canvas (5 files)
│   │   │   │   ├── editor-3d/             # 3D Three.js scene (10 files)
│   │   │   │   ├── editor-panels/         # Sidebar panels (8 files)
│   │   │   │   ├── project/               # Dashboard (5 files)
│   │   │   │   └── layout/                # Shell (3 files)
│   │   │   ├── stores/                    # Zustand (2 files)
│   │   │   ├── services/                  # API client (2 files)
│   │   │   ├── hooks/                     # Custom hooks (2 files)
│   │   │   ├── lib/                       # Utilities (2 files)
│   │   │   └── types/                     # TypeScript types (3 files)
│   │   ├── next.config.js
│   │   ├── tailwind.config.js
│   │   └── package.json
│   │
│   └── api/                               # FastAPI backend
│       ├── app/
│       │   ├── routers/                   # 6 routers (auth, projects, parsing, presets, export)
│       │   ├── models/                    # 5 models (User, Project, Job, DesignPreset, Base)
│       │   ├── schemas/                   # 3 schemas (user, project, design_preset)
│       │   ├── services/                  # 3 services (auth, project, preset_library)
│       │   └── core/                      # 5 modules (security, storage, job_queue, auth_deps, exceptions)
│       ├── alembic/                       # DB migration
│       ├── tests/                         # Backend tests
│       └── requirements.txt
│
├── services/
│   └── parsing/                           # ML parsing microservice
│       ├── app/
│       │   ├── processors/                # 4 processors (wall, opening, room, OCR)
│       │   ├── models/                    # YOLOv8 wrapper
│       │   ├── schemas/                   # FloorPlanGraph schema
│       │   └── utils/                     # Image preprocessing
│       └── requirements.txt
│
├── packages/
│   └── shared-types/                      # Shared TypeScript interfaces
│
├── sprints/                               # Sprint docs
├── .github/workflows/                     # CI/CD
├── docker-compose.yml
├── CHANGELOG.md
└── NOTES.md
```

---

## What Was Built vs Planned

### MVP — All 6 Sprints

| Sprint | Focus | Status | Files Created | Coverage |
|--------|-------|--------|---------------|----------|
| 1 | Foundation & Auth | ✅ **Complete** | ~30 | Monorepo, FastAPI, JWT auth, Next.js, stores, Project CRUD, migration |
| 2 | Upload, Parse & 2D Canvas | ✅ **Complete** | ~25 | S3/local storage, parsing scaffold, YOLOv8, 2D Konva.js, dashboard |
| 3 | Complete Parsing & 2D Polish | ✅ **Complete** | ~20 | Opening/room/OCR processors, job queue + WebSocket, editor tools |
| 4 | 3D Viewer & Mesh Pipeline | ✅ **Complete** | ~15 | Three.js scene, mesh builder, sync hook, lighting, split pane |
| 5 | Materials, Openings & Presets | ✅ **Complete** | ~20 | Wall-splitting openings, material panel, 8 presets, user presets |
| 6 | Export, Auto-Save & Integration | ✅ **Complete** | ~15 | GLTF/PNG export, auto-save, tests, CI/CD, Docker Compose |

### MVP Coverage: ~80%

**What's implemented:**
- Monorepo with pnpm workspaces, Turbo, Docker Compose
- FastAPI backend with JWT auth, Project CRUD, Preset CRUD
- PostgreSQL async with SQLAlchemy 2.0 + Alembic migrations
- Next.js 14 frontend with App Router, TailwindCSS
- Zustand stores (floorPlan + ui) with reactive state
- 2D Konva.js canvas with grid, wall drawing, room polygons, door/window placement, selection + delete
- Parsing microservice with YOLOv8 detection, wall/opening/room extraction, Tesseract OCR
- 3D Three.js scene with walls, floors, ceilings, door/window frames + glass
- Client-side mesh builder (FloorPlanGraph → geometry descriptors)
- Reactive 2D ↔ 3D sync via memoized hook
- Resizable split pane (2D left, 3D right)
- Material panel with room selector + color picker (24 swatches + hex input)
- 8 built-in design presets + user preset CRUD with backend
- GLTF binary export + PNG render (1080p/2K/4K)
- Auto-save (30s debounce) + beforeunload save
- Redis job queue with WebSocket progress
- S3/local storage abstraction
- Backend test suite (13 tests)
- GitHub Actions CI (API tests, web lint/typecheck, Docker build)
- Auth guard on protected frontend routes

**What's missing from MVP scope:**
| Item | Planned In | Reason Not Done |
|------|-----------|-----------------|
| Undo/redo | Sprint 3 | Zustand temporal middleware not wired |
| "Accept & Continue" parse flow | Sprint 3 | No explicit accept step after parsing |
| Low-confidence parsing fallback UI | Sprint 3 | No fallback shown when confidence < 0.6 |
| projectStore in Zustand | Sprint 1 | Project data fetched directly via service |
| WebGL error boundary | Sprint 4 | Scene3D has no error handling |
| Celery (raw Redis used instead) | Sprint 3 | Simpler approach chosen for MVP |
| E2E Playwright tests | Sprint 6 | Not created |
| Rate limiting | Security | Not implemented |
| File upload MIME validation | Security | Not enforced server-side |
| Mesh generator service | Architecture | Server-side mesh gen deferred (client-side sufficient for MVP) |

**Phase 2/3 features (not started):**
- AI design assistant (LLM integration + rules engine)
- Texture/PBR material library (50+ materials)
- Advanced ceiling geometry (tray, coffered, cathedral, exposed beam)
- From-scratch 2D drawing improvements (templates, annotations)
- Furniture library + transform gizmo
- Walkthrough/first-person camera
- Project sharing / real-time collaboration
- Mobile responsive editor
- AR preview (WebXR)
- Version history with visual diff

---

## Core Data Flow

```
1. UPLOAD
  User uploads floor plan image → stored in S3/local → job queued in Redis
  
2. PARSE
  Parsing service picks up job → YOLOv8 detection → wall/opening/room extraction
  → OCR labeling → FloorPlanGraph JSON → stored in project
  
3. EDIT 2D
  Frontend fetches graph → 2D canvas renders walls/rooms/doors/windows
  → User can draw new walls, place doors/windows, select + delete elements
  
4. VIEW 3D
  meshBuilder.ts converts graph → geometry descriptors → Three.js scene
  → Walls split around openings → door/window frames + glass rendered
  → 2D edits sync to 3D via useFloorPlanSync hook (memoized, 300ms debounce)
  
5. STYLE
  User selects room → picks wall/floor/ceiling colors → store updates
  → Mesh colors change WITHOUT geometry rebuild (material props only)
  
6. PRESETS
  User clicks built-in preset → one-click room styling
  Or "Save as My Design" → current style saved to backend
  
7. EXPORT
  GLTF binary export of current scene (geometry + materials baked)
  PNG render at 1080p/2K/4K resolution
```

### Single Source of Truth

All state flows from `FloorPlanGraph` in `floorPlanStore`:
- **2D canvas** reads graph → renders walls/rooms/openings
- **3D scene** reads graph → builds meshes via `meshBuilder.ts`
- **Material panel** reads `roomStyles` → controls colors
- **Room list** reads `rooms` → displays + selection

---

## Tech Stack

### Frontend
| Library | Version | Purpose |
|---------|---------|---------|
| Next.js | 14.2 | React framework with App Router |
| React | 18.3 | UI library |
| Three.js | 0.170 | 3D rendering |
| @react-three/fiber | 8.17 | React renderer for Three.js |
| @react-three/drei | 9.114 | Three.js helpers (OrbitControls) |
| Konva.js | 9.3 | 2D canvas drawing |
| react-konva | 18.2 | React bindings for Konva |
| Zustand | 5.0 | State management |
| Axios | 1.7 | HTTP client |
| TailwindCSS | 3.4 | Utility-first CSS |
| react-colorful | 5.6 | Color picker |
| react-dropzone | 14.3 | File upload drag & drop |

### Backend
| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.115 | Web framework |
| SQLAlchemy | 2.0 | ORM with async support |
| asyncpg | 0.30 | Async PostgreSQL driver |
| Alembic | 1.14 | DB migrations |
| python-jose | 3.3 | JWT encoding/decoding |
| passlib + bcrypt | 1.7/4.2 | Password hashing |
| redis | 5.2 | Job queue + pub/sub |
| boto3 | 1.35 | S3 storage |
| uvicorn | 0.32 | ASGI server |
| httpx | 0.28 | Async HTTP client |
| pytest | 8.3 | Testing |

### Parsing Service
| Library | Version | Purpose |
|---------|---------|---------|
| ultralytics | 8.3 | YOLOv8 object detection |
| opencv-python | 4.10 | Image processing |
| pytesseract | 0.3 | OCR text extraction |
| pdf2image | 1.17 | PDF → image conversion |
| Pillow | 11.0 | Image handling |

---

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- Docker & Docker Compose (for PostgreSQL and Redis — the easy way)
- pnpm (`corepack enable && corepack prepare pnpm@latest --activate`)

### Recommended: Docker for DB + Local dev for apps

This is the fastest workflow — Docker runs only PostgreSQL and Redis, while the app servers run locally for live reload.

```bash
# 1. Start DB services only (Docker)
docker compose up -d postgres redis

# 2. Install dependencies
pnpm install

# 3. Install Python deps + run migrations
cd apps/api
pip install -r requirements.txt
alembic upgrade head
cd ../..

# 4. Install parsing service deps
cd services/parsing
pip install -r requirements.txt
cd ../..

# 5. Start all dev servers (in separate terminals or use tmux)
pnpm dev                                   # terminal 1: web + API
uvicorn services.parsing.app.main:app --reload --port 8001  # terminal 2: parsing
```

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Parsing Service**: http://localhost:8001

### All-in-One: Docker full stack

```bash
docker compose up --build
```

Starts all 5 services: postgres, redis, API, parsing, web. Slower for development (no hot reload), good for testing.

### Without Docker at all

Install PostgreSQL 16 and Redis 7 locally (via package manager or installer), then follow steps 2–5 above.

### Environment Variables

Copy `.env.example` to `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://app:devpassword@localhost:5432/plancraft3d` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `JWT_SECRET` | 64-char random string for JWT | `change-me-to-a-random-64-char-string` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `STORAGE_BACKEND` | `local` or `s3` | `local` |
| `STORAGE_PATH` | Local file storage path | `./data/uploads` |
| `S3_BUCKET` | S3 bucket name | `plancraft3d-uploads` |
| `S3_REGION` | S3 region | `us-east-1` |
| `NEXT_PUBLIC_API_URL` | API URL for frontend | `http://localhost:8000` |

### Running Tests

```bash
# Backend tests (requires postgres running)
cd apps/api && pytest tests/ -v

# Frontend lint + typecheck
cd apps/web && pnpm lint && pnpm typecheck
```

---

## API Reference

### Auth (`/api/v1/auth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Register new user → `{access_token, refresh_token}` |
| POST | `/auth/login` | No | Login → `{access_token, refresh_token}` |
| POST | `/auth/refresh` | No | Refresh tokens → `{access_token, refresh_token}` |
| GET | `/auth/me` | Yes | Current user info |

### Projects (`/api/v1/projects`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/projects` | Yes | List user's projects (paginated) |
| POST | `/projects` | Yes | Create project |
| GET | `/projects/{id}` | Yes | Get project (with graph + styles) |
| PUT | `/projects/{id}` | Yes | Update project (graph, styles, name) |
| DELETE | `/projects/{id}` | Yes | Delete project |
| POST | `/projects/{id}/export` | Yes | Queue export job |
| POST | `/projects/{id}/render` | Yes | Queue thumbnail render |

### Parsing (`/api/v1/parsing`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/parsing/upload` | Yes | Upload floor plan image → `{job_id, status}` |
| GET | `/parsing/jobs/{job_id}` | Yes | Get job status |
| GET | `/parsing/jobs/{job_id}/result` | Yes | Get parsed graph result |
| WS | `/parsing/ws/jobs/{job_id}` | No | WebSocket job progress stream |

### Presets (`/api/v1/presets`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/presets` | Yes | List presets (filter by room_type, style, is_built_in) |
| POST | `/presets` | Yes | Save custom preset |
| DELETE | `/presets/{id}` | Yes | Delete custom preset |

### General

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | No | Health check → `{"status": "ok"}` |

---

## Frontend Component Map

```
<AppShell>
  <TopBar />                        ← Project name, Export menu, User info
  <Sidebar>
    <Tabs>                          ← Rooms | Materials | Designs
      <RoomListPanel>               ← Lists rooms, click to select
        <RoomListItem />            ← Color swatch + name + area
      <MaterialPanel>               ← Per-room color controls
        <ColorPicker />             ← 24 swatches + hex input
        <CeilingStylePicker />      ← Flat/Tray/Coffered/etc.
      <DesignPresetGallery>         ← Built-in + user presets
        <DesignPresetCard />        ← Color swatches + Apply button
        <MyDesignsTab />            ← Save/list/delete user presets
    </Tabs>
  </Sidebar>
  <MainArea>
    <EditorToolbar />               ← Select | Draw Wall | Door | Window
    <SplitPane>                     ← Resizable horizontal split
      <FloorPlanCanvas>             ← Konva.js stage
        <GridLines />               ← 50px grid
        <WallLine />                ← Per wall segment
        <RoomPolygon />             ← Per room with label
        <DoorSymbol /> / <WindowSymbol />  ← Opening indicators
      <Viewport3D>                  ← Three.js scene
        <Scene3D>
          <OrbitControls />         ← Camera with damping
          <LightingPresets />       ← Daylight/Evening/Overcast
          <WallMesh />              ← Per wall (BoxGeometry)
          <FloorMesh />             ← Per room (ShapeGeometry)
          <CeilingMesh />           ← Per room (flat, 85% opacity)
          <OpeningFrame />          ← Door/window frames
          <OpeningGlass />          ← Translucent glass panes
    </SplitPane>
  </MainArea>
</AppShell>
```

---

## State Management

### Stores (Zustand)

**`floorPlanStore`** — Single source of truth:
- `graph: FloorPlanGraph` — walls, rooms, openings
- `roomStyles: Record<roomId, RoomStyle>` — per-room material overrides
- `isDirty: boolean` — unsaved changes flag
- Actions: `addWall`, `updateWall`, `deleteWall`, `addRoom`, `addOpening`, `setRoomStyle`, `applyPreset`, `setGraph`

**`uiStore`** — UI state:
- `activeTool: ToolType` — 'select' | 'drawWall' | 'addDoor' | 'addWindow'
- `selectedWallId`, `selectedRoomId`, `selectedOpeningId` — current selection
- `activeRoomId` — room being styled in material panel
- `sidebarTab` — 'rooms' | 'materials' | 'designs'

### Sync Flow

```
User draws wall in 2D
  → floorPlanStore.addWall() → isDirty = true
    → FloorPlanCanvas re-renders (reads graph.walls)
    → useFloorPlanSync hook re-memoizes (graph changed)
      → Viewport3D re-renders with new mesh descriptors
        → New WallMesh appears in 3D scene

User changes wall color in material panel
  → floorPlanStore.setRoomStyle() → roomStyles updated
    → useFloorPlanSync hook re-memoizes (roomStyles changed)
      → WallMesh color prop changes → material.update() — no geometry rebuild
```

---

## Testing Strategy

### Unit Tests (pytest — 13 tests)
| Test File | Tests |
|-----------|-------|
| `apps/api/tests/test_api.py` | Health, register, duplicate, login, invalid login, refresh, auth guard, project CRUD (create/list/update/delete), preset CRUD |

### CI Pipeline (GitHub Actions)
3 jobs run on push/PR:
1. **API tests**: spins up PostgreSQL container → runs pytest
2. **Web lint + typecheck**: runs `pnpm lint` + `pnpm typecheck`
3. **Docker build check**: verifies API + web Dockerfiles build

---

## Deployment

### Architecture
```
Cloudflare CDN (static assets)
       ↓
Vercel (Next.js app)
       ↓ HTTPS
Fly.io / ECS (FastAPI + Uvicorn)
       ↓
PostgreSQL (Neon/RDS) + Redis (Upstash) + S3 (Cloudflare R2)
```

### Docker Compose (full stack)
```bash
docker compose up --build
```
Services: postgres, redis, api, parsing, web

### Environment-Specific Config
Set env vars per environment (see `.env.example` for all options).

---

## Known Gaps & Limitations

### MVPs Bugs / Missing Features
1. **No undo/redo** — once you delete a wall, it's gone. Planned via Zustand temporal middleware.
2. **No parse confidence UI** — if parsing fails or has low confidence, no fallback is shown.
3. **No "Accept & Continue" flow** — parsed graphs are loaded directly without user review step.
4. **No rate limiting** — API has no per-user or per-IP rate limits.
5. **No file validation** — upload endpoint doesn't check MIME type or enforce size limit server-side.
6. **Collinear wall merging stub** — `_merge_collinear` in `wall_detector.py` is a no-op.
7. **Swing direction stub** — `_detect_swing` always returns `'inward'`.
8. **Opening cutouts simplified** — uses manual wall-splitting; no CSG boolean operations.

### Missing Services
- `services/mesh-generator/` — server-side mesh generation not implemented (client-side only)
- Celery not used — job queue uses raw Redis instead

### Phase 2/3 Features Not Started
- AI design assistant
- Texture/PBR material library
- Advanced ceiling geometry
- Furniture library
- Walkthrough mode
- Collaboration / sharing
- Mobile responsiveness
- AR preview
- Version history

---

## Roadmap Post-MVP

### Phase 2 (Next)
- [ ] AI design assistant (Claude/OpenAI API + curated design dataset)
- [ ] Texture library (50+ PBR materials: wood, tile, carpet, paint)
- [ ] Advanced ceiling styles (tray, coffered, cathedral, exposed beam)
- [ ] From-scratch 2D drawing improvements (templates, dimension annotations)
- [ ] Undo/redo
- [ ] Parse confidence UI + fallback
- [ ] Rate limiting + upload validation

### Phase 3 (Future)
- [ ] Furniture placement library (GLTF blocks)
- [ ] Walkthrough / first-person camera
- [ ] Project sharing with real-time collaboration
- [ ] Mobile-responsive editor
- [ ] AR preview (WebXR)
- [ ] Version history with visual diff
- [ ] Server-side mesh generator (high-res export)
- [ ] High-quality rendering (SSAO, bloom, lightmaps)

---

## File Inventory

| Path | Lines | Purpose |
|------|-------|---------|
| `apps/api/app/main.py` | 30 | FastAPI entry point |
| `apps/api/app/config.py` | 16 | Environment config |
| `apps/api/app/dependencies.py` | 16 | DB session DI |
| `apps/api/app/core/security.py` | 34 | JWT + bcrypt |
| `apps/api/app/core/auth_deps.py` | 22 | Auth dependency |
| `apps/api/app/core/exceptions.py` | 22 | Error classes |
| `apps/api/app/core/storage.py` | 58 | S3/local storage |
| `apps/api/app/core/job_queue.py` | 50 | Redis job queue |
| `apps/api/app/models/user.py` | 12 | User ORM |
| `apps/api/app/models/project.py` | 16 | Project ORM |
| `apps/api/app/models/job.py` | 16 | Job ORM |
| `apps/api/app/models/design_preset.py` | 16 | Preset ORM |
| `apps/api/app/models/base.py` | 20 | Base model + mixins |
| `apps/api/app/schemas/user.py` | 26 | Auth schemas |
| `apps/api/app/schemas/project.py` | 33 | Project schemas |
| `apps/api/app/schemas/design_preset.py` | 22 | Preset schemas |
| `apps/api/app/services/auth_service.py` | 44 | Auth logic |
| `apps/api/app/services/project_service.py` | 52 | Project CRUD |
| `apps/api/app/services/preset_library.py` | 44 | Preset CRUD |
| `apps/api/app/routers/auth.py` | 17 | Auth endpoints |
| `apps/api/app/routers/projects.py` | 60 | Project endpoints |
| `apps/api/app/routers/parsing.py` | 52 | Upload + job endpoints |
| `apps/api/app/routers/presets.py` | 36 | Preset endpoints |
| `apps/api/app/routers/export.py` | 23 | Export endpoints |
| `apps/api/alembic/versions/001_initial_migration.py` | 79 | DB migration |
| `apps/api/tests/test_api.py` | 180 | Backend tests |
| `apps/web/src/app/(marketing)/page.tsx` | 30 | Landing page |
| `apps/web/src/app/login/page.tsx` | 43 | Login form |
| `apps/web/src/app/register/page.tsx` | 49 | Register form |
| `apps/web/src/app/(app)/dashboard/page.tsx` | 56 | Dashboard |
| `apps/web/src/app/(app)/project/[projectId]/page.tsx` | 87 | Editor page |
| `apps/web/src/components/editor-2d/FloorPlanCanvas.tsx` | 185 | 2D canvas |
| `apps/web/src/components/editor-2d/EditorToolbar.tsx` | 39 | Toolbar |
| `apps/web/src/components/editor-3d/Scene3D.tsx` | 18 | 3D scene |
| `apps/web/src/components/editor-3d/Viewport3D.tsx` | 57 | 3D viewport |
| `apps/web/src/components/editor-3d/WallMesh.tsx` | 29 | Wall mesh |
| `apps/web/src/components/editor-3d/FloorMesh.tsx` | 26 | Floor mesh |
| `apps/web/src/components/editor-3d/CeilingMesh.tsx` | 28 | Ceiling mesh |
| `apps/web/src/components/editor-3d/OpeningFrame.tsx` | 16 | Door/window frame |
| `apps/web/src/components/editor-3d/OpeningGlass.tsx` | 20 | Glass pane |
| `apps/web/src/components/editor-3d/OrbitControls.tsx` | 13 | Camera controls |
| `apps/web/src/components/editor-3d/LightingPresets.tsx` | 30 | 3 lighting presets |
| `apps/web/src/components/editor-3d/SplitPane.tsx` | 45 | Resizable split |
| `apps/web/src/components/editor-panels/MaterialPanel.tsx` | 93 | Material controls |
| `apps/web/src/components/editor-panels/ColorPicker.tsx` | 51 | Color picker |
| `apps/web/src/components/editor-panels/RoomListPanel.tsx` | 52 | Room list |
| `apps/web/src/components/editor-panels/DesignPresetGallery.tsx` | 107 | Preset gallery |
| `apps/web/src/components/editor-panels/DesignPresetCard.tsx` | 28 | Preset card |
| `apps/web/src/components/editor-panels/MyDesignsTab.tsx` | 100 | User presets |
| `apps/web/src/components/project/ProjectCard.tsx` | 29 | Project card |
| `apps/web/src/components/project/ProjectList.tsx` | 38 | Project grid |
| `apps/web/src/components/project/CreateProjectDialog.tsx` | 88 | Create dialog |
| `apps/web/src/components/project/UploadFloorPlan.tsx` | 52 | Upload zone |
| `apps/web/src/components/project/ExportMenu.tsx` | 57 | Export dropdown |
| `apps/web/src/components/layout/AppShell.tsx` | 16 | Shell layout |
| `apps/web/src/components/layout/TopBar.tsx` | 14 | Top bar |
| `apps/web/src/components/layout/Sidebar.tsx` | 10 | Sidebar |
| `apps/web/src/stores/floorPlanStore.ts` | 118 | Main store |
| `apps/web/src/stores/uiStore.ts` | 35 | UI store |
| `apps/web/src/services/apiClient.ts` | 40 | Axios client |
| `apps/web/src/services/projectService.ts` | 31 | Project API |
| `apps/web/src/hooks/useFloorPlanSync.ts` | 36 | 2D↔3D sync |
| `apps/web/src/hooks/useAutoSave.ts` | 39 | Auto-save |
| `apps/web/src/lib/meshBuilder.ts` | 160 | Geometry builder |
| `apps/web/src/lib/exportUtils.ts` | 38 | GLTF/PNG export |
| `apps/web/src/types/floorPlan.ts` | 79 | TypeScript types |
| `services/parsing/app/main.py` | 20 | Parsing entry |
| `services/parsing/app/orchestrator.py` | 53 | Parse pipeline |
| `services/parsing/app/routers.py` | 27 | Parse endpoint |
| `services/parsing/app/processors/wall_detector.py` | 50 | Wall detection |
| `services/parsing/app/processors/opening_detector.py` | 62 | Opening detection |
| `services/parsing/app/processors/room_extractor.py` | 100 | Room extraction |
| `services/parsing/app/processors/ocr_labeler.py` | 44 | OCR labeling |
| `services/parsing/app/utils/image_preprocessing.py` | 38 | Image processing |
| `packages/shared-types/src/floor-plan-graph.ts` | 42 | Shared types |
| `packages/shared-types/src/design-presets.ts` | 27 | Shared presets |
