import { http } from '../http'

export interface User {
  id: string
  username: string
  is_active: boolean
  roles: string[]
  permissions: string[]
}

export interface UserCreate {
  username: string
  password?: string
  is_active?: boolean
  roles: string[]
}

export interface UserUpdate {
  username?: string
  password?: string
  is_active?: boolean
  roles?: string[]
}

export const getUsers = (params?: { skip?: number; limit?: number; role?: string }): Promise<User[]> => {
  return http.get('/users/', { params })
}

export const createUser = (data: UserCreate): Promise<User> => {
  return http.post('/users/', data)
}

export const updateUser = (id: string, data: UserUpdate): Promise<User> => {
  return http.put(`/users/${id}`, data)
}

export const deleteUser = (id: string): Promise<void> => {
  return http.delete(`/users/${id}`)
}

export interface Role {
  code: string
  name: string
}

export const getRoles = (): Promise<Role[]> => {
  return http.get('/users/roles')
}
