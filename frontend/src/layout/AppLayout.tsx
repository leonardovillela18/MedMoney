import {
  Bell,
  BriefcaseMedical,
  Building2,
  CalendarDays,
  ChartNoAxesCombined,
  ChevronDown,
  FileText,
  LayoutDashboard,
  Lightbulb,
  LogOut,
  Menu,
  Receipt,
  Repeat2,
  Scissors,
  Settings,
  SlidersHorizontal,
  Stethoscope,
  Target,
  UserRound,
  Users,
  WalletCards,
} from 'lucide-react'
import { Navigate, NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertBadge } from '@/components/alerts/AlertBadge'
import { alertsService } from '@/services/alerts'
import { expensesService } from '@/services/expenses'
import { receivablesService } from '@/services/receivables'
import { cn } from '@/lib/utils'

type GroupId = 'servico' | 'administrativo' | 'gerenciamento'
type MenuItem = readonly [
  path: string,
  label: string,
  icon: typeof LayoutDashboard,
]
type MenuGroup = {
  id: GroupId
  label: string
  icon: typeof LayoutDashboard
  items: readonly MenuItem[]
}

const groups: readonly MenuGroup[] = [
  {
    id: 'servico',
    label: 'Serviço',
    icon: BriefcaseMedical,
    items: [
      ['/consultas', 'Consultas', Stethoscope],
      ['/plantoes', 'Plantões', CalendarDays],
      ['/cirurgias', 'Cirurgias', Scissors],
      ['/recebimentos-recorrentes', 'Recebimentos Recorrentes', Repeat2],
      ['/contratantes', 'Contratantes', Building2],
    ],
  },
  {
    id: 'administrativo',
    label: 'Administrativo',
    icon: FileText,
    items: [
      ['/notas-fiscais', 'Notas Fiscais', FileText],
      ['/impostos', 'Impostos', FileText],
      ['/metas', 'Metas', Target],
      ['/insights', 'Insights', Lightbulb],
    ],
  },
  {
    id: 'gerenciamento',
    label: 'Gerenciamento',
    icon: SlidersHorizontal,
    items: [
      ['/financeiro', 'Financeiro', WalletCards],
      ['/fluxo-de-caixa', 'Fluxo de Caixa', ChartNoAxesCombined],
      ['/despesas', 'Despesas', Receipt],
      ['/calendario', 'Calendário', CalendarDays],
    ],
  },
]

function groupForPath(pathname: string): GroupId | null {
  return (
    groups.find((group) =>
      group.items.some(([path]) => pathname.startsWith(path))
    )?.id ?? null
  )
}

export function AppLayout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const headerRef = useRef<HTMLDivElement>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [openGroup, setOpenGroup] = useState<GroupId | null>(() =>
    groupForPath(location.pathname)
  )
  const [headerPanel, setHeaderPanel] = useState<
    'account' | 'notifications' | null
  >(null)
  const [criticalToast, setCriticalToast] = useState(false)
  const queryClient = useQueryClient()
  const payExpense = useMutation({
    mutationFn: (id: string) => expensesService.pay(id),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['alerts-dashboard'] }),
        queryClient.invalidateQueries({ queryKey: ['today'] }),
        queryClient.invalidateQueries({ queryKey: ['expenses'] }),
        queryClient.invalidateQueries({ queryKey: ['financial-dashboard'] }),
      ])
    },
  })
  const confirmReceipt = useMutation({
    mutationFn: receivablesService.confirm,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['alerts-dashboard'] }),
        queryClient.invalidateQueries({ queryKey: ['today'] }),
        queryClient.invalidateQueries({ queryKey: ['financial-summary'] }),
        queryClient.invalidateQueries({ queryKey: ['recurring-income-occurrences'] }),
      ])
    },
  })
  const assistantAllowed = [
    '/dashboard',
    '/consultas',
    '/plantoes',
    '/cirurgias',
    '/contratantes',
    '/calendario',
  ]
  const alerts = useQuery({
    queryKey: ['alerts-dashboard'],
    queryFn: alertsService.dashboard,
    staleTime: 15_000,
    refetchInterval: 30_000,
    enabled: !user?.is_assistant,
  })

  useEffect(() => {
    const activeGroup = groupForPath(location.pathname)
    if (activeGroup) setOpenGroup(activeGroup)
  }, [location.pathname])

  useEffect(() => {
    const closePanels = (event: MouseEvent) => {
      if (!headerRef.current?.contains(event.target as Node))
        setHeaderPanel(null)
    }
    document.addEventListener('mousedown', closePanels)
    return () => document.removeEventListener('mousedown', closePanels)
  }, [])

  useEffect(() => {
    const count = alerts.data?.counts.Crítica ?? 0
    const previous = Number(
      localStorage.getItem('crmoney_critical_alerts') ?? 0
    )
    if (count > previous) {
      setCriticalToast(true)
      const timer = window.setTimeout(() => setCriticalToast(false), 4000)
      localStorage.setItem('crmoney_critical_alerts', String(count))
      return () => window.clearTimeout(timer)
    }
    localStorage.setItem('crmoney_critical_alerts', String(count))
  }, [alerts.data?.counts.Crítica])

  const navItem = ([path, label, Icon]: MenuItem, nested = false) => (
    <NavLink
      onClick={() => setMobileMenuOpen(false)}
      key={path}
      to={path}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-900',
          nested && 'ml-4 border-l border-slate-200 pl-4',
          isActive && 'bg-blue-50 text-blue-700'
        )
      }
    >
      <Icon size={18} />
      <span>{label}</span>
    </NavLink>
  )

  const side = (
    <aside className="flex h-full w-[min(16rem,calc(100vw-2.75rem))] flex-col border-r bg-white p-4 md:w-64">
      <div className="mb-8 px-2">
        <img src="/img/Logo_vazada.png" alt="CRMoney" className="h-auto w-48" />
      </div>
      <nav className="space-y-1 overflow-y-auto pb-4">
        {navItem(['/dashboard', 'Meu Dia', LayoutDashboard])}
        {(user?.is_assistant ? groups.slice(0, 1) : groups).map((group) => {
          const GroupIcon = group.icon
          const expanded = openGroup === group.id
          const active = group.items.some(([path]) =>
            location.pathname.startsWith(path)
          )
          return (
            <div key={group.id}>
              <button
                type="button"
                aria-expanded={expanded}
                onClick={() => setOpenGroup(expanded ? null : group.id)}
                className={cn(
                  'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-900',
                  active && 'text-blue-700'
                )}
              >
                <GroupIcon size={18} />
                <span className="flex-1">{group.label}</span>
                <ChevronDown
                  size={16}
                  className={cn(
                    'transition-transform',
                    expanded && 'rotate-180'
                  )}
                />
              </button>
              <div
                className={cn(
                  'grid transition-all duration-200',
                  expanded
                    ? 'grid-rows-[1fr] opacity-100'
                    : 'grid-rows-[0fr] opacity-0'
                )}
              >
                <div className="overflow-hidden py-1">
                  {group.items.map((item) => navItem(item, true))}
                </div>
              </div>
            </div>
          )
        })}
        {user?.is_assistant &&
          navItem(['/calendario', 'Calendário', CalendarDays])}
        {!user?.is_assistant && navItem(['/auxiliares', 'Auxiliares', Users])}
        {!user?.is_assistant &&
          navItem(['/configuracoes', 'Configurações', Settings])}
        {user?.is_admin && navItem(['/usuarios', 'Usuários', Users])}
      </nav>
      <button
        onClick={() => void logout()}
        className="mt-auto flex w-full items-center gap-3 border-t px-3 pt-4 text-sm text-slate-500 hover:text-slate-900"
      >
        <LogOut size={18} />
        Sair
      </button>
    </aside>
  )

  if (
    user?.is_assistant &&
    !assistantAllowed.some((path) => location.pathname.startsWith(path))
  )
    return <Navigate to="/dashboard" replace />

  return (
    <div className="min-h-screen bg-[var(--app-bg)]">
      <a
        href="#main-content"
        className="sr-only z-[110] rounded bg-white p-3 focus:not-sr-only focus:fixed focus:left-3 focus:top-3"
      >
        Ir para o conteúdo principal
      </a>
      {criticalToast && (
        <div className="fixed inset-x-3 bottom-3 z-[70] rounded-xl bg-red-600 px-4 py-3 text-sm font-medium text-white shadow-xl sm:inset-x-auto sm:bottom-5 sm:right-5">
          Um novo alerta crítico precisa da sua atenção.
        </div>
      )}

      <div className="hidden h-screen md:fixed md:inset-y-0 md:flex">
        {side}
      </div>
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 transition-transform md:hidden',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {side}
      </div>

      <main id="main-content" tabIndex={-1} className="md:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center border-b bg-white/95 px-5 shadow-sm backdrop-blur">
          <button
            aria-label="Abrir menu"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(true)}
          >
            <Menu />
          </button>
          <img
            src="/img/Logo_vazada.png"
            alt="CRMoney"
            className="ml-3 hidden h-8 w-auto min-[380px]:block md:hidden"
          />

          <div
            ref={headerRef}
            className="relative ml-auto flex items-center gap-2"
          >
            <div className="relative">
              <button
                type="button"
                aria-label="Abrir notificações"
                aria-expanded={headerPanel === 'notifications'}
                onClick={() =>
                  setHeaderPanel(
                    headerPanel === 'notifications' ? null : 'notifications'
                  )
                }
                className="relative grid h-10 w-10 place-items-center rounded-full text-slate-500 hover:bg-slate-100 hover:text-slate-900"
              >
                <Bell size={20} />
                <span className="absolute -right-1 -top-1">
                  <AlertBadge count={alerts.data?.unread ?? 0} />
                </span>
              </button>
              {headerPanel === 'notifications' && (
                <div className="absolute right-0 top-12 w-[min(22rem,calc(100vw-2rem))] rounded-xl border bg-white p-3 shadow-xl">
                  <div className="flex items-center justify-between border-b px-1 pb-3">
                    <p className="font-semibold text-slate-900">Notificações</p>
                    <span className="text-xs text-slate-500">
                      {alerts.data?.unread ?? 0} não lidas
                    </span>
                  </div>
                  <div className="max-h-72 overflow-y-auto py-2">
                    {alerts.data?.highlights.length ? (
                      alerts.data.highlights.slice(0, 4).map((alert) => {
                        const expenseId = alert.referencia_id.startsWith('expense-due:')
                          ? alert.referencia_id.slice('expense-due:'.length)
                          : null
                        const receivableId = alert.referencia_id.startsWith('due-today:')
                          ? alert.referencia_id.slice('due-today:'.length)
                          : null
                        return <div key={alert.id} className="rounded-lg px-3 py-2.5 hover:bg-slate-50">
                          <NavLink to={alert.url_destino || `/alertas/${alert.id}`} onClick={() => setHeaderPanel(null)}>
                          <p className="text-sm font-medium text-slate-800">
                            {alert.titulo}
                          </p>
                          <p className="mt-1 line-clamp-2 text-xs text-slate-500">
                            {alert.descricao}
                          </p>
                          </NavLink>
                          {expenseId && <div className="mt-2 flex gap-2 text-xs font-semibold"><button disabled={payExpense.isPending} onClick={() => payExpense.mutate(expenseId)} className="rounded bg-emerald-600 px-2 py-1 text-white">Pago</button><button onClick={() => setHeaderPanel(null)} className="rounded border px-2 py-1 text-slate-600">Pendente</button></div>}
                          {receivableId && <div className="mt-2 flex gap-2 text-xs font-semibold"><button disabled={confirmReceipt.isPending} onClick={() => confirmReceipt.mutate(receivableId)} className="rounded bg-emerald-600 px-2 py-1 text-white">Sim, recebi</button><button onClick={() => setHeaderPanel(null)} className="rounded border px-2 py-1 text-slate-600">Ainda não</button></div>}
                        </div>
                      })
                    ) : (
                      <p className="px-3 py-8 text-center text-sm text-slate-400">
                        Nenhuma notificação no momento.
                      </p>
                    )}
                  </div>
                  <NavLink
                    to="/alertas"
                    onClick={() => setHeaderPanel(null)}
                    className="block border-t pt-3 text-center text-sm font-semibold text-blue-600"
                  >
                    Ver todas as notificações
                  </NavLink>
                </div>
              )}
            </div>

            <div className="relative">
              <button
                type="button"
                aria-label="Abrir informações da conta"
                aria-expanded={headerPanel === 'account'}
                onClick={() =>
                  setHeaderPanel(headerPanel === 'account' ? null : 'account')
                }
                className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-slate-100"
              >
                <span className="grid h-9 w-9 place-items-center rounded-full bg-blue-100 text-blue-700">
                  <UserRound size={19} />
                </span>
                <span className="hidden sm:block">
                  <span className="block max-w-44 truncate text-sm font-semibold text-slate-800">
                    {user?.is_assistant ? 'Auxiliar' : 'Dr(a).'} {user?.name}
                  </span>
                  <span className="block text-xs text-slate-500">
                    {user?.is_assistant
                      ? `Dr(a). ${user.doctor_name}`
                      : user?.specialty}
                  </span>
                </span>
                <ChevronDown
                  size={15}
                  className="hidden text-slate-400 sm:block"
                />
              </button>
              {headerPanel === 'account' && (
                <div className="absolute right-0 top-12 w-[min(20rem,calc(100vw-1rem))] rounded-xl border bg-white p-4 shadow-xl">
                  <div className="flex items-center gap-3 border-b pb-4">
                    <span className="grid h-11 w-11 place-items-center rounded-full bg-blue-100 font-bold text-blue-700">
                      {user?.name.slice(0, 2).toUpperCase()}
                    </span>
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-slate-900">
                        {user?.name}
                      </p>
                      <p className="truncate text-xs text-slate-500">
                        {user?.email}
                      </p>
                    </div>
                  </div>
                  <dl className="space-y-3 py-4 text-sm">
                    <div className="flex gap-3">
                      <Stethoscope
                        size={17}
                        className="mt-0.5 text-slate-400"
                      />
                      <div>
                        <dt className="text-xs text-slate-400">CRM</dt>
                        <dd className="text-slate-700">
                          {user?.crm} / {user?.crm_uf}
                        </dd>
                      </div>
                    </div>
                    <div>
                      <dt className="text-xs text-slate-400">Especialidade</dt>
                      <dd className="text-slate-700">{user?.specialty}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate-400">Localização</dt>
                      <dd className="text-slate-700">
                        {user?.city} / {user?.state}
                      </dd>
                    </div>
                  </dl>
                  <NavLink
                    to="/configuracoes"
                    onClick={() => setHeaderPanel(null)}
                    className="block rounded-lg bg-blue-50 px-3 py-2 text-center text-sm font-semibold text-blue-700"
                  >
                    Ver informações da conta
                  </NavLink>
                  <button
                    onClick={() => void logout()}
                    className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-500 hover:bg-slate-50"
                  >
                    <LogOut size={16} />
                    Sair
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>
        <div className="min-w-0 p-3 min-[380px]:p-4 sm:p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
