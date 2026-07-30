export const LAST_ACTIVITY_KEY = 'crmoney_last_activity'
export const AUTH_EVENT_KEY = 'crmoney_auth_event'
export const idleTimeoutMs =
  Number(import.meta.env.VITE_SESSION_IDLE_TIMEOUT_MINUTES ?? 15) * 60_000
export const lastActivity = () =>
  Number(localStorage.getItem(LAST_ACTIVITY_KEY) ?? Date.now())
export const recordActivity = () =>
  localStorage.setItem(LAST_ACTIVITY_KEY, String(Date.now()))
export const isIdle = () => Date.now() - lastActivity() >= idleTimeoutMs
