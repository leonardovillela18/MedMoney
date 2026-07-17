export type SeriesPoint = { label: string; value: number }
export type RankingPoint = { name: string; value: number }
export type AnalyticsExecutive = {
  kpis: Record<string, number | string>
  revenue: RevenueAnalytics
  expenses: ExpenseAnalytics
  profit: ProfitAnalytics
  tax: {
    estimated: number
    reserved: number
    effective_percentage: number
    monthly: SeriesPoint[]
  }
  comparisons: {
    label: string
    revenue: number
    shifts: number
    hours: number
  }[]
}
export type RevenueAnalytics = {
  monthly: SeriesPoint[]
  annual: SeriesPoint[]
  accumulated: SeriesPoint[]
  by_hospital: RankingPoint[]
  by_city: RankingPoint[]
  by_specialty: RankingPoint[]
  by_type: RankingPoint[]
  expected: number
  received: number
  overdue: number
  top_receivables: RankingPoint[]
}
export type ShiftAnalytics = {
  count: number
  hours: number
  by_hospital: RankingPoint[]
  by_city: RankingPoint[]
  by_weekday: RankingPoint[]
  by_hour: RankingPoint[]
  day: number
  night: number
  cancelled: number
  received: number
  heatmap: { day: number; hour: number; value: number; count: number }[]
  top: RankingPoint[]
}
export type ExpenseAnalytics = {
  total: number
  fixed: number
  variable: number
  by_category: RankingPoint[]
  by_supplier: RankingPoint[]
  monthly: SeriesPoint[]
  top: RankingPoint[]
}
export type ProfitAnalytics = {
  gross: number
  net: number
  net_margin: number
  operating_margin: number
  monthly: {
    label: string
    gross: number
    expenses: number
    taxes: number
    net: number
    margin: number
  }[]
}
export type ContractorAnalytics = {
  ranking: {
    id: string
    name: string
    revenue: number
    shifts: number
    average_ticket: number
    average_delay: number | null
    share: number
  }[]
}
