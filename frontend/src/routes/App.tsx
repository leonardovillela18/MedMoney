import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { FullPageLoader } from '@/components/common/FullPageLoader'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RegisterPage } from '@/pages/auth/RegisterPage'
import {
  ForgotPasswordPage,
  ResetPasswordPage,
} from '@/pages/auth/PasswordPages'
import { AppLayout } from '@/layout/AppLayout'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { ComingSoonPage } from '@/pages/dashboard/ComingSoonPage'
import { ContractorsPage } from '@/pages/contractors/ContractorsPage'
import { ContractorFormPage } from '@/pages/contractors/ContractorFormPage'
import { ContractorDetailPage } from '@/pages/contractors/ContractorDetailPage'
import { ShiftsPage } from '@/pages/shifts/ShiftsPage'
import { ShiftFormPage } from '@/pages/shifts/ShiftFormPage'
import { ShiftDetailPage } from '@/pages/shifts/ShiftDetailPage'
import { SettingsPage } from '@/pages/settings/SettingsPage'
import { CalendarPage } from '@/pages/calendar/CalendarPage'
import { SurgeriesPage } from '@/pages/surgeries/SurgeriesPage'
import { SurgeryFormPage } from '@/pages/surgeries/SurgeryFormPage'
import { SurgeryDetailPage } from '@/pages/surgeries/SurgeryDetailPage'
import { UsersPage } from '@/pages/admin/UsersPage'
import { AssistantsPage } from '@/pages/assistants/AssistantsPage'
import { ConsultationsPage } from '@/pages/consultations/ConsultationsPage'
import { RecurringIncomesPage } from '@/pages/recurringIncomes/RecurringIncomesPage'
import { FinancialPage } from '@/pages/financial/FinancialPage'
const TaxesPage = lazy(() =>
  import('@/pages/taxes/TaxesPage').then((x) => ({ default: x.TaxesPage }))
)
const CashflowPage = lazy(() =>
  import('@/pages/cashflow/CashflowPage').then((x) => ({
    default: x.CashflowPage,
  }))
)
const ExpensesPage = lazy(() =>
  import('@/pages/expenses/ExpensesPage').then((x) => ({
    default: x.ExpensesPage,
  }))
)
const ExpenseFormPage = lazy(() =>
  import('@/pages/expenses/ExpenseFormPage').then((x) => ({
    default: x.ExpenseFormPage,
  }))
)
const ExpenseDetailPage = lazy(() =>
  import('@/pages/expenses/ExpenseDetailPage').then((x) => ({
    default: x.ExpenseDetailPage,
  }))
)
const ExpenseCategoriesPage = lazy(() =>
  import('@/pages/expenses/ExpenseCategoriesPage').then((x) => ({
    default: x.ExpenseCategoriesPage,
  }))
)
const ExpenseReportsPage = lazy(() =>
  import('@/pages/expenses/ExpenseReportsPage').then((x) => ({
    default: x.ExpenseReportsPage,
  }))
)
const InsightsPage = lazy(() =>
  import('@/pages/insights/InsightsPage').then((x) => ({
    default: x.InsightsPage,
  }))
)
const InsightDetailPage = lazy(() =>
  import('@/pages/insights/InsightDetailPage').then((x) => ({
    default: x.InsightDetailPage,
  }))
)
const AnalyticsPage = lazy(() =>
  import('@/pages/analytics/AnalyticsPage').then((x) => ({
    default: x.AnalyticsPage,
  }))
)
const GoalsPage = lazy(() =>
  import('@/pages/goals/GoalsPage').then((x) => ({ default: x.GoalsPage }))
)
const GoalFormPage = lazy(() =>
  import('@/pages/goals/GoalFormPage').then((x) => ({
    default: x.GoalFormPage,
  }))
)
const GoalDetailPage = lazy(() =>
  import('@/pages/goals/GoalDetailPage').then((x) => ({
    default: x.GoalDetailPage,
  }))
)
const AlertsPage = lazy(() =>
  import('@/pages/alerts/AlertsPage').then((x) => ({ default: x.AlertsPage }))
)
const AlertDetailPage = lazy(() =>
  import('@/pages/alerts/AlertDetailPage').then((x) => ({
    default: x.AlertDetailPage,
  }))
)
function Private({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <FullPageLoader />
  return user ? <>{children}</> : <Navigate to="/login" replace />
}
function Guest({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <FullPageLoader />
  return user ? <Navigate to="/dashboard" replace /> : <>{children}</>
}
function AdminOnly({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <FullPageLoader />
  return user?.is_admin ? <>{children}</> : <Navigate to="/dashboard" replace />
}
function DoctorOnly({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <FullPageLoader />
  return !user?.is_assistant ? (
    <>{children}</>
  ) : (
    <Navigate to="/dashboard" replace />
  )
}
const lazyPage = (page: React.ReactNode) => (
  <Suspense fallback={<FullPageLoader />}>{page}</Suspense>
)
export function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <Guest>
            <LoginPage />
          </Guest>
        }
      />
      <Route
        path="/cadastro"
        element={
          <Guest>
            <RegisterPage />
          </Guest>
        }
      />
      <Route path="/esqueci-senha" element={<ForgotPasswordPage />} />
      <Route path="/redefinir-senha" element={<ResetPasswordPage />} />
      <Route
        element={
          <Private>
            <AppLayout />
          </Private>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/contratantes" element={<ContractorsPage />} />
        <Route path="/contratantes/novo" element={<ContractorFormPage />} />
        <Route path="/contratantes/:id" element={<ContractorDetailPage />} />
        <Route
          path="/contratantes/:id/editar"
          element={<ContractorFormPage />}
        />
        <Route path="/plantoes" element={<ShiftsPage />} />
        <Route path="/plantoes/novo" element={<ShiftFormPage />} />
        <Route path="/plantoes/calendario" element={<CalendarPage />} />
        <Route path="/plantoes/:id" element={<ShiftDetailPage />} />
        <Route path="/plantoes/:id/editar" element={<ShiftFormPage />} />
        <Route path="/consultas" element={<ConsultationsPage />} />
        <Route path="/consultas/nova" element={<ShiftFormPage />} />
        <Route
          path="/recebimentos-recorrentes"
          element={
            <DoctorOnly>
              <RecurringIncomesPage />
            </DoctorOnly>
          }
        />
        <Route path="/impostos" element={lazyPage(<TaxesPage />)} />
        <Route path="/fluxo-de-caixa" element={lazyPage(<CashflowPage />)} />
        <Route
          path="/financeiro"
          element={
            <DoctorOnly>
              <FinancialPage />
            </DoctorOnly>
          }
        />
        <Route path="/despesas" element={lazyPage(<ExpensesPage />)} />
        <Route path="/despesas/nova" element={lazyPage(<ExpenseFormPage />)} />
        <Route
          path="/despesas/categorias"
          element={lazyPage(<ExpenseCategoriesPage />)}
        />
        <Route
          path="/despesas/relatorios"
          element={lazyPage(<ExpenseReportsPage />)}
        />
        <Route path="/despesas/:id" element={lazyPage(<ExpenseDetailPage />)} />
        <Route
          path="/despesas/:id/editar"
          element={lazyPage(<ExpenseFormPage />)}
        />
        <Route path="/insights" element={lazyPage(<InsightsPage />)} />
        <Route path="/insights/:id" element={lazyPage(<InsightDetailPage />)} />
        <Route path="/analytics" element={lazyPage(<AnalyticsPage />)} />
        <Route path="/metas" element={lazyPage(<GoalsPage />)} />
        <Route path="/metas/nova" element={lazyPage(<GoalFormPage />)} />
        <Route path="/metas/:id" element={lazyPage(<GoalDetailPage />)} />
        <Route path="/metas/:id/editar" element={lazyPage(<GoalFormPage />)} />
        <Route path="/alertas" element={lazyPage(<AlertsPage />)} />
        <Route path="/alertas/:id" element={lazyPage(<AlertDetailPage />)} />
        <Route path="/configuracoes" element={<SettingsPage />} />
        <Route
          path="/usuarios"
          element={
            <AdminOnly>
              <UsersPage />
            </AdminOnly>
          }
        />
        <Route
          path="/auxiliares"
          element={
            <DoctorOnly>
              <AssistantsPage />
            </DoctorOnly>
          }
        />
        <Route path="/calendario" element={<CalendarPage />} />
        <Route path="/cirurgias" element={<SurgeriesPage />} />
        <Route path="/cirurgias/nova" element={<SurgeryFormPage />} />
        <Route path="/cirurgias/:id" element={<SurgeryDetailPage />} />
        <Route path="/cirurgias/:id/editar" element={<SurgeryFormPage />} />
        {['notas-fiscais', 'perfil'].map((p) => (
          <Route key={p} path={'/' + p} element={<ComingSoonPage />} />
        ))}
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
