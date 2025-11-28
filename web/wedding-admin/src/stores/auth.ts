import { defineStore } from 'pinia'
import { loginApi, getMeApi } from '../api/modules/auth'

interface User {
  id: string
  name: string
  role: 'ADMIN' | 'MANAGER' | 'PLANNER' | 'VENDOR' | 'FINANCE'
  roles: string[]
}

interface AuthState {
  token: string | null
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({ token: localStorage.getItem('token'), user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null }),
  actions: {
    async login(username: string, password: string) {
      // 1. Get Token
      const tokenRes = await loginApi({ username, password })
      this.token = tokenRes.access_token
      localStorage.setItem('token', tokenRes.access_token)

      // 2. Get User Info
      try {
        const userRes = await getMeApi()
        // Map backend user to frontend user model
        // Use first role as primary role for backward compatibility
        const primaryRole = (userRes.roles && userRes.roles.length > 0) ? userRes.roles[0] : 'PLANNER'
        
        this.user = {
          id: userRes.id,
          name: userRes.username,
          role: primaryRole as any,
          roles: userRes.roles
        }
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch (e) {
        // If getting user info fails, clear token
        this.logout()
        throw e
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})

