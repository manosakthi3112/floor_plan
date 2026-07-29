export interface Point {
  x: number;
  y: number;
}

export interface Wall {
  id: string;
  start: Point;
  end: Point;
  thickness: number;
  height: number;
  type: 'exterior' | 'interior';
}

export interface Room {
  id: string;
  label: string;
  polygon: Point[];
  level: number;
  area: number;
}

export interface Opening {
  id: string;
  type: 'door' | 'window' | 'sliding_door' | 'french_window';
  wallId: string;
  position: number;
  width: number;
  height: number;
  sillHeight: number;
  swingDirection?: 'left' | 'right' | 'inward' | 'outward';
}

export interface Stair {
  id: string;
  start: Point; // bottom of the staircase
  end: Point; // top of the staircase
  width: number; // mm
  numSteps: number;
  stepHeight: number; // mm (riser height)
  direction: 'up' | 'down';
  roomId?: string;
}

export interface FloorPlanGraph {
  version: 1;
  unit: 'mm';
  walls: Wall[];
  rooms: Room[];
  openings: Opening[];
  stairs: Stair[];
  metadata: {
    projectId: string;
    source: 'upload' | 'manual' | 'template';
    scale?: number;
    createdAt: string;
  };
}

export interface CeilingStyle {
  type: 'flat' | 'tray' | 'coffered' | 'cathedral' | 'exposed_beam' | 'tin_tile';
  color: string;
  height?: number;
  beamColor?: string;
  beamSpacing?: number;
}

export interface RoomStyle {
  roomId: string;
  wallColor: string;
  wallTexture?: string;
  wallTextureScale?: number;
  floorColor: string;
  floorTexture?: string;
  floorTextureScale?: number;
  ceiling: CeilingStyle;
  baseboardColor?: string;
  baseboardHeight?: number;
}

export interface DesignPreset {
  id: string;
  name: string;
  roomType: string;
  style: string;
  wallColor: string;
  wallTexture?: string;
  floorColor: string;
  floorTexture?: string;
  ceiling: CeilingStyle;
  tags: string[];
  isBuiltIn: boolean;
  userId?: string;
  createdAt: string;
  updatedAt: string;
}
