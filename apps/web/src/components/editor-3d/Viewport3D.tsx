import { useMemo } from 'react';
import { useFloorPlanSync } from '@/hooks/useFloorPlanSync';
import { Scene3D } from './Scene3D';
import { OrbitControls } from './OrbitControls';
import { LightingPresets } from './LightingPresets';
import { WallMesh } from './WallMesh';
import { FloorMesh } from './FloorMesh';
import { CeilingMesh } from './CeilingMesh';
import { OpeningFrame } from './OpeningFrame';
import { OpeningGlass } from './OpeningGlass';

export function Viewport3D() {
  const meshes = useFloorPlanSync();

  const walls = meshes.filter((m) => m.type === 'wall');
  const floors = meshes.filter((m) => m.type === 'floor');
  const ceilings = meshes.filter((m) => m.type === 'ceiling');
  const frames = meshes.filter((m) => m.type === 'door_frame' || m.type === 'window_frame');
  const glasses = meshes.filter((m) => m.type === 'door_glass' || m.type === 'window_glass');

  const { center, cameraPos } = useMemo(() => {
    if (meshes.length === 0) {
      return {
        center: [0, 0, 0] as [number, number, number],
        cameraPos: [500, 500, 500] as [number, number, number],
      };
    }
    let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    for (const m of meshes) {
      minX = Math.min(minX, m.position.x);
      maxX = Math.max(maxX, m.position.x);
      minZ = Math.min(minZ, m.position.z);
      maxZ = Math.max(maxZ, m.position.z);
    }
    const cx = (minX + maxX) / 2;
    const cz = (minZ + maxZ) / 2;
    const span = Math.max(maxX - minX, maxZ - minZ, 300);
    return {
      center: [cx, 0, cz] as [number, number, number],
      cameraPos: [cx, span * 1.3, cz + span * 1.3] as [number, number, number],
    };
  }, [meshes]);

  if (meshes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <p className="text-gray-400">Draw walls in the 2D editor to see them in 3D</p>
      </div>
    );
  }

  return (
    <Scene3D cameraPosition={cameraPos}>
      <OrbitControls target={center} />
      <LightingPresets preset="daylight" />

      {floors.map((m) => (
        <FloorMesh key={m.id} geometry={m.geometry} position={[m.position.x, m.position.y, m.position.z]} color={m.color} />
      ))}
      {walls.map((m) => (
        <WallMesh key={m.id} geometry={m.geometry} position={[m.position.x, m.position.y, m.position.z]} rotation={[m.rotation.x, m.rotation.y, m.rotation.z]} color={m.color} />
      ))}
      {ceilings.map((m) => (
        <CeilingMesh key={m.id} geometry={m.geometry} position={[m.position.x, m.position.y, m.position.z]} color={m.color} />
      ))}
      {frames.map((m) => (
        <OpeningFrame key={m.id} geometry={m.geometry} position={[m.position.x, m.position.y, m.position.z]} rotation={[m.rotation.x, m.rotation.y, m.rotation.z]} color={m.color} />
      ))}
      {glasses.map((m) => (
        <OpeningGlass key={m.id} geometry={m.geometry} position={[m.position.x, m.position.y, m.position.z]} rotation={[m.rotation.x, m.rotation.y, m.rotation.z]} color={m.color} />
      ))}
    </Scene3D>
  );
}
