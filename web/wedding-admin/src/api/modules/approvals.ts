import { http } from '../http'

export const createApproval = (body: { project_id: string; type: string; content: any }) => http.post('/approvals', body)

export const auditApproval = (id: string, body: { status: 'APPROVED' | 'REJECTED'; comment?: string }) => http.patch(`/approvals/${id}/audit`, body)

