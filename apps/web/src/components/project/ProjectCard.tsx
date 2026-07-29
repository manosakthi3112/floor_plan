'use client';

interface ProjectCardProps {
  id: string;
  name: string;
  thumbnailUrl?: string;
  createdAt: string;
  onClick: (id: string) => void;
  onDelete?: (id: string) => void;
}

export function ProjectCard({ id, name, thumbnailUrl, createdAt, onClick, onDelete }: ProjectCardProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(id);
    }
  };

  return (
    <div
      onClick={() => onClick(id)}
      className="group relative cursor-pointer overflow-hidden rounded-xl border bg-white shadow-sm transition-all hover:shadow-md hover:border-primary-300"
    >
      <div className="aspect-video bg-gray-100 flex items-center justify-center relative">
        {thumbnailUrl ? (
          <img src={thumbnailUrl} alt={name} className="h-full w-full object-cover" />
        ) : (
          <span className="text-3xl text-gray-300">🏠</span>
        )}
        {onDelete && (
          <button
            onClick={handleDelete}
            title="Delete project"
            className="absolute top-2 right-2 hidden group-hover:flex h-7 w-7 items-center justify-center rounded-lg bg-red-600/90 text-white shadow hover:bg-red-700 transition-all"
          >
            🗑️
          </button>
        )}
      </div>
      <div className="p-3">
        <h3 className="font-medium text-gray-900 truncate">{name}</h3>
        <p className="text-xs text-gray-400 mt-1">{new Date(createdAt).toLocaleDateString()}</p>
      </div>
    </div>
  );
}

