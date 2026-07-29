import * as THREE from 'three';
import type { FloorPlanGraph, Wall, Room, Opening } from '@/types/floorPlan';

export interface MeshDescriptor {
  id: string;
  geometry: THREE.BufferGeometry;
  position: THREE.Vector3;
  rotation: THREE.Euler;
  color: string;
  type: 'wall' | 'floor' | 'ceiling' | 'door_frame' | 'window_frame' | 'door_glass' | 'window_glass';
  roomId?: string;
  openingId?: string;
}

export function buildMeshes(graph: FloorPlanGraph, wallColors?: Record<string, string>): MeshDescriptor[] {

  const meshes: MeshDescriptor[] = [];
  const openingsByWall = groupOpeningsByWall(graph.openings);

  for (const wall of graph.walls) {
    const wallOpenings = openingsByWall.get(wall.id) || [];
    meshes.push(...buildWallWithOpenings(wall, wallOpenings));
  }

  for (const room of graph.rooms) {
    const floor = buildFloorMesh(room);
    if (floor) meshes.push(floor);
    const ceil = buildCeilingMesh(room, graph.walls[0]?.height ?? 270);
    if (ceil) meshes.push(ceil);
  }

  for (const opening of graph.openings) {
    const wall = graph.walls.find((w) => w.id === opening.wallId);
    if (wall) {
      meshes.push(...buildFrameMesh(opening, wall));
    }
  }

  return meshes;
}

function groupOpeningsByWall(openings: Opening[]): Map<string, Opening[]> {
  const map = new Map<string, Opening[]>();
  for (const o of openings) {
    const list = map.get(o.wallId) || [];
    list.push(o);
    map.set(o.wallId, list);
  }
  return map;
}

function buildWallWithOpenings(wall: Wall, openings: Opening[]): MeshDescriptor[] {
  const dx = wall.end.x - wall.start.x;
  const dy = wall.end.y - wall.start.y;
  const wallLength = Math.hypot(dx, dy);
  const angle = Math.atan2(dy, dx);
  const nx = -dy / wallLength;
  const ny = dx / wallLength;

  if (wallLength === 0) {
    const geo = new THREE.BoxGeometry(1, wall.height, wall.thickness);
    geo.translate(0, wall.height / 2, 0);
    return [{
      id: wall.id, geometry: geo,
      position: new THREE.Vector3(wall.start.x, 0, wall.start.y),
      rotation: new THREE.Euler(0, 0, 0),
      color: '#e5e7eb', type: 'wall',
    }];
  }

  if (openings.length === 0) {
    return [buildSolidWall(wall, wallLength, angle)];
  }


  const sorted = [...openings].sort((a, b) => a.position - b.position);
  const segments: { tStart: number; tEnd: number }[] = [];

  let cursor = 0;
  for (const o of sorted) {
    const margin = (o.width / 2) / wallLength;
    const ocStart = Math.max(0, o.position - margin);
    const ocEnd = Math.min(1, o.position + margin);
    if (ocStart > cursor) {
      segments.push({ tStart: cursor, tEnd: ocStart });
    }
    cursor = ocEnd;
  }
  if (cursor < 1) {
    segments.push({ tStart: cursor, tEnd: 1 });
  }

  const results: MeshDescriptor[] = [];
  for (const seg of segments) {
    const segLen = (seg.tEnd - seg.tStart) * wallLength;
    if (segLen < 5) continue;

    const sx = wall.start.x + seg.tStart * dx;
    const sy = wall.start.y + seg.tStart * dy;
    const ex = wall.start.x + seg.tEnd * dx;
    const ey = wall.start.y + seg.tEnd * dy;
    const midX = (sx + ex) / 2;
    const midY = (sy + ey) / 2;

    const geo = new THREE.BoxGeometry(segLen, wall.height, wall.thickness);
    geo.translate(0, wall.height / 2, 0);

    results.push({
      id: `${wall.id}_seg_${seg.tStart.toFixed(3)}`,
      geometry: geo,
      position: new THREE.Vector3(midX, 0, midY),
      rotation: new THREE.Euler(0, -angle, 0),
      color: '#e5e7eb',
      type: 'wall',
    });
  }

  for (const opening of openings) {
    const px = wall.start.x + opening.position * dx;
    const py = wall.start.y + opening.position * dy;
    const headerH = wall.height - (opening.sillHeight + opening.height);
    if (headerH > 10) {
      const headerGeo = new THREE.BoxGeometry(opening.width, headerH, wall.thickness);
      headerGeo.translate(0, opening.sillHeight + opening.height + headerH / 2, 0);
      results.push({
        id: `${wall.id}_header_${opening.id}`,
        geometry: headerGeo,
        position: new THREE.Vector3(px, 0, py),
        rotation: new THREE.Euler(0, -angle, 0),
        color: '#e5e7eb',
        type: 'wall',
      });
    }
  }

  return results;
}

function buildSolidWall(wall: Wall, wallLength: number, angle: number): MeshDescriptor {
  const midX = (wall.start.x + wall.end.x) / 2;
  const midY = (wall.start.y + wall.end.y) / 2;
  const geo = new THREE.BoxGeometry(wallLength, wall.height, wall.thickness);
  geo.translate(0, wall.height / 2, 0);
  return {
    id: wall.id,
    geometry: geo,
    position: new THREE.Vector3(midX, 0, midY),
    rotation: new THREE.Euler(0, -angle, 0),
    color: '#e5e7eb',
    type: 'wall',
  };
}

function buildFloorMesh(room: Room): MeshDescriptor | null {
  const pts = room.polygon;
  if (pts.length < 3) return null;
  const shape = new THREE.Shape();
  shape.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) shape.lineTo(pts[i].x, pts[i].y);
  shape.closePath();

  const geo = new THREE.ShapeGeometry(shape);
  geo.rotateX(Math.PI / 2);
  return {
    id: `floor_${room.id}`,
    geometry: geo,
    position: new THREE.Vector3(0, 0, 0),
    rotation: new THREE.Euler(0, 0, 0),
    color: '#d1d5db',
    type: 'floor',
    roomId: room.id,
  };
}

function buildCeilingMesh(room: Room, wallHeight: number): MeshDescriptor | null {
  const pts = room.polygon;
  if (pts.length < 3) return null;
  const shape = new THREE.Shape();
  shape.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) shape.lineTo(pts[i].x, pts[i].y);
  shape.closePath();

  const geo = new THREE.ShapeGeometry(shape);
  geo.rotateX(Math.PI / 2);
  return {
    id: `ceiling_${room.id}`,
    geometry: geo,
    position: new THREE.Vector3(0, wallHeight, 0),
    rotation: new THREE.Euler(0, 0, 0),
    color: '#f3f4f6',
    type: 'ceiling',
    roomId: room.id,
  };
}

function buildFrameMesh(opening: Opening, wall: Wall): MeshDescriptor[] {
  const dx = wall.end.x - wall.start.x;
  const dy = wall.end.y - wall.start.y;
  const wallLength = Math.hypot(dx, dy);
  const angle = Math.atan2(dy, dx);
  const px = wall.start.x + opening.position * dx;
  const py = wall.start.y + opening.position * dy;

  const isDoor = opening.type === 'door' || opening.type === 'sliding_door';
  const frameColor = isDoor ? '#92400e' : '#2563eb';
  const glassColor = isDoor ? '#fef3c7' : '#93c5fd';
  const frameThick = 4;

  const frameGeo = new THREE.BoxGeometry(opening.width, opening.height, frameThick);
  frameGeo.translate(0, opening.sillHeight + opening.height / 2, 0);

  const glassGeo = new THREE.BoxGeometry(opening.width - frameThick * 2, opening.height - frameThick * 2, frameThick);
  glassGeo.translate(0, opening.sillHeight + opening.height / 2, 0);

  return [
    {
      id: `${opening.id}_frame`,
      geometry: frameGeo,
      position: new THREE.Vector3(px, 0, py),
      rotation: new THREE.Euler(0, -angle, 0),
      color: frameColor,
      type: isDoor ? 'door_frame' : 'window_frame',
      openingId: opening.id,
    },
    {
      id: `${opening.id}_glass`,
      geometry: glassGeo,
      position: new THREE.Vector3(px, 0, py),
      rotation: new THREE.Euler(0, -angle, 0),
      color: glassColor,
      type: isDoor ? 'door_glass' : 'window_glass',
      openingId: opening.id,
    },
  ];
}
