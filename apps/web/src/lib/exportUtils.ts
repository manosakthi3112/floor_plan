import * as THREE from 'three';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';

export async function exportGLTF(scene: THREE.Scene): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const exporter = new GLTFExporter();
    exporter.parse(
      scene,
      (result: ArrayBuffer | { [key: string]: any }) => {
        if (result instanceof ArrayBuffer) {
          resolve(new Blob([result], { type: 'model/gltf-binary' }));
        } else {
          const json = JSON.stringify(result);
          resolve(new Blob([json], { type: 'model/gltf+json' }));
        }
      },
      (error: unknown) => reject(error),
      { binary: true, trs: false, onlyVisible: true },
    );
  });
}


export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function captureCanvasPNG(canvas: HTMLCanvasElement, resolution: '1080p' | '2k' | '4k' = '1080p'): string {
  const scales = { '1080p': 1, '2k': 1.5, '4k': 3 };
  const scale = scales[resolution];
  const w = Math.round(canvas.width * scale);
  const h = Math.round(canvas.height * scale);

  const offscreen = document.createElement('canvas');
  offscreen.width = w;
  offscreen.height = h;
  const ctx = offscreen.getContext('2d')!;
  ctx.scale(scale, scale);
  ctx.drawImage(canvas, 0, 0);

  return offscreen.toDataURL('image/png');
}
