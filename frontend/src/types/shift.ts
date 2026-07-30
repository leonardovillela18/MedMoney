export type Shift = {
  id: string
  contractor_id: string
  title?: string
  type: string
  specialty?: string
  specialty_id?: string
  hospital_sector?: string
  city?: string
  city_ibge_code?: string
  state?: string
  date: string
  start_time: string
  end_time: string
  duration_hours: number
  gross_value: number
  estimated_net_value: number
  tax_reserve_percentage?: number
  tax_treatment: 'PJ_TAXABLE' | 'NON_PJ' | 'CUSTOM'
  status: string
  payment_method?: string
  expected_payment_date?: string
  notes?: string
}
export type ShiftPage = {
  items: Shift[]
  total: number
  page: number
  page_size: number
}
