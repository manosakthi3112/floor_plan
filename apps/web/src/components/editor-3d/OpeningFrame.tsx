'use client';

import { useMemo } from 'react';
import * as THREE from 'three';
import { MeshStandardMaterial } from 'three';


interface OpeningFrameProps {
  geometry: THREE.BufferGeometry;
  position: [number, number, number];
  rotation: [number, number, number];
  color: string;
}

export function OpeningFrame({ geometry, position, rotation, color }: OpeningFrameProps) {
  const material = useMemo(() => new MeshStandardMaterial({ color, roughness: 0.6, metalness: 0.2 }), [color]);

  return (
    <mesh geometry={geometry} material={material} position={position} rotation={rotation} />
  );
}
