# PlanCraft3D — Sprint Roadmap & Task Tracker

## Overview

| Sprint | Days | Focus | Dependencies |
|--------|------|-------|-------------|
| **Sprint 1** | 1–5 | Foundation & Auth | None |
| **Sprint 2** | 6–10 | Upload, Parse & 2D Canvas | Sprint 1 |
| **Sprint 3** | 11–15 | Complete Parsing & 2D Polish | Sprint 2 |
| **Sprint 4** | 16–20 | 3D Viewer & Mesh Pipeline | Sprint 1 (stores + types) |
| **Sprint 5** | 21–25 | Materials, Openings & Presets | Sprint 4 (3D scene) |
| **Sprint 6** | 26–30 | Export, Auto-Save & Integration | Sprint 3 + Sprint 5 |

## Parallel Track Strategy

```
Week 1-2         Week 3-4         Week 5-6
┌────────────────┐┌────────────────┐┌────────────────┐
│  BACKEND       ││  PARSING       ││  POLISH        │
│  Sprint 1-2    ││  Sprint 3      ││  Sprint 6      │
│  (auth, crud)  ││  (full parse)  ││  (tests, deploy)│
└────────────────┘└────────────────┘└────────────────┘
┌────────────────┐┌────────────────┐┌────────────────┐
│  FRONTEND      ││  3D ENGINE     ││  MATERIALS     │
│  Sprint 1-2    ││  Sprint 4      ││  Sprint 5      │
│  (2D canvas)   ││  (mesh build)  ││  (presets)     │
└────────────────┘└────────────────┘└────────────────┘
```

## Task Status Key

- [ ] Pending — not started
- [-] In Progress — actively working
- [x] Completed — done and verified
- [!] Blocked — waiting on dependency

## Per-Sprint Task Breakdown

See individual sprint files:
- `sprints/Sprint-01-DeepDive.md`
- `sprints/Sprint-02-DeepDive.md`
- `sprints/Sprint-03-DeepDive.md`
- `sprints/Sprint-04-DeepDive.md`
- `sprints/Sprint-05-DeepDive.md`
- `sprints/Sprint-06-DeepDive.md`

## Phase 2 & 3 (Post-MVP)

See `deep-dive-implementation-plan.md` sections 3 and 4 for scope.

---

## Quick Reference — File Map

```
apps/web/src/
├── components/editor-2d/   → 7 files (canvas, tools, grid, toolbar)
├── components/editor-3d/   → 10 files (scene, meshes, controls, lighting)
├── components/editor-panels/ → 8 files (material, color, presets, AI)
├── components/project/     → 5 files (cards, upload, export)
├── components/layout/      → 4 files (shell, sidebar, topbar)
├── stores/                 → 4 files (floorPlan, project, ui, presets)
├── services/               → 5 files (api client, project, parsing, export, AI)
├── hooks/                  → 4 files (sync, mesh, autosave, AI)
├── lib/                    → 5 files (meshBuilder, validation, export)
└── types/                  → 4 files (floorPlan, project, design, api)

apps/api/app/
├── routers/                → 7 files (auth, projects, parsing, model, export, AI, presets)
├── models/                 → 5 files (user, project, graph, style, preset)
├── schemas/                → 5 files (user, project, floorPlan, preset, AI)
├── services/               → 5 files (auth, project, parsing, presets, AI)
└── core/                   → 4 files (security, storage, queue, exceptions)

services/parsing/app/
├── processors/             → 4 files (walls, openings, rooms, OCR)
├── models/                 → 1 file (detection model)
├── schemas/                → 1 file (floor plan graph)
└── utils/                  → 2 files (preprocessing, postprocessing)

services/mesh-generator/app/  → future (Phase 2+)
├── generators/             → 5 files (walls, floors, ceiling, openings, materials)
├── schemas/                → 1 file (scene)
└── utils/                  → 1 file (GLTF export)
```

## Notes

- **Commit convention**: `type(scope): message` — e.g. `feat(parsing): add wall detection`, `fix(3d): debounce mesh rebuild`
- **Branch strategy**: `main` (stable) → `develop` → `sprint-*` / `feat/*`
- **Code review**: Every PR needs at least 1 approval. CI must pass (lint + test)
- **Definition of Done**: Code merged → tests passing → deployed to staging → verified by QA
