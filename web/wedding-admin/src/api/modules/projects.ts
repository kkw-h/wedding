import { http } from '../http'

export interface CreateProjectParams {
  lead_id: string
  name: string
  wedding_date: string
  hotel_name?: string
  total_budget?: number
}

export interface ProjectItem {
  id: string
  lead_id: string
  name: string
  wedding_date: string
  hotel_name?: string
  total_budget?: number
  stage: string
}

export const getProjects = (params: { skip?: number; limit?: number }) => http.get<ProjectItem[]>('/projects/', { params })

export const createProject = (data: CreateProjectParams) => http.post('/projects/', data)

export const getProjectDetail = (id: string) => http.get<ProjectItem>(`/projects/${id}`)

export const updateProject = (id: string, data: Partial<CreateProjectParams>) => http.put<ProjectItem>(`/projects/${id}`, data)

