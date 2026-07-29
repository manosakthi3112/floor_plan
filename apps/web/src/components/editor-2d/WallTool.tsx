import { useFloorPlanStore } from '@/stores/floorPlanStore';

interface WallToolProps {
  onComplete: () => void;
}

export function WallTool({ onComplete }: WallToolProps) {
  const addWall = useFloorPlanStore((s) => s.addWall);

  const handleDrawWall = (startX: number, startY: number, endX: number, endY: number) => {
    addWall({
      start: { x: startX, y: startY },
      end: { x: endX, y: endY },
      thickness: 10,
      height: 270,
      type: 'interior',
    });
    onComplete();
  };

  return null;
}
