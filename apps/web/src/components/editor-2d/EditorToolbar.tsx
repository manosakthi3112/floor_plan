'use client';

import { useUIStore, type ToolType } from '@/stores/uiStore';
import { useUndoRedo, useFloorPlanStore } from '@/stores/floorPlanStore';

const tools: { id: ToolType; label: string; icon: string }[] = [
  { id: 'select', label: 'Select', icon: '⬚' },
  { id: 'drawWall', label: 'Draw Wall', icon: '━' },
  { id: 'addDoor', label: 'Door', icon: '⊓' },
  { id: 'addWindow', label: 'Window', icon: '⊞' },
];

export function EditorToolbar() {
  const activeTool = useUIStore((s) => s.activeTool);
  const setActiveTool = useUIStore((s) => s.setActiveTool);
  const { undo, redo, canUndo, canRedo } = useUndoRedo();

  const backgroundImageUrl = useFloorPlanStore((s) => s.backgroundImageUrl);
  const backgroundOpacity = useFloorPlanStore((s) => s.backgroundOpacity);
  const setBackgroundImage = useFloorPlanStore((s) => s.setBackgroundImage);
  const setBackgroundOpacity = useFloorPlanStore((s) => s.setBackgroundOpacity);

  const toggleBackground = () => {
    if (backgroundImageUrl) {
      setBackgroundImage(null);
    } else {
      setBackgroundImage('/samples/floorplan-blueprint.svg', 0.45);
    }
  };

  return (
    <div className="flex items-center gap-1 rounded-lg border bg-white p-1 shadow-sm">
      <button
        onClick={undo}
        disabled={!canUndo}
        className="rounded-md px-2 py-1.5 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
        title="Undo (Ctrl+Z)"
      >
        ↩
      </button>
      <button
        onClick={redo}
        disabled={!canRedo}
        className="rounded-md px-2 py-1.5 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
        title="Redo (Ctrl+Shift+Z)"
      >
        ↪
      </button>
      <div className="w-px h-5 bg-gray-200 mx-1" />
      {tools.map((tool) => (
        <button
          key={tool.id}
          onClick={() => setActiveTool(tool.id)}
          className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors ${
            activeTool === tool.id
              ? 'bg-primary-100 text-primary-700 font-medium'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <span className="text-base">{tool.icon}</span>
          <span>{tool.label}</span>
        </button>
      ))}

      <div className="w-px h-5 bg-gray-200 mx-1" />

      {/* Blueprint Image Background Overlay Toggle */}
      <button
        onClick={toggleBackground}
        className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
          backgroundImageUrl
            ? 'bg-blue-100 text-blue-700 border border-blue-300'
            : 'bg-gray-50 text-gray-600 border hover:bg-gray-100'
        }`}
        title="Show/Hide Real Floor Plan Blueprint Image in Background"
      >
        <span>🖼️</span>
        <span>{backgroundImageUrl ? 'Hide Blueprint' : 'Show Real Floor Plan'}</span>
      </button>

      {backgroundImageUrl && (
        <div className="flex items-center gap-2 px-2 border-l border-gray-200 text-xs text-gray-500">
          <span>Opacity:</span>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.05"
            value={backgroundOpacity}
            onChange={(e) => setBackgroundOpacity(parseFloat(e.target.value))}
            className="w-20 cursor-pointer accent-blue-600"
          />
          <span className="font-mono text-gray-700">{Math.round(backgroundOpacity * 100)}%</span>
        </div>
      )}
    </div>
  );
}
