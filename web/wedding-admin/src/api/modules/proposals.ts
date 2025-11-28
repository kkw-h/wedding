import { http } from '../http'

export interface ProposalItem {
  id: string
  project_id: string
  name: string
  description?: string
  status: string
  created_at: string
  updated_at?: string
  created_by: string
  creator?: {
    id: string
    username: string
  }
  current_data?: any
}

export interface ProposalVersion {
  id: string
  proposal_id: string
  parent_version_id?: string
  snapshot_data: any
  change_log?: any
  action_type: 'AUTO_SAVE' | 'MANUAL_SAVE' | 'PUBLISH'
  editor_id: string
  created_at: string
  version_number?: string
  change_type?: 'MAJOR' | 'MINOR'
}

export const getProposalsByProject = (projectId: string) => http.get<ProposalItem[]>(`/proposals/project/${projectId}`)

export const createProposal = (projectId: string, data: { name: string; description?: string }) => 
  http.post<ProposalItem>(`/proposals/project/${projectId}`, { ...data, project_id: projectId })

export const getProposal = (id: string) => http.get<ProposalItem>(`/proposals/${id}`)

export const updateProposal = (id: string, data: Partial<ProposalItem>) => http.put<ProposalItem>(`/proposals/${id}`, data)

export const getVersions = (id: string) => http.get<ProposalVersion[]>(`/proposals/${id}/versions`)

export const createVersion = (id: string, data: { snapshot_data: any; change_log?: any; action_type?: string; change_type?: 'MAJOR' | 'MINOR' }) => 
  http.post<ProposalVersion>(`/proposals/${id}/versions`, { ...data, proposal_id: id })

export const restoreVersion = (id: string, versionId: string) => http.post<ProposalItem>(`/proposals/${id}/restore/${versionId}`, {})
