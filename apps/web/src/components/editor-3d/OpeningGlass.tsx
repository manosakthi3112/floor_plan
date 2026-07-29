'use client';

import { useMemo } from 'react';
import * as THREE from 'three';
import { MeshPhysicalMaterial } from 'three';


interface OpeningGlassProps {
  geometry: THREE.BufferGeometry;
  position: [number, number, number];
  rotation: [number, number, number];
  color: string;
}

export function OpeningGlass({ geometry, position, rotation, color }: OpeningGlassProps) {
  const material = useMemo(() => new MeshPhysicalMaterial({
    color,
    transparent: true,
    opacity: 0.4,
    roughness: 0.1,
    metalness: 0.0,
    side: 2,
  }), [color]);

  return (
    <mesh geometry={geometry} material={material} position={position} rotation={rotation} />
  );
}
