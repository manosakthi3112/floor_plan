'use client';

import { useState } from 'react';

interface CreateProjectDialogProps {
  open: boolean;
  onClose: () => void;
  onCreate: (name: string) => void;
  onUpload: (file: File) => void;
}

export function CreateProjectDialog({ open, onClose, onCreate, onUpload }: CreateProjectDialogProps) {
  const [name, setName] = useState('');
  const [tab, setTab] = useState<'blank' | 'upload'>('blank');

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <div
        className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-bold mb-4">New Project</h2>

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setTab('blank')}
            className={`flex-1 rounded-lg py-2 text-sm font-medium ${
              tab === 'blank' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'
            }`}
          >
            Start Blank
          </button>
          <button
            onClick={() => setTab('upload')}
            className={`flex-1 rounded-lg py-2 text-sm font-medium ${
              tab === 'upload' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'
            }`}
          >
            Upload Plan
          </button>
        </div>

        {tab === 'blank' ? (
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Project name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
            />
            <div className="flex justify-end gap-2">
              <button onClick={onClose} className="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">
                Cancel
              </button>
              <button
                onClick={() => onCreate(name || 'Untitled Project')}
                className="rounded-lg bg-primary-600 px-4 py-2 text-sm text-white hover:bg-primary-700"
              >
                Create
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <label className="flex flex-col items-center justify-center h-32 rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 cursor-pointer hover:border-primary-400">
              <span className="text-sm text-gray-500">Drop a floor plan image here</span>
              <span className="text-xs text-gray-400 mt-1">PNG, JPG, or PDF</span>
              <input
                type="file"
                accept="image/*,.pdf"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) onUpload(file);
                }}
              />
            </label>
          </div>
        )}
      </div>
    </div>
  );
}
