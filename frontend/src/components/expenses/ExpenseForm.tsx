import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { expensesService, type ExpensePayload } from '@/services/expenses'
import type { Category, Expense } from '@/types/expense'
const today = new Date().toISOString().slice(0, 10)
const empty: ExpensePayload = {
  titulo: '',
  descricao: '',
  categoria_id: '',
  valor: 0,
  tipo: 'Variável',
  forma_pagamento: 'PIX',
  fornecedor: '',
  competencia: today.slice(0, 8) + '01',
  data_vencimento: today,
  status: 'Pendente',
  recorrente: false,
  centro_custo: 'Administrativo',
  observacoes: '',
}
export function ExpenseForm({
  categories,
  initial,
  onSubmit,
  pending,
}: {
  categories: Category[]
  initial?: Expense
  onSubmit: (data: ExpensePayload) => void
  pending: boolean
}) {
  const [data, setData] = useState<ExpensePayload>(
      initial ? (({ id, ...rest }) => { void id; return rest })(initial) : empty
    ),
    [uploading, setUploading] = useState(false)
  const set = <K extends keyof ExpensePayload>(k: K, v: ExpensePayload[K]) =>
    setData((x) => ({ ...x, [k]: v }))
  const upload = async (file?: File) => {
    if (!file) return
    setUploading(true)
    try {
      const x = await expensesService.upload(file)
      set('comprovante_url', x.url)
    } finally {
      setUploading(false)
    }
  }
  return (
    <form
      className="card p-6"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit(data)
      }}
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="label sm:col-span-2">
          Descrição
          <input
            required
            className="field"
            value={data.titulo}
            onChange={(e) => set('titulo', e.target.value)}
          />
        </label>
        <label className="label">
          Categoria
          <select
            required
            className="field"
            value={data.categoria_id}
            onChange={(e) => set('categoria_id', e.target.value)}
          >
            <option value="">Selecione</option>
            {categories.map((x) => (
              <option value={x.id} key={x.id}>
                {x.nome}
              </option>
            ))}
          </select>
        </label>
        <label className="label">
          Valor
          <input
            required
            min="0.01"
            step="0.01"
            type="number"
            className="field"
            value={data.valor}
            onChange={(e) => set('valor', Number(e.target.value))}
          />
        </label>
        <label className="label">
          Tipo
          <select
            className="field"
            value={data.tipo}
            onChange={(e) =>
              set('tipo', e.target.value as ExpensePayload['tipo'])
            }
          >
            <option>Fixa</option>
            <option>Variável</option>
          </select>
        </label>
        <label className="label">
          Fornecedor
          <input
            className="field"
            value={data.fornecedor}
            onChange={(e) => set('fornecedor', e.target.value)}
          />
        </label>
        <label className="label">
          Forma de pagamento
          <select
            className="field"
            value={data.forma_pagamento}
            onChange={(e) => set('forma_pagamento', e.target.value)}
          >
            {[
              'PIX',
              'TED',
              'Cartão',
              'Boleto',
              'Débito',
              'Dinheiro',
              'Outro',
            ].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label className="label">
          Status
          <select
            className="field"
            value={data.status}
            onChange={(e) =>
              set('status', e.target.value as ExpensePayload['status'])
            }
          >
            {['Pendente', 'Pago', 'Atrasado', 'Cancelado'].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label className="label">
          Competência
          <input
            type="date"
            className="field"
            value={data.competencia}
            onChange={(e) => set('competencia', e.target.value)}
          />
        </label>
        <label className="label">
          Data de vencimento
          <input
            type="date"
            className="field"
            value={data.data_vencimento}
            onChange={(e) => set('data_vencimento', e.target.value)}
          />
        </label>
        <label className="label">
          Data de pagamento
          <input
            type="date"
            className="field"
            value={data.data_pagamento ?? ''}
            onChange={(e) => set('data_pagamento', e.target.value || undefined)}
          />
        </label>
        <label className="label">
          Centro de custos
          <select
            className="field"
            value={data.centro_custo}
            onChange={(e) => set('centro_custo', e.target.value)}
          >
            {['Consultório', 'Plantões', 'Administrativo', 'Pessoal'].map(
              (x) => (
                <option key={x}>{x}</option>
              )
            )}
          </select>
        </label>
        <label className="label flex items-center gap-2 sm:col-span-2">
          <input
            type="checkbox"
            checked={data.recorrente}
            onChange={(e) => set('recorrente', e.target.checked)}
          />{' '}
          Despesa recorrente
        </label>
        {data.recorrente && (
          <label className="label">
            Intervalo
            <select
              className="field"
              value={data.intervalo_recorrencia ?? ''}
              onChange={(e) => set('intervalo_recorrencia', e.target.value)}
            >
              <option value="">Selecione</option>
              {['Mensal', 'Semanal', 'Anual', 'Trimestral', 'Semestral'].map(
                (x) => (
                  <option key={x}>{x}</option>
                )
              )}
            </select>
          </label>
        )}
        <label className="label">
          Comprovante PDF/JPG/PNG
          <input
            className="field"
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={(e) => void upload(e.target.files?.[0])}
          />
          <small className="text-slate-400">
            {uploading
              ? 'Enviando...'
              : data.comprovante_url
                ? 'Comprovante anexado'
                : 'Máximo 5 MB'}
          </small>
        </label>
        <label className="label sm:col-span-2">
          Observações
          <textarea
            className="field min-h-24"
            value={data.observacoes}
            onChange={(e) => set('observacoes', e.target.value)}
          />
        </label>
      </div>
      <Button className="mt-5" disabled={pending || uploading}>
        {pending ? 'Salvando...' : 'Salvar despesa'}
      </Button>
    </form>
  )
}
