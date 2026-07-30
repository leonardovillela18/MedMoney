export type TaxStatus = 'Estimado' | 'Reservado' | 'Pago' | 'Ignorado'
export type TaxEstimation = {
  id: string
  base_calculo: number
  percentual: number
  valor_estimado: number
  tipo: string
  competencia: string
  status: TaxStatus
  observacoes?: string
}
export type TaxDashboard = {
  estimated_month: number
  reserved_total: number
  not_reserved: number
  estimated_net_profit: number
  gross_month: number
  coverage: number
  series: { month: string; gross: number; tax: number; net: number }[]
  insights: string[]
  disclaimer: string
}
export type TaxPageData = {
  items: TaxEstimation[]
  total: number
  page: number
  page_size: number
}
export type Simulation = {
  receita: number
  percentual: number
  reserva_sugerida: number
  disponivel_apos_reserva: number
  disclaimer: string
}
export type TaxSettings = {
  simples_nacional: boolean | null
  simples_annex: 'III' | 'V' | 'OTHER' | 'UNKNOWN'
  fator_r: number | null
  rbt12: number | null
  das_effective_percentage: number | null
  iss_effective_percentage: number | null
  has_separate_darfs: boolean
  separate_darfs: ('IRRF' | 'INSS' | 'CSLL' | 'PIS' | 'COFINS' | 'OUTRO')[]
  recommended_reserve_percentage: number
  effective_from: string | null
  accountant_notes: string | null
  disclaimer: string
}
