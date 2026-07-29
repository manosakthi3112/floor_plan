import { useEffect, useRef } from 'react';
import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { projectService } from '@/services/projectService';

export function useAutoSave(projectId: string) {
  const isDirty = useFloorPlanStore((s) => s.isDirty);
  const graph = useFloorPlanStore((s) => s.graph);
  const roomStyles = useFloorPlanStore((s) => s.roomStyles);
  const markSaved = useFloorPlanStore((s) => s.markSaved);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!isDirty) return;

    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(async () => {
      try {
        await projectService.update(projectId, {
          floor_plan_graph: graph as any,
          room_styles: roomStyles as any,
        });
        markSaved();
      } catch (e) {
        console.error('Auto-save failed:', e);
      }
    }, 30000);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isDirty, graph, roomStyles, projectId, markSaved]);

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (useFloorPlanStore.getState().isDirty) {
        e.preventDefault();
        const state = useFloorPlanStore.getState();
        navigator.sendBeacon(
          `/api/v1/projects/${projectId}`,
          JSON.stringify({
            floor_plan_graph: state.graph,
            room_styles: state.roomStyles,
          }),
        );
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [projectId]);
}
