import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { referenceDataService } from '@/services/referenceData'
export function LocationFields({
  state,
  city,
  cityCode,
  onChange,
  required = false,
}: {
  state?: string
  city?: string
  cityCode?: string
  onChange: (value: {
    state?: string
    city?: string
    city_ibge_code?: string
  }) => void
  required?: boolean
}) {
  const [search, setSearch] = useState(city ?? ''),
    [debounced, setDebounced] = useState(city ?? '')
  useEffect(() => setSearch(city ?? ''), [city])
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(search), 300)
    return () => clearTimeout(timer)
  }, [search])
  const states = useQuery({
      queryKey: ['locations-states'],
      queryFn: referenceDataService.states,
      staleTime: 86_400_000,
    }),
    cities = useQuery({
      queryKey: ['locations-cities', state, debounced],
      queryFn: () => referenceDataService.cities(state!, debounced),
      enabled: !!state && debounced.length >= 2,
      staleTime: 3_600_000,
    })
  return (
    <>
      <label className="label">
        Estado
        <select
          required={required}
          className="field"
          value={state ?? ''}
          onChange={(e) => {
            setSearch('')
            onChange({
              state: e.target.value || undefined,
              city: undefined,
              city_ibge_code: undefined,
            })
          }}
        >
          <option value="">Selecione</option>
          {states.data?.map((x) => (
            <option value={x.uf} key={x.uf}>
              {x.name} ({x.uf})
            </option>
          ))}
        </select>
      </label>
      <label className="label relative">
        Cidade
        <input
          required={required}
          disabled={!state}
          autoComplete="off"
          className="field"
          value={search}
          placeholder={state ? 'Digite para buscar' : 'Escolha primeiro a UF'}
          onChange={(e) => {
            setSearch(e.target.value)
            onChange({ state, city: e.target.value, city_ibge_code: undefined })
          }}
        />
        {state && search.length >= 2 && !cityCode && cities.data && (
          <div className="absolute z-20 max-h-52 w-full overflow-y-auto rounded-lg border bg-white shadow-lg">
            {cities.data.map((x) => (
              <button
                type="button"
                className="block w-full px-3 py-2 text-left text-sm hover:bg-blue-50"
                key={x.ibge_code}
                onClick={() => {
                  setSearch(x.name)
                  onChange({
                    state: x.state,
                    city: x.name,
                    city_ibge_code: x.ibge_code,
                  })
                }}
              >
                {x.name}
              </button>
            ))}
          </div>
        )}
        {cityCode && (
          <small className="text-emerald-600">Cidade validada pelo IBGE</small>
        )}
      </label>
    </>
  )
}
