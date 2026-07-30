import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { contractorsService } from '@/services/contractors'
import { shiftsService } from '@/services/shifts'
import { taxesService } from '@/services/taxes'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/context/AuthContext'
import type { Shift } from '@/types/shift'
import { LocationFields } from '@/components/common/LocationFields'
import { SpecialtySelect } from '@/components/common/SpecialtySelect'

export function ShiftFormPage() {
  const { id } = useParams(),
    nav = useNavigate(),
    [params] = useSearchParams(),
    { user } = useAuth(),
    assistant = !!user?.is_assistant,
    qc = useQueryClient(),
    initializedId = useRef<string | undefined>(undefined)
  const [s, setS] = useState<Partial<Shift>>({
      type: params.get('type') || 'Plantão Presencial',
      status: 'Agendado',
      payment_method: 'PIX',
      gross_value: 0,
    }),
    [step, setStep] = useState(1),
    [error, setError] = useState('')
  const { data: contractors } = useQuery({
    queryKey: ['contractors'],
    queryFn: () => contractorsService.list({ page: 1, page_size: 100 }),
  })
  const { data: taxSettings } = useQuery({
    queryKey: ['tax-settings'],
    queryFn: taxesService.settings,
    enabled: !assistant,
  })
  const { data: existingShift, isLoading: isLoadingShift } = useQuery({
    queryKey: ['shift', id],
    enabled: !!id,
    queryFn: () => shiftsService.get(id!),
  })
  useEffect(() => {
    if (existingShift && initializedId.current !== id) {
      setS(existingShift)
      initializedId.current = id
    }
  }, [existingShift, id])
  const f = (k: keyof Shift) => (
    <input
      className="field"
      type={
        k === 'date' || k === 'expected_payment_date'
          ? 'date'
          : k.includes('time')
            ? 'time'
            : k.includes('value')
              ? 'number'
              : 'text'
      }
      value={String(s[k] ?? '')}
      onChange={(e) => setS({ ...s, [k]: e.target.value })}
    />
  )
  const selectContractor = (contractorId: string) => {
    const contractor = contractors?.items.find((x) => x.id === contractorId)
    setS((current) => ({
      ...current,
      contractor_id: contractorId,
      hospital_sector: contractor?.name,
      city: contractor?.city,
      city_ibge_code: contractor?.city_ibge_code,
      state: contractor?.state,
      gross_value: assistant
        ? 0
        : current.gross_value || contractor?.default_shift_value || 0,
    }))
  }
  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await shiftsService.save(
        { ...s, gross_value: assistant ? 0 : s.gross_value } as Omit<
          Shift,
          'id' | 'duration_hours' | 'estimated_net_value'
        >,
        id
      )
      await Promise.all([
        qc.invalidateQueries({ queryKey: ['shifts'] }),
        qc.invalidateQueries({ queryKey: ['shift', id] }),
        qc.invalidateQueries({ queryKey: ['receivables'] }),
        qc.invalidateQueries({ queryKey: ['cashflow'] }),
        qc.invalidateQueries({ queryKey: ['dashboard'] }),
      ])
      nav('/plantoes')
    } catch (saveError) {
      const detail = axios.isAxiosError(saveError)
        ? saveError.response?.data?.detail
        : undefined
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg).filter(Boolean).join(' ')
        : typeof detail === 'string'
          ? detail
          : ''
      setError(
        message || 'Não foi possível salvar o compromisso. Revise os dados.'
      )
    }
  }
  const steps = assistant ? [1, 3] : [1, 2, 3]
  const percentage =
      s.tax_reserve_percentage ??
      (!id ? (taxSettings?.recommended_reserve_percentage ?? 15) : ''),
    numericPercentage = Number(percentage || 0),
    serviceValue = Number(s.gross_value ?? 0),
    reserve = (serviceValue * numericPercentage) / 100,
    available = serviceValue - reserve
  if (id && isLoadingShift)
    return <div className="h-64 animate-pulse rounded-xl bg-slate-100" />
  return (
    <form onSubmit={save} className="mx-auto max-w-3xl">
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">
          {id ? 'Editar compromisso' : 'Novo compromisso'}
        </h1>
        <Button>Salvar</Button>
      </div>
      <div className="mb-5 flex gap-3 text-sm">
        {steps.map((n) => (
          <button
            type="button"
            key={n}
            onClick={() => setStep(n)}
            className={
              step === n ? 'font-bold text-blue-600' : 'text-slate-400'
            }
          >
            {n === 1 ? 'Agenda' : n === 2 ? 'Financeiro' : 'Observações'}
          </button>
        ))}
      </div>
      {step === 1 && (
        <section className="card grid gap-4 p-5 sm:grid-cols-2">
          <h2 className="font-semibold sm:col-span-2">Informações gerais</h2>
          <div className="sm:col-span-2">
            <label className="label">Contratante *</label>
            <select
              required
              className="field"
              value={s.contractor_id ?? ''}
              onChange={(e) => selectContractor(e.target.value)}
            >
              <option value="">Selecione</option>
              {contractors?.items.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <Field label="Título">{f('title')}</Field>
          <Field label="Tipo">
            <select
              className="field"
              value={s.type}
              onChange={(e) => setS({ ...s, type: e.target.value })}
            >
              {[
                'Plantão Presencial',
                'Plantão Sobreaviso',
                'Telemedicina',
                'Consulta',
                'Cirurgia',
                'Outro',
              ].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </Field>
          <div>
            <SpecialtySelect
              value={s.specialty_id}
              defaultToPrimary={!id}
              onChange={(specialtyId, specialtyName) =>
                setS({
                  ...s,
                  specialty_id: specialtyId,
                  specialty: specialtyName,
                })
              }
            />
          </div>
          <Field label="Ou digite uma especialidade">{f('specialty')}</Field>
          <Field label="Hospital / setor">{f('hospital_sector')}</Field>
          <LocationFields
            state={s.state}
            city={s.city}
            cityCode={s.city_ibge_code}
            onChange={(location) =>
              setS((current) => ({ ...current, ...location }))
            }
          />
          <Field label="Data *">{f('date')}</Field>
          <Field label="Início *">{f('start_time')}</Field>
          <Field label="Fim *">{f('end_time')}</Field>
        </section>
      )}
      {step === 2 && !assistant && (
        <section className="card grid gap-4 p-5 sm:grid-cols-2">
          <h2 className="font-semibold sm:col-span-2">Financeiro</h2>
          <Field label="Valor do serviço *">{f('gross_value')}</Field>
          <Field label="Alíquota de reserva tributária">
            <input
              className="field"
              type="number"
              min="0"
              max="100"
              step="0.001"
              value={percentage}
              placeholder={id ? 'Não informada' : '15'}
              onChange={(e) =>
                setS({
                  ...s,
                  tax_reserve_percentage:
                    e.target.value === '' ? undefined : Number(e.target.value),
                })
              }
            />
          </Field>
          <div>
            <p className="label">Reserva tributária sugerida</p>
            <p className="mt-2 font-semibold">
              {reserve.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL',
              })}
            </p>
          </div>
          <div>
            <p className="label">Disponível após reserva</p>
            <p className="mt-2 font-semibold">
              {available.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL',
              })}
            </p>
          </div>
          <Field label="Recebimento previsto">
            {f('expected_payment_date')}
          </Field>
          <p className="sm:col-span-2 rounded-lg bg-amber-50 p-3 text-xs text-amber-900">
            Esta é uma estimativa para planejamento financeiro e não substitui a
            apuração tributária realizada pelo seu contador.
          </p>
          <Field label="Forma de pagamento">
            <select
              className="field"
              value={s.payment_method}
              onChange={(e) => setS({ ...s, payment_method: e.target.value })}
            >
              {['PIX', 'TED', 'Depósito', 'Transferência', 'Outro'].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </Field>
        </section>
      )}
      {step === 3 && (
        <section className="card p-5">
          <h2 className="font-semibold">Observações</h2>
          <textarea
            className="field mt-4 min-h-36"
            value={s.notes ?? ''}
            onChange={(e) => setS({ ...s, notes: e.target.value })}
          />
        </section>
      )}
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      <div className="mt-5 flex justify-between">
        <button
          type="button"
          onClick={() => setStep(steps[Math.max(0, steps.indexOf(step) - 1)])}
        >
          Voltar
        </button>
        {step !== steps.at(-1) ? (
          <Button
            type="button"
            onClick={() => setStep(steps[steps.indexOf(step) + 1])}
          >
            Continuar
          </Button>
        ) : (
          <Button>Salvar compromisso</Button>
        )}
      </div>
    </form>
  )
}
function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <div>
      <label className="label">{label}</label>
      {children}
    </div>
  )
}
