import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { referenceDataService } from '@/services/referenceData'
export function SpecialtySelect({
  value,
  onChange,
  label = 'Especialidade',
  required = false,
  defaultToPrimary = false,
}: {
  value?: string
  onChange: (id?: string, name?: string) => void
  label?: string
  required?: boolean
  defaultToPrimary?: boolean
}) {
  const list = useQuery({
      queryKey: ['medical-specialties'],
      queryFn: referenceDataService.specialties,
      staleTime: 86_400_000,
    }),
    mine = useQuery({
      queryKey: ['my-specialties'],
      queryFn: referenceDataService.mySpecialties,
      staleTime: 300_000,
    })
  const preferred = [mine.data?.primary?.id, mine.data?.secondary?.id].filter(
    Boolean
  ) as string[]
  useEffect(() => {
    if (defaultToPrimary && !value && mine.data?.primary) {
      onChange(mine.data.primary.id, mine.data.primary.name)
    }
  }, [defaultToPrimary, mine.data?.primary, onChange, value])
  return (
    <label className="label">
      {label}
      <select
        required={required}
        className="field"
        value={value ?? ''}
        onChange={(e) => {
          const item = list.data?.find((x) => x.id === e.target.value)
          onChange(item?.id, item?.name)
        }}
      >
        <option value="">Não informada</option>
        {list.data
          ?.slice()
          .sort(
            (a, b) =>
              Number(preferred.includes(b.id)) -
                Number(preferred.includes(a.id)) || a.name.localeCompare(b.name)
          )
          .map((x) => (
            <option value={x.id} key={x.id}>
              {preferred.includes(x.id) ? '★ ' : ''}
              {x.name}
            </option>
          ))}
      </select>
    </label>
  )
}
