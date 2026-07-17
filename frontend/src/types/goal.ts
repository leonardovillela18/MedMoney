export type Goal = {
  id: string
  titulo: string
  descricao?: string
  tipo: string
  valor_meta: number
  valor_atual: number
  percentual: number
  data_inicio: string
  data_final: string
  status: string
  cor: string
  icone: string
  created_at: string
  updated_at: string
}
export type GoalPageData = {
  items: Goal[]
  total: number
  page: number
  page_size: number
}
export type GoalDetail = {
  goal: Goal
  insight: string
  comparisons: { label: string; value: number }[]
  forecast: {
    remaining: number
    days_remaining: number
    forecast_date?: string
    forecast_days?: number
    daily_pace: number
    required_daily_pace: number
    on_track: boolean
  }
  history: { date: string; value: number; percentage: number }[]
}
export type GoalDashboard = {
  active: number
  completed: number
  closest?: Goal
  farthest?: Goal
  goals: Goal[]
}
