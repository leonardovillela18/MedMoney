import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  CalendarDays,
  Landmark,
  Receipt,
  Stethoscope,
  TrendingUp,
  Wallet,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { QuickActions } from '@/components/today/QuickActions'
import { RecentActivity } from '@/components/today/RecentActivity'
import { TodayAgenda } from '@/components/today/TodayAgenda'
import { TodayAlerts } from '@/components/today/TodayAlerts'
import { TodayGoals } from '@/components/today/TodayGoals'
import { TodayHeader } from '@/components/today/TodayHeader'
import { TodayInsights } from '@/components/today/TodayInsights'
import { TodayPayments } from '@/components/today/TodayPayments'
import { TodaySummary } from '@/components/today/TodaySummary'
import { InsightWidget } from '@/components/insights/InsightWidget'
import { AlertWidget } from '@/components/alerts/AlertWidget'
import { todayService } from '@/services/today'
import { insightsService } from '@/services/insights'
import { alertsService } from '@/services/alerts'
import type { TodayData } from '@/types/today'
const money = (n = 0) =>
  n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
function Skeleton() {
  return (
    <div className="space-y-5">
      <div className="h-20 w-2/3 animate-pulse rounded-xl bg-slate-100" />
      <div className="h-72 animate-pulse rounded-2xl bg-slate-200" />
      <div className="grid gap-4 sm:grid-cols-4">
        {[1, 2, 3, 4].map((x) => (
          <div className="h-28 animate-pulse rounded-xl bg-slate-100" key={x} />
        ))}
      </div>
    </div>
  )
}
function Metric({
  label,
  value,
  icon: Icon,
}: {
  label: string
  value: string
  icon: typeof Wallet
}) {
  return (
    <motion.article whileHover={{ y: -2 }} className="card p-4">
      <Icon size={17} className="text-blue-600" />
      <p className="mt-4 text-xs text-slate-400">{label}</p>
      <p className="mt-1 truncate font-semibold">{value}</p>
    </motion.article>
  )
}
function CompactChart({
  title,
  data,
}: {
  title: string
  data: { label: string; value: number }[]
}) {
  const max = Math.max(1, ...data.map((x) => Math.abs(x.value)))
  return (
    <section className="card p-5">
      <h3 className="text-sm font-semibold">{title}</h3>
      <div className="mt-5 flex h-28 items-end justify-around gap-3">
        {data.map((x) => (
          <div
            className="flex h-full flex-1 flex-col justify-end"
            key={x.label}
          >
            <div
              title={money(x.value)}
              className={`mx-auto w-full max-w-10 rounded-t ${x.value < 0 ? 'bg-red-300' : 'bg-blue-500'}`}
              style={{
                height: `${Math.max(4, (Math.abs(x.value) / max) * 90)}px`,
              }}
            />
            <p className="mt-2 truncate text-center text-[9px] text-slate-400">
              {x.label}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
function MiniCalendar({ items }: { items: TodayData['calendar'] }) {
  return (
    <section className="card p-5">
      <h2 className="font-semibold">Próximos 30 dias</h2>
      <div className="mt-4 grid grid-cols-7 gap-1">
        {Array.from({ length: 31 }, (_, i) => {
          const d = new Date()
          d.setDate(d.getDate() + i)
          const key = d.toISOString().slice(0, 10),
            events = items.filter((x) => x.date === key)
          return (
            <div
              title={events.map((x) => `${x.type}: ${x.label}`).join('\n')}
              className={`grid aspect-square place-items-center rounded text-xs ${events.length ? 'bg-blue-600 font-semibold text-white' : 'bg-slate-50 text-slate-400'}`}
              key={key}
            >
              {d.getDate()}
            </div>
          )
        })}
      </div>
      <div className="mt-4 flex gap-3 text-[10px] text-slate-400">
        <span>Plantões</span>
        <span>Recebimentos</span>
        <span>Despesas</span>
      </div>
    </section>
  )
}
export function DashboardPage() {
  const { user } = useAuth()
  const q = useQuery({
    queryKey: ['today'],
    queryFn: todayService.get,
    staleTime: 30_000,
    refetchOnWindowFocus: true,
  })
  const insightQuery = useQuery({
    queryKey: ['insights-dashboard'],
    queryFn: insightsService.dashboard,
    staleTime: 60_000,
  })
  const alertQuery = useQuery({
    queryKey: ['alerts-dashboard'],
    queryFn: alertsService.dashboard,
    staleTime: 15_000,
    refetchInterval: 30_000,
  })
  if (q.isLoading) return <Skeleton />
  const d = q.data!
  const i = d.indicators
  const cash = d.charts.cashflow.map((x) => ({
    label: x.date.slice(5),
    value: x.balance,
  }))
  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <TodayHeader
        name={user?.name ?? 'Doutor'}
        date={d.date}
        message={d.message}
      />
      <div className="grid gap-5 xl:grid-cols-[1.35fr_.65fr]">
        <TodaySummary
          receivable={d.summary.receivable}
          tax={d.summary.tax_reserve_suggested}
          net={d.summary.estimated_net}
        />
        <section className="card p-5">
          <h2 className="font-semibold">Ações recomendadas</h2>
          <div className="mt-4 space-y-2">
            {d.actions.map((x) => (
              <Link
                className="flex items-center justify-between rounded-lg bg-slate-50 p-3 text-sm transition hover:bg-blue-50 hover:text-blue-700"
                to={x.href}
                key={x.label}
              >
                <span>{x.label}</span>
                <span>→</span>
              </Link>
            ))}
          </div>
        </section>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
        <Metric
          label="Receita do mês"
          value={money(Number(i.month_revenue))}
          icon={TrendingUp}
        />
        <Metric
          label="Lucro líquido"
          value={money(Number(i.net_profit))}
          icon={Wallet}
        />
        <Metric
          label="Plantões realizados"
          value={String(i.completed_shifts)}
          icon={Stethoscope}
        />
        <Metric
          label="Próximo pagamento"
          value={money(Number(i.next_payment))}
          icon={CalendarDays}
        />
        <Metric
          label="Próximo plantão"
          value={
            i.next_shift
              ? new Date(`${i.next_shift}T12:00`).toLocaleDateString('pt-BR')
              : 'Não agendado'
          }
          icon={CalendarDays}
        />
        <Metric
          label="Despesas do mês"
          value={money(Number(i.month_expenses))}
          icon={Receipt}
        />
        <Metric
          label="Reserva tributária"
          value={money(Number(i.tax_reserved))}
          icon={Landmark}
        />
      </div>
      <QuickActions />
      {insightQuery.data && <InsightWidget items={insightQuery.data.highlights} />}
      {alertQuery.data && <AlertWidget items={alertQuery.data.highlights} />}
      <div className="grid gap-5 lg:grid-cols-2">
        <TodayAgenda items={d.agenda} />
        <TodayPayments items={d.payments} />
      </div>
      <div className="grid gap-5 lg:grid-cols-3">
        <TodayAlerts items={d.alerts} />
        <TodayInsights items={d.insights} />
        <TodayGoals {...d.goal} format={money} />
      </div>
      <section>
        <div className="mb-3">
          <h2 className="font-semibold">Comparativo financeiro</h2>
          <p className="text-sm text-slate-500">
            Este mês, mês anterior e mesmo período do ano passado.
          </p>
        </div>
        <div className="overflow-x-auto rounded-xl border bg-white">
          <table className="w-full min-w-[650px] text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-400">
              <tr>
                <th className="p-3">Período</th>
                <th>Receita</th>
                <th>Lucro</th>
                <th>Horas</th>
                <th>Plantões</th>
              </tr>
            </thead>
            <tbody>
              {d.comparisons.map((x) => (
                <tr className="border-t" key={x.label}>
                  <td className="p-3 font-medium">{x.label}</td>
                  <td>{money(x.revenue)}</td>
                  <td>{money(x.profit)}</td>
                  <td>{x.hours}h</td>
                  <td>{x.shifts}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <div className="grid gap-5 lg:grid-cols-3">
        <CompactChart title="Receita" data={d.charts.revenue} />
        <CompactChart title="Lucro" data={d.charts.profit} />
        <CompactChart title="Fluxo de Caixa" data={cash} />
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <MiniCalendar items={d.calendar} />
        <RecentActivity items={d.activity} />
      </div>
    </div>
  )
}
