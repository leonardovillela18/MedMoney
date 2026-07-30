import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowDownCircle,
  ArrowUpCircle,
  Landmark,
  PiggyBank,
  Plus,
  Scale,
  Wallet,
  WalletCards,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { financialService } from '@/services/financial'

const money = (value = 0) =>
  value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export function FinancialPage() {
  const queryClient = useQueryClient()
  const [period, setPeriod] = useState('month')
  const [modal, setModal] = useState<'account' | 'transaction' | null>(null)
  const dates = periodDates(period)
  const summary = useQuery({
    queryKey: ['financial-summary', dates],
    queryFn: () => financialService.summary(dates.start, dates.end),
  })
  const accounts = useQuery({
    queryKey: ['financial-accounts'],
    queryFn: financialService.accounts,
  })
  const refresh = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['financial-summary'] }),
      queryClient.invalidateQueries({ queryKey: ['financial-accounts'] }),
      queryClient.invalidateQueries({ queryKey: ['cashflow-list'] }),
    ])
    setModal(null)
  }
  const data = summary.data
  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-blue-600">Visão executiva</p>
          <h1 className="text-2xl font-bold">Financeiro</h1>
          <p className="mt-1 text-sm text-slate-500">
            Dinheiro confirmado separado do que ainda está previsto.
          </p>
        </div>
        <div className="flex gap-2">
          <Button type="button" onClick={() => setModal('transaction')}>
            <Plus size={17} /> Lançamento
          </Button>
          <Button type="button" onClick={() => setModal('account')}>
            Nova conta
          </Button>
        </div>
      </header>
      <select
        className="field w-full sm:w-52"
        value={period}
        onChange={(event) => setPeriod(event.target.value)}
      >
        <option value="month">Este mês</option>
        <option value="last30">Últimos 30 dias</option>
        <option value="next30">Próximos 30 dias</option>
      </select>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <Card
          label="Saldo atual"
          help="Somente movimentações confirmadas"
          value={money(data?.current_balance)}
          icon={Wallet}
        />
        <Card
          label="A receber"
          help="Recebíveis com saldo pendente"
          value={money(data?.receivable)}
          icon={ArrowUpCircle}
        />
        <Card
          label="A pagar"
          help="Despesas pendentes ou atrasadas no período"
          value={money(data?.payable)}
          icon={ArrowDownCircle}
        />
        <Card
          label="Saldo projetado"
          help="Saldo atual mais entradas e saídas previstas"
          value={money(data?.forecast_balance)}
          icon={Scale}
        />
        <Card
          label="Reserva tributária sugerida"
          help="Planejamento; não reduz o saldo atual"
          value={money(data?.tax_reserve_suggested)}
          icon={Landmark}
        />
        <Card
          label="Disponível atual"
          help={`Deduz apenas o efetivamente reservado (${money(data?.tax_reserve_effective)})`}
          value={money(data?.available)}
          icon={PiggyBank}
        />
      </div>
      <section className="card p-5">
        <h2 className="font-semibold">Resultado confirmado do período</h2>
        <div className="mt-5 grid gap-4 sm:grid-cols-3">
          <Metric label="Entradas" value={data?.month_inflows} />
          <Metric label="Saídas" value={data?.month_outflows} />
          <Metric label="Resultado" value={data?.month_result} />
        </div>
      </section>
      <section className="card p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold">Contas financeiras</h2>
            <p className="text-sm text-slate-500">
              Saldo calculado pelos lançamentos confirmados.
            </p>
          </div>
          <WalletCards className="text-blue-600" />
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {accounts.data?.map((account) => (
            <div className="rounded-xl border p-4" key={account.id}>
              <p className="font-medium">{account.account_name}</p>
              <p className="text-xs text-slate-500">
                {account.institution_name || 'Conta manual'}
                {account.last4 ? ` • final ${account.last4}` : ''}
              </p>
              <p className="mt-3 text-lg font-bold">{money(account.balance)}</p>
            </div>
          ))}
        </div>
      </section>
      <div className="flex flex-wrap gap-3">
        <Link className="font-medium text-blue-600" to="/fluxo-de-caixa">
          Ver transações →
        </Link>
        <Link className="font-medium text-blue-600" to="/despesas">
          Ver contas a pagar →
        </Link>
      </div>
      {modal === 'account' && (
        <AccountModal close={() => setModal(null)} saved={refresh} />
      )}{' '}
      {modal === 'transaction' && (
        <TransactionModal
          accounts={accounts.data ?? []}
          close={() => setModal(null)}
          saved={refresh}
        />
      )}
    </div>
  )
}

function Card({
  label,
  help,
  value,
  icon: Icon,
}: {
  label: string
  help: string
  value: string
  icon: typeof Wallet
}) {
  return (
    <article className="card p-5">
      <div className="flex justify-between">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-2 text-xl font-bold">{value}</p>
        </div>
        <Icon className="text-blue-600" />
      </div>
      <p className="mt-3 text-xs text-slate-400">{help}</p>
    </article>
  )
}
function Metric({ label, value = 0 }: { label: string; value?: number }) {
  return (
    <div>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-xl font-bold">{money(value)}</p>
    </div>
  )
}
function Modal({
  children,
  close,
}: {
  children: React.ReactNode
  close: () => void
}) {
  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-slate-900/40 p-4"
      onClick={close}
    >
      <div
        className="card w-full max-w-lg p-6"
        onClick={(event) => event.stopPropagation()}
      >
        {children}
      </div>
    </div>
  )
}
function AccountModal({
  close,
  saved,
}: {
  close: () => void
  saved: () => Promise<void>
}) {
  const [form, setForm] = useState({
    account_name: '',
    institution_name: '',
    account_type: 'CHECKING',
    last4: '',
    opening_balance: 0,
    opening_date: new Date().toISOString().slice(0, 10),
    is_default: false,
  })
  return (
    <Modal close={close}>
      <form
        onSubmit={async (event) => {
          event.preventDefault()
          await financialService.createAccount({
            ...form,
            last4: form.last4 || null,
          })
          await saved()
        }}
      >
        <h2 className="text-lg font-semibold">Cadastrar conta manual</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <Input
            label="Nome"
            value={form.account_name}
            change={(value) => setForm({ ...form, account_name: value })}
          />
          <Input
            label="Instituição"
            value={form.institution_name}
            change={(value) => setForm({ ...form, institution_name: value })}
          />
          <label className="label">
            Tipo
            <select
              className="field"
              value={form.account_type}
              onChange={(e) =>
                setForm({ ...form, account_type: e.target.value })
              }
            >
              <option value="CHECKING">Conta corrente</option>
              <option value="PAYMENT">Conta pagamento</option>
              <option value="CASH">Dinheiro/Caixa</option>
              <option value="INVESTMENT">Investimento</option>
              <option value="OTHER">Outra</option>
            </select>
          </label>
          <Input
            label="Últimos 4 dígitos"
            value={form.last4}
            change={(value) =>
              setForm({ ...form, last4: value.replace(/\D/g, '').slice(0, 4) })
            }
          />
          <Input
            label="Saldo inicial"
            type="number"
            value={String(form.opening_balance)}
            change={(value) =>
              setForm({ ...form, opening_balance: Number(value) })
            }
          />
        </div>
        <p className="mt-3 text-xs text-slate-500">
          O saldo inicial será registrado como ajuste auditável. Nenhuma
          credencial bancária é solicitada.
        </p>
        <Button className="mt-5">Salvar conta</Button>
      </form>
    </Modal>
  )
}
function TransactionModal({
  accounts,
  close,
  saved,
}: {
  accounts: { id: string; account_name: string }[]
  close: () => void
  saved: () => Promise<void>
}) {
  const [form, setForm] = useState({
    description: '',
    amount: 0,
    transaction_date: new Date().toISOString().slice(0, 10),
    type: 'INCOME',
    status: 'CONFIRMED',
    account_id: '',
    category: '',
    notes: '',
  })
  return (
    <Modal close={close}>
      <form
        onSubmit={async (event) => {
          event.preventDefault()
          await financialService.manual({
            ...form,
            account_id: form.account_id || null,
          })
          await saved()
        }}
      >
        <h2 className="text-lg font-semibold">Novo lançamento manual</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <Input
            label="Descrição"
            value={form.description}
            change={(value) => setForm({ ...form, description: value })}
          />
          <Input
            label="Valor"
            type="number"
            value={String(form.amount)}
            change={(value) => setForm({ ...form, amount: Number(value) })}
          />
          <label className="label">
            Tipo
            <select
              className="field"
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
            >
              <option value="INCOME">Entrada</option>
              <option value="EXPENSE">Saída</option>
              <option value="ADJUSTMENT">Ajuste</option>
            </select>
          </label>
          <label className="label">
            Status
            <select
              className="field"
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
            >
              <option value="CONFIRMED">Confirmado</option>
              <option value="FORECAST">Previsto</option>
            </select>
          </label>
          <label className="label sm:col-span-2">
            Conta
            <select
              className="field"
              value={form.account_id}
              onChange={(e) => setForm({ ...form, account_id: e.target.value })}
            >
              <option value="">Não informada</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.account_name}
                </option>
              ))}
            </select>
          </label>
        </div>
        <Button className="mt-5">Criar lançamento</Button>
      </form>
    </Modal>
  )
}
function Input({
  label,
  value,
  change,
  type = 'text',
}: {
  label: string
  value: string
  change: (value: string) => void
  type?: string
}) {
  return (
    <label className="label">
      {label}
      <input
        required
        className="field"
        type={type}
        value={value}
        onChange={(event) => change(event.target.value)}
      />
    </label>
  )
}
function periodDates(period: string) {
  const today = new Date(),
    start = new Date(today),
    end = new Date(today)
  if (period === 'month') {
    start.setDate(1)
    end.setMonth(end.getMonth() + 1, 1)
  } else if (period === 'last30') {
    start.setDate(start.getDate() - 30)
    end.setDate(end.getDate() + 1)
  } else {
    end.setDate(end.getDate() + 30)
  }
  return {
    start: start.toISOString().slice(0, 10),
    end: end.toISOString().slice(0, 10),
  }
}
