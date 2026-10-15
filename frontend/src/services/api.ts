import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const baseURL =
  import.meta.env.VITE_API_BASE_URL?.toString() || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const tokens = useAuthStore.getState().tokens
  if (tokens?.access_token) {
    config.headers.Authorization = `Bearer ${tokens.access_token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status as number | undefined
    const original = error?.config as
      | (Record<string, unknown> & {
          headers?: Record<string, string>
          _retry?: boolean
        })
      | undefined

    if (status === 401 && original && !original._retry) {
      const refreshToken = useAuthStore.getState().tokens?.refresh_token
      if (refreshToken) {
        original._retry = true
        try {
          const { data } = await axios.post(`${baseURL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const session = data?.data
          if (session?.tokens && session?.user) {
            useAuthStore.getState().setSession(session.user, session.tokens)
            original.headers = original.headers ?? {}
            original.headers.Authorization = `Bearer ${session.tokens.access_token}`
            return apiClient(original)
          }
        } catch {
          useAuthStore.getState().clearSession()
        }
      }
    }
    return Promise.reject(error)
  },
)
