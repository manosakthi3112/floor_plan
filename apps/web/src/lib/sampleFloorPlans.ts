import type { FloorPlanGraph } from '@/types/floorPlan';

/**
 * Walls-only vector graph extracted directly from 2_walls_overlay.png / diagnostic_report.json
 * Perfectly aligned with the uploaded 738x414 floor plan blueprint image (real-blueprint.jpg).
 */
export const DIAGNOSTIC_WALLS_ONLY_GRAPH: FloorPlanGraph = {
  version: 1,
  unit: 'mm',
  walls: [
    { id: 'w1', start: { x: 329, y: 45 }, end: { x: 405, y: 45 }, thickness: 10, height: 2700, type: 'exterior' },
    { id: 'w2', start: { x: 196, y: 238 }, end: { x: 293, y: 238 }, thickness: 8, height: 2700, type: 'interior' },
    { id: 'w3', start: { x: 202, y: 352 }, end: { x: 248, y: 352 }, thickness: 10, height: 2700, type: 'exterior' },
    { id: 'w4', start: { x: 197, y: 45 }, end: { x: 197, y: 352 }, thickness: 12, height: 2700, type: 'exterior' },
    { id: 'w5', start: { x: 328, y: 238 }, end: { x: 364, y: 239 }, thickness: 8, height: 2700, type: 'interior' },
    { id: 'w6', start: { x: 417, y: 346 }, end: { x: 542, y: 349 }, thickness: 12, height: 2700, type: 'exterior' },
    { id: 'w7', start: { x: 364, y: 239 }, end: { x: 364, y: 351 }, thickness: 8, height: 2700, type: 'interior' },
    { id: 'w8', start: { x: 541, y: 236 }, end: { x: 541, y: 320 }, thickness: 8, height: 2700, type: 'exterior' },
    { id: 'w9', start: { x: 512, y: 45 }, end: { x: 516, y: 185 }, thickness: 8, height: 2700, type: 'exterior' },
    { id: 'w10', start: { x: 419, y: 238 }, end: { x: 417, y: 346 }, thickness: 12, height: 2700, type: 'interior' },
    { id: 'w11', start: { x: 466, y: 45 }, end: { x: 512, y: 45 }, thickness: 10, height: 2700, type: 'exterior' },
    { id: 'w12', start: { x: 512, y: 45 }, end: { x: 514, y: 110 }, thickness: 8, height: 2700, type: 'exterior' },
    { id: 'w13', start: { x: 310, y: 351 }, end: { x: 364, y: 351 }, thickness: 8, height: 2700, type: 'exterior' },
    { id: 'w14', start: { x: 254, y: 237 }, end: { x: 293, y: 238 }, thickness: 8, height: 2700, type: 'interior' },
    { id: 'w15', start: { x: 457, y: 238 }, end: { x: 541, y: 236 }, thickness: 12, height: 2700, type: 'interior' },
    { id: 'w16', start: { x: 197, y: 45 }, end: { x: 232, y: 45 }, thickness: 10, height: 2700, type: 'exterior' },
    { id: 'w17', start: { x: 463, y: 188 }, end: { x: 516, y: 185 }, thickness: 12, height: 2700, type: 'interior' },
    { id: 'w18', start: { x: 418, y: 297 }, end: { x: 417, y: 346 }, thickness: 12, height: 2700, type: 'interior' },
  ],
  rooms: [],
  openings: [],
  stairs: [],
  metadata: {
    projectId: 'walls-only-overlay',
    source: 'template',
    createdAt: new Date().toISOString(),
  },
};

export const APARTMENT_IMAGE2_GRAPH: FloorPlanGraph = DIAGNOSTIC_WALLS_ONLY_GRAPH;
