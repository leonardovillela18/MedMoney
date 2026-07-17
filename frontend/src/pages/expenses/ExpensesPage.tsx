import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Coins, PiggyBank, Receipt, TrendingDown, Wallet } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { ExpenseCard } from '@/components/expenses/ExpenseCard'
import { ExpenseChart } from '@/components/expenses/ExpenseChart'
import { ExpenseTable } from '@/components/expenses/ExpenseTable'
import { CategoryCard } from '@/components/expenses/CategoryCard'
import { ExpenseTimeline } from '@/components/expenses/ExpenseTimeline'
import { expensesService } from '@/services/expenses'
const money = (n = 0) =>
  n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
export function ExpensesPage() {
  const qc = useQueryClient(),
    [status, setStatus] = useState(''),
    [toast, setToast] = useState('')
  const list = useQuery({
    queryKey: ['expenses', status],
    queryFn: () =>
      expensesService.list({ page_size: 50, status: status || undefined }),
    staleTime: 30_000,
  })
  const dash = useQuery({
    queryKey: ['expenses-dashboard'],
    queryFn: expensesService.dashboard,
    staleTime: 30_000,
  })
  const categories = useQuery({
    queryKey: ['expense-categories'],
    queryFn: expensesService.categories,
    staleTime: 300_000,
  })
  const remove = useMutation({
    mutationFn: expensesService.remove,
    onSuccess: async () => {
      await Promise.all([
        qc.invalidateQueries({ queryKey: ['expenses'] }),
        qc.invalidateQueries({ queryKey: ['expenses-dashboard'] }),
        qc.invalidateQueries({ queryKey: ['cashflow-projection'] }),
        qc.invalidateQueries({ queryKey: ['dashboard'] }),
      ])
      setToast('Despesa excluída e indicadores atualizados.')
      setTimeout(() => setToast(''), 2500)
    },
  })
  if (list.isLoading || dash.isLoading)
    return (
      <div className="grid gap-4 sm:grid-cols-3">
        {[1, 2, 3, 4, 5].map((x) => (
          <div className="h-32 animate-pulse rounded-xl bg-slate-100" key={x} />
        ))}
      </div>
    )
  const d = dash.data!,
    items = list.data?.items ?? []
  return (
    <div>
      <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-blue-600">
            Gestão Inteligente de Despesas
          </p>
          <h1 className="mt-1 text-2xl font-bold">
            Entenda seus custos em poucos segundos.
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Gastos, tendências e impacto financeiro atualizados automaticamente.
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/despesas/relatorios">
            <Button className="bg-white text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50">
              Relatórios
            </Button>
          </Link>
          <Link to="/despesas/categorias">
            <Button className="bg-white text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50">
              Categorias
            </Button>
          </Link>
          <Link to="/despesas/nova">
            <Button>Nova Despesa</Button>
          </Link>
        </div>
      </header>
      {toast && (
        <div className="fixed bottom-5 right-5 z-50 rounded-lg bg-emerald-600 p-3 text-sm text-white">
          {toast}
        </div>
      )}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <ExpenseCard
          label="Total gasto mês"
          value={money(d.total_month)}
          icon={Receipt}
          tone="red"
        />
        <ExpenseCard
          label="Despesas fixas"
          value={money(d.fixed)}
          icon={Wallet}
        />
        <ExpenseCard
          label="Despesas variáveis"
          value={money(d.variable)}
          icon={Coins}
          tone="amber"
        />
        <ExpenseCard
          label="Maior categoria"
          value={d.largest_category}
          icon={TrendingDown}
        />
        <ExpenseCard
          label="Economia estimada"
          value={money(d.estimated_savings)}
          icon={PiggyBank}
          tone="green"
        />
      </div>
      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <ExpenseChart data={d.categories} />
        <section className="card p-5">
          <h2 className="font-semibold">Inteligência de custos</h2>
          <div className="mt-4 space-y-3">
            {d.insights.map((x) => (
              <p
                className="rounded-lg bg-blue-50 p-3 text-sm text-blue-900"
                key={x}
              >
                {x}
              </p>
            ))}
          </div>
          <div className="mt-5 space-y-3">
            {d.categories.slice(0, 3).map((x) => (
              <CategoryCard
                key={x.name}
                name={x.name}
                value={x.value}
                total={d.total_month}
              />
            ))}
          </div>
        </section>
      </div>
      <div className="mt-5">
        <ExpenseTimeline items={items.filter((x) => x.status !== 'Pago')} />
      </div>
      <section className="card mt-5 overflow-hidden">
        <div className="flex flex-wrap justify-between gap-3 border-b p-5">
          <div>
            <h2 className="font-semibold">Despesas</h2>
            <p className="text-sm text-slate-500">
              {list.data?.total ?? 0} lançamentos.
            </p>
          </div>
          <select
            className="field mt-0 w-auto"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">Todos os status</option>
            {['Pendente', 'Pago', 'Atrasado', 'Cancelado'].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </div>
        <ExpenseTable
          items={items}
          categories={categories.data ?? []}
          onDelete={(id) => {
            if (confirm('Excluir esta despesa?')) remove.mutate(id)
          }}
        />
      </section>
    </div>
  )
}
