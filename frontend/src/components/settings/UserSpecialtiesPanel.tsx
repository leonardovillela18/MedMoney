import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Stethoscope } from 'lucide-react'
import { referenceDataService } from '@/services/referenceData'
import { Button } from '@/components/ui/Button'

export function UserSpecialtiesPanel() {
  const queryClient = useQueryClient()
  const specialties = useQuery({
    queryKey: ['medical-specialties'],
    queryFn: referenceDataService.specialties,
    staleTime: 86_400_000,
  })
  const mine = useQuery({
    queryKey: ['my-specialties'],
    queryFn: referenceDataService.mySpecialties,
  })
  const [primary, setPrimary] = useState('')
  const [secondary, setSecondary] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (mine.data) {
      setPrimary(mine.data.primary?.id ?? '')
      setSecondary(mine.data.secondary?.id ?? '')
    }
  }, [mine.data])

  const save = async () => {
    if (!primary || primary === secondary) {
      setMessage('Escolha uma principal e mantenha as duas diferentes.')
      return
    }
    await referenceDataService.saveSpecialties(primary, secondary || undefined)
    await queryClient.invalidateQueries({ queryKey: ['my-specialties'] })
    setMessage('Especialidades salvas.')
  }

  return (
    <section className="card p-6 sm:p-8">
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <Stethoscope size={19} /> Especialidades médicas
      </h2>
      <p className="mt-1 text-sm text-slate-500">
        A principal será sugerida primeiro ao cadastrar um compromisso.
      </p>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <SpecialtyField
          label="Principal *"
          value={primary}
          onChange={setPrimary}
        />
        <SpecialtyField
          label="Secundária"
          value={secondary}
          onChange={setSecondary}
          excluded={primary}
        />
      </div>
      {message && <p className="mt-3 text-sm text-slate-600">{message}</p>}
      <Button className="mt-5" type="button" onClick={save} disabled={!primary}>
        Salvar especialidades
      </Button>
    </section>
  )

  function SpecialtyField({
    label,
    value,
    onChange,
    excluded,
  }: {
    label: string
    value: string
    onChange: (value: string) => void
    excluded?: string
  }) {
    return (
      <label className="label">
        {label}
        <select
          className="field"
          value={value}
          onChange={(event) => onChange(event.target.value)}
        >
          <option value="">Não informada</option>
          {specialties.data
            ?.filter((item) => item.id !== excluded)
            .map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
        </select>
      </label>
    )
  }
}
