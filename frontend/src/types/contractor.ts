export const contractorTypes = [
  'Hospital',
  'Clínica',
  'UPA',
  'Santa Casa',
  'Consultório',
  'Prefeitura',
  'Cooperativa',
  'Empresa',
  'Plano de Saúde',
  'Outro',
] as const
export type ContractorType = (typeof contractorTypes)[number]
export interface Contractor {
  id: string
  name: string
  type: ContractorType
  cnpj?: string
  email?: string
  phone?: string
  mobile?: string
  site?: string
  zip_code?: string
  street?: string
  number?: string
  neighborhood?: string
  city?: string
  city_ibge_code?: string
  state?: string
  complement?: string
  primary_contact?: string
  contact_role?: string
  contact_phone?: string
  contact_email?: string
  payment_day?: string
  payment_term_days?: number
  default_shift_value?: number
  notes?: string
  active: boolean
}
export interface ContractorPage {
  items: Contractor[]
  total: number
  page: number
  page_size: number
}
