import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { expensesService } from '@/services/expenses'

export function ExpenseDetailPage() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  const query = useQuery({ queryKey: ['expense', id], queryFn: () => expensesService.get(id!) })
  const payment = useMutation({
    mutationFn: () => expensesService.pay(id!),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['expense', id] }),
        queryClient.invalidateQueries({ queryKey: ['expenses'] }),
        queryClient.invalidateQueries({ queryKey: ['expenses-dashboard'] }),
        queryClient.invalidateQueries({ queryKey: ['cashflow'] }),
        queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
      ])
    },
  })
  if (query.isLoading) return <div className="h-72 animate-pulse rounded-xl bg-slate-100" />
  const expense = query.data!
  const today = new Date().toISOString().slice(0, 10)
  const displayStatus = expense.status === 'Pendente' && expense.data_vencimento === today ? 'Vence hoje' : expense.status
  const details = {
    Valor: expense.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }),
    Fornecedor: expense.fornecedor || '—', Tipo: expense.tipo, Status: displayStatus,
    Pagamento: expense.forma_pagamento,
    Vencimento: new Date(`${expense.data_vencimento}T12:00`).toLocaleDateString('pt-BR'),
    'Centro de custo': expense.centro_custo || '—',
    Recorrência: expense.recorrente ? expense.intervalo_recorrencia || 'Sim' : 'Não',
  }
  return <div className="mx-auto max-w-3xl"><div className="mb-5 flex flex-wrap items-center justify-between gap-3"><h1 className="text-2xl font-bold">{expense.titulo}</h1><div className="flex gap-3">{expense.status !== 'Pago' && expense.status !== 'Cancelado' && <button disabled={payment.isPending} onClick={() => payment.mutate()} className="text-emerald-600">{payment.isPending ? 'Confirmando...' : 'Marcar como pago'}</button>}<Link className="text-blue-600" to={`/despesas/${id}/editar`}>Editar</Link></div></div><section className="card grid gap-5 p-6 sm:grid-cols-2">{Object.entries(details).map(([key, value]) => <div key={key}><p className="text-xs uppercase text-slate-400">{key}</p><p className="mt-1 font-medium">{value}</p></div>)}{expense.observacoes && <div className="sm:col-span-2"><p className="text-xs uppercase text-slate-400">Observações</p><p className="mt-1">{expense.observacoes}</p></div>}</section></div>
}
