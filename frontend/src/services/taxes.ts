import { api } from '@/services/api'
import type {
  Simulation,
  TaxDashboard,
  TaxPageData,
  TaxStatus,
  TaxSettings,
} from '@/types/tax'
export const taxesService = {
  dashboard: () =>
    api.get<TaxDashboard>('/taxes/dashboard').then((r) => r.data),
  history: () =>
    api
      .get<TaxPageData>('/taxes', { params: { page_size: 100 } })
      .then((r) => r.data),
  simulate: (receita: number, percentual: number) =>
    api
      .post<Simulation>('/taxes/simulate', { receita, percentual })
      .then((r) => r.data),
  update: (id: string, data: { status?: TaxStatus; observacoes?: string }) =>
    api.put(`/taxes/${id}`, data).then((r) => r.data),
  settings: () => api.get<TaxSettings>('/taxes/settings').then((r) => r.data),
  saveSettings: (settings: Omit<TaxSettings, 'disclaimer'>) =>
    api.put<TaxSettings>('/taxes/settings', settings).then((r) => r.data),
}
