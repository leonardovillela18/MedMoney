import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Calculator } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { taxesService } from '@/services/taxes'
import type { Simulation } from '@/types/tax'
const money = (n: number) =>
  n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
export function Simulator({
  defaultPercentage,
}: {
  defaultPercentage: number
}) {
  const [revenue, setRevenue] = useState(45000),
    [percentage, setPercentage] = useState(defaultPercentage)
  const mutation = useMutation<Simulation, Error>({
    mutationFn: () => taxesService.simulate(revenue, percentage),
  })
  return (
    <section className="grid gap-5 lg:grid-cols-[1fr_1.1fr]">
      <div className="card p-6">
        <div className="mb-5 flex items-center gap-3">
          <span className="rounded-xl bg-blue-50 p-2 text-blue-600">
            <Calculator />
          </span>
          <div>
            <h2 className="font-semibold">Simulador de reserva</h2>
            <p className="text-sm text-slate-500">
              Explore cenários de reserva.
            </p>
          </div>
        </div>
        <label className="label">
          Receita estimada
          <input
            className="field"
            type="number"
            min="0"
            value={revenue}
            onChange={(e) => setRevenue(Number(e.target.value))}
          />
        </label>
        <label className="label mt-4 block">
          Alíquota para reserva
          <input
            className="field"
            type="number"
            min="0"
            max="100"
            step="0.1"
            value={percentage}
            onChange={(e) => setPercentage(Number(e.target.value))}
          />
        </label>
        <Button
          className="mt-5 w-full"
          disabled={mutation.isPending}
          onClick={() => mutation.mutate()}
        >
          {mutation.isPending ? 'Simulando...' : 'Calcular simulação'}
        </Button>
      </div>
      <div className="card flex min-h-72 flex-col justify-center bg-slate-900 p-7 text-white">
        <p className="text-sm text-slate-300">Reserva sugerida</p>
        <p className="mt-2 text-4xl font-bold">
          {money(
            mutation.data?.reserva_sugerida ?? (revenue * percentage) / 100
          )}
        </p>
        <div className="my-6 border-t border-slate-700" />
        <p className="text-sm text-slate-300">Disponível após reserva</p>
        <p className="mt-2 text-2xl font-semibold text-emerald-400">
          {money(
            mutation.data?.disponivel_apos_reserva ??
              revenue * (1 - percentage / 100)
          )}
        </p>
        <p className="mt-6 text-xs text-slate-400">
          {mutation.data?.disclaimer ??
            'Simulação informativa. Não representa cálculo tributário oficial.'}
        </p>
      </div>
    </section>
  )
}
