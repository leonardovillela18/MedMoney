export function TodayGoals({
  target,
  current,
  progress,
  source,
  format,
}: {
  target: number
  current: number
  progress: number
  source: string
  format: (n: number) => string
}) {
  const now = new Date()
  const pace = current / Math.max(now.getDate(), 1)
  const remaining = Math.max(0, target - current)
  const forecast = pace > 0 ? new Date(now.getTime() + Math.ceil(remaining / pace) * 86_400_000) : null
  return (
    <section className="card p-5">
      <h2 className="font-semibold">Referência mensal</h2>
      <div className="mt-4 flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold">{format(current)}</p>
          <p className="text-xs text-slate-400">de {format(target)}</p>
        </div>
        <b className="text-blue-600">{progress.toFixed(0)}%</b>
      </div>
      <div className="mt-4 h-2 rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-blue-600"
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      <p className="mt-3 text-xs text-slate-400">{source}</p>
      <p className="mt-1 text-xs text-slate-500">
        {forecast
          ? remaining === 0
            ? 'Referência mensal já atingida.'
            : `No ritmo atual, previsão para ${forecast.toLocaleDateString('pt-BR')}.`
          : 'Ainda não há ritmo de receita suficiente para uma previsão.'}
      </p>
    </section>
  )
}
