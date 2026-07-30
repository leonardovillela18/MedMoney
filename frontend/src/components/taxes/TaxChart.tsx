import type { TaxDashboard } from '@/types/tax'
const money = (n: number) =>
  n.toLocaleString('pt-BR', {
    notation: 'compact',
    style: 'currency',
    currency: 'BRL',
  })
export function TaxChart({ data }: { data: TaxDashboard['series'] }) {
  const max = Math.max(1, ...data.flatMap((x) => [x.gross, x.tax, x.net]))
  return (
    <section className="card p-5">
      <h2 className="font-semibold">Receita PJ e reserva sugerida</h2>
      <p className="mt-1 text-sm text-slate-500">
        Estimativas dos últimos períodos registrados
      </p>
      <div className="mt-6 flex h-56 items-end gap-4 overflow-x-auto border-b px-2">
        {data.length ? (
          data.map((x) => (
            <div
              key={x.month}
              className="flex min-w-20 flex-1 items-end justify-center gap-1"
            >
              <div
                title={`Receita PJ ${money(x.gross)}`}
                className="w-5 rounded-t bg-blue-200"
                style={{ height: `${Math.max(3, (x.gross / max) * 180)}px` }}
              />
              <div
                title={`Reserva ${money(x.tax)}`}
                className="w-5 rounded-t bg-amber-400"
                style={{ height: `${Math.max(3, (x.tax / max) * 180)}px` }}
              />
              <div
                title={`Disponível após reserva ${money(x.net)}`}
                className="w-5 rounded-t bg-emerald-500"
                style={{ height: `${Math.max(3, (x.net / max) * 180)}px` }}
              />
              <span className="absolute translate-y-6 text-[10px] text-slate-500">
                {x.month.slice(5)}/{x.month.slice(2, 4)}
              </span>
            </div>
          ))
        ) : (
          <p className="m-auto text-sm text-slate-400">
            Registre movimentações para visualizar o gráfico.
          </p>
        )}
      </div>
      <div className="mt-8 flex flex-wrap gap-4 text-xs text-slate-500">
        <span>● Receita PJ</span>
        <span className="text-amber-600">● Reserva sugerida</span>
        <span className="text-emerald-600">● Disponível após reserva</span>
      </div>
    </section>
  )
}
