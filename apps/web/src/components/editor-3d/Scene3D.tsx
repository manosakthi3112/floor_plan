'use client';

import { Canvas } from '@react-three/fiber';
import type { ReactNode } from 'react';

interface Scene3DProps {
  children: ReactNode;
  cameraPosition?: [number, number, number];
}

export function Scene3D({ children, cameraPosition = [500, 500, 500] }: Scene3DProps) {
  return (
    <Canvas
      camera={{ position: cameraPosition, fov: 45, near: 1, far: 10000 }}
      gl={{ antialias: true }}
      style={{ width: '100%', height: '100%' }}
    >
      <ambientLight intensity={0.6} />
      <directionalLight position={[300, 500, 300]} intensity={0.9} />
      <directionalLight position={[-300, 200, -300]} intensity={0.4} />
      {children}
    </Canvas>
  );
}
