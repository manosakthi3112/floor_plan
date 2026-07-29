'use client';

import { OrbitControls as DreiOrbitControls } from '@react-three/drei';

export function OrbitControls({ target }: { target?: [number, number, number] }) {
  return (
    <DreiOrbitControls
      target={target || [0, 0, 0]}
      enableDamping
      dampingFactor={0.15}
      minDistance={50}
      maxDistance={5000}
      maxPolarAngle={Math.PI / 2.1}
    />
  );
}
