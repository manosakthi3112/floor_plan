# PlanCraft3D — Code Notes & Design Annotations

> Quick-reference notes for developers. Read before coding.

---

## STATE: Single Source of Truth

```typescript
// ALL state flows from FloorPlanGraph in floorPlanStore.
// 2D canvas reads graph → renders walls/rooms/openings.
// 3D scene reads graph → builds meshes.
// Material panel reads roomStyles → controls colors.
//
// RULE: Never mutate graph outside store actions.
// RULE: Never keep duplicate state in component local state.
// RULE: API responses update store → UI reacts automatically.
```

## ARCH: Mesh Performance

```typescript
// Colors ≠ Geometry. They are separate:
//   - graph change (add/delete/move wall) → rebuild geometry
//   - style change (color/texture) → just update material props
//
// Debounce mesh rebuild at 300ms.
// Use hash(graph) as memoization key.
// For 50+ rooms: virtualize list, use InstancedMesh for repeated walls.
```

## ARCH: Parsing Reliability

```typescript
// ML is never perfect. Build the UI assuming parse WILL fail sometimes.
// Flow: upload → parse → SHOW RESULT in 2D editor → USER CORRECTS → accept
// If confidence < 0.6: show raw image side-by-side with partial graph.
// User must explicitly click "Accept" before saving graph to project.
```

## ARCH: AI Safety

```typescript
// LLM outputs are validated against curated preset list BEFORE returning.
// Filter pseudocode:
//   1. Parse LLM JSON response
//   2. For each color value: verify it matches a known palette color
//   3. For each material: verify it exists in our texture library
//   4. Remove any suggestion with <50% match rate
//   5. Sort remaining by match rate descending
//   6. Return top 3
//
// Rules engine fallback: no LLM needed, pure JSON matching.
```

## SECURITY: Auth & Permissions

```typescript
// JWT access token: 15 min expiry
// JWT refresh token: 7 day expiry, rotated on use
// All /api/v1/projects/* endpoints verify userId matches token sub
// File upload: 20MB limit, validate MIME type server-side
// Rate limit: 100 req/min per IP, 500 req/min per authenticated user
```

## DB: Key Queries

```sql
-- Get all projects for user (dashboard)
SELECT id, name, thumbnail_url, created_at, updated_at
FROM projects
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 20;

-- Get full project (editor load)
SELECT id, name, floor_plan_graph, room_styles, source_image_url
FROM projects
WHERE id = :id AND user_id = :user_id;

-- Get applicable presets for a room type
SELECT id, name, style, preset_data
FROM design_presets
WHERE is_built_in = true OR user_id = :user_id
  AND (room_type = :room_type OR room_type = 'any')
ORDER BY is_built_in DESC, created_at DESC;
```

## UI: Component Responsibilities

| Component | Reads From | Writes To | Re-renders On |
|-----------|-----------|-----------|---------------|
| FloorPlanCanvas | `graph` (store) | — (canvas events call store actions) | graph change |
| WallMesh (each) | `graph.walls[i]`, `roomStyles[roomId].wallColor` | — | wall geometry OR color change |
| MaterialPanel | `roomStyles[activeRoomId]` | `setRoomStyle()` | activeRoomId change OR style change |
| DesignPresetGallery | `presets` (API) | `applyPreset()` | filter change OR user preset save |

## TESTING: Key Assertions

```typescript
// Mesh builder test
expect(meshBuilder(wallFixture).walls).toHaveLength(1);
expect(meshBuilder(wallFixture).walls[0].geometry).toBeInstanceOf(BoxGeometry);

// Store test
store.addWall({ start: {x:0,y:0}, end: {x:100,y:0}, thickness: 10, height: 270 });
expect(store.graph.walls).toHaveLength(1);
expect(store.isDirty).toBe(true);

// Parsing service test
const result = await parsingService.parse(testImagePath);
expect(result.status).toBe('done');
expect(result.floorPlanGraph.walls.length).toBeGreaterThan(0);
expect(result.floorPlanGraph.rooms.length).toBeGreaterThan(0);
```

## FRONTEND: Package Dependencies

```json
{
  "react": "^18.3",
  "next": "^14.2",
  "three": "^0.170",
  "@react-three/fiber": "^8.17",
  "@react-three/drei": "^9.114",
  "react-konva": "^18.2",
  "konva": "^9.3",
  "zustand": "^5.0",
  "axios": "^1.7",
  "react-colorful": "^5.6",
  "react-hot-toast": "^2.4",
  "zod": "^3.23"
}
```

## BACKEND: Package Dependencies

```txt
# API
fastapi==0.115
uvicorn[standard]==0.31
sqlalchemy[asyncio]==2.0
asyncpg==0.30
alembic==1.14
python-jose[cryptography]==3.3
passlib[bcrypt]==1.7
celery[redis]==5.4
boto3==1.35
python-multipart==0.0.18
pydantic-settings==2.6

# Parsing service
ultralytics==8.3    # YOLOv8
opencv-python==4.10
pytesseract==0.3.10
pdf2image==1.17
pillow==11.0
fastapi==0.115
redis==5.2
```

## DEPLOY: Env Vars

```bash
# API
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://host:6379
JWT_SECRET=<random-64-chars>
JWT_ALGORITHM=HS256
STORAGE_BACKEND=s3  # or "local" for dev
S3_BUCKET=plancraft3d-uploads
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Parsing service
MODEL_PATH=/models/floorplan_yolov8.pt
REDIS_URL=redis://host:6379
```

## GIT: Workflow

```bash
# Branch from develop for features
git checkout develop
git checkout -b feat/sprint-4-mesh-builder

# Commit messages
# feat(scope): message   — new feature
# fix(scope): message    — bug fix
# chore(scope): message  — tooling, deps, config
# docs(scope): message   — documentation
# test(scope): message   — tests

# Merge back
git checkout develop
git merge --no-ff feat/sprint-4-mesh-builder
```

## MONOREPO: Commands

```bash
# Install all
pnpm install

# Dev (all services)
docker compose up -d postgres redis
pnpm dev              # runs web + api in parallel

# Run single service
pnpm --filter @plancraft3d/web dev
pnpm --filter @plancraft3d/api dev

# Lint all
pnpm lint

# Test all
pnpm test

# Type check all
pnpm typecheck
```
