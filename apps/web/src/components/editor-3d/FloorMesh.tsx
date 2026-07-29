'use client';

import { useMemo } from 'react';
import * as THREE from 'three';
import { MeshStandardMaterial } from 'three';


interface FloorMeshProps {
  geometry: THREE.BufferGeometry;
  position: [number, number, number];
  color: string;
}

export function FloorMesh({ geometry, position, color }: FloorMeshProps) {
  const material = useMemo(() => new MeshStandardMaterial({
    color,
    roughness: 0.9,
    metalness: 0.0,
    side: 2,
  }), [color]);

  return (
    <mesh
      geometry={geometry}
      material={material}
      position={position}
      receiveShadow
    />
  );
}
