# Sprint 4 — 3D Viewer & Mesh Pipeline (Days 16–20)

## Goal
Three.js scene rendering, mesh builder from graph, 2D↔3D sync, camera + lighting.

---

## Task List

### 4.1 3D scene setup
- [ ] Create `Scene3D.tsx` — `@react-three/fiber` Canvas wrapper
- [ ] Responsive resize handling
- [ ] Error boundary for WebGL failures
- [ ] **Files:** `components/editor-3d/Scene3D.tsx`

### 4.2 Mesh builder library
- [ ] Create `lib/meshBuilder.ts` — pure function: `FloorPlanGraph → {walls, floors, ceilings}[]`
- [ ] Wall: `BoxGeometry` positioned at wall midpoint, rotated to wall angle
- [ ] Floor: `ShapeGeometry` from room polygon vertices
- [ ] Ceiling: same geometry as floor, offset to wall height
- [ ] Return typed mesh descriptors `{geometry, position, rotation, material}`
- [ ] **Files:** `lib/meshBuilder.ts`

### 4.3 Wall meshes
- [ ] Create `WallMesh.tsx` — receives wall descriptor, renders mesh
- [ ] Each wall = separate `mesh` instance (needed for per-wall coloring)
- [ ] **Files:** `components/editor-3d/WallMesh.tsx`

### 4.4 Floor meshes
- [ ] Create `FloorMesh.tsx` — per-room floor polygon
- [ ] Slight thickness (5mm) for shadow rendering
- [ ] **Files:** `components/editor-3d/FloorMesh.tsx`

### 4.5 Ceiling meshes
- [ ] Create `CeilingMesh.tsx` — flat ceiling per room at wall height
- [ ] Default material: white (#FFFFFF)
- [ ] **Files:** `components/editor-3d/CeilingMesh.tsx`

### 4.6 Camera controls
- [ ] Create `OrbitControls.tsx` — `@react-three/drei` OrbitControls
- [ ] Default camera: 45° top-down, 10m distance
- [ ] Min/max distance limits
- [ ] **Files:** `components/editor-3d/OrbitControls.tsx`

### 4.7 Lighting presets
- [ ] Create `LightingPresets.tsx` — ambient light + 2 directional lights
- [ ] Presets: daylight (cool), evening (warm), overcast (soft)
- [ ] **Files:** `components/editor-3d/LightingPresets.tsx`

### 4.8 2D ↔ 3D sync
- [ ] Create `hooks/useFloorPlanSync.ts` — subscribe to floorPlanStore
- [ ] On graph change → rebuild affected meshes
- [ ] Debounce (300ms) to avoid rebuild on every drag frame
- [ ] Memoized mesh key based on `hash(graph)` to skip unchanged elements
- [ ] **Files:** `hooks/useFloorPlanSync.ts`

### 4.9 Split pane layout
- [ ] Create `SplitPane.tsx` — resizable horizontal split
- [ ] 2D on left, 3D on right
- [ ] Save ratio preference in localStorage
- [ ] **Files:** (in `components/editor-3d/` or shared)

---

## Notes / Design Decisions

- **Client-side mesh generation**: Instant feedback for editor. No server round-trip for real-time editing.
- **Separate meshes per wall**: Enables per-wall coloring without regenerating entire geometry. Trade-off: more draw calls.
- **Mesh keying**: Use `hash(graph)` as dependency. If graph hasn't changed, skip rebuild entirely.
- **Material separation**: Meshes use `MeshStandardMaterial` with `color` prop driven by store. Colors are reactive without rebuild.
- **Debounce 300ms**: Balances responsiveness vs performance. 300ms = below human perception threshold for "lag."

## Acceptance Criteria
- [ ] 3D scene renders with walls, floors, ceiling from graph
- [ ] Camera orbits around model (drag to rotate, scroll to zoom)
- [ ] 3 lighting presets change scene appearance
- [ ] Draw a wall in 2D → wall appears in 3D within 300ms
- [ ] Delete wall in 2D → wall disappears from 3D
- [ ] Resize split pane between 2D and 3D
- [ ] 50+ room plan maintains >30fps
