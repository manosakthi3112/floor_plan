# PlanCraft3D — Deep Dive Implementation Plan

> Based on `floorplan-3d-webapp-architecture.md` — turns the high-level architecture into actionable build steps.

---

## Table of Contents
1. [Monorepo Structure](#1-monorepo-structure)
2. [Phase 1: MVP — Detailed Breakdown](#2-phase-1-mvp)
3. [Phase 2: Editor + AI](#3-phase-2-editor--ai)
4. [Phase 3: Polish + Advanced](#4-phase-3-polish--advanced)
5. [Data Models & Schemas](#5-data-models--schemas)
6. [Full API Contract](#6-full-api-contract)
7. [Frontend Component Tree](#7-frontend-component-tree)
8. [State Management Design](#8-state-management-design)
9. [Service Contracts](#9-service-contracts)
10. [Testing Strategy](#10-testing-strategy)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Dependency Graph & Critical Path](#12-dependency-graph--critical-path)
13. [Risk Mitigation Checklist](#13-risk-mitigation-checklist)

---

## 1. Monorepo Structure

```
planCraft3D/
├── apps/
│   ├── web/                              # Next.js frontend
│   │   ├── public/                       # Static assets, textures
│   │   ├── src/
│   │   │   ├── app/                      # Next.js App Router pages
│   │   │   │   ├── (marketing)/          # Landing, pricing, docs
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   └── layout.tsx
│   │   │   │   ├── (app)/                # Authenticated app routes
│   │   │   │   │   ├── dashboard/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   ├── project/
│   │   │   │   │   │   └── [projectId]/
│   │   │   │   │   │       ├── page.tsx  # Editor (2D + 3D)
│   │   │   │   │   │   └── new/page.tsx
│   │   │   │   │   └── layout.tsx        # Auth-guarded layout
│   │   │   │   ├── api/                  # Next.js API routes (BFF)
│   │   │   │   └── layout.tsx
│   │   │   ├── components/
│   │   │   │   ├── editor-2d/            # 2D floor plan editor
│   │   │   │   │   ├── FloorPlanCanvas.tsx
│   │   │   │   │   ├── WallTool.tsx
│   │   │   │   │   ├── RoomTool.tsx
│   │   │   │   │   ├── DoorWindowTool.tsx
│   │   │   │   │   ├── GridSnapOverlay.tsx
│   │   │   │   │   ├── DimensionOverlay.tsx
│   │   │   │   │   └── EditorToolbar.tsx
│   │   │   │   ├── editor-3d/            # 3D viewer/editor
│   │   │   │   │   ├── Scene3D.tsx
│   │   │   │   │   ├── WallMesh.tsx
│   │   │   │   │   ├── FloorMesh.tsx
│   │   │   │   │   ├── CeilingMesh.tsx
│   │   │   │   │   ├── DoorOpening.tsx
│   │   │   │   │   ├── WindowOpening.tsx
│   │   │   │   │   ├── CameraController.tsx
│   │   │   │   │   ├── LightingPresets.tsx
│   │   │   │   │   ├── OrbitControls.tsx
│   │   │   │   │   └── TransformGizmo.tsx
│   │   │   │   ├── editor-panels/        # Side panels
│   │   │   │   │   ├── MaterialPanel.tsx
│   │   │   │   │   ├── ColorPicker.tsx
│   │   │   │   │   ├── TextureSwatch.tsx
│   │   │   │   │   ├── CeilingStylePicker.tsx
│   │   │   │   │   ├── RoomListPanel.tsx
│   │   │   │   │   ├── DesignPresetGallery.tsx
│   │   │   │   │   ├── DesignPresetCard.tsx
│   │   │   │   │   ├── MyDesignsTab.tsx
│   │   │   │   │   └── AiAssistantPanel.tsx
│   │   │   │   ├── project/              # Project management
│   │   │   │   │   ├── ProjectCard.tsx
│   │   │   │   │   ├── ProjectList.tsx
│   │   │   │   │   ├── CreateProjectDialog.tsx
│   │   │   │   │   ├── UploadFloorPlan.tsx
│   │   │   │   │   └── ExportMenu.tsx
│   │   │   │   ├── layout/               # Shared layout
│   │   │   │   │   ├── AppShell.tsx
│   │   │   │   │   ├── Sidebar.tsx
│   │   │   │   │   ├── TopBar.tsx
│   │   │   │   │   └── LoadingSpinner.tsx
│   │   │   │   └── ui/                   # Generic UI primitives
│   │   │   │       ├── Button.tsx
│   │   │   │       ├── Dialog.tsx
│   │   │   │       ├── Dropdown.tsx
│   │   │   │       └── Tabs.tsx
│   │   │   ├── stores/                   # Zustand stores
│   │   │   │   ├── floorPlanStore.ts     # Single source of truth
│   │   │   │   ├── projectStore.ts
│   │   │   │   ├── uiStore.ts            # Panel open/close, active tool
│   │   │   │   └── designPresetStore.ts
│   │   │   ├── services/                 # API calls to backend
│   │   │   │   ├── apiClient.ts          # Axios/fetch wrapper
│   │   │   │   ├── projectService.ts
│   │   │   │   ├── parsingService.ts
│   │   │   │   ├── modelExportService.ts
│   │   │   │   └── aiService.ts
│   │   │   ├── hooks/                    # Custom React hooks
│   │   │   │   ├── useFloorPlanSync.ts   # Bidirectional 2D↔3D sync
│   │   │   │   ├── useMeshGeneration.ts  # JSON → Three.js geometry
│   │   │   │   ├── useAutoSave.ts
│   │   │   │   └── useDesignSuggestions.ts
│   │   │   ├── lib/                      # Utilities
│   │   │   │   ├── floorPlanSchema.ts    # Zod validation
│   │   │   │   ├── meshBuilder.ts        # Client-side mesh generation
│   │   │   │   ├── textureLoader.ts
│   │   │   │   ├── exportUtils.ts
│   │   │   │   └── constants.ts
│   │   │   └── types/                    # TypeScript types
│   │   │       ├── floorPlan.ts
│   │   │       ├── project.ts
│   │   │       ├── design.ts
│   │   │       └── api.ts
│   │   ├── next.config.js
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── api/                              # FastAPI backend
│       ├── app/
│       │   ├── main.py                   # FastAPI entry
│       │   ├── config.py                 # Settings (pydantic-settings)
│       │   ├── dependencies.py           # DI (auth, db session)
│       │   ├── routers/
│       │   │   ├── auth.py
│       │   │   ├── projects.py
│       │   │   ├── parsing.py
│       │   │   ├── model_gen.py
│       │   │   ├── export.py
│       │   │   ├── ai_design.py
│       │   │   └── presets.py
│       │   ├── models/                   # SQLAlchemy ORM models
│       │   │   ├── user.py
│       │   │   ├── project.py
│       │   │   ├── floor_plan_graph.py
│       │   │   ├── room_style.py
│       │   │   ├── design_preset.py
│       │   │   └── user_preset.py
│       │   ├── schemas/                  # Pydantic request/response
│       │   │   ├── user.py
│       │   │   ├── project.py
│       │   │   ├── floor_plan.py
│       │   │   ├── design_preset.py
│       │   │   └── ai_suggestion.py
│       │   ├── services/                 # Business logic
│       │   │   ├── auth_service.py
│       │   │   ├── project_service.py
│       │   │   ├── parsing_orchestrator.py
│       │   │   ├── preset_library.py
│       │   │   └── ai_assistant.py
│       │   └── core/                     # Cross-cutting
│       │       ├── security.py           # JWT, hashing
│       │       ├── storage.py            # S3 client wrapper
│       │       ├── job_queue.py          # Redis/Celery integration
│       │       └── exceptions.py
│       ├── alembic/                      # DB migrations
│       ├── tests/
│       ├── requirements.txt
│       ├── Dockerfile
│       └── docker-compose.yml
│
├── services/
│   ├── parsing/                           # Python microservice
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── models/
│   │   │   │   └── detection_model.py    # YOLOv8 / Mask R-CNN wrapper
│   │   │   ├── processors/
│   │   │   │   ├── wall_detector.py
│   │   │   │   ├── opening_detector.py
│   │   │   │   ├── room_extractor.py
│   │   │   │   └── ocr_labeler.py
│   │   │   ├── schemas/
│   │   │   │   └── floor_plan_graph.py   # Output JSON schema
│   │   │   └── utils/
│   │   │       ├── image_preprocessing.py
│   │   │       └── postprocessing.py
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── mesh-generator/                    # Python mesh service (optional)
│       ├── app/
│       │   ├── main.py
│       │   ├── generators/
│       │   │   ├── wall_mesher.py
│       │   │   ├── floor_mesher.py
│       │   │   ├── ceiling_mesher.py
│       │   │   ├── opening_cutter.py
│       │   │   └── material_baker.py
│       │   ├── schemas/
│       │   │   └── scene.py
│       │   └── utils/
│       │       └── gltf_exporter.py
│       ├── tests/
│       └── requirements.txt
│
├── packages/                              # Shared libraries
│   └── shared-types/                      # JSON schemas, TypeScript types
│       ├── src/
│       │   ├── floor-plan-graph.ts
│       │   ├── design-presets.ts
│       │   └── index.ts
│       └── package.json
│
└── docker-compose.yml                     # Full stack orchestration
```

---

## 2. Phase 1: MVP — Detailed Breakdown

**Goal**: Upload → parse → basic 3D box model → manual color editor → export.

### 2.1 Backend Foundation (Week 1–2)

| Task | Files | Details |
|------|-------|---------|
| **2.1.1 Project scaffolding** | `apps/api/` structure, `docker-compose.yml`, `Dockerfile` | FastAPI app with health check, CORS, error handlers. Alembic initialized. Config via env vars. |
| **2.1.2 Auth system** | `routers/auth.py`, `models/user.py`, `services/auth_service.py`, `core/security.py` | JWT-based (access + refresh tokens). Register, login, me endpoints. Password hashing via bcrypt. |
| **2.1.3 User & Project CRUD** | `routers/projects.py`, `models/project.py`, `services/project_service.py` | Create/list/get/delete projects. Project stores: `id`, `user_id`, `name`, `floor_plan_graph` (JSONB), `thumbnail_url`, `created_at`, `updated_at`. |
| **2.1.4 File upload endpoint** | `routers/parsing.py` | Accept image/PDF upload → store in S3 → queue parsing job → return job ID. Use `python-multipart`. |
| **2.1.5 Job queue** | `core/job_queue.py` | Redis + Celery integration. Job states: queued → processing → done/error. WebSocket endpoint for job status push. |
| **2.1.6 DB migrations** | `alembic/` | Initial migration: users, projects, job_queue tables. |

### 2.2 Parsing Service (Week 2–3)

| Task | Files | Details |
|------|-------|---------|
| **2.2.1 Model integration** | `models/detection_model.py` | Wrap YOLOv8 (pre-trained on floor plans) or `rikhoffbauer2/floorplan-parser`. Download model at container start. CPU inference for MVP, GPU optional. |
| **2.2.2 Image preprocessing** | `utils/image_preprocessing.py` | Convert to grayscale, deskew, threshold, detect page boundaries. Handle scanned PDFs via `pdf2image`. |
| **2.2.3 Wall detection** | `processors/wall_detector.py` | Take detection output → extract line segments → merge collinear → output wall segments with thickness. |
| **2.2.4 Opening detection** | `processors/opening_detector.py` | Classify door vs window. Determine position along wall (normalized 0–1), width, swing direction. |
| **2.2.5 Room extraction** | `processors/room_extractor.py` | Flood-fill from wall-bounded regions. Output room polygons. Detect room type from shape heuristics. |
| **2.2.6 OCR labeling** | `processors/ocr_labeler.py` | Tesseract OCR on detected text regions. Match labels to rooms via proximity. Fallback to "Room 1", "Room 2". |
| **2.2.7 Graph output** | `schemas/floor_plan_graph.py` | Validate output JSON against the shared schema. Post to webhook or store in S3. |

### 2.3 Frontend Foundation (Week 1–2, parallel with backend)

| Task | Files | Details |
|------|-------|---------|
| **2.3.1 Next.js setup** | `apps/web/` | App Router, TailwindCSS, TypeScript strict. Layout shell with sidebar + topbar. |
| **2.3.2 API client** | `services/apiClient.ts` | Axios instance with interceptors for JWT refresh. Base URL from env. |
| **2.3.3 Auth pages** | `app/(marketing)/` + `app/(app)/layout.tsx` | Login/register pages. Auth guard that redirects to login. Clerk or custom JWT integration. |
| **2.3.4 Dashboard page** | `project/ProjectList.tsx`, `ProjectCard.tsx`, `CreateProjectDialog.tsx` | List user's projects with thumbnail, name, date. Create new → upload dialog or blank. |
| **2.3.5 Upload flow** | `UploadFloorPlan.tsx` | Drag & drop upload → progress bar → polling job status → auto-navigate to editor on completion. |
| **2.3.6 Zustand store setup** | `stores/floorPlanStore.ts` | Initial store shape with walls, rooms, openings. Actions: addWall, moveWall, deleteWall, addRoom, setRoomLabel, etc. |

### 2.4 2D Floor Plan Editor (Week 3–4)

| Task | Files | Details |
|------|-------|---------|
| **2.4.1 Konva.js canvas** | `FloorPlanCanvas.tsx` | Responsive canvas with zoom/pan. Renders walls as lines, rooms as filled polygons, doors/windows as symbols. |
| **2.4.2 Wall editing** | `WallTool.tsx` | Click two points → create wall segment. Select + drag endpoints. Delete wall (with confirmation if it has door/window). Snapping to grid + adjacent walls. |
| **2.4.3 Room display** | (in `FloorPlanCanvas.tsx`) | Auto-detect rooms from closed wall loops. Show room label in center. Highlight on hover. |
| **2.4.4 Door/Window placement** | `DoorWindowTool.tsx` | Click on a wall → place opening. Toggle door ↔ window. Adjust width and position via drag. |
| **2.4.5 Grid & snapping** | `GridSnapOverlay.tsx` | Configurable grid size. Snap points: wall endpoints, midpoints, intersections. Visual snap indicator. |
| **2.4.6 Toolbar** | `EditorToolbar.tsx` | Tool selector (select, draw wall, add door, add window). Undo/redo. Zoom controls. |
| **2.4.7 Undo/redo** | `stores/floorPlanStore.ts` | Command pattern or Zustand temporal middleware. Capture state snapshots on each mutation. |

### 2.5 3D Viewer (Week 4–5)

| Task | Files | Details |
|------|-------|---------|
| **2.5.1 3D scene setup** | `Scene3D.tsx` | `@react-three/fiber` Canvas with default lighting, background, camera position. |
| **2.5.2 Mesh generation** | `lib/meshBuilder.ts` | Pure function: `floorPlanGraph → Three.js geometry`. Create wall boxes, floor planes, ceiling planes. Return as a scene graph object. |
| **2.5.3 Wall meshes** | `WallMesh.tsx` | `BoxGeometry` per wall segment with proper position, rotation, dimensions (length, thickness, height). |
| **2.5.4 Floor meshes** | `FloorMesh.tsx` | `ShapeGeometry` from room polygon. Extrude slightly or keep flat. |
| **2.5.5 Ceiling meshes** | `CeilingMesh.tsx` | Same geometry as floor, offset to wall height. Default flat. |
| **2.5.6 Door/Window openings** | `DoorOpening.tsx`, `WindowOpening.tsx` | Subtract from wall mesh via CSG (three-bvh-csg or manual approach). Render door/window frame and glass. |
| **2.5.7 Camera controls** | `OrbitControls.tsx` | `@react-three/drei` OrbitControls. Default top-down angled view. |
| **2.5.8 Lighting** | `LightingPresets.tsx` | Ambient light + directional light. Presets: daylight, evening, warm. |
| **2.5.9 2D ↔ 3D sync** | `hooks/useFloorPlanSync.ts` | Subscribe to floorPlanStore. On each change, rebuild affected meshes. Debounce to avoid jank. |

### 2.6 Material Editor (Week 5)

| Task | Files | Details |
|------|-------|---------|
| **2.6.1 Material panel** | `MaterialPanel.tsx` | Room selector dropdown + per-room style controls. Wall color, floor color, ceiling color + style. |
| **2.6.2 Color picker** | `ColorPicker.tsx` | Custom color picker or `react-colorful`. Preset color swatches. Recent colors. |
| **2.6.3 Style application** | `hooks/useFloorPlanSync.ts` | Store material overrides in store as `roomStyles: Record<roomId, RoomStyle>`. Meshes reactively update when style changes. |
| **2.6.4 Design preset library** | `DesignPresetGallery.tsx` | Show built-in presets (5-10 hardcoded). Each is a `DesignPreset` JSON: `{name, roomType, style, wallColor, floorColor, ceilingStyle}`. One-click apply. |
| **2.6.5 "Save as My Design"** | `MyDesignsTab.tsx` | Button to save current room styling as user preset. List user's saved presets. Apply/delete. |

### 2.7 Export (Week 5–6)

| Task | Files | Details |
|------|-------|---------|
| **2.7.1 GLTF export** | `lib/exportUtils.ts`, `services/modelExportService.ts` | Client-side: use three.js GLTFExporter. Server-side: trimesh or HeadlessGL for high-res. |
| **2.7.2 PNG render** | `ExportMenu.tsx` | Render current Three.js view to PNG with `canvas.toDataURL()`. Download or save to project. |
| **2.7.3 Auto-save** | `hooks/useAutoSave.ts` | Debounced save of floor plan graph + room styles to backend every 30s. On unmount, force save. |

### 2.8 MVP Integration (Week 6)

| Task | Details |
|------|---------|
| End-to-end flow test | Upload → parse → view 2D → generate 3D → change colors → export PNG |
| Error handling | Parsing failure fallback (show raw image, manual wall draw UI). Network error retry. |
| Loading states | Skeleton screens for dashboard. Progress bar for parse. Spinner for 3D generation. |

---

## 3. Phase 2: Editor + AI

### 3.1 From-Scratch 2D Drawing (Week 7–8)

| Task | Details |
|------|---------|
| **Draw wall tool (improved)** | Click-drag to place walls with real-time length display. Right-angle constraint with Shift. |
| **Room auto-detect** | When walls form a closed loop, auto-create room. User can override. |
| **Dimension annotations** | Show wall lengths and room areas on the 2D canvas. |
| **Snapping improvements** | Midpoint, endpoint, perpendicular, parallel snap modes. |
| **Wall editing** | Split wall at point. Merge collinear walls. Move wall parallel. |
| **Stencil / template** | Start from common room shapes (rectangle, L-shape, T-shape). |

### 3.2 Texture Library (Week 8–9)

| Task | Details |
|------|---------|
| **Texture asset pipeline** | Source 50+ textures (wood, tile, carpet, paint finishes, brick, stone). Optimize to WebP + compressed. |
| **Texture swatch UI** | Visual grid of texture thumbnails. Filter by category. Search. |
| **UV mapping** | Correct UV coordinates on wall/floor/ceiling meshes for texture repeat. Per-room tile scale control. |
| **PBR materials** | Roughness/metalness maps for realistic rendering. Use `@react-three/drei` `MeshStandardMaterial`. |
| **Ceiling styles** | Flat, tray/coffered (recessed center panel), cathedral (sloped), exposed beam, coffered grid, tin tiles. Each is a small geometry generator. |

### 3.3 AI Design Assistant (Week 9–10)

| Task | Details |
|------|---------|
| **Curated design dataset** | Build 50–100 presets covering: room types (bedroom, living, kitchen, bath, dining, office), styles (modern, Scandinavian, Tamil traditional, industrial, bohemian, minimalist, coastal). Each as JSON. |
| **Rules engine** | (Optional lightweight alternative to LLM calls) Rule-based: if room=bedroom & style=modern → suggest these 3 palettes. No API cost. |
| **LLM integration** | `services/ai_assistant.py` — prompt template: "Room type: {type}, dimensions: {w}x{l}, style keywords: {keywords}. Respond with JSON palette and materials from this curated list: {curated_list}". Filter LLM output against curated list for safety. |
| **AI panel UI** | `AiAssistantPanel.tsx` — text input for style prompt, suggestion cards (palette swatches + material names), "Apply" button per suggestion. Streaming response display. |
| **Room-type-aware suggestions** | Pass room label (bedroom vs kitchen) to AI so suggestions are context-relevant. |
| **User preset saving** | Extend "Save as My Design" — store user's custom styles in DB. Show in gallery alongside built-in and AI-suggested. |

---

## 4. Phase 3: Polish + Advanced

| Feature | Details |
|---------|---------|
| **Furniture library** | 3D furniture blocks (bed, sofa, table, chair, cabinet) as GLTF. Drag from library into 3D scene. Position via transform gizmo. Snap to walls/floors. |
| **Walkthrough mode** | First-person camera with WASD + mouse look. Collision detection against walls. Room labels on hover. |
| **Project sharing** | Shareable link with view-only or edit permissions. Real-time collaboration via WebSocket (CRDT or operational transform). |
| **Mobile responsive** | Adaptive 2D editor for tablets. Touch gestures for draw/drag. Simplified 3D viewer (tap to change materials). |
| **AR preview (WebXR)** | AR button → place 3D model on real-world floor via camera. Lighting estimation from environment. |
| **Rendering quality** | Bake lighting to lightmaps. Ambient occlusion. Post-processing (bloom, SSAO). High-res export (4k+). |
| **Version history** | Project snapshots on each save. Visual diff timeline. Restore any version. |

---

## 5. Data Models & Schemas

### 5.1 Floor Plan Graph (Single Source of Truth)

```typescript
// packages/shared-types/src/floor-plan-graph.ts

interface Point {
  x: number;  // mm from origin
  y: number;
}

interface Wall {
  id: string;           // UUID
  start: Point;
  end: Point;
  thickness: number;    // mm (standard: 100–200)
  height: number;       // mm (standard: 2700)
  type: 'exterior' | 'interior';
}

interface Room {
  id: string;
  label: string;         // "Bedroom", "Kitchen", or auto-generated
  polygon: Point[];      // Closed polygon, CCW winding, mm coords
  level: number;         // 0 = ground floor
  area: number;          // Computed, m²
}

interface Opening {
  id: string;
  type: 'door' | 'window' | 'sliding_door' | 'french_window';
  wallId: string;
  position: number;      // 0–1 normalized along wall
  width: number;         // mm
  height: number;        // mm (default: door=2100, window=1200)
  sillHeight: number;    // mm from floor (default: 0 for door, 900 for window)
  swingDirection?: 'left' | 'right' | 'inward' | 'outward';
}

interface FloorPlanGraph {
  version: 1;
  unit: 'mm';
  walls: Wall[];
  rooms: Room[];
  openings: Opening[];
  metadata: {
    projectId: string;
    source: 'upload' | 'manual' | 'template';
    scale?: number;       // px-per-mm if from upload
    createdAt: string;    // ISO
  };
}
```

### 5.2 Room Style (Per-Room Material Override)

```typescript
interface CeilingStyle {
  type: 'flat' | 'tray' | 'coffered' | 'cathedral' | 'exposed_beam' | 'tin_tile';
  color: string;             // hex
  height?: number;           // mm (tray recess depth, beam height)
  beamColor?: string;        // for exposed beam
  beamSpacing?: number;      // mm
}

interface RoomStyle {
  roomId: string;
  wallColor: string;         // hex
  wallTexture?: string;      // texture URL (nullable = solid color)
  wallTextureScale?: number; // 1–10
  floorColor: string;
  floorTexture?: string;
  floorTextureScale?: number;
  ceiling: CeilingStyle;
  baseboardColor?: string;
  baseboardHeight?: number;
}

// Stored alongside project: { roomStyles: Record<string, RoomStyle> }
```

### 5.3 Design Preset

```typescript
interface DesignPreset {
  id: string;
  name: string;                // "Modern Minimalist Bedroom"
  roomType: string;            // "bedroom" | "living_room" | "kitchen" | ...
  style: string;               // "modern" | "scandinavian" | "tamil_traditional" | ...
  wallColor: string;
  wallTexture?: string;
  floorColor: string;
  floorTexture?: string;
  ceiling: CeilingStyle;
  tags: string[];              // ["warm", "neutral", "earthy"]
  isBuiltIn: boolean;          // false = user-created
  userId?: string;             // owner if !isBuiltIn
  createdAt: string;
  updatedAt: string;
}
```

### 5.4 Database Tables (PostgreSQL)

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL DEFAULT 'Untitled Project',
  floor_plan_graph JSONB,           -- The shared graph
  room_styles JSONB DEFAULT '{}',   -- Record<roomId, RoomStyle>
  thumbnail_url TEXT,
  source_image_url TEXT,
  width_mm FLOAT,                   -- Bounding box
  height_mm FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAZ DEFAULT NOW()
);
CREATE INDEX idx_projects_user_id ON projects(user_id);

-- Design Presets (built-in + user)
CREATE TABLE design_presets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  room_type VARCHAR(50) NOT NULL,
  style VARCHAR(50) NOT NULL,
  preset_data JSONB NOT NULL,       -- Full RoomStyle + metadata
  is_built_in BOOLEAN DEFAULT FALSE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_presets_room_style ON design_presets(room_type, style);
CREATE INDEX idx_presets_user ON design_presets(user_id) WHERE NOT is_built_in;

-- Jobs (for async parsing)
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  type VARCHAR(50) NOT NULL,        -- 'parsing', 'model_export'
  status VARCHAR(20) DEFAULT 'queued', -- queued, processing, done, error
  progress FLOAT DEFAULT 0,
  result_url TEXT,                  -- URL to output (parsed JSON or GLTF)
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 6. Full API Contract

### 6.1 Auth Endpoints

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| POST | `/api/v1/auth/register` | Register | `{email, password, name}` | `{user, accessToken, refreshToken}` |
| POST | `/api/v1/auth/login` | Login | `{email, password}` | `{user, accessToken, refreshToken}` |
| POST | `/api/v1/auth/refresh` | Refresh token | `{refreshToken}` | `{accessToken, refreshToken}` |
| GET | `/api/v1/auth/me` | Current user | — | `{user}` |

### 6.2 Project Endpoints

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| GET | `/api/v1/projects` | List user's projects | `?page=1&limit=20` | `{projects[], total}` |
| POST | `/api/v1/projects` | Create project | `{name?, sourceImage?}` | `{project}` |
| GET | `/api/v1/projects/{id}` | Get project | — | `{project}` |
| PUT | `/api/v1/projects/{id}` | Update project | `{name?, floorPlanGraph?, roomStyles?}` | `{project}` |
| DELETE | `/api/v1/projects/{id}` | Delete project | — | `{success}` |
| POST | `/api/v1/projects/{id}/duplicate` | Duplicate project | — | `{project}` |

### 6.3 Parsing Endpoints

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| POST | `/api/v1/parsing/upload` | Upload floor plan | `multipart: file` | `{jobId, status}` |
| GET | `/api/v1/parsing/jobs/{jobId}` | Get job status | — | `{jobId, status, progress, result?, error?}` |
| GET | `/api/v1/parsing/jobs/{jobId}/result` | Get parsed graph | — | `{floorPlanGraph}` |
| PUT | `/api/v1/parsing/jobs/{jobId}/correct` | Submit corrections | `{floorPlanGraph}` | `{project}` |

### 6.4 Export Endpoints

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| POST | `/api/v1/projects/{id}/export` | Queue export job | `{format: 'gltf' \| 'obj', bakeMaterials: bool}` | `{jobId}` |
| GET | `/api/v1/exports/{jobId}/download` | Download exported file | — | Binary file |
| POST | `/api/v1/projects/{id}/render` | Generate PNG render | `{camera, resolution, lighting}` | `{imageUrl}` |

### 6.5 AI Design Endpoints

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| POST | `/api/v1/ai/suggest` | Get design suggestions | `{roomType, dimensions, styleKeywords, currentStyle?}` | `{suggestions[]}` |
| POST | `/api/v1/ai/suggest-stream` | Streaming suggestions | SSE stream | `{event: chunk \| done}` |

### 6.6 Design Preset Endpoints

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| GET | `/api/v1/presets` | List presets | `?roomType=&style=&isBuiltIn=` | `{presets[]}` |
| POST | `/api/v1/presets` | Save user preset | `{name, roomType, style, presetData}` | `{preset}` |
| DELETE | `/api/v1/presets/{id}` | Delete user preset | — | `{success}` |

### 6.7 WebSocket Endpoints

| Path | Description | Events |
|------|-------------|--------|
| `/ws/jobs/{jobId}` | Job status updates | `{event: "progress", data: {progress, status}}`, `{event: "done", data: {resultUrl}}`, `{event: "error", data: {message}}` |
| `/ws/projects/{projectId}` | Real-time collaboration (Phase 3) | Op/merge events |

---

## 7. Frontend Component Tree

```
<AppShell>
  <TopBar>
    <ProjectNameEditor />
    <UndoRedoButtons />
    <AutoSaveIndicator />
    <ExportMenu />
    <UserMenu />
  </TopBar>
  <Sidebar>
    <Tabs>
      <Tab label="Rooms">
        <RoomListPanel>
          <RoomListItem />  (per room, click to select)
        </RoomListPanel>
      </Tab>
      <Tab label="Materials">
        <MaterialPanel>
          <Section label="Wall">
            <ColorPicker />
            <TextureSwatch />  (Phase 2)
          </Section>
          <Section label="Floor">
            <ColorPicker />
            <TextureSwatch />  (Phase 2)
          </Section>
          <Section label="Ceiling">
            <CeilingStylePicker />
            <ColorPicker />
          </Section>
        </MaterialPanel>
      </Tab>
      <Tab label="Designs">
        <DesignPresetGallery>
          <FilterBar />       (room type + style filters)
          <TabBar>
            <Tab label="Built-in" />
            <Tab label="My Designs" />
            <Tab label="AI Suggestions" />  (Phase 2)
          </TabBar>
          <DesignPresetCard />  (per preset, with "Apply" button)
        </DesignPresetGallery>
      </Tab>
      <Tab label="AI">         (Phase 2)
        <AiAssistantPanel>
          <StylePromptInput />
          <SuggestionList>
            <SuggestionCard />  (palette swatches + Apply)
          </SuggestionList>
        </AiAssistantPanel>
      </Tab>
    </Tabs>
  </Sidebar>

  <MainArea>
    <Toolbar>
      <ToolButton tool="select" />
      <ToolButton tool="drawWall" />
      <ToolButton tool="addDoor" />
      <ToolButton tool="addWindow" />
      <ToolButton tool="addRoom" />  (Phase 2)
    </Toolbar>

    <SplitPane direction="horizontal" defaultRatio={0.5}>
      <Pane>
        <FloorPlanCanvas />
          <GridSnapOverlay />
          <DimensionOverlay />
      </Pane>
      <Pane>
        <Scene3D>
          <CameraController />
          <OrbitControls />
          <LightingPresets />
          <Suspense>
            <WallMesh />      (per wall)
            <FloorMesh />     (per room)
            <CeilingMesh />   (per room)
            <DoorOpening />   (per opening)
            <WindowOpening /> (per opening)
          </Suspense>
          <TransformGizmo />  (Phase 3 for furniture)
        </Scene3D>
      </Pane>
    </SplitPane>

    <StatusBar>
      <ToolHint />          (context-sensitive help)
      <CursorCoordinates />
      <ZoomLevel />
    </StatusBar>
  </MainArea>
</AppShell>
```

---

## 8. State Management Design

### 8.1 Zustand Store: `floorPlanStore`

```typescript
interface FloorPlanStore {
  // Floor plan graph (single source of truth)
  graph: FloorPlanGraph;

  // Per-room styling
  roomStyles: Record<string, RoomStyle>;

  // Editor state
  activeTool: ToolType;
  selectedWallId: string | null;
  selectedRoomId: string | null;
  selectedOpeningId: string | null;
  activeRoomId: string | null;  // Room being styled

  // UI state
  isDirty: boolean;
  lastSavedAt: number | null;

  // Graph mutations
  addWall: (wall: Omit<Wall, 'id'>) => void;
  updateWall: (id: string, updates: Partial<Wall>) => void;
  deleteWall: (id: string) => void;
  addRoom: (room: Omit<Room, 'id'>) => void;
  updateRoom: (id: string, updates: Partial<Room>) => void;
  addOpening: (opening: Omit<Opening, 'id'>) => void;
  updateOpening: (id: string, updates: Partial<Opening>) => void;
  deleteOpening: (id: string) => void;
  setGraph: (graph: FloorPlanGraph) => void;

  // Room style mutations
  setRoomStyle: (roomId: string, style: Partial<RoomStyle>) => void;
  applyPreset: (roomId: string, preset: DesignPreset) => void;

  // Editor state mutations
  setActiveTool: (tool: ToolType) => void;
  setSelection: (type: string, id: string | null) => void;
  setActiveRoom: (id: string | null) => void;

  // Persistence
  markDirty: () => void;
  markSaved: () => void;
  loadFromProject: (project: Project) => void;
}
```

### 8.2 Derivation / Selectors

```typescript
const selectRoomPolygons = (state: FloorPlanStore) =>
  state.graph.rooms.map(r => r.polygon);

const selectWallLengths = (state: FloorPlanStore) =>
  state.graph.walls.map(w => distance(w.start, w.end));

const selectActiveRoomStyle = (state: FloorPlanStore) =>
  state.activeRoomId ? state.roomStyles[state.activeRoomId] : null;

const selectMeshesDirty = (state: FloorPlanStore) =>
  // Memoized check: has graph changed since last mesh build?
  hash(state.graph);
```

### 8.3 Auto-Save Side Effect

`useAutoSave` hook subscribes to `isDirty` every 30s, calls PUT `/projects/{id}` with serialized `graph + roomStyles`. On tab close, `beforeunload` triggers synchronous save.

---

## 9. Service Contracts

### 9.1 Parsing Service → API → Frontend

```
Request (API → Parsing):
  POST /parse
  {
    imageUrl: "s3://bucket/uploads/abc.png",
    callbackUrl: "https://api.planCraft3D.com/v1/parsing/callback"
  }

Response (Parsing → API callback):
  {
    jobId: "...",
    status: "done",
    floorPlanGraph: FloorPlanGraph,
    confidence: 0.87,
    processingTimeMs: 3400
  }

Error case:
  {
    jobId: "...",
    status: "error",
    error: "Could not detect any wall boundaries",
    partialGraph?: FloorPlanGraph  // best-effort
  }
```

### 9.2 Mesh Generator Service (Server-side)

```
Request (API → MeshGen):
  POST /generate
  {
    floorPlanGraph: FloorPlanGraph,
    roomStyles: Record<string, RoomStyle>,
    format: "gltf" | "glb" | "obj",
    options: { bakeMaterials: true, quality: "high" }
  }

Response:
  {
    jobId: "...",
    status: "done",
    modelUrl: "s3://bucket/exports/abc.gltf",
    thumbnailUrl: "s3://bucket/thumbnails/abc.png",
    fileSizeBytes: 245600
  }
```

### 9.3 AI Design Service

```
Request (API → AI):
  POST /suggest
  {
    roomType: "bedroom",
    dimensions: { width: 4000, length: 5000 },
    styleKeywords: ["modern", "minimalist", "warm"],
    currentStyle?: RoomStyle   // optional, for "remix"
  }

Response:
  {
    suggestions: [
      {
        id: "...",
        palette: {
          wall: { color: "#F5F0EB", texture: null },
          floor: { color: "#8B7355", texture: "oak_light" },
          ceiling: { type: "flat", color: "#FFFFFF" }
        },
        rationale: "Warm neutral walls with light oak flooring...",
        confidence: 0.92
      },
      // ... 2–3 more
    ]
  }
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

| Layer | Framework | Coverage Targets |
|-------|-----------|-----------------|
| Frontend stores | Vitest | All Zustand actions and selectors |
| Mesh builder | Vitest | All geometry functions (wall extrusion, opening cutout) |
| Python parsing processors | pytest | Wall detection, room extraction, OCR matching |
| Python services | pytest | Preset matching, AI prompt formatting |
| API routes | pytest + httpx | All endpoints, auth guards, validation |

### 10.2 Integration Tests

| Test | Tools | What It Validates |
|------|-------|-------------------|
| Upload → Parse → Project update | Docker Compose + pytest | Full parsing pipeline, S3 upload, DB write |
| Graph → 3D mesh generation | Vitest + three.js headless | Mesh count, vertex positions match expected |
| WebSocket job progress | pytest + websockets | Real-time status flow |
| AI suggestion ground truth | pytest | LLM output is valid JSON and references only curated presets |

### 10.3 E2E Tests (MVP+)

| Test | Tool | Flow |
|------|------|------|
| Upload floor plan → see 3D | Playwright | File input → wait for job → verify 3D canvas has meshes |
| Draw wall → 3D updates | Playwright | Click canvas → verify wall appears in both 2D and 3D |
| Change wall color → 3D reflects | Playwright | Open material panel → pick color → verify mesh color |
| Apply preset → style applied | Playwright | Click preset → verify style panel values + 3D mesh colors |
| Save project → reload → data persists | Playwright | Save → refresh → verify state restored |

### 10.4 Load Tests

| Scenario | Tool | Metric |
|----------|------|--------|
| 10 concurrent parse requests | Locust | Average processing time < 30s |
| 50 concurrent project saves | Locust | P99 latency < 500ms |
| Large floor plan (100+ rooms) render | Custom benchmark | Frame rate > 30fps, mesh build < 2s |

---

## 11. Deployment Architecture

```
                        ┌──────────────────┐
                        │   Cloudflare CDN  │
                        │   (static assets) │
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │   Vercel         │
                        │   (Next.js app)  │
                        └────────┬─────────┘
                                 │ HTTPS
                        ┌────────▼─────────┐
                        │   API Server      │
                        │   (Fly.io / ECS)  │
                        │   FastAPI + Uvicorn│
                        └───┬──────┬───────┘
                            │      │
               ┌────────────┘      └────────────┐
               │                                 │
     ┌─────────▼─────────┐           ┌───────────▼──────────┐
     │  PostgreSQL        │           │  Redis               │
     │  (Render / RDS)    │           │  (Upstash / ElastiCache)
     └───────────────────┘           └───────────┬──────────┘
                                                  │
                                        ┌─────────▼──────────┐
                                        │  Celery Worker      │
                                        │  (GPU instance)     │
                                        │  - Parsing tasks    │
                                        │  - Mesh generation  │
                                        └────────────────────┘
                                                  │
                                        ┌─────────▼──────────┐
                                        │  Object Storage     │
                                        │  (S3 / Cloudflare R2)│
                                        └────────────────────┘
```

### 11.1 Docker Compose (Local Dev)

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: plancraft3d
      POSTGRES_USER: app
      POSTGRES_PASSWORD: devpassword
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  api:
    build: ./apps/api
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://app:devpassword@postgres/plancraft3d
      REDIS_URL: redis://redis:6379
      STORAGE_BACKEND: local
      STORAGE_PATH: /data/uploads
    volumes: ["./data:/data"]
    depends_on: [postgres, redis]

  parsing:
    build: ./services/parsing
    ports: ["8001:8001"]
    environment:
      REDIS_URL: redis://redis:6379
      MODEL_PATH: /models/floorplan_yolov8.pt
    volumes: ["./models:/models"]
    depends_on: [redis]
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]    # optional for MVP

  web:
    build: ./apps/web
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on: [api]
```

---

## 12. Dependency Graph & Critical Path

```
Week 1    Week 2    Week 3    Week 4    Week 5    Week 6
 ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
 │2.1.1├───┤2.1.2├───┤2.1.3├───┤2.1.4├───┤2.1.5├───┤2.1.6│
 └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘
                             │         │
 ┌─────┐   ┌─────┐   ┌─────▼──┐  ┌──▼──────┐
 │2.2.1├───┤2.2.2├───┤2.2.3-6│  │ 2.2.7   │
 └─────┘   └─────┘   └────┬───┘  └──┬──────┘
                          │         │
 ┌─────┐   ┌─────┐   ┌───▼─────────▼──┐
 │2.3.1├───┤2.3.2├───┤  2.3.3-6      │
 └─────┘   └─────┘   └───┬────────────┘
                          │
 ┌─────┐   ┌─────┐   ┌───▼────┐   ┌─────┐   ┌─────┐
 │2.4.1├───┤2.4.2├───┤2.4.3-5 ├───┤2.4.6├───┤2.4.7│
 └─────┘   └─────┘   └────────┘   └─────┘   └─────┘
                                          │
 ┌────────────────────────────────────────┘
 │
 ┌──▼────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
 │2.5.1-2├───┤2.5.3├───┤2.5.4├───┤2.5.5├───┤2.5.6│
 └───────┘   └─────┘   └─────┘   └─────┘   └──┬──┘
                                               │
 ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌───▼────┐
 │2.6.1├───┤2.6.2├───┤2.6.3├───┤2.6.4├───┤2.6.5  │
 └─────┘   └─────┘   └─────┘   └─────┘   └────────┘
                                               │
 ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌───▼────┐
 │2.7.1├───┤2.7.2├───┤2.7.3├───┤2.8.1├───┤2.8.2-3│
 └─────┘   └─────┘   └─────┘   └─────┘   └────────┘
```

**Critical Path**: 2.1.1 → 2.1.2 → 2.1.3 → 2.3.3 → 2.4.1 → 2.4.2 → 2.4.3–5 → 2.4.6 → 2.5.1–2 → 2.5.3 → 2.5.4 → 2.5.5 → 2.5.6 → 2.6.1 → 2.6.2 → 2.6.3 → 2.7.1 → 2.7.2 → 2.8.1

**Total MVP**: ~6 weeks (small team of 2–3 devs)

---

## 🧠 Sprint Notes & Annotations

### Cross-Cutting Concerns

```
// NOTE: State Architecture Decision
// Single source of truth = FloorPlanGraph JSON in floorPlanStore
// All mutations go through store actions → auto-syncs 2D + 3D + panels
// Never edit graph/rooms/walls directly outside store actions
```

```
// NOTE: Mesh Performance Rule
// Colors are separate from geometry. Changing a color does NOT rebuild geometry.
// Geometry rebuilds ONLY when graph structure changes (add/delete/move wall).
// Debounce mesh rebuild at 300ms — use meshBuilder.ts hash to detect changes.
```

```
// NOTE: Parsing Fallback Contract
// NEVER assume ML output is perfect. The 2D editor IS the correction UI.
// If confidence < 0.6 → show raw image side-by-side with partial graph.
// User must explicitly "Accept" before graph is saved to project.
```

```
// NOTE: Scaling Concern — 50+ Rooms
// Virtualize RoomListPanel, useInstances for repeated meshes, LOD on far meshes.
// If frame rate < 30fps → degrade to flat-shaded mode (no PBR).
```

```
// NOTE: API Security
// All project endpoints require auth middleware.
// Validate project ownership (userId match) on every write operation.
// Rate limit: 100 req/min per user. File upload: max 20MB.
```

```
// NOTE: AI Design — Ground Truth
// LLM output MUST be validated against curated preset list before returning.
// Never pass hallucinated hex codes to user. Filter, sort by confidence.
// Rules engine fallback if LLM API is down (no-cost alternative).
```

### Sprint Dependency Chain

```
Sprint 1 → Sprint 2 → Sprint 3
    ↓                        ↓
Sprint 4 → Sprint 5 → Sprint 6
```

- **Critical path**: Sprint 1 → Sprint 2 → Sprint 3 → Sprint 4 → Sprint 5 → Sprint 6
- **Parallel tracks**: Backend foundation (1.2, 1.3, 1.7) can run parallel with Frontend foundation (1.4, 1.5, 1.6)
- **Blocking dependency**: Parsing service (Sprint 2–3) must be done before end-to-end upload flow connects
- **No blocking dependency**: 2D editor (Sprint 2) can be built independently of parsing — works with manual graph input

### Key Interfaces (Contract-First)

```typescript
// NOTE: Define these types in shared-types/ FIRST before writing any implementation.
// Both frontend and backend import from packages/shared-types/src/

interface FloorPlanGraph { /* ... */ }  // Defines ONCE, used everywhere
interface RoomStyle { /* ... */ }        // Material overrides per room
interface DesignPreset { /* ... */ }     // Built-in + user presets
```

### MVP Scope Lock

```
// NOTE: Feature Freeze After Day 25
// Days 26–30 are for integration, testing, deploy, bug fixes ONLY.
// NO new features after day 25. Resist scope creep.
```

---

## 13. Risk Mitigation Checklist

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Parsing model inaccurate on diverse floor plans | High | High | Build manual correction UI as first-class feature. Never assume parse is perfect. Support partial/corrupted graphs. |
| 2D ↔ 3D sync performance degrades with complex plans | Medium | High | Use memoized selectors. Debounce mesh rebuilds. Virtualize room list. Test with 50+ room plan. |
| AI suggestions are low quality or hallucinate | Medium | Medium | Ground LLM with curated dataset. Parse LLM output against allowed presets. Show "Powered by AI" disclosure. |
| GPU cost for parsing scales poorly | Medium | High | MVP runs CPU inference (slower but free). Add GPU burst only when needed. Batch process during off-peak. |
| Real-time collaboration conflict resolution | Low | High | Defer to Phase 3. For MVP, use simple save → reload model. Research CRDT (Yjs) for Phase 3. |
| Three.js bundle size too large | Medium | Medium | Code-split 3D components. Dynamic import `@react-three/fiber`. Use `next/dynamic` with `ssr: false`. |
| Mobile browser can't handle 3D | Low | Medium | Detect WebGL support. Show simplified 2D-only mode. Graceful degradation message. |
| Texture licensing / copyright | Medium | Medium | Only use CC0 / public domain textures, or generate procedurally. Keep an asset license manifest. |

---

## Implementation Order (Recommended Build Sequence)

**Sprint 1** (Days 1–5):
- Monorepo scaffold + Docker Compose
- FastAPI foundation (config, db, health)
- Next.js scaffold with auth pages
- Zustand store shape
- User + Project CRUD backend

**Sprint 2** (Days 6–10):
- File upload + S3 storage
- Parsing service skeleton (model loads, basic wall detection)
- 2D canvas with Konva.js (grid, draw walls, rooms auto-detect)
- Project dashboard UI

**Sprint 3** (Days 11–15):
- Complete parsing service (openings, rooms, OCR)
- Job queue + WebSocket progress
- 2D canvas complete (doors, windows, edit, delete, selection)
- Connect upload → parse → show 2D → manual correction flow

**Sprint 4** (Days 16–20):
- 3D scene with Three.js + react-three-fiber
- Mesh builder (walls, floors, ceiling from graph)
- 2D ↔ 3D sync (graph changes → mesh updates)
- Camera controls + lighting

**Sprint 5** (Days 21–25):
- Door/window openings in 3D meshes
- Material panel (color picker per room)
- Design preset library (5 built-in presets)
- "Save as My Design" feature

**Sprint 6** (Days 26–30):
- GLTF export + PNG render
- Auto-save
- E2E integration testing
- Deploy to staging
- Bug fixes + polish

---

*This plan assumes a small team (2–3 developers). For a solo developer, double the timeline. For a larger team, sprints 1–3 can be parallelized across backend and frontend developers.*
