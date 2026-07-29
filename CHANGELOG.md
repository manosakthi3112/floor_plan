# Changelog — PlanCraft3D

> All notable changes to this project will be documented here.

---

## [Unreleased]

### Improvements (Post-MVP Deep Dive)

#### Added
- Undo/redo via Zustand temporal middleware (zundo) — tracks 50 history states
- Undo/redo buttons in editor toolbar with disabled states
- Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Shift+Z / Ctrl+Y (redo)
- Rate limiting middleware (100 req/min per IP) for all API endpoints
- File upload validation: MIME type check (PNG, JPG, PDF) + 20MB size limit
- Parsing low-confidence fallback UI (shown when confidence < 50%)
- Parsing output now includes `confidence` score (0–1) based on detection averages
- Error state UI in upload flow (retry button, error message display)
- Celery task config stub (`core/celery_app.py` + `core/tasks.py`) for future async job processing
- Auth guard on all protected frontend routes (redirects to /login if no JWT)
- Parsing service Dockerfile (Tesseract OCR + OpenCV + Python 3.12)

#### Fixed
- Editor page now shows parse confidence fallback before entering editor
- Upload validation rejects unsupported file types with clear error message
- Rate limited requests return 429 with Retry-After header
- Undo/redo is now a real feature instead of a known gap

### Sprint 6 — Export & Integration (Days 26–30)

#### Added
- GLTF/GLB export (client-side via `GLTFExporter`)
- PNG render export with resolution options (1080p, 2K, 4K)
- Auto-save every 30s with visual "Saved" indicator
- `beforeunload` save on tab close via `navigator.sendBeacon`
- Skeleton loading states for dashboard, progress bar for parsing
- Error toasts for network failures, parsing fallback UI
- End-to-end Playwright tests for full user flow
- Backend test suite (pytest + httpx) for all endpoints
- Staging deployment to Vercel + Fly.io + Neon + Upstash

#### Fixed
- 3D mesh rebuild debounce (300ms) prevents jank during rapid edits
- CSG edge cases for openings near wall endpoints
- Color picker reactivity on initial load

---

### Sprint 5 — Materials, Openings & Presets (Days 21–25)

#### Added
- Door/window 3D cutouts via manual wall-splitting
- Door/window frame + glass geometry
- Material panel (room selector + wall/floor/ceiling sections)
- Color picker with presets, hex input, recent colors
- Reactive color sync: store → mesh material without rebuild
- Room list panel with area display and inline label editing
- 10 built-in design presets (Modern, Scandinavian, Warm, etc.)
- Design preset gallery with room type filtering
- "Save as My Design" — user preset CRUD
- Backend preset endpoints + database model

---

### Sprint 4 — 3D Viewer & Mesh Pipeline (Days 16–20)

#### Added
- Three.js + react-three-fiber 3D scene
- `meshBuilder.ts`: pure function FloorPlanGraph → geometry descriptors
- Wall meshes (BoxGeometry per wall, positioned + rotated)
- Floor meshes (ShapeGeometry from room polygons, 5mm thickness)
- Ceiling meshes (flat, offset to wall height)
- OrbitControls with 45° default camera angle
- Lighting presets (daylight, evening, overcast)
- `useFloorPlanSync` hook: reactive 2D ↔ 3D sync with 300ms debounce
- Resizable horizontal split pane (2D left, 3D right)
- Mesh memoization via graph hash to skip unchanged rebuilds

---

### Sprint 3 — Complete Parsing & 2D Editor Polish (Days 11–15)

#### Added
- Opening detection: classify door vs window, position, swing direction
- Room extraction via flood-fill, polygon output with room type heuristics
- OCR labeling with Tesseract, fallback naming
- Redis + Celery job queue for async parsing
- WebSocket endpoint `/ws/jobs/{jobId}` for real-time progress
- Door/window placement tool on 2D canvas
- Element selection (click to select, highlight + bounding box)
- Drag wall endpoints to move, delete with confirmation
- Editor toolbar (tool selector, undo/redo, zoom controls)
- Zustand temporal middleware for undo/redo
- End-to-end upload → parse → 2D display → manual correction flow
- "Accept & Continue" workflow

---

### Sprint 2 — Upload, Parse & 2D Canvas (Days 6–10)

#### Added
- S3-compatible storage abstraction with local filesystem fallback
- File upload endpoint (multipart, image/PDF)
- Parsing microservice scaffold with FastAPI
- YOLOv8 model integration with CPU inference
- Image preprocessing pipeline (grayscale, deskew, threshold, PDF)
- Basic wall detection (line segments, merge collinear)
- Dashboard with project grid, cards, create dialog
- Drag & drop upload UI with progress bar
- Job polling → auto-navigate to editor
- 2D Konva.js canvas with zoom/pan
- Grid snap overlay (configurable grid size)
- Wall drawing tool (click two points → segment)
- Room auto-detect from closed wall loops

---

### Sprint 1 — Foundation & Auth (Days 1–5)

#### Added
- Monorepo scaffold (pnpm workspaces, Turbo, Docker Compose)
- FastAPI foundation (health check, CORS, error handlers, logging)
- PostgreSQL async setup with SQLAlchemy 2.0 + Alembic
- JWT auth (access 15min + refresh 7d, bcrypt hashing)
- User registration, login, refresh, me endpoints
- Next.js 14 with App Router + TypeScript strict
- TailwindCSS + custom UI component primitives
- App shell layout (TopBar, Sidebar, MainArea)
- Login / register pages with form validation
- Auth guard layout (redirect to login if no JWT)
- Axios API client with JWT interceptor
- Zustand stores: floorPlanStore, projectStore, uiStore
- TypeScript types: FloorPlanGraph, Wall, Room, Opening, DesignPreset
- Project CRUD backend endpoints
- Initial Alembic migration (users + projects tables)

---

## [1.0.0] — Planned MVP Release

- Upload → parse → 3D model generation
- Manual color/material editor per room
- Design preset library (10 built-in + user presets)
- GLTF + PNG export
- Auto-save, project management
- Auth with JWT

---

## [2.0.0] — Planned (Phase 2)

- From-scratch 2D drawing editor
- Texture library (50+ materials with PBR)
- AI design assistant (LLM + curated dataset)
- Ceiling style variants (tray, coffered, cathedral, exposed beam)
- Streaming AI suggestions

---

## [3.0.0] — Planned (Phase 3)

- Furniture placement library
- Walkthrough / first-person camera
- Project sharing with real-time collaboration
- Mobile-responsive editor
- AR preview (WebXR)
- Version history with visual diff
- Advanced rendering (SSAO, bloom, lightmaps)
