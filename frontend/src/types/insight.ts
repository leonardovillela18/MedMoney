export type Insight = {
  id: string
  tipo: string
  titulo: string
  descricao: string
  categoria: string
  severidade: 'Informativo' | 'Atenção' | 'Crítico'
  status: 'Novo' | 'Visualizado' | 'Arquivado'
  prioridade: number
  acao_recomendada: string
  referencia: string
  created_at: string
  updated_at: string
  dismissed_at?: string
}
export type InsightPageData = {
  items: Insight[]
  total: number
  page: number
  page_size: number
}
export type InsightDashboard = {
  highlights: Insight[]
  counts: Record<string, number>
  total: number
  categories: Record<string, number>
  projections: {
    month_revenue: number
    month_profit: number
    taxes: number
    cashflow: number
    goal: number
    goal_progress: number
  }
}
