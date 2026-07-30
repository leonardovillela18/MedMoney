import { api } from './api'
import type { AuthTokens, User } from '@/types/auth'
export type Session = {
  id: string
  ip_address?: string
  user_agent?: string
  session_name?: string
  last_used_at?: string
  expires_at: string
  current: boolean
}
export const authService = {
  login: (email: string, password: string) =>
    api
      .post<AuthTokens>(
        '/auth/login',
        { email, password },
        { headers: { 'X-Device-Name': navigator.userAgent.slice(0, 100) } }
      )
      .then((r) => r.data),
  register: (data: Record<string, string>) =>
    api.post<AuthTokens>('/auth/register', data).then((r) => r.data),
  refresh: (refresh_token: string) =>
    api
      .post<AuthTokens>('/auth/refresh', { refresh_token })
      .then((r) => r.data),
  me: () => api.get<User>('/auth/me').then((r) => r.data),
  forgot: (email: string) =>
    api
      .post<{ message: string }>('/auth/forgot-password', { email })
      .then((r) => r.data),
  reset: (token: string, password: string) =>
    api.post('/auth/reset-password', { token, password }),
  changePassword: (current_password: string, new_password: string) =>
    api.post('/auth/change-password', { current_password, new_password }),
  logout: (refresh_token: string, reason?: 'idle') =>
    api.post('/auth/logout', { refresh_token, reason }),
  logoutAll: () => api.post('/auth/logout-all'),
  sessions: () => api.get<Session[]>('/auth/sessions').then((r) => r.data),
  revokeSession: (id: string) => api.delete(`/auth/sessions/${id}`),
}
