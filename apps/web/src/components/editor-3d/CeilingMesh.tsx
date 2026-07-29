'use client';

import { useMemo } from 'react';
import * as THREE from 'three';
import { MeshStandardMaterial } from 'three';


interface CeilingMeshProps {
  geometry: THREE.BufferGeometry;
  position: [number, number, number];
  color: string;
}

export function CeilingMesh({ geometry, position, color }: CeilingMeshProps) {
  const material = useMemo(() => new MeshStandardMaterial({
    color,
    roughness: 0.9,
    metalness: 0.0,
    side: 2,
    transparent: true,
    opacity: 0.85,
  }), [color]);

  return (
    <mesh
      geometry={geometry}
      material={material}
      position={position}
    />
  );
}
