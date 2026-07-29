import { useCallback, useRef, useState, useEffect } from 'react';
import { Stage, Layer, Rect, Line, Circle, Group, Text, Arc, Image as KonvaImage } from 'react-konva';
import type Konva from 'konva';
import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { useUIStore } from '@/stores/uiStore';
import type { Wall } from '@/types/floorPlan';

const GRID_SIZE = 50;
const SNAP_DISTANCE = 10;

interface FloorPlanCanvasProps {
  width: number;
  height: number;
}

export function FloorPlanCanvas({ width, height }: FloorPlanCanvasProps) {
  const stageRef = useRef<Konva.Stage>(null);
  const walls = useFloorPlanStore((s) => s.graph.walls);
  const rooms = useFloorPlanStore((s) => s.graph.rooms);
  const openings = useFloorPlanStore((s) => s.graph.openings);
  const roomStyles = useFloorPlanStore((s) => s.roomStyles);
  const globalFloorColor = useFloorPlanStore((s) => s.globalFloorColor);
  const backgroundImageUrl = useFloorPlanStore((s) => s.backgroundImageUrl);
  const backgroundOpacity = useFloorPlanStore((s) => s.backgroundOpacity);
  const activeTool = useUIStore((s) => s.activeTool);
  const selectedWallId = useUIStore((s) => s.selectedWallId);
  const setSelection = useUIStore((s) => s.setSelection);
  const addWall = useFloorPlanStore((s) => s.addWall);
  const updateWall = useFloorPlanStore((s) => s.updateWall);
  const deleteWall = useFloorPlanStore((s) => s.deleteWall);
  const addOpening = useFloorPlanStore((s) => s.addOpening);
  const deleteOpening = useFloorPlanStore((s) => s.deleteOpening);

  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);

  const handleMouseDown = useCallback(
    (e: Konva.KonvaEventObject<MouseEvent>) => {
      const pos = e.target.getStage()?.getPointerPosition();
      if (!pos) return;

      if (activeTool === 'drawWall') {
        const snapped = snapToGrid(pos.x, pos.y);
        if (!drawStart) {
          setDrawStart(snapped);
        } else {
          addWall({
            start: drawStart,
            end: snapped,
            thickness: 10,
            height: 270,
            type: 'interior',
          });
          setDrawStart(null);
        }
        return;
      }

      if (activeTool === 'select') {
        const clickedOn = e.target;
        const id = clickedOn.id();
        if (id.startsWith('wall_')) {
          setSelection('wall', id.replace('wall_', ''));
        } else if (id.startsWith('opening_')) {
          setSelection('opening', id.replace('opening_', ''));
        } else {
          setSelection('wall', null);
          setSelection('room', null);
          setSelection('opening', null);
        }
      }
    },
    [activeTool, drawStart, addWall, setSelection],
  );

  const handleMouseMove = useCallback(
    (e: Konva.KonvaEventObject<MouseEvent>) => {
      if (activeTool === 'addDoor' || activeTool === 'addWindow') {
        const pos = e.target.getStage()?.getPointerPosition();
        if (!pos) return;
        const wallId = findWallAtPoint(pos.x, pos.y, walls);
        const previewRef = stageRef.current?.findOne('#preview');
        if (previewRef) {
          previewRef.visible(!!wallId);
          if (wallId) {
            const t = projectPointOnWall(pos.x, pos.y, walls.find((w) => w.id === wallId)!);
            const p = pointOnWallAt(walls.find((w) => w.id === wallId)!, t);
            previewRef.position({ x: p.x, y: p.y });
          }
        }
      }
    },
    [activeTool, walls],
  );

  const handleMouseUp = useCallback(
    (e: Konva.KonvaEventObject<MouseEvent>) => {
      if (activeTool === 'addDoor' || activeTool === 'addWindow') {
        const pos = e.target.getStage()?.getPointerPosition();
        if (!pos) return;
        const wallId = findWallAtPoint(pos.x, pos.y, walls);
        if (wallId) {
          const wall = walls.find((w) => w.id === wallId);
          if (wall) {
            const t = projectPointOnWall(pos.x, pos.y, wall);
            addOpening({
              type: activeTool === 'addDoor' ? 'door' : 'window',
              wallId,
              position: Math.round(t * 100) / 100,
              width: activeTool === 'addDoor' ? 90 : 120,
              height: activeTool === 'addDoor' ? 210 : 120,
              sillHeight: activeTool === 'addDoor' ? 0 : 90,
            });
          }
        }
      }
    },
    [activeTool, walls, addOpening],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedWallId) {
          deleteWall(selectedWallId);
          setSelection('wall', null);
        }
      }
    },
    [selectedWallId, deleteWall, setSelection],
  );

  return (
    <Stage
      ref={stageRef}
      width={width}
      height={height}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
    >
      <Layer>
        <GridLines width={width} height={height} />
        {backgroundImageUrl && (
          <BackgroundImageLayer url={backgroundImageUrl} opacity={backgroundOpacity} />
        )}
        {rooms.map((room) => (
          <RoomPolygon
            key={room.id}
            points={room.polygon}
            label={room.label}
            fillColor={roomStyles[room.id]?.floorColor ?? globalFloorColor ?? '#f3f4f6'}
          />
        ))}
        {walls.map((wall) => (
          <WallLine
            key={wall.id}
            wall={wall}
            isSelected={selectedWallId === wall.id}
          />
        ))}
        {openings.map((opening) => {
          const wall = walls.find((w) => w.id === opening.wallId);
          if (!wall) return null;
          const p = pointOnWallAt(wall, opening.position);
          const wallAngle = (Math.atan2(wall.end.y - wall.start.y, wall.end.x - wall.start.x) * 180) / Math.PI;
          return (
            <Group key={opening.id} id={`opening_${opening.id}`} x={p.x} y={p.y} rotation={wallAngle}>
              {opening.type === 'door' ? (
                <DoorSymbol size={opening.width} />
              ) : (
                <WindowSymbol size={opening.width} />
              )}
            </Group>
          );
        })}
        {drawStart && (
          <Circle x={drawStart.x} y={drawStart.y} radius={4} fill="#3b82f6" />
        )}
        <Circle id="preview" radius={6} fill="#3b82f6" visible={false} />
      </Layer>
    </Stage>
  );
}

function GridLines({ width, height }: { width: number; height: number }) {
  const lines = [];
  for (let x = 0; x < width; x += GRID_SIZE) {
    lines.push(
      <Line key={`v${x}`} points={[x, 0, x, height]} stroke="#e5e7eb" strokeWidth={1} />,
    );
  }
  for (let y = 0; y < height; y += GRID_SIZE) {
    lines.push(
      <Line key={`h${y}`} points={[0, y, width, y]} stroke="#e5e7eb" strokeWidth={1} />,
    );
  }
  return <>{lines}</>;
}

function RoomPolygon({
  points,
  label,
  fillColor,
}: {
  points: { x: number; y: number }[];
  label: string;
  fillColor: string;
}) {
  const flat = points.flatMap((p) => [p.x, p.y]);
  if (flat.length < 6) return null;

  let cx = 0;
  let cy = 0;
  points.forEach((p) => {
    cx += p.x;
    cy += p.y;
  });
  cx /= points.length;
  cy /= points.length;

  return (
    <>
      <Line points={flat} closed fill={fillColor} stroke="#d1d5db" strokeWidth={1} />
      <Text
        x={cx - 35}
        y={cy - 7}
        text={label}
        fontSize={13}
        fontStyle="bold"
        fill="#374151"
        align="center"
      />
    </>
  );
}

function WallLine({
  wall,
  isSelected,
}: {
  wall: Wall;
  isSelected: boolean;
}) {
  return (
    <>
      <Line
        id={`wall_${wall.id}`}
        points={[wall.start.x, wall.start.y, wall.end.x, wall.end.y]}
        stroke={isSelected ? '#3b82f6' : '#dc2626'}
        strokeWidth={isSelected ? 6 : Math.max(3, (wall.thickness || 10) / 2)}
        lineCap="round"
      />
      <Circle x={wall.start.x} y={wall.start.y} radius={3.5} fill="#1d4ed8" />
      <Circle x={wall.end.x} y={wall.end.y} radius={3.5} fill="#1d4ed8" />
    </>
  );
}

function DoorSymbol({ size }: { size: number }) {
  const width = Math.min(size, 60);
  return (
    <Group>
      <Line points={[-width / 2, 0, width / 2, 0]} stroke="#ffffff" strokeWidth={6} />
      <Line points={[-width / 2, 0, -width / 2, -width]} stroke="#92400e" strokeWidth={3} />
      <Arc
        x={-width / 2}
        y={0}
        innerRadius={0}
        outerRadius={width}
        angle={90}
        rotation={-90}
        stroke="#92400e"
        strokeWidth={1}
        dash={[4, 4]}
      />
    </Group>
  );
}

function WindowSymbol({ size }: { size: number }) {
  const width = Math.min(size, 80);
  return (
    <Group>
      <Line points={[-width / 2, 0, width / 2, 0]} stroke="#ffffff" strokeWidth={6} />
      <Rect x={-width / 2} y={-3} width={width} height={6} fill="#93c5fd" stroke="#2563eb" strokeWidth={1} />
    </Group>
  );
}

function snapToGrid(x: number, y: number): { x: number; y: number } {
  return {
    x: Math.round(x / GRID_SIZE) * GRID_SIZE,
    y: Math.round(y / GRID_SIZE) * GRID_SIZE,
  };
}

function findWallAtPoint(px: number, py: number, walls: Wall[]): string | null {
  const threshold = 15;
  for (const wall of walls) {
    const d = distToSegment(px, py, wall.start.x, wall.start.y, wall.end.x, wall.end.y);
    if (d < threshold) return wall.id;
  }
  return null;
}

function distToSegment(
  px: number, py: number,
  ax: number, ay: number,
  bx: number, by: number,
): number {
  const dx = bx - ax;
  const dy = by - ay;
  const lenSq = dx * dx + dy * dy;
  if (lenSq === 0) return Math.hypot(px - ax, py - ay);
  let t = ((px - ax) * dx + (py - ay) * dy) / lenSq;
  t = Math.max(0, Math.min(1, t));
  return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
}

function projectPointOnWall(px: number, py: number, wall: Wall): number {
  const dx = wall.end.x - wall.start.x;
  const dy = wall.end.y - wall.start.y;
  const lenSq = dx * dx + dy * dy;
  if (lenSq === 0) return 0;
  return ((px - wall.start.x) * dx + (py - wall.start.y) * dy) / lenSq;
}

function pointOnWallAt(wall: Wall, t: number): { x: number; y: number } {
  return {
    x: wall.start.x + t * (wall.end.x - wall.start.x),
    y: wall.start.y + t * (wall.end.y - wall.start.y),
  };
}

function BackgroundImageLayer({ url, opacity }: { url: string; opacity: number }) {
  const [image, setImage] = useState<HTMLImageElement | null>(null);

  useEffect(() => {
    if (!url) {
      setImage(null);
      return;
    }
    const img = new window.Image();
    img.src = url;
    img.crossOrigin = 'Anonymous';
    img.onload = () => setImage(img);
  }, [url]);

  if (!image) return null;

  return (
    <KonvaImage
      image={image}
      x={0}
      y={0}
      width={738}
      height={414}
      opacity={opacity}
      listening={false}
    />
  );
}


