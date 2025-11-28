import { http } from '../http'

interface LoginBody { username: string; password: string }
interface TokenResp { access_token: string; token_type: string }
export interface UserInfo {
  id: string
  username: string
  roles: string[]
  is_active: boolean
  permissions: string[]
}

export const loginApi = (body: LoginBody): Promise<TokenResp> => {
  const formData = new URLSearchParams()
  formData.append('username', body.username)
  formData.append('password', body.password)
  
  return http.post('/auth/login/access-token', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export const getMeApi = (): Promise<UserInfo> => http.get('/users/me')


