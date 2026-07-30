export type StateOption = { uf: string; name: string }
export type CityOption = { ibge_code: string; name: string; state: string }
export type MedicalSpecialty = {
  id: string
  code: string
  name: string
  active: boolean
}
export type UserSpecialties = {
  primary?: { id: string; name: string }
  secondary?: { id: string; name: string }
}
