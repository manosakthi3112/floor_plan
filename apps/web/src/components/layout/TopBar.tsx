'use client';

export function TopBar() {
  return (
    <header className="flex h-12 items-center justify-between border-b bg-white px-4">
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold text-primary-600">PlanCraft3D</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-500">user@example.com</span>
      </div>
    </header>
  );
}
