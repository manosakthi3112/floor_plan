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
