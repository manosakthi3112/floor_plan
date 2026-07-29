import { create } from 'zustand';
import type { ToolType } from '@/types/ui';
export type { ToolType };

interface UIState {
  activeTool: ToolType;
  selectedWallId: string | null;
  selectedRoomId: string | null;
  selectedOpeningId: string | null;
  activeRoomId: string | null;
  sidebarTab: 'rooms' | 'materials' | 'designs' | 'ai';

  setActiveTool: (tool: ToolType) => void;
  setSelection: (type: 'wall' | 'room' | 'opening', id: string | null) => void;
  setActiveRoom: (id: string | null) => void;
  setSidebarTab: (tab: UIState['sidebarTab']) => void;
}

export const useUIStore = create<UIState>((set) => ({
  activeTool: 'select',
  selectedWallId: null,
  selectedRoomId: null,
  selectedOpeningId: null,
  activeRoomId: null,
  sidebarTab: 'rooms',

  setActiveTool: (tool) => set({ activeTool: tool }),
  setSelection: (type, id) =>
    set({
      selectedWallId: type === 'wall' ? id : null,
      selectedRoomId: type === 'room' ? id : null,
      selectedOpeningId: type === 'opening' ? id : null,
    }),
  setActiveRoom: (id) => set({ activeRoomId: id }),
  setSidebarTab: (tab) => set({ sidebarTab: tab }),
}));
