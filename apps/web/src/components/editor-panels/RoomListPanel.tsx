'use client';

import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { useUIStore } from '@/stores/uiStore';

export function RoomListPanel() {
  const rooms = useFloorPlanStore((s) => s.graph.rooms);
  const roomStyles = useFloorPlanStore((s) => s.roomStyles);
  const updateRoom = useFloorPlanStore((s) => s.updateRoom);
  const activeRoomId = useUIStore((s) => s.activeRoomId);
  const setActiveRoom = useUIStore((s) => s.setActiveRoom);

  if (rooms.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-gray-400">
        No rooms yet.
      </div>
    );
  }

  return (
    <div className="p-2 space-y-1">
      {rooms.map((room) => {
        const style = roomStyles[room.id];
        const isActive = activeRoomId === room.id;

        return (
          <button
            key={room.id}
            onClick={() => setActiveRoom(room.id)}
            className={`w-full flex items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors ${
              isActive ? 'bg-primary-50 border border-primary-200' : 'hover:bg-gray-50 border border-transparent'
            }`}
          >
            <div
              className="h-6 w-6 rounded border border-gray-200 shrink-0"
              style={{ backgroundColor: style?.wallColor || '#e5e7eb' }}
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{room.label}</p>
              <p className="text-xs text-gray-400">{room.area} m²</p>
            </div>
          </button>
        );
      })}
    </div>
  );
}
