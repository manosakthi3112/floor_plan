'use client';

import { useRef, useState, useEffect, type ReactNode } from 'react';

interface SplitPaneProps {
  left: ReactNode;
  right: ReactNode;
  defaultRatio?: number;
}

export function SplitPane({ left, right, defaultRatio = 0.5 }: SplitPaneProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [ratio, setRatio] = useState(defaultRatio);
  const dragging = useRef(false);

  const handleMouseDown = () => {
    dragging.current = true;
    document.body.style.cursor = 'col-resize';
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!dragging.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const newRatio = (e.clientX - rect.left) / rect.width;
      setRatio(Math.max(0.2, Math.min(0.8, newRatio)));
    };

    const handleMouseUp = () => {
      dragging.current = false;
      document.body.style.cursor = '';
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  return (
    <div ref={containerRef} className="flex flex-1 overflow-hidden">
      <div style={{ width: `${ratio * 100}%` }} className="overflow-hidden">
        {left}
      </div>
      <div
        onMouseDown={handleMouseDown}
        className="w-1 cursor-col-resize bg-gray-300 hover:bg-primary-400 shrink-0"
      />
      <div style={{ width: `${(1 - ratio) * 100}%` }} className="overflow-hidden">
        {right}
      </div>
    </div>
  );
}
