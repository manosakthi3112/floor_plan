# Sprint 2 — Upload, Parse & 2D Canvas (Days 6–10)

## Goal
File upload pipeline, parsing service skeleton, 2D canvas drawing, dashboard UI.

---

## Task List

### 2.1 File upload + S3 storage
- [ ] Create `core/storage.py` — S3-compatible client (boto3) with local filesystem fallback
- [ ] Create `routers/parsing.py` — POST `/parsing/upload` multipart endpoint
- [ ] Uploaded file → stored in S3 → queue parse job → return `jobId`
- [ ] **Files:** `core/storage.py`, `routers/parsing.py`

### 2.2 Parsing service skeleton
- [ ] Scaffold `services/parsing/` — FastAPI microservice
- [ ] Create `models/detection_model.py` — YOLOv8 wrapper with warm-start
- [ ] Download pre-trained floor plan model at container start
- [ ] Create `utils/image_preprocessing.py` — grayscale, deskew, threshold, PDF handling
- [ ] **Files:** `services/parsing/app/main.py`, `config.py`, `models/detection_model.py`, `utils/image_preprocessing.py`

### 2.3 Basic wall detection
- [ ] Create `processors/wall_detector.py` — detection output → line segments → merge collinear
- [ ] Output wall segments with positions and thickness
- [ ] Create `schemas/floor_plan_graph.py` — validate output JSON
- [ ] **Files:** `processors/wall_detector.py`, `schemas/floor_plan_graph.py`

### 2.4 Dashboard UI
- [ ] Create `ProjectList.tsx` — grid layout with project cards
- [ ] Create `ProjectCard.tsx` — thumbnail, name, date, menu (delete/duplicate)
- [ ] Create `CreateProjectDialog.tsx` — create blank or upload dialog
- [ ] Connect to `projectService.ts` for data fetching
- [ ] **Files:** `components/project/*.tsx`

### 2.5 Upload flow UI
- [ ] Create `UploadFloorPlan.tsx` — drag & drop zone, file type validation (png, jpg, pdf)
- [ ] Progress bar for upload status
- [ ] Poll job status after upload → auto-navigate to editor on completion
- [ ] **Files:** `UploadFloorPlan.tsx`

### 2.6 2D Canvas — grid & walls
- [ ] Create `FloorPlanCanvas.tsx` — Konva.js stage with zoom/pan
- [ ] Create `GridSnapOverlay.tsx` — configurable grid, snap indicators
- [ ] Create `WallTool.tsx` — click-to-place endpoints, drag to draw
- [ ] Wall render: lines with thickness visualization
- [ ] **Files:** `components/editor-2d/FloorPlanCanvas.tsx`, `GridSnapOverlay.tsx`, `WallTool.tsx`

### 2.7 Room auto-detect (basic)
- [ ] Algorithm: flood-fill from wall-bounded closed loops
- [ ] Render room polygons as filled shapes with labels
- [ ] **Files:** `FloorPlanCanvas.tsx` (room display logic)

---

## Notes / Design Decisions

- **Parsing as separate service**: Keeps ML dependencies isolated. Communicates via Redis queue + HTTP callback.
- **S3 fallback**: Local filesystem for dev (`STORAGE_BACKEND=local`), S3 for prod. Transparent via abstraction.
- **YOLOv8**: Use `ultralytics` package. Model can run CPU-only at ~3–5s per image for MVP.
- **Konva.js**: Good for CAD-like drawing. Use `react-konva` wrapper.
- **Room auto-detect**: Start simple — detect rectangles from 4-wall intersections. More complex polygons later.

## Acceptance Criteria
- [ ] Upload a floor plan image → stored in S3 → job queued
- [ ] Parsing service picks up job → basic wall detection runs
- [ ] Parsed walls appear in `FloorPlanGraph` JSON
- [ ] Dashboard shows project list with thumbnails
- [ ] New project dialog (blank or upload) works
- [ ] 2D canvas renders with grid
- [ ] Click two points on canvas → wall segment created
- [ ] Rooms auto-detect from closed wall loops
