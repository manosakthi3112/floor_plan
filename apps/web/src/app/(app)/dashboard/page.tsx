'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProjectList } from '@/components/project/ProjectList';
import { CreateProjectDialog } from '@/components/project/CreateProjectDialog';
import { UploadFloorPlan } from '@/components/project/UploadFloorPlan';
import { projectService, type Project } from '@/services/projectService';
import apiClient from '@/services/apiClient';

export default function DashboardPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'done' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    projectService.list().then((data) => setProjects(data.projects)).catch(() => {});
  }, []);

  const handleCreate = async (name: string) => {
    try {
      const project = await projectService.create(name);
      setProjects((prev) => [project, ...prev]);
      setShowCreate(false);
      router.push(`/project/${project.id}`);
    } catch {}
  };

  const handleUpload = async (file: File) => {
    setUploadStatus('uploading');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await apiClient.post('/api/v1/parsing/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) setUploadProgress(Math.round((e.loaded / e.total) * 100));
        },
      });
      setUploadStatus('processing');
      const projectName = file.name.replace(/\.[^/.]+$/, '') || 'Uploaded Floor Plan';
      const project = await projectService.create({
        name: projectName,
        floor_plan_graph: data.floor_plan_graph,
        source_image_url: data.image_url,
      });
      setUploadStatus('done');
      router.push(`/project/${project.id}`);
    } catch {
      setUploadStatus('error');
    }
  };


  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await projectService.delete(id);
        setProjects((prev) => prev.filter((p) => p.id !== id));
      } catch (e) {
        console.error('Failed to delete project:', e);
      }
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Projects</h1>
        <p className="text-sm text-gray-500 mt-1">{projects.length} project{projects.length !== 1 ? 's' : ''}</p>
      </div>

      <ProjectList
        projects={projects}
        onSelect={(id) => router.push(`/project/${id}`)}
        onCreateNew={() => setShowCreate(true)}
        onDelete={handleDelete}
      />


      <CreateProjectDialog
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreate={handleCreate}
        onUpload={handleUpload}
      />
    </div>
  );
}
