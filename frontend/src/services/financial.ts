import { api } from '@/services/api'
import type { FinancialAccount, FinancialSummary } from '@/types/financial'

export const financialService = {
  summary: (start?: string, end?: string) =>
    api
      .get<FinancialSummary>('/financial/summary', { params: { start, end } })
      .then((response) => response.data),
  accounts: () =>
    api
      .get<FinancialAccount[]>('/financial/accounts')
      .then((response) => response.data),
  createAccount: (data: Record<string, unknown>) =>
    api.post('/financial/accounts', data).then((response) => response.data),
  manual: (data: Record<string, unknown>) =>
    api
      .post('/financial/transactions/manual', data)
      .then((response) => response.data),
  transfer: (data: Record<string, unknown>) =>
    api.post('/financial/transfers', data).then((response) => response.data),
}
