'use client';

import { useUIStore } from '@/stores/uiStore';
import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { ColorPicker } from './ColorPicker';

export function MaterialPanel() {
  const activeRoomId = useUIStore((s) => s.activeRoomId);
  const setActiveRoom = useUIStore((s) => s.setActiveRoom);
  const rooms = useFloorPlanStore((s) => s.graph.rooms);
  const roomStyles = useFloorPlanStore((s) => s.roomStyles);
  const setRoomStyle = useFloorPlanStore((s) => s.setRoomStyle);
  const globalFloorColor = useFloorPlanStore((s) => s.globalFloorColor);
  const setGlobalFloorColor = useFloorPlanStore((s) => s.setGlobalFloorColor);

  const activeRoom = rooms.find((r) => r.id === activeRoomId);
  const style = activeRoomId ? roomStyles[activeRoomId] : null;

  if (rooms.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-gray-400">
        No rooms yet. Draw walls to create rooms.
      </div>
    );
  }

  return (
    <div className="p-3 space-y-4">
      <Section label="Global Floor Color">
        <p className="text-[11px] text-gray-400 mb-2">
          Applies to every room that has no per-room floor color set below.
        </p>
        <div className="flex items-center gap-2">
          <ColorPicker
            value={globalFloorColor || '#d1d5db'}
            onChange={(c) => setGlobalFloorColor(c)}
          />
          <button
            onClick={() => setGlobalFloorColor(null)}
            disabled={globalFloorColor === null}
            className="rounded-md border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
            title="Clear global floor color"
          >
            Clear
          </button>
        </div>
      </Section>

      <div className="border-t border-gray-200 pt-3">
        <label className="block text-xs font-medium text-gray-500 mb-1">Room</label>
        <select
          value={activeRoomId || ''}
          onChange={(e) => setActiveRoom(e.target.value || null)}
          className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:border-primary-500 focus:outline-none"
        >
          <option value="">Select a room...</option>
          {rooms.map((r) => (
            <option key={r.id} value={r.id}>
              {r.label} ({r.area} m²)
            </option>
          ))}
        </select>
      </div>

      {activeRoom && (
        <>
          <Section label="Wall Color">
            <ColorPicker
              value={style?.wallColor || '#e5e7eb'}
              onChange={(c) => setRoomStyle(activeRoom.id, { wallColor: c })}
            />
          </Section>

          <Section label="Floor Color">
            <ColorPicker
              value={style?.floorColor || '#d1d5db'}
              onChange={(c) => setRoomStyle(activeRoom.id, { floorColor: c })}
            />
          </Section>

          <Section label="Ceiling">
            <select
              value={style?.ceiling?.type || 'flat'}
              onChange={(e) =>
                setRoomStyle(activeRoom.id, {
                  ceiling: { type: e.target.value as any, color: style?.ceiling?.color || '#f3f4f6' },
                })
              }
              className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-sm mb-2 focus:border-primary-500 focus:outline-none"
            >
              <option value="flat">Flat</option>
              <option value="tray">Tray</option>
              <option value="coffered">Coffered</option>
              <option value="cathedral">Cathedral</option>
              <option value="exposed_beam">Exposed Beam</option>
              <option value="tin_tile">Tin Tile</option>
            </select>
            <ColorPicker
              value={style?.ceiling?.color || '#f3f4f6'}
              onChange={(c) =>
                setRoomStyle(activeRoom.id, {
                  ceiling: { ...(style?.ceiling || { type: 'flat' }), color: c },
                })
              }
            />
          </Section>
        </>
      )}
    </div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-500 mb-1.5">{label}</label>
      {children}
    </div>
  );
}
