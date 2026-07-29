'use client';

import { useCallback, useRef } from 'react';
import * as THREE from 'three';
import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { exportGLTF, downloadBlob, captureCanvasPNG } from '@/lib/exportUtils';


interface ExportMenuProps {
  sceneRef?: React.RefObject<THREE.Scene | null>;
  canvasRef?: React.RefObject<HTMLCanvasElement | null>;
}

export function ExportMenu({ sceneRef, canvasRef }: ExportMenuProps) {
  const projectId = useFloorPlanStore((s) => s.graph.metadata.projectId);

  const handleExportGLTF = useCallback(async () => {
    if (!sceneRef?.current) return;
    try {
      const blob = await exportGLTF(sceneRef.current);
      downloadBlob(blob, `plancraft3d-${projectId || 'export'}.glb`);
    } catch (e) {
      console.error('Export failed:', e);
    }
  }, [sceneRef, projectId]);

  const handleExportPNG = useCallback((resolution: '1080p' | '2k' | '4k' = '1080p') => {
    if (!canvasRef?.current) return;
    const dataUrl = captureCanvasPNG(canvasRef.current, resolution);
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = `plancraft3d-${projectId || 'render'}-${resolution}.png`;
    a.click();
  }, [canvasRef, projectId]);

  return (
    <div className="relative group">
      <button className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
        Export
      </button>
      <div className="absolute right-0 top-full z-50 mt-1 hidden w-40 rounded-xl border bg-white shadow-lg group-hover:block">
        <button
          onClick={handleExportGLTF}
          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 first:rounded-t-xl"
        >
          Export GLB (3D)
        </button>
        <button
          onClick={() => handleExportPNG('1080p')}
          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
        >
          Export PNG (1080p)
        </button>
        <button
          onClick={() => handleExportPNG('2k')}
          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
        >
          Export PNG (2K)
        </button>
        <button
          onClick={() => handleExportPNG('4k')}
          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 last:rounded-b-xl"
        >
          Export PNG (4K)
        </button>
      </div>
    </div>
  );
}
