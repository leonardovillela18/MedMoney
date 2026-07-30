import { useQuery } from '@tanstack/react-query'
import { Building2, CircleDollarSign, Phone, UserRound } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { useState } from 'react'
import { contractorsService } from '@/services/contractors'
import { contractorTypes, type Contractor } from '@/types/contractor'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/context/AuthContext'
import { LocationFields } from '@/components/common/LocationFields'

export function ContractorFormPage() {
  const { id } = useParams(),
    nav = useNavigate(),
    { user } = useAuth(),
    assistant = !!user?.is_assistant,
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
  const set = (key: keyof Contractor, value: string | number | undefined) =>
    setData((d) => ({ ...d, [key]: value }))
  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setError('')
      const payload = {
        ...data,
        name: data.name?.trim() || '',
        type: data.type || 'Hospital',
        default_shift_value: assistant
          ? undefined
          : data.default_shift_value
            ? Number(data.default_shift_value)
            : undefined,
      } as Omit<Contractor, 'id'>
      if (id) await contractorsService.update(id, payload)
      else await contractorsService.create(payload)
      nav('/contratantes')
    } catch {
      setError('Não foi possível salvar. Informe pelo menos o nome do local.')
    }
  }
  return (
    <form onSubmit={save} className="mx-auto max-w-3xl">
      <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">
            Hospitais, clínicas e locais de trabalho
          </p>
          <h1 className="text-2xl font-bold">
            {id ? 'Editar local' : 'Novo local'}
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Cadastre apenas o necessário. Você poderá completar as informações
            depois.
          </p>
        </div>
        <Button>Salvar local</Button>
      </div>
      <section className="card p-5 sm:p-6">
        <div className="grid gap-5 sm:grid-cols-2">
          <label className="label sm:col-span-2">
            <span className="flex items-center gap-2">
              <Building2 size={16} />
              Nome do local *
            </span>
            <input
              autoFocus
              required
              className="field text-base"
              placeholder="Ex.: Hospital São Lucas"
              value={data.name ?? ''}
              onChange={(e) => set('name', e.target.value)}
            />
          </label>
          <label className="label">
            Tipo
            <select
              className="field"
              value={data.type}
              onChange={(e) => set('type', e.target.value)}
            >
              {contractorTypes.map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </label>
          <label className="label">
            <span className="flex items-center gap-2">
              <Phone size={15} />
              Telefone
            </span>
            <input
              className="field"
              placeholder="Opcional"
              value={data.phone ?? ''}
              onChange={(e) => set('phone', e.target.value)}
            />
          </label>
          <LocationFields
            state={data.state}
            city={data.city}
            cityCode={data.city_ibge_code}
            onChange={(location) =>
              setData((current) => ({ ...current, ...location }))
            }
          />
          <label className="label sm:col-span-2">
            <span className="flex items-center gap-2">
              <UserRound size={15} />
              Contato ou responsável
            </span>
            <input
              className="field"
              placeholder="Nome da pessoa de contato (opcional)"
              value={data.primary_contact ?? ''}
              onChange={(e) => set('primary_contact', e.target.value)}
            />
          </label>
          {!assistant && (
            <label className="label sm:col-span-2">
              <span className="flex items-center gap-2">
                <CircleDollarSign size={16} />
                Valor padrão por compromisso
              </span>
              <div className="relative">
                <span className="absolute left-3 top-3 text-sm text-slate-400">
                  R$
                </span>
                <input
                  min="0"
                  step="0.01"
                  type="number"
                  className="field pl-10"
                  placeholder="Opcional — será preenchido automaticamente"
                  value={data.default_shift_value ?? ''}
                  onChange={(e) =>
                    set(
                      'default_shift_value',
                      e.target.value ? Number(e.target.value) : undefined
                    )
                  }
                />
              </div>
              <span className="mt-1 block text-xs font-normal text-slate-400">
                Você ainda poderá alterar o valor em cada plantão, consulta ou
                cirurgia.
              </span>
            </label>
          )}
          <label className="label sm:col-span-2">
            Observações
            <textarea
              className="field min-h-24"
              placeholder="Setor, orientações de acesso ou outra informação útil..."
              value={data.notes ?? ''}
              onChange={(e) => set('notes', e.target.value)}
            />
          </label>
        </div>
      </section>
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      <div className="mt-5 flex justify-end gap-3">
        <button
          type="button"
          className="text-sm text-slate-500"
          onClick={() => nav('/contratantes')}
        >
          Cancelar
        </button>
        <Button>Salvar local</Button>
      </div>
    </form>
  )
}
