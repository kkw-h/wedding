import axios from 'axios'

const client = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || '/api',
  timeout: 10000
})

client.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err)
)

export default client