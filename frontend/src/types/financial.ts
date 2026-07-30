export type FinancialSummary = {
  current_balance: number
  forecast_balance: number
  receivable: number
  payable: number
  tax_reserve_suggested: number
  tax_reserve_effective: number
  available: number
  month_inflows: number
  month_outflows: number
  month_result: number
}
export type FinancialAccount = {
  id: string
  account_name: string
  institution_name?: string
  account_type: string
  last4?: string
  status: string
  is_default: boolean
  balance: number
}
