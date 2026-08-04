import { api } from '@/services/api'

type Receivable = { id: string; remaining_balance: number }

export const receivablesService = {
  confirm: async (id: string) => {
    const item = await api.get<Receivable>(`/receivables/${id}`).then((r) => r.data)
    return api.post(`/receivables/${id}/receive`, {
      value: item.remaining_balance,
      date: new Date().toISOString().slice(0, 10),
      method: 'Outro',
    }).then((r) => r.data)
  },
}
