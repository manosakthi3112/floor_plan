'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { UploadFloorPlan } from '@/components/project/UploadFloorPlan';
import { projectService } from '@/services/projectService';
import apiClient from '@/services/apiClient';

export default function NewProjectPage() {
  const router = useRouter();
  const [projectName, setProjectName] = useState('My Floor Plan');
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'done' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [creatingBlank, setCreatingBlank] = useState(false);

  const handleUpload = async (file: File) => {
    setUploadStatus('uploading');
    setErrorMessage('');
    setUploadProgress(0);

    try {
      // 1. Upload floor plan image
      const formData = new FormData();
      formData.append('file', file);

      const uploadRes = await apiClient.post('/api/v1/parsing/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) {
            setUploadProgress(Math.round((e.loaded / e.total) * 100));
          }
        },
      });

      setUploadStatus('processing');

      // 2. Create project entry
      const nameToUse = projectName.trim() || file.name.replace(/\.[^/.]+$/, '') || 'Uploaded Floor Plan';
      const project = await projectService.create(nameToUse);

      setUploadStatus('done');

      // 3. Open editor
      router.push(`/project/${project.id}`);
    } catch (err: any) {
      console.error('Upload error:', err);
      setUploadStatus('error');
      setErrorMessage(err.response?.data?.detail || 'Failed to upload and parse floor plan.');
    }
  };

  const handleStartFromScratch = async () => {
    setCreatingBlank(true);
    try {
      const nameToUse = projectName.trim() || 'Blank Floor Plan';
      const project = await projectService.create(nameToUse);
      router.push(`/project/${project.id}`);
    } catch (err: any) {
      console.error('Create error:', err);
      setErrorMessage('Failed to create new project.');
    } finally {
      setCreatingBlank(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center p-6 bg-gray-50">
      <div className="w-full max-w-xl rounded-2xl bg-white p-8 shadow-sm border border-gray-100">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Create New Project</h1>
          <p className="text-sm text-gray-500 mt-1">
            Upload an existing 2D floor plan image or start designing from scratch.
          </p>
        </div>

        {/* Project Name Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
          <input
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="e.g. Dream Apartment 2026"
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        {/* Upload Component */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Option A: Upload 2D Floor Plan</label>
          <UploadFloorPlan
            onUpload={handleUpload}
            progress={uploadProgress}
            status={uploadStatus}
            errorMessage={errorMessage}
            onRetry={() => setUploadStatus('idle')}
          />
        </div>

        {/* Divider */}
        <div className="relative my-6 flex items-center justify-center">
          <div className="w-full border-t border-gray-200" />
          <span className="absolute bg-white px-3 text-xs font-semibold uppercase text-gray-400">OR</span>
        </div>

        {/* Start from Scratch Option */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Option B: Draw Manually</label>
          <button
            type="button"
            onClick={handleStartFromScratch}
            disabled={creatingBlank || uploadStatus === 'uploading' || uploadStatus === 'processing'}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-gray-300 bg-white py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition disabled:opacity-50"
          >
            <span className="text-lg">✏️</span>
            {creatingBlank ? 'Creating Canvas...' : 'Start from Scratch (Blank 2D/3D Canvas)'}
          </button>
        </div>
      </div>
    </div>
  );
}
