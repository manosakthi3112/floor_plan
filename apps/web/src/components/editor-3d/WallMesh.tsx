'use client';

import { useMemo } from 'react';
import * as THREE from 'three';
import { MeshStandardMaterial } from 'three';


interface WallMeshProps {
  geometry: THREE.BufferGeometry;
  position: [number, number, number];
  rotation: [number, number, number];
  color: string;
}

export function WallMesh({ geometry, position, rotation, color }: WallMeshProps) {
  const material = useMemo(() => new MeshStandardMaterial({
    color,
    roughness: 0.8,
    metalness: 0.0,
    side: 2,
  }), [color]);

  return (
    <mesh
      geometry={geometry}
      material={material}
      position={position}
      rotation={rotation}
      receiveShadow
      castShadow
    />
  );
}
