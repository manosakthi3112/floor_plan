import { useMemo } from 'react';
import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { buildMeshes } from '@/lib/meshBuilder';

export function useFloorPlanSync() {
  const graph = useFloorPlanStore((s) => s.graph);
  const roomStyles = useFloorPlanStore((s) => s.roomStyles);
  const globalFloorColor = useFloorPlanStore((s) => s.globalFloorColor);

  const meshes = useMemo(() => {
    const wallColors: Record<string, string> = {};
    for (const room of graph.rooms) {
      const style = roomStyles[room.id];
      if (style) {
        for (const wall of graph.walls) {
          wallColors[wall.id] = style.wallColor;
        }
      }
    }

    const descriptors = buildMeshes(graph, wallColors);

    return descriptors.map((d) => {
      let color = d.color;
      if (d.type === 'wall' && wallColors[d.id]) {
        color = wallColors[d.id];
      }
      if (d.type === 'floor' && d.roomId) {
        // Per-room floor color takes precedence; global floor color is the
        // base applied to every room that has no explicit per-room color.
        const perRoom = roomStyles[d.roomId]?.floorColor;
        color = perRoom ?? globalFloorColor ?? color;
      }
      if (d.type === 'ceiling' && d.roomId && roomStyles[d.roomId]?.ceiling?.color) {
        color = roomStyles[d.roomId].ceiling.color;
      }
      return { ...d, color };
    });
  }, [graph, roomStyles, globalFloorColor]);

  return meshes;
}
