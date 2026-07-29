'use client';

export function Sidebar() {
  return (
    <aside className="flex w-72 flex-col border-r bg-white">
      <div className="flex-1 overflow-y-auto p-4">
        <p className="text-sm text-gray-400 text-center mt-8">Sidebar content</p>
      </div>
    </aside>
  );
}
