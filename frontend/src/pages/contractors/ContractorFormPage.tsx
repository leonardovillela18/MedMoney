import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { useState } from 'react'
import { contractorsService } from '@/services/contractors'
import { contractorTypes, type Contractor } from '@/types/contractor'
import { Button } from '@/components/ui/Button'
const fields: [keyof Contractor, string, string?][] = [
  ['name', 'Nome *'],
  ['cnpj', 'CNPJ'],
  ['email', 'E-mail', 'email'],
  ['phone', 'Telefone'],
  ['mobile', 'Celular'],
  ['site', 'Site'],
  ['zip_code', 'CEP'],
  ['street', 'Rua'],
  ['number', 'Número'],
  ['neighborhood', 'Bairro'],
  ['city', 'Cidade'],
  ['state', 'Estado'],
  ['complement', 'Complemento'],
  ['primary_contact', 'Nome do responsável'],
  ['contact_role', 'Cargo'],
  ['contact_phone', 'Telefone do responsável'],
  ['contact_email', 'E-mail do responsável', 'email'],
  ['payment_term_days', 'Prazo médio de pagamento', 'number'],
  ['payment_day', 'Dia padrão do pagamento'],
]
export function ContractorFormPage() {
  const { id } = useParams(),
    nav = useNavigate(),
    [data, setData] = useState<Partial<Contractor>>({
      active: true,
      type: 'Hospital',
    }),
    [error, setError] = useState('')
  useQuery({
    queryKey: ['contractor', id],
    enabled: !!id,
    queryFn: () => contractorsService.get(id!),
    select: (item) => {
      setData(item)
      return item
    },
  })
  const set = (key: keyof Contractor, value: string) =>
    setData((d) => ({ ...d, [key]: value }))
  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setError('')
      const payload = {
        ...data,
        name: data.name ?? '',
        type: data.type ?? 'Hospital',
        payment_term_days: data.payment_term_days
          ? Number(data.payment_term_days)
          : undefined,
      } as Omit<Contractor, 'id'>
      if (id) {
        await contractorsService.update(id, payload)
      } else {
        await contractorsService.create(payload)
      }
      nav('/contratantes')
    } catch {
      setError(
        'Não foi possível salvar o contratante. Revise os campos e tente novamente.'
      )
    }
  }
  return (
    <form onSubmit={save} className="mx-auto max-w-4xl">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">Contratantes</p>
          <h1 className="mt-1 text-2xl font-bold">
            {id ? 'Editar contratante' : 'Novo contratante'}
          </h1>
        </div>
        <Button>Salvar contratante</Button>
      </div>
      {['Informações gerais', 'Endereço', 'Contato', 'Financeiro'].map(
        (section, index) => (
          <section key={section} className="card mb-5 p-5">
            <h2 className="mb-5 font-semibold">{section}</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {index === 0 && (
                <>
                  <div className="sm:col-span-2">
                    <label className="label">Tipo *</label>
                    <select
                      className="field"
                      value={data.type}
                      onChange={(e) => set('type', e.target.value)}
                    >
                      {contractorTypes.map((type) => (
                        <option key={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                  {fields.slice(0, 6).map(([key, label, type]) => (
                    <Field
                      key={key}
                      field={key}
                      label={label}
                      type={type}
                      data={data}
                      set={set}
                    />
                  ))}
                </>
              )}
              {index === 1 &&
                fields
                  .slice(6, 12)
                  .map(([key, label, type]) => (
                    <Field
                      key={key}
                      field={key}
                      label={label}
                      type={type}
                      data={data}
                      set={set}
                    />
                  ))}
              {index === 2 &&
                fields
                  .slice(12, 16)
                  .map(([key, label, type]) => (
                    <Field
                      key={key}
                      field={key}
                      label={label}
                      type={type}
                      data={data}
                      set={set}
                    />
                  ))}
              {index === 3 &&
                fields
                  .slice(16)
                  .map(([key, label, type]) => (
                    <Field
                      key={key}
                      field={key}
                      label={label}
                      type={type}
                      data={data}
                      set={set}
                    />
                  ))}
            </div>
          </section>
        )
      )}
      <section className="card p-5">
        <h2 className="mb-3 font-semibold">Observações</h2>
        <textarea
          className="field min-h-28"
          value={data.notes ?? ''}
          onChange={(e) => set('notes', e.target.value)}
        />
      </section>
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      <div className="mt-5 flex justify-end gap-3">
        <button
          type="button"
          onClick={() => nav('/contratantes')}
          className="text-sm"
        >
          Cancelar
        </button>
        <Button>Salvar contratante</Button>
      </div>
    </form>
  )
}
function Field({
  field,
  label,
  type,
  data,
  set,
}: {
  field: keyof Contractor
  label: string
  type?: string
  data: Partial<Contractor>
  set: (key: keyof Contractor, value: string) => void
}) {
  return (
    <div>
      <label className="label">{label}</label>
      <input
        required={field === 'name'}
        className="field"
        type={type}
        value={String(data[field] ?? '')}
        onChange={(e) => set(field, e.target.value)}
      />
    </div>
  )
}
