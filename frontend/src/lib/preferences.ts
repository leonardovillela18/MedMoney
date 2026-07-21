export type Preferences = { theme: 'light' | 'dark'; fontSize: 'normal' | 'large'; reduceMotion: boolean }
const key = 'medfinance_preferences'
export const defaultPreferences: Preferences = { theme: 'light', fontSize: 'normal', reduceMotion: false }
export function loadPreferences(): Preferences { try { return { ...defaultPreferences, ...JSON.parse(localStorage.getItem(key) ?? '{}') } } catch { return defaultPreferences } }
export function applyPreferences(value: Preferences) { const root=document.documentElement;root.dataset.theme=value.theme;root.dataset.fontSize=value.fontSize;root.dataset.reduceMotion=String(value.reduceMotion) }
export function savePreferences(value: Preferences) { localStorage.setItem(key,JSON.stringify(value));applyPreferences(value) }
