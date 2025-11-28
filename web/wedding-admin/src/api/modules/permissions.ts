import { http } from '../http'

export interface Permission {
  id: string
  code: string
  name: string
  module: string
  description?: string
}

export const getPermissions = (): Promise<Permission[]> => {
  return http.get('/permissions/')
}

export const getPermissionMatrix = (): Promise<Record<string, string[]>> => {
  return http.get('/permissions/matrix')
}

export const updateRolePermissions = (role: string, permissions: string[]): Promise<void> => {
  return http.put(`/permissions/roles/${role}`, permissions)
}
