import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { isIdle } from '@/lib/authActivity'
const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'
export const api = axios.create({ baseURL, timeout: 20_000 })
const refreshClient = axios.create({ baseURL, timeout: 15_000 })
let refreshing: Promise<string> | null = null
const storage = () =>
  localStorage.getItem('crmoney_refresh_token') ? localStorage : sessionStorage
const clearAuth = () => {
  for (const store of [localStorage, sessionStorage]) {
    store.removeItem('crmoney_access_token')
    store.removeItem('crmoney_refresh_token')
  }
}
api.interceptors.request.use((config) => {
  const token =
    localStorage.getItem('crmoney_access_token') ||
    sessionStorage.getItem('crmoney_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['X-Request-ID'] = crypto.randomUUID()
  return config
})
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined
    if (
      error.response?.status !== 401 ||
      !original ||
      original._retry ||
      original.url?.includes('/auth/refresh')
    )
      throw error
    const token =
      localStorage.getItem('crmoney_refresh_token') ||
      sessionStorage.getItem('crmoney_refresh_token')
    if (!token) {
      clearAuth()
      window.dispatchEvent(new Event('crmoney:auth-expired'))
      throw error
    }
    if (isIdle()) {
      clearAuth()
      window.dispatchEvent(
        new CustomEvent('crmoney:auth-expired', { detail: 'idle' })
      )
      throw error
    }
    original._retry = true
    try {
      refreshing ??= refreshClient
        .post<{ access_token: string; refresh_token: string }>(
          '/auth/refresh',
          { refresh_token: token },
          { headers: { 'X-Device-Name': navigator.userAgent.slice(0, 100) } }
        )
        .then(({ data }) => {
          const store = storage()
          store.setItem('crmoney_access_token', data.access_token)
          store.setItem('crmoney_refresh_token', data.refresh_token)
          return data.access_token
        })
        .finally(() => {
          refreshing = null
        })
      const access = await refreshing
      original.headers.Authorization = `Bearer ${access}`
      return api(original)
    } catch (refreshError) {
      clearAuth()
      window.dispatchEvent(new Event('crmoney:auth-expired'))
      throw refreshError
    }
  }
)
