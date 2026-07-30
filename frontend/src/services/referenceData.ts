import { api } from '@/services/api'
import type {
  CityOption,
  MedicalSpecialty,
  StateOption,
  UserSpecialties,
} from '@/types/referenceData'
export const referenceDataService = {
  states: () => api.get<StateOption[]>('/locations/states').then((r) => r.data),
  cities: (state: string, search: string) =>
    api
      .get<CityOption[]>('/locations/cities', {
        params: { state, search, limit: 50 },
      })
      .then((r) => r.data),
  specialties: () =>
    api.get<MedicalSpecialty[]>('/medical-specialties').then((r) => r.data),
  mySpecialties: () =>
    api.get<UserSpecialties>('/users/me/specialties').then((r) => r.data),
  saveSpecialties: (primary_id: string, secondary_id?: string) =>
    api
      .put<UserSpecialties>('/users/me/specialties', {
        primary_id,
        secondary_id: secondary_id || null,
      })
      .then((r) => r.data),
}
