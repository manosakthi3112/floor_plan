# Sprint 3 — Complete Parsing & 2D Editor Polish (Days 11–15)

## Goal
Full parsing pipeline (openings, rooms, OCR), job queue with WebSocket, complete 2D editor.

---

## Task List

### 3.1 Opening detection
- [ ] Create `processors/opening_detector.py` — classify door vs window
- [ ] Calculate position along wall (normalized 0–1), width, height
- [ ] Detect swing direction from symbology
- [ ] **Files:** `services/parsing/app/processors/opening_detector.py`

### 3.2 Room extraction
- [ ] Create `processors/room_extractor.py` — flood-fill from wall-bounded regions
- [ ] Output room polygons (ordered vertices, CCW winding)
- [ ] Detect room type from aspect ratio and size heuristics
- [ ] **Files:** `services/parsing/app/processors/room_extractor.py`

### 3.3 OCR labeling
- [ ] Create `processors/ocr_labeler.py` — Tesseract OCR integration
- [ ] Match detected text to nearest room via proximity
- [ ] Fallback: "Room 1", "Room 2", etc.
- [ ] **Files:** `services/parsing/app/processors/ocr_labeler.py`

### 3.4 Job queue + WebSocket
- [ ] Create `core/job_queue.py` — Celery tasks for parsing
- [ ] Create WebSocket endpoint `/ws/jobs/{jobId}` — push progress events
- [ ] Create `routers/parsing.py` — GET job status, GET result, PUT corrections
- [ ] **Files:** `apps/api/app/core/job_queue.py`, `routers/parsing.py`

### 3.5 2D Editor — doors & windows
- [ ] Create `DoorWindowTool.tsx` — click wall → place opening
- [ ] Toggle door ↔ window type
- [ ] Drag to adjust position along wall, resize width handles
- [ ] Render door/window symbols on canvas
- [ ] **Files:** `components/editor-2d/DoorWindowTool.tsx`

### 3.6 2D Editor — editing & selection
- [ ] Click to select walls, rooms, openings (highlight + bounding box)
- [ ] Drag wall endpoints to move
- [ ] Delete selected element (with confirmation for loaded walls)
- [ ] **Files:** `FloorPlanCanvas.tsx` (selection handlers)

### 3.7 2D Editor — toolbar
- [ ] Create `EditorToolbar.tsx` — tool selector buttons
- [ ] Undo/redo via Zustand temporal middleware
- [ ] Zoom in/out/reset buttons
- [ ] **Files:** `components/editor-2d/EditorToolbar.tsx`

### 3.8 Connect upload → parse → show 2D flow
- [ ] On parse job completion, auto-load graph into store
- [ ] Show parsed walls/rooms/doors on canvas
- [ ] Manual correction: user can edit any misdetected element
- [ ] "Accept & Continue" button → save graph to project
- [ ] **Files:** `hooks/useFloorPlanSync.ts` (partial), `UploadFlowConnector.tsx`

---

## Notes / Design Decisions

- **Tesseract**: Install in Dockerfile. Use `pytesseract` wrapper. Preprocess image for better OCR (binarize, contrast).
- **Celery**: Use Redis as broker. Task queue for parsing only (not for lightweight operations).
- **Swing direction**: Parsed from arc notation in floor plans. Arc on one side of door line = swing toward that side.
- **Manual correction**: Assume parse will be imperfect. The 2D editor IS the correction UI.

## Acceptance Criteria
- [ ] Parsing outputs complete graph (walls, rooms, openings, labels)
- [ ] WebSocket pushes real-time progress during parsing
- [ ] Job status endpoint returns queued → processing → done/error
- [ ] Doors and windows can be placed on walls in 2D editor
- [ ] Select + drag + delete works for all element types
- [ ] Undo/redo cycles through state history
- [ ] Full flow: upload → parse → 2D shows result → manual edit → save
