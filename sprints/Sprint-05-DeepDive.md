# Sprint 5 — Materials, Openings & Presets (Days 21–25)

## Goal
Door/window 3D cutouts, material panel, color picker, design preset library, "Save as My Design."

---

## Task List

### 5.1 Door/window openings in 3D
- [ ] Create `DoorOpening.tsx` — subtract opening from wall via CSG or manual approach
- [ ] Create `WindowOpening.tsx` — similar with sill height
- [ ] Render door/window frame + glass geometry
- [ ] **Approach options:**
  - *Manual*: Split wall into 3 segments (left, opening, right) + header
  - *CSG*: Use `three-bvh-csg` for boolean subtraction
  - **Recommended**: Start with manual (more predictable), optimize to CSG later
- [ ] **Files:** `components/editor-3d/DoorOpening.tsx`, `WindowOpening.tsx`

### 5.2 Material panel
- [ ] Create `MaterialPanel.tsx` — room selector dropdown + style controls
- [ ] Three sections: Wall, Floor, Ceiling (collapsible)
- [ ] Each section: color swatch + picker trigger
- [ ] Active room highlighted in 2D + 3D
- [ ] **Files:** `components/editor-panels/MaterialPanel.tsx`

### 5.3 Color picker
- [ ] Create `ColorPicker.tsx` — popover with `react-colorful`
- [ ] Preset swatches row (whites, grays, earth tones, accent colors)
- [ ] Hex input field for exact values
- [ ] Recent colors list (last 10)
- [ ] **Files:** `components/editor-panels/ColorPicker.tsx`

### 5.4 Style application
- [ ] Store `roomStyles` in floorPlanStore as `Record<roomId, RoomStyle>`
- [ ] `setRoomStyle(roomId, partial)` updates store → mesh colors react
- [ ] `applyPreset(roomId, preset)` applies full preset to room
- [ ] **Files:** `stores/floorPlanStore.ts` (extend), `hooks/useFloorPlanSync.ts` (color sync)

### 5.5 Room list panel
- [ ] Create `RoomListPanel.tsx` — sidebar list of all rooms
- [ ] Click to select room (highlights in 2D + 3D)
- [ ] Show room name, area (m²), wall color swatch
- [ ] Inline label editing
- [ ] **Files:** `components/editor-panels/RoomListPanel.tsx`

### 5.6 Design preset library (MVP)
- [ ] Hardcode 5–10 presets as JSON constants:
  - Bedroom: Modern Minimalist, Scandinavian, Warm Cozy
  - Living Room: Modern, Traditional, Bohemian
  - Kitchen: Clean White, Warm Wood
- [ ] Create `DesignPresetCard.tsx` — preset thumbnail + name + "Apply"
- [ ] Create `DesignPresetGallery.tsx` — filter by room type, show grids
- [ ] Create `services/presetService.ts` — API calls for presets
- [ ] **Files:** `components/editor-panels/DesignPreset*.tsx`, `services/presetService.ts`

### 5.7 "Save as My Design"
- [ ] Create `MyDesignsTab.tsx` — "Save Current" button
- [ ] Save current room style as user preset (POST `/presets`)
- [ ] List user's saved presets with delete/apply actions
- [ ] Show in DesignPresetGallery as second tab
- [ ] **Files:** `components/editor-panels/MyDesignsTab.tsx`, `routers/presets.py`

### 5.8 Preset endpoints (backend)
- [ ] Create `models/design_preset.py` — preset DB model
- [ ] Create `schemas/design_preset.py` — Pydantic schemas
- [ ] Create `routers/presets.py` — GET/POST/DELETE
- [ ] Create `services/preset_library.py` — built-in + user presets
- [ ] **Files:** `routers/presets.py`, `models/design_preset.py`, `schemas/design_preset.py`, `services/preset_library.py`

---

## Notes / Design Decisions

- **Opening approach**: Manual wall-splitting is more reliable for MVP. CSG can produce non-manifold geometry. Split logic: `wallStart → openingStart → openingEnd → wallEnd` with separate header beam above opening.
- **Color reactivity**: Uses Three.js `color` prop on `MeshStandardMaterial`. No geometry rebuild needed for color/style changes.
- **Preset format**: `DesignPreset = {name, roomType, style, wallColor, floorColor, ceiling}`. Ceiling includes type + color.
- **"Apply"**: Copies preset values into `roomStyles[roomId]`. User can still tweak after applying.

## Acceptance Criteria
- [ ] Door/window openings visible in 3D as framed holes
- [ ] Selecting a room in 2D highlights it in 3D
- [ ] Change wall color → 3D updates immediately
- [ ] Built-in presets display and apply correctly
- [ ] "Save as My Design" saves current style to DB
- [ ] User presets listed and applicable from gallery
