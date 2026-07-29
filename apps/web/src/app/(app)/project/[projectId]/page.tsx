'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { EditorToolbar } from '@/components/editor-2d/EditorToolbar';
import { SplitPane } from '@/components/editor-3d/SplitPane';
import { RoomListPanel } from '@/components/editor-panels/RoomListPanel';
import { MaterialPanel } from '@/components/editor-panels/MaterialPanel';
import { DesignPresetGallery } from '@/components/editor-panels/DesignPresetGallery';
import { MyDesignsTab } from '@/components/editor-panels/MyDesignsTab';
import { useUIStore } from '@/stores/uiStore';
import { useFloorPlanStore } from '@/stores/floorPlanStore';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

const FloorPlanCanvas = dynamic(
  () => import('@/components/editor-2d/FloorPlanCanvas').then((m) => ({ default: m.FloorPlanCanvas })),
  { ssr: false, loading: () => <div className="flex items-center justify-center h-full text-gray-400">Loading 2D Editor...</div> },
);

const Viewport3D = dynamic(
  () => import('@/components/editor-3d/Viewport3D').then((m) => ({ default: m.Viewport3D })),
  { ssr: false, loading: () => <div className="flex items-center justify-center h-full bg-gray-900 text-gray-400">Loading 3D...</div> },
);

const SIDEBAR_TABS = [
  { id: 'rooms' as const, label: 'Rooms' },
  { id: 'materials' as const, label: 'Materials' },
  { id: 'designs' as const, label: 'Designs' },
];

export default function ProjectEditorPage({ params }: { params: { projectId: string } }) {
  useKeyboardShortcuts();
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 800, height: 600 });
  const sidebarTab = useUIStore((s) => s.sidebarTab);
  const setSidebarTab = useUIStore((s) => s.setSidebarTab);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setSize({ width: entry.contentRect.width, height: entry.contentRect.height });
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    import('@/lib/sampleFloorPlans').then(({ DIAGNOSTIC_WALLS_ONLY_GRAPH }) => {
      useFloorPlanStore.getState().setGraph(DIAGNOSTIC_WALLS_ONLY_GRAPH);
      useFloorPlanStore.getState().setBackgroundImage('/samples/real-blueprint.jpg', 0.50);
    });

    import('@/services/projectService').then(({ projectService }) => {
      projectService.get(params.projectId).then((project) => {
        if (project.floor_plan_graph && project.floor_plan_graph.walls?.length > 0) {
          useFloorPlanStore.getState().setGraph(project.floor_plan_graph);
        }
        if (project.source_image_url) {
          useFloorPlanStore.getState().setBackgroundImage(project.source_image_url, 0.50);
        }
      }).catch(() => {});
    });
  }, [params.projectId]);



  const handleDeleteProject = async () => {

    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        const { projectService } = await import('@/services/projectService');
        await projectService.delete(params.projectId);
        window.location.href = '/dashboard';
      } catch (e) {
        console.error('Failed to delete project:', e);
      }
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b bg-white px-4 py-2 shrink-0">
        <EditorToolbar />
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-400">Project: {params.projectId}</span>
          <button
            onClick={handleDeleteProject}
            className="rounded-lg border border-red-200 bg-red-50 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-100 transition-colors"
          >
            Delete Project
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <aside className="flex w-72 flex-col border-r bg-white shrink-0">
          <div className="flex border-b">
            {SIDEBAR_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSidebarTab(tab.id)}
                className={`flex-1 py-2 text-xs font-medium text-center ${
                  sidebarTab === tab.id
                    ? 'border-b-2 border-primary-500 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <div className="flex-1 overflow-y-auto">
            {sidebarTab === 'rooms' && <RoomListPanel />}
            {sidebarTab === 'materials' && <MaterialPanel />}
            {sidebarTab === 'designs' && (
              <DesignPresetGallery />
            )}
          </div>
        </aside>
        <SplitPane
          left={
            <div ref={containerRef} className="h-full bg-gray-50">
              <FloorPlanCanvas width={size.width} height={size.height} />
            </div>
          }
          right={
            <div className="h-full bg-gray-900">
              <Viewport3D />
            </div>
          }
        />
      </div>
    </div>
  );
}
