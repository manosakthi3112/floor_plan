'use client';

import type { DesignPreset } from '@/types/floorPlan';

interface DesignPresetCardProps {
  preset: DesignPreset;
  onApply: (preset: DesignPreset) => void;
}

export function DesignPresetCard({ preset, onApply }: DesignPresetCardProps) {
  return (
    <div className="rounded-xl border bg-white p-3 hover:shadow-sm transition-shadow">
      <div className="flex gap-2 mb-2">
        <div className="h-8 w-8 rounded-lg border" style={{ backgroundColor: preset.wallColor }} />
        <div className="h-8 w-8 rounded-lg border" style={{ backgroundColor: preset.floorColor }} />
        <div className="h-8 w-8 rounded-lg border" style={{ backgroundColor: preset.ceiling.color }} />
      </div>
      <p className="text-sm font-medium text-gray-900 truncate">{preset.name}</p>
      <p className="text-xs text-gray-400 mb-2">{preset.style}</p>
      <button
        onClick={() => onApply(preset)}
        className="w-full rounded-lg bg-primary-50 py-1.5 text-xs font-medium text-primary-700 hover:bg-primary-100 transition-colors"
      >
        Apply
      </button>
    </div>
  );
}
