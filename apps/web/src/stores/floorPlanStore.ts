import { create } from 'zustand';
import { temporal } from 'zundo';
import type { FloorPlanGraph, RoomStyle, Wall, Room, Opening, Stair } from '@/types/floorPlan';

let idCounter = 0;
export const generateId = () => `e${++idCounter}_${Date.now()}`;

interface FloorPlanState {
  graph: FloorPlanGraph;
  roomStyles: Record<string, RoomStyle>;
  /** Global floor color applied to all rooms that lack an explicit per-room color. */
  globalFloorColor: string | null;
  /** Per-opening door-open state. Transient (NOT undoable) — animation/play state. */
  doorOpenState: Record<string, boolean>;
  /** Background floor plan image URL for 2D overlay verification. */
  backgroundImageUrl: string | null;
  backgroundOpacity: number;
  isDirty: boolean;
  lastSavedAt: number | null;

  setGraph: (graph: FloorPlanGraph) => void;
  setBackgroundImage: (url: string | null, opacity?: number) => void;
  setBackgroundOpacity: (opacity: number) => void;
  markDirty: () => void;
  markSaved: () => void;
  setRoomStyle: (roomId: string, style: Partial<RoomStyle>) => void;
  setGlobalFloorColor: (color: string | null) => void;
  toggleDoor: (openingId: string) => void;

  addWall: (wall: Omit<Wall, 'id'>) => void;
  updateWall: (id: string, updates: Partial<Wall>) => void;
  deleteWall: (id: string) => void;
  addRoom: (room: Omit<Room, 'id'>) => void;
  updateRoom: (id: string, updates: Partial<Room>) => void;
  addOpening: (opening: Omit<Opening, 'id'>) => void;
  updateOpening: (id: string, updates: Partial<Opening>) => void;
  deleteOpening: (id: string) => void;
  addStair: (stair: Omit<Stair, 'id'>) => void;
  updateStair: (id: string, updates: Partial<Stair>) => void;
  deleteStair: (id: string) => void;
}

const emptyGraph = (): FloorPlanGraph => ({
  version: 1,
  unit: 'mm',
  walls: [],
  rooms: [],
  openings: [],
  stairs: [],
  metadata: {
    projectId: '',
    source: 'manual',
    createdAt: new Date().toISOString(),
  },
});

export const useFloorPlanStore = create<FloorPlanState>()(
  temporal(
    (set) => ({
      graph: emptyGraph(),
      roomStyles: {},
      globalFloorColor: null,
      doorOpenState: {},
      backgroundImageUrl: null,
      backgroundOpacity: 0.45,
      isDirty: false,
      lastSavedAt: null,

      setGraph: (graph) => set({ graph, isDirty: true }),
      setBackgroundImage: (url, opacity = 0.45) => set({ backgroundImageUrl: url, backgroundOpacity: opacity }),
      setBackgroundOpacity: (opacity) => set({ backgroundOpacity: opacity }),
      markDirty: () => set({ isDirty: true }),
      markSaved: () => set({ isDirty: false, lastSavedAt: Date.now() }),

      setRoomStyle: (roomId, style) =>
        set((state) => ({
          roomStyles: {
            ...state.roomStyles,
            [roomId]: { ...state.roomStyles[roomId], ...style } as RoomStyle,
          },
          isDirty: true,
        })),

      setGlobalFloorColor: (color) => set({ globalFloorColor: color, isDirty: true }),

      toggleDoor: (openingId) =>
        set((state) => ({
          doorOpenState: {
            ...state.doorOpenState,
            [openingId]: !state.doorOpenState[openingId],
          },
          // Door-open state is intentionally NOT marked dirty (no save needed).
        })),

      addWall: (wall) =>
        set((state) => ({
          graph: { ...state.graph, walls: [...state.graph.walls, { id: generateId(), ...wall }] },
          isDirty: true,
        })),

      updateWall: (id, updates) =>
        set((state) => ({
          graph: {
            ...state.graph,
            walls: state.graph.walls.map((w) => (w.id === id ? { ...w, ...updates } : w)),
          },
          isDirty: true,
        })),

      deleteWall: (id) =>
        set((state) => ({
          graph: {
            ...state.graph,
            walls: state.graph.walls.filter((w) => w.id !== id),
            openings: state.graph.openings.filter((o) => o.wallId !== id),
          },
          isDirty: true,
        })),

      addRoom: (room) =>
        set((state) => ({
          graph: { ...state.graph, rooms: [...state.graph.rooms, { id: generateId(), ...room }] },
          isDirty: true,
        })),

      updateRoom: (id, updates) =>
        set((state) => ({
          graph: {
            ...state.graph,
            rooms: state.graph.rooms.map((r) => (r.id === id ? { ...r, ...updates } : r)),
          },
          isDirty: true,
        })),

      addOpening: (opening) =>
        set((state) => ({
          graph: {
            ...state.graph,
            openings: [...state.graph.openings, { id: generateId(), ...opening }],
          },
          isDirty: true,
        })),

      updateOpening: (id, updates) =>
        set((state) => ({
          graph: {
            ...state.graph,
            openings: state.graph.openings.map((o) =>
              o.id === id ? { ...o, ...updates } : o,
            ),
          },
          isDirty: true,
        })),

      deleteOpening: (id) =>
        set((state) => ({
          graph: {
            ...state.graph,
            openings: state.graph.openings.filter((o) => o.id !== id),
          },
          isDirty: true,
        })),

      addStair: (stair) =>
        set((state) => ({
          graph: { ...state.graph, stairs: [...state.graph.stairs, { id: generateId(), ...stair }] },
          isDirty: true,
        })),

      updateStair: (id, updates) =>
        set((state) => ({
          graph: {
            ...state.graph,
            stairs: state.graph.stairs.map((s) => (s.id === id ? { ...s, ...updates } : s)),
          },
          isDirty: true,
        })),

      deleteStair: (id) =>
        set((state) => ({
          graph: {
            ...state.graph,
            stairs: state.graph.stairs.filter((s) => s.id !== id),
          },
          isDirty: true,
        })),
    }),
    {
      limit: 50,
      partialize: (state) => ({
        graph: state.graph,
        roomStyles: state.roomStyles,
        globalFloorColor: state.globalFloorColor,
        // NOTE: doorOpenState is deliberately excluded — animation state
        // should not be undone.
      }),
    },
  ),
);

export const useUndoRedo = () => {
  const store = useFloorPlanStore;
  return {
    undo: () => store.temporal.getState().undo(),
    redo: () => store.temporal.getState().redo(),
    canUndo: store.temporal.getState().pastStates.length > 0,
    canRedo: store.temporal.getState().futureStates.length > 0,
  };
};
