import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { authService } from '@/services/auth'
import type { AuthTokens, User } from '@/types/auth'
import { AUTH_EVENT_KEY, recordActivity } from '@/lib/authActivity'
import { IdleSessionManager } from '@/components/security/IdleSessionManager'
type AuthContextValue = {
  user: User | null
  loading: boolean
  login: (email: string, password: string, keep: boolean) => Promise<void>
  register: (data: Record<string, string>) => Promise<void>
  logout: (reason?: 'idle') => Promise<void>
  logoutAll: () => Promise<void>
}
const AuthContext = createContext<AuthContextValue | null>(null)
const clear = () => {
  for (const store of [localStorage, sessionStorage]) {
    store.removeItem('crmoney_access_token')
    store.removeItem('crmoney_refresh_token')
  }
}
const save = (tokens: AuthTokens, persistent = true) => {
  clear()
  const store = persistent ? localStorage : sessionStorage
  store.setItem('crmoney_access_token', tokens.access_token)
  store.setItem('crmoney_refresh_token', tokens.refresh_token)
}
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState<User | null>(null),
    [loading, setLoading] = useState(true)
  useEffect(() => {
    const expired = (event?: Event) => {
      clear()
      queryClient.clear()
      setUser(null)
      if ((event as CustomEvent)?.detail === 'idle')
        sessionStorage.setItem(
          'crmoney_auth_notice',
          'Sua sessão expirou por inatividade. Faça login novamente.'
        )
    }
    const synchronizedLogout = (event: StorageEvent) => {
      if (event.key === AUTH_EVENT_KEY && event.newValue?.startsWith('logout:'))
        expired()
    }
    window.addEventListener('crmoney:auth-expired', expired)
    window.addEventListener('storage', synchronizedLogout)
    const load = async () => {
      const token =
        localStorage.getItem('crmoney_access_token') ||
        sessionStorage.getItem('crmoney_access_token')
      if (!token) {
        setLoading(false)
        return
      }
      try {
        setUser(await authService.me())
      } catch {
        clear()
      } finally {
        setLoading(false)
      }
    }
    void load()
    return () => {
      window.removeEventListener('crmoney:auth-expired', expired)
      window.removeEventListener('storage', synchronizedLogout)
    }
  }, [queryClient])
  const login = async (email: string, password: string, keep: boolean) => {
    const tokens = await authService.login(email, password)
    save(tokens, keep)
    recordActivity()
    setUser(await authService.me())
  }
  const register = async (data: Record<string, string>) => {
    const tokens = await authService.register(data)
    save(tokens)
    recordActivity()
    setUser(await authService.me())
  }
  const logout = useCallback(
    async (reason?: 'idle') => {
      const token =
        localStorage.getItem('crmoney_refresh_token') ||
        sessionStorage.getItem('crmoney_refresh_token')
      try {
        if (token) await authService.logout(token, reason)
      } finally {
        clear()
        queryClient.clear()
        setUser(null)
        localStorage.setItem(AUTH_EVENT_KEY, `logout:${Date.now()}`)
        if (reason === 'idle')
          sessionStorage.setItem(
            'crmoney_auth_notice',
            'Sua sessão expirou por inatividade. Faça login novamente.'
          )
      }
    },
    [queryClient]
  )
  const logoutAll = async () => {
    try {
      await authService.logoutAll()
    } finally {
      clear()
      queryClient.clear()
      setUser(null)
      localStorage.setItem(AUTH_EVENT_KEY, `logout:${Date.now()}`)
    }
  }
  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, logoutAll }}
    >
      {children}
      <IdleSessionManager active={!!user} logout={logout} />
    </AuthContext.Provider>
  )
}
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('AuthProvider ausente')
  return context
}
