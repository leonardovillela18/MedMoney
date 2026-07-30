import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { contractorsService } from '@/services/contractors'
import { shiftsService } from '@/services/shifts'
import { taxesService } from '@/services/taxes'
import { Button } from '@/components/ui/Button'
import type { Shift } from '@/types/shift'
import { SpecialtySelect } from '@/components/common/SpecialtySelect'
export function SurgeryFormPage() {
  const { id } = useParams(),
    nav = useNavigate(),
    queryClient = useQueryClient(),
    [form, setForm] = useState<Partial<Shift>>({
      type: 'Cirurgia',
      status: 'Agendado',
      gross_value: 0,
      payment_method: 'PIX',
    }),
    [error, setError] = useState('')
  const { data: contractors } = useQuery({
    queryKey: ['contractors-surgery'],
    queryFn: () => contractorsService.list({ page: 1, page_size: 100 }),
  })
  const { data: taxSettings } = useQuery({
    queryKey: ['tax-settings'],
    queryFn: taxesService.settings,
  })
  const existing = useQuery({
    queryKey: ['surgery', id],
    enabled: !!id,
    queryFn: () => shiftsService.get(id!),
  })
  useEffect(() => {
    if (existing.data) setForm(existing.data)
  }, [existing.data])
  const set = (key: keyof Shift, value: unknown) =>
    setForm({ ...form, [key]: value })
  const percentage =
      form.tax_reserve_percentage ??
      (!id ? (taxSettings?.recommended_reserve_percentage ?? 15) : ''),
    numericPercentage = Number(percentage || 0),
    serviceValue = Number(form.gross_value ?? 0),
    reserve = (serviceValue * numericPercentage) / 100,
    available = serviceValue - reserve
  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setError('')
      await shiftsService.save(
        { ...form, type: 'Cirurgia' } as Omit<
          Shift,
          'id' | 'duration_hours' | 'estimated_net_value'
        >,
        id
      )
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['surgeries'] }),
        queryClient.invalidateQueries({ queryKey: ['surgery', id] }),
        queryClient.invalidateQueries({ queryKey: ['shifts'] }),
        queryClient.invalidateQueries({ queryKey: ['receivables'] }),
        queryClient.invalidateQueries({ queryKey: ['cashflow'] }),
        queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
      ])
      nav('/cirurgias')
    } catch {
      setError(
        'Não foi possível salvar. Confira hospital, data, horário e valor.'
      )
    }
  }
  return (
    <form onSubmit={save} className="mx-auto max-w-3xl">
      <div className="mb-8 flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">Agenda cirúrgica</p>
          <h1 className="text-2xl font-bold">
            {id ? 'Editar cirurgia' : 'Nova cirurgia'}
          </h1>
        </div>
        <Button>Salvar</Button>
      </div>
      <section className="card grid gap-5 p-4 min-[380px]:p-5 sm:grid-cols-2 sm:p-6">
        <Field label="Tipo da cirurgia *" wide>
          <input
            required
            className="field"
            value={form.title ?? ''}
            onChange={(e) => set('title', e.target.value)}
            placeholder="Ex.: Colecistectomia, cesariana..."
          />
        </Field>
        <Field label="Hospital / contratante *" wide>
          <select
            required
            className="field"
            value={form.contractor_id ?? ''}
            onChange={(e) => {
              const c = contractors?.items.find((x) => x.id === e.target.value)
              setForm({
                ...form,
                contractor_id: e.target.value,
                hospital_sector: c?.name,
                city: c?.city,
                city_ibge_code: c?.city_ibge_code,
                state: c?.state,
              })
            }}
          >
            <option value="">Selecione</option>
            {contractors?.items.map((c) => (
              <option value={c.id} key={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Especialidade">
          <SpecialtySelect
            value={form.specialty_id}
            defaultToPrimary={!id}
            onChange={(specialtyId, specialtyName) =>
              setForm({
                ...form,
                specialty_id: specialtyId,
                specialty: specialtyName,
              })
            }
          />
        </Field>
        <div className="rounded-lg bg-slate-50 p-3 text-sm">
          <p className="text-xs text-slate-500">Local selecionado</p>
          <p className="mt-1 font-medium">
            {form.hospital_sector || 'Selecione um contratante'}
          </p>
          {(form.city || form.state) && (
            <p className="mt-1 text-slate-500">
              {[form.city, form.state].filter(Boolean).join(' / ')}
            </p>
          )}
        </div>
        <Field label="Data *">
          <input
            required
            type="date"
            className="field"
            value={form.date ?? ''}
            onChange={(e) => set('date', e.target.value)}
          />
        </Field>
        <Field label="Horário inicial *">
          <input
            required
            type="time"
            className="field"
            value={form.start_time ?? ''}
            onChange={(e) => set('start_time', e.target.value)}
          />
        </Field>
        <Field label="Horário final *">
          <input
            required
            type="time"
            className="field"
            value={form.end_time ?? ''}
            onChange={(e) => set('end_time', e.target.value)}
          />
        </Field>
        <Field label="Honorários previstos">
          <input
            required
            min="1"
            type="number"
            className="field"
            value={form.gross_value || ''}
            onChange={(e) => set('gross_value', Number(e.target.value))}
          />
        </Field>
        <Field label="Alíquota de reserva tributária">
          <input
            required={!id}
            min="0"
            max="100"
            step="0.001"
            type="number"
            className="field"
            value={percentage}
            placeholder={id ? 'Não informada' : '15'}
            onChange={(e) =>
              set(
                'tax_reserve_percentage',
                e.target.value === '' ? undefined : Number(e.target.value)
              )
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
        <Field label="Pagamento previsto">
          <input
            required
            type="date"
            min={form.date}
            className="field"
            value={form.expected_payment_date ?? form.date ?? ''}
            onChange={(e) => set('expected_payment_date', e.target.value)}
          />
        </Field>
        <Field label="Forma de pagamento">
          <select
            className="field"
            value={form.payment_method ?? 'PIX'}
            onChange={(e) => set('payment_method', e.target.value)}
          >
            {['PIX', 'TED', 'Depósito', 'Transferência', 'Outro'].map(
              (method) => (
                <option key={method}>{method}</option>
              )
            )}
          </select>
        </Field>
        <Field label="Observações" wide>
          <textarea
            className="field min-h-28"
            value={form.notes ?? ''}
            onChange={(e) => set('notes', e.target.value)}
            placeholder="Equipe, preparo, materiais ou outras informações..."
          />
        </Field>
        <p className="sm:col-span-2 rounded-lg bg-amber-50 p-3 text-xs text-amber-900">
          Esta é uma estimativa para planejamento financeiro e não substitui a
          apuração tributária realizada pelo seu contador.
        </p>
      </section>
      {error && (
        <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}
    </form>
  )
}
function Field({
  label,
  wide,
  children,
}: {
  label: string
  wide?: boolean
  children: React.ReactNode
}) {
  return (
    <label className={wide ? 'label sm:col-span-2' : 'label'}>
      {label}
      {children}
    </label>
  )
}
