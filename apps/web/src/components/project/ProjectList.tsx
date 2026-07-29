'use client';

import { ProjectCard } from './ProjectCard';

interface Project {
  id: string;
  name: string;
  thumbnail_url?: string;
  created_at: string;
}

interface ProjectListProps {
  projects: Project[];
  onSelect: (id: string) => void;
  onCreateNew: () => void;
  onDelete?: (id: string) => void;
}

export function ProjectList({ projects, onSelect, onCreateNew, onDelete }: ProjectListProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <button
        onClick={onCreateNew}
        className="flex aspect-video items-center justify-center rounded-xl border-2 border-dashed border-gray-300 bg-white hover:border-primary-400 hover:bg-primary-50/50 transition-colors"
      >
        <div className="text-center">
          <span className="text-2xl text-gray-400">+</span>
          <p className="text-sm text-gray-400 mt-1 font-medium">New Project</p>
        </div>
      </button>
      {projects.map((p) => (
        <ProjectCard
          key={p.id}
          id={p.id}
          name={p.name}
          thumbnailUrl={p.thumbnail_url}
          createdAt={p.created_at}
          onClick={onSelect}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

