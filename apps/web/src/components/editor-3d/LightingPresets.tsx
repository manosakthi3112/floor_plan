'use client';

import { useMemo } from 'react';
import type { ReactNode } from 'react';

interface LightingPresetsProps {
  preset?: 'daylight' | 'evening' | 'overcast';
  children?: ReactNode;
}

export function LightingPresets({ preset = 'daylight' }: LightingPresetsProps) {
  const lights = useMemo(() => {
    switch (preset) {
      case 'daylight':
        return { ambient: 0.5, main: { intensity: 0.8, position: [200, 300, 200] as [number, number, number], color: '#fff8e7' }, fill: { intensity: 0.3, position: [-200, 100, -200] as [number, number, number], color: '#b0c4de' } };
      case 'evening':
        return { ambient: 0.3, main: { intensity: 0.5, position: [100, 50, 200] as [number, number, number], color: '#ffa07a' }, fill: { intensity: 0.2, position: [-100, 50, -200] as [number, number, number], color: '#4a4a6a' } };
      case 'overcast':
        return { ambient: 0.7, main: { intensity: 0.4, position: [0, 200, 0] as [number, number, number], color: '#ffffff' }, fill: { intensity: 0.3, position: [100, 50, 100] as [number, number, number], color: '#d3d3d3' } };
    }
  }, [preset]);

  return (
    <>
      <ambientLight intensity={lights.ambient} />
      <directionalLight position={lights.main.position} intensity={lights.main.intensity} color={lights.main.color} />
      <directionalLight position={lights.fill.position} intensity={lights.fill.intensity} color={lights.fill.color} />
    </>
  );
}
