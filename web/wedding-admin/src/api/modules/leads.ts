import { http } from '../http'

export interface LeadItem {
  id: string
  customer_name: string
  phone: string
  wedding_date?: string
  status: string
  owner_name?: string
}

export const getLeads = (params: { page?: number; size?: number; status?: string; keyword?: string }) => http.get('/leads', { params }) as Promise<{ total: number; list: LeadItem[] }>

export const createLead = (body: { customer_name: string; phone: string; source?: string; wedding_date?: string }) => http.post('/leads', body)

export const claimLead = (id: string) => http.put(`/leads/${id}/claim`)

export const deleteLead = (id: string) => http.delete(`/leads/${id}`)

