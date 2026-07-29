'use client';

import { useState, useEffect } from 'react';
import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { useUIStore } from '@/stores/uiStore';
import apiClient from '@/services/apiClient';
import type { DesignPreset } from '@/types/floorPlan';

export function MyDesignsTab() {
  const [presets, setPresets] = useState<DesignPreset[]>([]);
  const [saving, setSaving] = useState(false);
  const [presetName, setPresetName] = useState('');
  const activeRoomId = useUIStore((s) => s.activeRoomId);
  const rooms = useFloorPlanStore((s) => s.graph.rooms);
  const roomStyles = useFloorPlanStore((s) => s.roomStyles);
  const setRoomStyle = useFloorPlanStore((s) => s.setRoomStyle);

  const activeRoom = rooms.find((r) => r.id === activeRoomId);
  const activeStyle = activeRoomId ? roomStyles[activeRoomId] : null;

  useEffect(() => {
    apiClient.get('/api/v1/presets?is_built_in=false')
      .then(({ data }) => setPresets(data.presets))
      .catch(() => {});
  }, []);

  const handleSave = async () => {
    if (!activeRoom || !activeStyle || !presetName.trim()) return;
    setSaving(true);
    try {
      await apiClient.post('/api/v1/presets', {
        name: presetName.trim(),
        room_type: activeRoom.label.toLowerCase().replace(/\s+/g, '_'),
        style: 'custom',
        preset_data: activeStyle,
      });
      setPresetName('');
      const { data } = await apiClient.get('/api/v1/presets?is_built_in=false');
      setPresets(data.presets);
    } catch {}
    setSaving(false);
  };

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/api/v1/presets/${id}`);
      setPresets((prev) => prev.filter((p) => p.id !== id));
    } catch {}
  };

  const handleApply = (preset: DesignPreset) => {
    if (!activeRoomId) return;
    const p = preset as any;
    const wallColor = p.preset_data?.wallColor || preset.wallColor || '#e5e7eb';
    const floorColor = p.preset_data?.floorColor || preset.floorColor || '#d1d5db';
    const ceiling = p.preset_data?.ceiling || preset.ceiling || { type: 'flat', color: '#f3f4f6' };
    setRoomStyle(activeRoomId, {
      wallColor,
      floorColor,
      ceiling,
    });
  };

  return (
    <div className="p-3 space-y-3">
      {activeRoom && activeStyle && (
        <div className="rounded-xl border bg-gray-50 p-3 space-y-2">
          <p className="text-xs font-medium text-gray-500">Save current style</p>
          <div className="flex gap-2">
            <input
              type="text"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              placeholder="My design name..."
              className="flex-1 rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:border-primary-500 focus:outline-none"
            />
            <button
              onClick={handleSave}
              disabled={saving || !presetName.trim()}
              className="shrink-0 rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      )}

      {presets.length === 0 ? (
        <p className="text-center text-sm text-gray-400 py-6">
          No saved designs yet. Style a room and save it above.
        </p>
      ) : (
        <div className="space-y-1">
          {presets.map((preset) => {
            const p = preset as any;
            const wallColor = p.preset_data?.wallColor || preset.wallColor || '#e5e7eb';
            const floorColor = p.preset_data?.floorColor || preset.floorColor || '#d1d5db';
            return (
              <div key={preset.id} className="flex items-center gap-3 rounded-lg border bg-white p-2.5">
                <div className="flex gap-1">
                  <div className="h-6 w-6 rounded border" style={{ backgroundColor: wallColor }} />
                  <div className="h-6 w-6 rounded border" style={{ backgroundColor: floorColor }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{preset.name}</p>
                  <p className="text-xs text-gray-400">{preset.roomType || p.room_type}</p>
                </div>
                <button
                  onClick={() => handleApply(preset)}
                  className="rounded-md bg-primary-50 px-2 py-1 text-xs font-medium text-primary-700 hover:bg-primary-100"
                >
                  Apply
                </button>
                <button
                  onClick={() => handleDelete(preset.id)}
                  className="rounded-md px-2 py-1 text-xs text-gray-400 hover:text-red-500"
                >
                  ✕
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

}
