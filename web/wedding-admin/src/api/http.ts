import axios from 'axios'
import { useAuthStore } from '../stores/auth'

export const http = axios.create({ baseURL: import.meta.env.VITE_API_BASE as string })

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

http.interceptors.response.use(
  (resp) => {
    const data = resp.data
    if (data && typeof data === 'object' && 'code' in data) {
      if (data.code !== 200) {
        return Promise.reject({ code: data.code, message: data.message, data: data.data })
      }
      return data.data
    }
    return resp.data
  },
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      location.href = '/login'
    }
    return Promise.reject(err)
  }
)

