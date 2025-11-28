import { http } from '../http'

export const getProjectBudget = (id: string) => http.get(`/projects/${id}/budget`)

export const batchUpdateBudget = (id: string, items: any[]) => http.put(`/projects/${id}/budget/batch-update`, { items })

