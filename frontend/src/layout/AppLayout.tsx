import {
  Building2,
  BarChart3,
  BellRing,
  CalendarDays,
  ChartNoAxesCombined,
  FileText,
  LayoutDashboard,
  Lightbulb,
  LogOut,
  Menu,
  Receipt,
  Settings,
  Target,
  WalletCards,
  X,
} from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertBadge } from '@/components/alerts/AlertBadge'
import { alertsService } from '@/services/alerts'
import { cn } from '@/lib/utils'
const items = [
  ['/dashboard', 'Meu Dia', LayoutDashboard],
  ['/contratantes', 'Contratantes', Building2],
  ['/plantoes', 'Plantões', CalendarDays],
  ['/financeiro', 'Financeiro', WalletCards],
  ['/fluxo-de-caixa', 'Fluxo de Caixa', ChartNoAxesCombined],
  ['/despesas', 'Despesas', Receipt],
  ['/notas-fiscais', 'Notas Fiscais', FileText],
  ['/impostos', 'Impostos', FileText],
  ['/insights', 'Insights', Lightbulb],
  ['/analytics', 'Analytics', BarChart3],
  ['/metas', 'Metas', Target],
  ['/alertas', 'Alertas', BellRing],
  ['/calendario', 'Calendário', CalendarDays],
  ['/configuracoes', 'Configurações', Settings],
] as const
export function AppLayout() {
  const { user, logout } = useAuth(),
    [open, setOpen] = useState(false),
    [criticalToast, setCriticalToast] = useState(false)
  const alerts = useQuery({
    queryKey: ['alerts-dashboard'],
    queryFn: alertsService.dashboard,
    staleTime: 15_000,
    refetchInterval: 30_000,
  })
  useEffect(() => {
    const count = alerts.data?.counts.Crítica ?? 0
    const previous = Number(localStorage.getItem('medmoney_critical_alerts') ?? 0)
    if (count > previous) {
      setCriticalToast(true)
      const timer = window.setTimeout(() => setCriticalToast(false), 4000)
      localStorage.setItem('medmoney_critical_alerts', String(count))
      return () => window.clearTimeout(timer)
    }
    localStorage.setItem('medmoney_critical_alerts', String(count))
  }, [alerts.data?.counts.Crítica])
  const side = (
    <aside className="flex h-full w-64 flex-col border-r bg-white p-4">
      <div className="mb-8 px-2 text-xl font-bold text-slate-900">
        <span className="text-blue-600">Med</span>Money
      </div>
      <nav className="space-y-1">
        {items.map(([path, label, Icon]) => (
          <NavLink
            onClick={() => setOpen(false)}
            key={path}
            to={path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-900',
                isActive && 'bg-blue-50 text-blue-700'
              )
            }
          >
            <Icon size={18} />
            <span className="flex-1">{label}</span>
            {path === '/alertas' && <AlertBadge count={alerts.data?.unread ?? 0} />}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto border-t pt-4">
        <NavLink
          to="/perfil"
          className="flex items-center gap-3 rounded-lg p-2 hover:bg-slate-50"
        >
          <div className="grid h-8 w-8 place-items-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
            {user?.name.slice(0, 2).toUpperCase()}
          </div>
          <span className="min-w-0 flex-1 truncate text-sm font-medium">
            {user?.name}
          </span>
        </NavLink>
        <button
          onClick={() => void logout()}
          className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-500 hover:bg-slate-50"
        >
          <LogOut size={18} />
          Sair
        </button>
      </div>
    </aside>
  )
  return (
    <div className="min-h-screen">
      <a href="#main-content" className="sr-only z-[110] rounded bg-white p-3 focus:not-sr-only focus:fixed focus:left-3 focus:top-3">Ir para o conteúdo principal</a>
      {criticalToast && (
        <div className="fixed bottom-5 right-5 z-[70] rounded-xl bg-red-600 px-4 py-3 text-sm font-medium text-white shadow-xl">
          Um novo alerta crítico precisa da sua atenção.
        </div>
      )}
      <div className="hidden h-screen md:fixed md:inset-y-0 md:flex">
        {side}
      </div>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/30 md:hidden"
          onClick={() => setOpen(false)}
        />
      )}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 transition-transform md:hidden',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {side}
        <button
          className="absolute left-64 top-3 rounded bg-white p-2"
          onClick={() => setOpen(false)}
        >
          <X size={18} />
        </button>
      </div>
      <main id="main-content" tabIndex={-1} className="md:pl-64">
        <header className="flex h-16 items-center border-b bg-white px-5">
          <button aria-label="Abrir menu" className="md:hidden" onClick={() => setOpen(true)}>
            <Menu />
          </button>
          <div className="ml-auto text-sm text-slate-500">
            Olá, {user?.name.split(' ')[0]}
          </div>
        </header>
        <div className="p-5 sm:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
