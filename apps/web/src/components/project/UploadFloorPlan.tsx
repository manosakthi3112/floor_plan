'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useRouter } from 'next/navigation';

interface UploadFloorPlanProps {
  onUpload: (file: File) => void;
  progress?: number;
  status?: 'idle' | 'uploading' | 'processing' | 'done' | 'error';
  confidence?: number;
  errorMessage?: string;
  onAccept?: () => void;
  onRetry?: () => void;
}

export function UploadFloorPlan({
  onUpload,
  progress = 0,
  status = 'idle',
  confidence,
  errorMessage,
  onAccept,
  onRetry,
}: UploadFloorPlanProps) {
  const router = useRouter();
  const [showFallback, setShowFallback] = useState(false);

  useEffect(() => {
    if (status === 'done' && confidence !== undefined && confidence < 0.5) {
      setShowFallback(true);
    }
  }, [status, confidence]);

  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted.length > 0) onUpload(accepted[0]);
    },
    [onUpload],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg'], 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 20 * 1024 * 1024,
  });

  if (showFallback) {
    return (
      <div className="rounded-xl border-2 border-amber-300 bg-amber-50 p-6 text-center">
        <span className="text-2xl mb-2 block">⚠️</span>
        <h3 className="text-sm font-medium text-amber-800 mb-1">Low Confidence Parse</h3>
        <p className="text-xs text-amber-600 mb-4">
          The floor plan detection confidence was low ({Math.round((confidence || 0) * 100)}%). 
          The result may need manual correction.
        </p>
        <div className="flex justify-center gap-2">
          <button
            onClick={onAccept}
            className="rounded-lg bg-amber-600 px-4 py-2 text-xs font-medium text-white hover:bg-amber-700"
          >
            Continue to Editor
          </button>
          <button
            onClick={onRetry}
            className="rounded-lg border border-amber-300 px-4 py-2 text-xs font-medium text-amber-700 hover:bg-amber-100"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="rounded-xl border-2 border-red-300 bg-red-50 p-6 text-center">
        <span className="text-2xl mb-2 block">❌</span>
        <h3 className="text-sm font-medium text-red-800 mb-1">Upload Failed</h3>
        <p className="text-xs text-red-600 mb-4">{errorMessage || 'Something went wrong. Please try again.'}</p>
        <button
          onClick={onRetry}
          className="rounded-lg bg-red-600 px-4 py-2 text-xs font-medium text-white hover:bg-red-700"
        >
          Retry Upload
        </button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`flex flex-col items-center justify-center h-40 rounded-xl border-2 border-dashed transition-colors cursor-pointer ${
        isDragActive
          ? 'border-primary-400 bg-primary-50'
          : 'border-gray-300 bg-gray-50 hover:border-primary-300'
      }`}
    >
      <input {...getInputProps()} />
      {status === 'uploading' ? (
        <div className="text-center">
          <div className="h-2 w-48 rounded-full bg-gray-200 mb-2">
            <div className="h-full rounded-full bg-primary-500 transition-all" style={{ width: `${progress}%` }} />
          </div>
          <p className="text-sm text-gray-500">Uploading... {progress}%</p>
        </div>
      ) : status === 'processing' ? (
        <div className="text-center">
          <p className="text-sm text-gray-500">Processing floor plan...</p>
          <p className="text-xs text-gray-400 mt-1">Detecting walls, rooms, doors & windows</p>
        </div>
      ) : (
        <>
          <span className="text-2xl text-gray-400 mb-1">📐</span>
          <p className="text-sm text-gray-500">
            {isDragActive ? 'Drop your file here' : 'Drag & drop floor plan, or click to browse'}
          </p>
          <p className="text-xs text-gray-400 mt-1">PNG, JPG, or PDF (max 20MB)</p>
        </>
      )}
    </div>
  );
}
