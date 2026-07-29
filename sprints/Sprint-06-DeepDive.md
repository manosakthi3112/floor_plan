# Sprint 6 — Export, Auto-Save & Integration (Days 26–30)

## Goal
GLTF/PNG export, auto-save, end-to-end testing, staging deploy, bug fixes.

---

## Task List

### 6.1 GLTF export
- [ ] Create `lib/exportUtils.ts` — client-side GLTFExporter wrapper
- [ ] Export current scene (geometry + materials baked) as `.glb` blob
- [ ] Trigger file download via blob URL
- [ ] **Files:** `lib/exportUtils.ts`

### 6.2 Server-side export (optional)
- [ ] Create `routers/export.py` — POST `/projects/{id}/export` endpoint
- [ ] Queue Celery task for headless rendering
- [ ] Use `pygltflib` or trimesh for server-side generation
- [ ] Store result in S3, return download URL
- [ ] **Files:** `routers/export.py`, `services/mesh-generator/` (if separate)

### 6.3 PNG render
- [ ] Create `ExportMenu.tsx` — dropdown with export options
- [ ] "Export PNG" → render current canvas to PNG, download
- [ ] Resolution options: 1080p, 2K, 4K (upscale)
- [ ] **Files:** `components/project/ExportMenu.tsx`

### 6.4 Auto-save
- [ ] Create `hooks/useAutoSave.ts` — subscribe to `isDirty` flag
- [ ] Debounced save every 30s (PUT `/projects/{id}`)
- [ ] `beforeunload` → synchronous save
- [ ] Visual indicator: "Saving..." → "Saved" → "Changes unsaved"
- [ ] **Files:** `hooks/useAutoSave.ts`

### 6.5 Loading & error states
- [ ] Skeleton screens for dashboard loading
- [ ] Progress bar for parsing (from WebSocket)
- [ ] Spinner for 3D initial render
- [ ] Error toast for network failures
- [ ] Parsing failure → fallback UI (show raw image, manual draw)
- [ ] **Files:** `components/layout/LoadingSpinner.tsx`, error boundaries

### 6.6 E2E integration test (full flow)
- [ ] Upload sample floor plan → wait for parse → 2D shows result
- [ ] Manual wall correction → verify 3D sync
- [ ] Apply color → verify 3D mesh colors
- [ ] Apply preset → verify style applied
- [ ] Save project → reload → verify data persists
- [ ] Export PNG → verify file downloaded
- [ ] **Files:** `apps/web/tests/e2e/` (Playwright)

### 6.7 Backend tests
- [ ] Auth: register, login, refresh, me (pytest + httpx)
- [ ] Project CRUD: create, list, get, update, delete
- [ ] Parsing: upload → job → result flow
- [ ] Presets: list built-in, save user, delete
- [ ] **Files:** `apps/api/tests/`

### 6.8 Bug bash + polish
- [ ] Test with real floor plan images (hand-drawn, CAD exports, scanned)
- [ ] Test edge cases: empty plan, single wall, 50+ rooms
- [ ] Mobile viewport: 2D editor should be usable (touch)
- [ ] Accessibility: keyboard navigation, screen reader labels
- [ ] Performance: profiler on 3D scene, optimize mesh rebuilds

### 6.9 Deploy to staging
- [ ] Vercel project setup for frontend
- [ ] Fly.io or Render deployment for API + microservices
- [ ] Managed PostgreSQL (Neon/Render/RDS)
- [ ] Managed Redis (Upstash)
- [ ] S3-compatible storage (Cloudflare R2 for MVP)
- [ ] Configure env vars, secrets, custom domain
- [ ] CI/CD: GitHub Actions → test → lint → deploy

---

## Notes / Design Decisions

- **GLTF vs GLB**: Export `.glb` (binary) — single file, smaller, faster to load.
- **Auto-save debounce**: 30s is safe. On tab close, `beforeunload` fires synchronous `navigator.sendBeacon()`.
- **Export resolution**: PNG export uses `canvas.toDataURL('image/png')` at canvas resolution. Upscale to 4K by rendering at higher res then downscaling.
- **Staging**: Use separate DB + S3 bucket. Enable CORS for staging domain only.

## Acceptance Criteria
- [ ] Export GLB downloads valid 3D file (openable in any viewer)
- [ ] Export PNG downloads rendered image
- [ ] Auto-save triggers every 30s on changes
- [ ] "Saved" indicator shows correctly
- [ ] Full E2E flow: register → create project → upload → parse → edit → apply preset → export
- [ ] All API endpoints have passing tests
- [ ] Staging deployment accessible at `staging.plancraft3d.com`
