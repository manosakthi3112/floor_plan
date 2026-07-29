# PlanCraft3D — Floor Plan to 3D Design Web App
### Architecture Plan (v1)

> Turns a 2D floor plan image into an editable 3D model, lets users design their own layouts from scratch, customize walls/floors/ceilings/colors, and get AI-based design suggestions.

Reference projects that informed the ML approach (both do floor-plan → structured data → 3D):
- Floor plan parsing models (wall/door/window/room detection via object detection models like Mask R-CNN / YOLO / Faster R-CNN — e.g. `rikhoffbauer2/floorplan-parser` on Hugging Face)
- Floor-plan-to-3D pipelines that take detected elements and generate a 3D scene (e.g. `Yytsi/floorplan-to-3d`, and similar projects like FloorPlanTo3D and FloorplanToBlender3d)

Your product idea combines **both stages** (parse → 3D) plus an **editor + AI design layer** on top, which is genuinely a good differentiator — most open-source repos stop at "generate a 3D mesh," they don't let a normal user then repaint walls, change flooring, or get AI suggestions in a polished web UI.

---

## 1. Product Scope

### Core user flows
1. **Upload existing floor plan** (image/PDF/scan) → AI parses it → auto-generates a 3D model.
2. **Draw a new floor plan from scratch** in a 2D editor (walls, rooms, doors, windows) → auto-generates 3D.
3. **Edit the 3D model**: move/resize walls, change room shapes, add furniture blocks.
4. **Customize materials**: wall colors/paint, wallpaper, flooring type per room, ceiling design (flat, false ceiling, coffered, exposed beam, etc.).
5. **AI design assistant**: suggests color palettes, material combos, and layout tweaks based on room type (bedroom, kitchen, living room) and a style prompt (e.g. "modern minimalist", "Tamil traditional").
6. **Save / export**: save project to account, export as image renders, GLTF/OBJ 3D file, or a shareable link; optional walkthrough view.

### MVP vs later phases
- **MVP**: upload → parse → basic 3D box model (walls+floor+ceiling+doors/windows) → manual color/material editor → export image.
- **Phase 2**: from-scratch 2D drawing editor, room-type-aware AI suggestions, texture library.
- **Phase 3**: furniture placement, walkthrough/first-person camera, AR preview, multi-user project sharing.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                        │
│  React + Three.js (react-three-fiber)                           │
│  - 2D Floor Plan Editor (Konva.js / Fabric.js canvas)            │
│  - 3D Viewer/Editor (react-three-fiber + drei)                  │
│  - Material/Color panel, AI Assistant chat panel                │
└───────────────┬───────────────────────────────────┬─────────────┘
                │ REST/GraphQL + WebSocket           │
┌───────────────▼───────────────────────────────────▼─────────────┐
│                        APPLICATION API (BFF)                     │
│  Node.js (NestJS) or Python (FastAPI)                            │
│  - Auth, Projects CRUD, Asset management, Orchestration          │
└──────┬───────────────┬───────────────┬───────────────┬──────────┘
       │               │               │               │
┌──────▼─────┐  ┌──────▼───────┐ ┌────▼───────┐ ┌──────▼────────┐
│ Floor Plan │  │  3D Model     │ │ AI Design  │ │  Storage       │
│ Parsing    │  │  Generator    │ │ Assistant  │ │  Service       │
│ Service    │  │  Service      │ │ Service    │ │  (S3/GCS)      │
│ (Python,   │  │  (Python/     │ │ (LLM API + │ │  - uploads     │
│  GPU)      │  │  Node,        │ │  rules     │ │  - renders     │
│ - detect   │  │  Trimesh/     │ │  engine)   │ │  - exported    │
│   walls,   │  │  Three.js     │ │ - palettes │ │    models      │
│   doors,   │  │  headless)    │ │ - layout   │ │                │
│   windows, │  │ - mesh gen    │ │   tips     │ │                │
│   rooms    │  │ - extrusion   │ │ - style    │ │                │
│ - OCR for  │  │ - UV mapping  │ │   prompts  │ │                │
│   room     │  │               │ │            │ │                │
│   labels   │  │               │ │            │ │                │
└────────────┘  └───────────────┘ └────────────┘ └────────────────┘
       │
┌──────▼─────────────┐
│ Postgres (metadata, │
│ projects, users)     │
└─────────────────────┘
```

---

## 3. Component Breakdown

### 3.1 Frontend (Web App)
- **Framework**: React (Next.js recommended for routing + SSR for marketing pages).
- **2D Editor**: `Konva.js` or `Fabric.js` for drawing/editing walls, rooms, doors, windows as vector shapes; snapping/grid, room-area auto-calculation.
- **3D Viewer/Editor**: `three.js` via `react-three-fiber` + `@react-three/drei` for camera controls, gizmos, lighting presets.
- **State management**: Zustand or Redux Toolkit for the floor-plan graph (rooms, walls, openings) so 2D and 3D views stay in sync from one source of truth.
- **Material panel**: color pickers, texture swatches (wood, tile, carpet, paint finishes), ceiling style picker.
- **AI Assistant panel**: chat-like sidebar, "suggest a palette for this bedroom" / "make this look Scandinavian".

### 3.2 Backend API (BFF — Backend For Frontend)
- **Framework**: FastAPI (Python) is a strong single-stack choice since your parsing/3D services are Python-heavy too — keeps the whole backend in one language. NestJS (Node/TypeScript) is the alternative if you prefer JS everywhere and plan to hire more web devs later.
- **Responsibilities**:
  - Auth (JWT, OAuth login)
  - Projects CRUD (create/save/list/delete floor plan projects)
  - Orchestrates calls to Parsing, 3D Generator, AI services
  - Job queue management for long-running ML tasks (parsing/mesh generation)
  - Rate limiting, usage quotas (if you plan free/paid tiers)

### 3.3 Floor Plan Parsing Service
- **Purpose**: take an uploaded raster floor plan (image/scanned PDF) and output a structured representation.
- **Approach**: object detection model (Mask R-CNN / YOLOv8 / Faster R-CNN, similar to the Hugging Face model you found) fine-tuned to detect:
  - Walls (as line segments/polygons)
  - Doors, windows (as bounding boxes + swing direction if possible)
  - Room boundaries (via wall-segment closure + flood fill)
  - Room labels via OCR (Tesseract or a lightweight VLM) to tag "bedroom", "kitchen", etc.
- **Output format**: a JSON "floor plan graph" — this becomes the single source of truth shared by the 2D editor, 3D generator, and AI assistant:
```json
{
  "walls": [{"id": "w1", "start": [0,0], "end": [500,0], "thickness": 10, "height": 270}],
  "rooms": [{"id": "r1", "label": "bedroom", "polygon": [[0,0],[500,0],[500,400],[0,400]]}],
  "openings": [{"id": "d1", "type": "door", "wallId": "w1", "position": 0.4, "width": 90}]
}
```
- **Hosting**: run as its own Python microservice (FastAPI + PyTorch/Ultralytics), on a GPU instance if volume is high, or CPU-only with a request queue for MVP.

### 3.4 3D Model Generator Service
- **Purpose**: convert the floor-plan-graph JSON into an actual 3D scene.
- **Approach**:
  - Extrude each wall polygon to wall height → produces wall meshes.
  - Generate floor mesh per room polygon; generate ceiling mesh (optional cap).
  - Cut door/window openings into wall meshes at the given positions.
  - Apply default materials, then let frontend override via the material panel (materials are separate from geometry so recoloring doesn't require regenerating the mesh).
- **Tooling options**:
  - Do heavy geometry generation server-side with `trimesh` (Python) and export GLTF/GLB, which the frontend loads into three.js. Good for consistent results and lets you also render server-side thumbnails.
  - Or generate geometry directly client-side in three.js from the JSON graph (lighter server load, more real-time editing feel). **Recommended**: generate client-side for the live editor (instant feedback), and reuse the same JSON-to-mesh logic server-side (Node + three.js headless, or Python + trimesh) only when you need a server-rendered export/thumbnail.

### 3.5 AI Design Assistant Service
- **Purpose**: color palette suggestions, material pairing, ceiling style suggestions, layout critique — based on room type + a style prompt.
- **Approach**: an LLM (via Claude/OpenAI API) with a structured prompt: feed it the room type, dimensions, and the user's style keywords, and ask for a JSON response (palette hex codes, suggested materials, short rationale). Pair this with a small **rules engine / curated design dataset** (e.g. known-good palettes per style, standard flooring-wall combos) so the LLM is suggesting *from* a curated set rather than hallucinating hex codes freely — better result quality.
- **Local design/style library** (presets, no AI call needed): ship a built-in set of ready-made "design presets" per room type and style (e.g. "Modern Minimalist Bedroom", "Tamil Traditional Living Room", "Scandinavian Kitchen") — each preset is just a JSON object (wall color, floor material, ceiling style) that applies instantly with one click. This gives users something to browse even before/instead of calling the AI, and it's what the AI's curated dataset (above) is built from.
- **User's own custom designs**: let users save *their own* styling combo (wall color + floor + ceiling they picked/tweaked) as a personal preset, named and reusable across rooms/projects — essentially "save as design" next to "apply design." Store these per-user in the database (own table, separate from the built-in preset library) so they show up in the same picker UI under a "My Designs" tab alongside the built-in and AI-suggested ones.
- **Optional stretch**: image generation (Stable Diffusion/DALL·E-style) for a quick concept render of a room before committing to the 3D version.

### 3.6 Storage & Data
- **Object storage** (S3/GCS/Cloudflare R2): uploaded floor plan images, generated GLTF/GLB models, rendered thumbnails/exports.
- **Postgres**: users, projects, project versions (so users can undo/revert), material/texture library metadata.
- **Redis** (optional but recommended): job queue for async ML tasks (Celery/RQ with FastAPI, or BullMQ with Node) + caching AI suggestion results.

---

## 4. Suggested Tech Stack Summary

| Layer | Choice | Why |
|---|---|---|
| Frontend framework | Next.js (React) | SSR for marketing + app in one repo |
| 2D canvas editor | Konva.js | Mature, good for CAD-like drawing |
| 3D rendering | Three.js + react-three-fiber | Industry standard, huge ecosystem |
| Backend API | FastAPI (Python) | One language across API + ML services |
| ML parsing | PyTorch + Ultralytics YOLOv8 / Mask R-CNN | Matches the reference repos' approach |
| Mesh generation | trimesh (Python) or three.js (Node/client) | Flexible geometry pipeline |
| AI suggestions | Claude/OpenAI API + curated rules dataset | Grounded, non-hallucinated suggestions |
| Database | PostgreSQL | Relational data (users/projects/versions) |
| Object storage | S3-compatible (AWS S3 / Cloudflare R2) | Cheap, standard for file assets |
| Queue | Redis + Celery/RQ or BullMQ | Async ML jobs |
| Auth | Auth0 / Clerk / custom JWT | Fast to integrate |
| Hosting | Frontend on Vercel; API + ML services on a GPU-capable host (Fly.io, Render, or AWS/GCP with a GPU node for parsing) | Split by workload needs |

---

## 5. Data Flow (End-to-End)

1. User uploads floor plan image → stored in object storage → job queued.
2. Parsing service picks up job → runs detection model → outputs floor-plan-graph JSON → saved to Postgres, linked to project.
3. Frontend fetches floor-plan-graph → renders 2D editable version immediately (user can fix/adjust any misdetected wall).
4. On "Generate 3D" → client-side (or server-side for export) mesh generation turns the graph into a 3D scene → rendered in the 3D viewer.
5. User customizes materials/colors/ceiling style → these are stored as a separate "styling" object attached to the project (not baked into geometry), so switching styles is instant.
6. User optionally asks the AI assistant for suggestions → assistant reads room type + current styling + style prompt → returns suggested palette/materials → user applies with one click.
7. User exports: server renders a GLTF/GLB (with styling baked in) + optional PNG renders for sharing/download.

---

## 6. Roadmap (Suggested Phases)

**Phase 1 — MVP (4–6 weeks for a small team)**
- Upload → parse → basic 3D extrusion (walls, floor, flat ceiling, door/window cutouts)
- Manual color picker for walls/floor/ceiling
- A small local design/style preset library (5-10 hardcoded JSON presets per room type — no AI call needed) with one-click "apply"
- "Save as my design" — let users store their own tweaked combo as a named, reusable preset (own DB table, shown in the same picker under a "My Designs" tab)
- Export as GLTF + PNG render
- Basic auth + save/load projects

**Phase 2 — Editor + AI (4–6 weeks)**
- From-scratch 2D drawing tool
- Texture/material library (wood, tile, paint finishes, false-ceiling styles)
- AI design assistant (palette + material suggestions by room type + style prompt)

**Phase 3 — Polish + Advanced (ongoing)**
- Furniture placement library
- Walkthrough/first-person camera mode
- Shareable public project links
- Mobile-responsive editor or companion app
- AR preview (WebXR) — stretch goal

---

## 7. Key Technical Risks to Plan For
- **Parsing accuracy on hand-drawn/noisy scans** — budget time for a "manual correction" UI step in the 2D editor; don't assume the model output is ever perfect.
- **Keeping 2D graph, 3D mesh, and styling in sync** — enforce a single source-of-truth JSON schema (Section 3.3) that all three layers read/write, rather than each layer keeping its own copy.
- **Server cost for ML parsing** — GPU inference is the most expensive part; consider batching, or a queue with a small always-on CPU model plus GPU burst capacity for high load.
- **AI suggestion quality** — ground the LLM with a curated dataset of good design pairings rather than open-ended generation, to avoid inconsistent/odd suggestions.

---

*This is a planning document to guide implementation — treat file/folder names and exact library versions as a starting recommendation, not a fixed requirement.*
