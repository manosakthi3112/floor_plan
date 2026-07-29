'use client';

import { useState, useMemo } from 'react';
import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { useUIStore } from '@/stores/uiStore';
import { DesignPresetCard } from './DesignPresetCard';
import type { DesignPreset, CeilingStyle } from '@/types/floorPlan';

const BUILT_IN_PRESETS: DesignPreset[] = [
  { id: 'p1', name: 'Modern Minimalist', roomType: 'bedroom', style: 'modern', wallColor: '#f5f0eb', floorColor: '#8b7355', ceiling: { type: 'flat', color: '#ffffff' }, tags: ['neutral', 'warm'], isBuiltIn: true, createdAt: '', updatedAt: '' },
  { id: 'p2', name: 'Scandinavian Bright', roomType: 'bedroom', style: 'scandinavian', wallColor: '#f8f9fa', floorColor: '#d4b895', ceiling: { type: 'flat', color: '#ffffff' }, tags: ['bright', 'minimal'], isBuiltIn: true, createdAt: '', updatedAt: '' },
  { id: 'p3', name: 'Warm Cozy', roomType: 'bedroom', style: 'cozy', wallColor: '#e8d5c4', floorColor: '#a0845c', ceiling: { type: 'tray', color: '#f5f0eb' }, tags: ['warm', 'earthy'], isBuiltIn: true, createdAt: '', updatedAt: '' },
  { id: 'p4', name: 'Modern Living', roomType: 'living_room', style: 'modern', wallColor: '#e8e0d5', floorColor: '#7a6b5a', ceiling: { type: 'flat', color: '#ffffff' }, tags: ['neutral', 'elegant'], isBuiltIn: true, createdAt: '', updatedAt: '' },
  { id: 'p5', name: 'Clean White Kitchen', roomType: 'kitchen', style: 'modern', wallColor: '#ffffff', floorColor: '#c4b5a0', ceiling: { type: 'flat', color: '#ffffff' }, tags: ['clean', 'bright'], isBuiltIn: true, createdAt: '', updatedAt: '' },
  { id: 'p6', name: 'Warm Wood Kitchen', roomType: 'kitchen', style: 'rustic', wallColor: '#f5e6d3', floorColor: '#8b6914', ceiling: { type: 'exposed_beam', color: '#f5f0eb', beamColor: '#5c4033', beamSpacing: 120 }, tags: ['warm', 'rustic'], isBuiltIn: true, createdAt: '', updatedAt: '' },
  { id: 'p7', name: 'Spa Bathroom', roomType: 'bathroom', style: 'modern', wallColor: '#d4e8d4', floorColor: '#a0b0a0', ceiling: { type: 'flat', color: '#ffffff' }, tags: ['calm', 'green'], isBuiltIn: true, createdAt: '', updatedAt: '' },
  { id: 'p8', name: 'Bohemian Living', roomType: 'living_room', style: 'bohemian', wallColor: '#e8d4c4', floorColor: '#8b7355', ceiling: { type: 'coffered', color: '#f5f0eb' }, tags: ['warm', 'eclectic'], isBuiltIn: true, createdAt: '', updatedAt: '' },
];

interface DesignPresetGalleryProps {
  userPresets?: DesignPreset[];
}

export function DesignPresetGallery({ userPresets = [] }: DesignPresetGalleryProps) {
  const [tab, setTab] = useState<'builtin' | 'mine'>('builtin');
  const [roomFilter, setRoomFilter] = useState('all');
  const rooms = useFloorPlanStore((s) => s.graph.rooms);
  const applyPreset = useFloorPlanStore((s) => s.setRoomStyle);
  const activeRoomId = useUIStore((s) => s.activeRoomId);

  const sourcePresets = tab === 'builtin' ? BUILT_IN_PRESETS : userPresets;

  const filtered = useMemo(() => {
    return sourcePresets.filter((p) => roomFilter === 'all' || p.roomType === roomFilter);
  }, [sourcePresets, roomFilter]);

  const handleApply = (preset: DesignPreset) => {
    const targetRoomId = activeRoomId || rooms[0]?.id;
    if (!targetRoomId) return;
    applyPreset(targetRoomId, {
      wallColor: preset.wallColor,
      floorColor: preset.floorColor,
      ceiling: preset.ceiling,
    });
  };

  const roomTypes = useMemo(() => {
    const types = new Set(BUILT_IN_PRESETS.map((p) => p.roomType));
    return ['all', ...Array.from(types)];
  }, []);

  return (
    <div className="p-3 space-y-3">
      <div className="flex gap-1 rounded-lg bg-gray-100 p-0.5">
        <button
          onClick={() => setTab('builtin')}
          className={`flex-1 rounded-md py-1 text-xs font-medium ${tab === 'builtin' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500'}`}
        >
          Built-in
        </button>
        <button
          onClick={() => setTab('mine')}
          className={`flex-1 rounded-md py-1 text-xs font-medium ${tab === 'mine' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500'}`}
        >
          My Designs
        </button>
      </div>

      <div className="flex gap-1 overflow-x-auto pb-1">
        {roomTypes.map((rt) => (
          <button
            key={rt}
            onClick={() => setRoomFilter(rt)}
            className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${
              roomFilter === rt ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {rt === 'all' ? 'All' : rt.replace('_', ' ')}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <p className="text-center text-sm text-gray-400 py-4">
          {tab === 'mine' ? 'Save your first design to see it here.' : 'No presets match this filter.'}
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-2">
          {filtered.map((preset) => (
            <DesignPresetCard key={preset.id} preset={preset} onApply={handleApply} />
          ))}
        </div>
      )}
    </div>
  );
}
