import apiClient from './apiClient';

export interface Project {
  id: string;
  name: string;
  thumbnail_url?: string;
  source_image_url?: string;
  floor_plan_graph?: any;
  room_styles?: any;
  created_at: string;
  updated_at: string;
}

export const projectService = {
  async list(): Promise<{ projects: Project[]; total: number }> {
    const { data } = await apiClient.get('/api/v1/projects');
    return data;
  },

  async get(id: string): Promise<Project> {
    const { data } = await apiClient.get(`/api/v1/projects/${id}`);
    return data;
  },

  async create(payload?: { name?: string; floor_plan_graph?: any; source_image_url?: string } | string): Promise<Project> {
    const body = typeof payload === 'string' ? { name: payload } : payload || {};
    const { data } = await apiClient.post('/api/v1/projects', body);
    return data;
  },


  async update(id: string, payload: Record<string, any>): Promise<Project> {
    const { data } = await apiClient.put(`/api/v1/projects/${id}`, payload);
    return data;
  },


  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/projects/${id}`);
  },
};
