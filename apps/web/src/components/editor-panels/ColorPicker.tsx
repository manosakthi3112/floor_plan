'use client';

import { useState } from 'react';


interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
}

const PRESETS = [
  '#ffffff', '#f5f5f4', '#e7e5e4', '#d6d3d1',
  '#fef2f2', '#fee2e2', '#fecaca',
  '#fefce8', '#fef9c3', '#fde68a',
  '#ecfdf5', '#d1fae5', '#a7f3d0',
  '#eff6ff', '#dbeafe', '#bfdbfe',
  '#faf5ff', '#f3e8ff', '#e9d5ff',
  '#f3f4f6', '#e5e7eb', '#d1d5db',
  '#78716c', '#57534e', '#292524',
  '#991b1b', '#b45309', '#15803d',
  '#1d4ed8', '#7c3aed', '#be185d',
];

export function ColorPicker({ value, onChange }: ColorPickerProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <div className="flex items-center gap-2">
        <button
          onClick={() => setOpen(!open)}
          className="h-8 w-8 rounded-lg border border-gray-300 shrink-0"
          style={{ backgroundColor: value }}
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 rounded-lg border border-gray-300 px-2 py-1 text-xs font-mono focus:border-primary-500 focus:outline-none"
        />
      </div>

      {open && (
        <div className="absolute top-10 left-0 z-50 rounded-xl border bg-white p-3 shadow-lg">
          <div className="grid grid-cols-6 gap-1.5 mb-3">
            {PRESETS.map((c) => (
              <button
                key={c}
                onClick={() => { onChange(c); setOpen(false); }}
                className={`h-7 w-7 rounded-md border ${value === c ? 'border-primary-500 ring-2 ring-primary-200' : 'border-gray-200'}`}
                style={{ backgroundColor: c }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
