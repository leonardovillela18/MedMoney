import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { InsightBadge } from '@/components/insights/InsightBadge'
import { RecommendationCard } from '@/components/insights/RecommendationCard'
import { insightsService } from '@/services/insights'
export function InsightDetailPage() {
  const { id } = useParams(),
    qc = useQueryClient()
  const q = useQuery({
    queryKey: ['insight', id],
    queryFn: () => insightsService.get(id!),
  })
  useEffect(() => {
    if (q.data) void qc.invalidateQueries({ queryKey: ['insights-dashboard'] })
  }, [q.data, qc])
  if (q.isLoading)
    return <div className="h-80 animate-pulse rounded-xl bg-slate-100" />
  const x = q.data!
  return (
    <div className="mx-auto max-w-3xl">
      <header>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-400">{x.categoria}</span>
          <InsightBadge severity={x.severidade} />
        </div>
        <h1 className="mt-3 text-3xl font-bold">{x.titulo}</h1>
        <p className="mt-3 text-sm text-slate-400">
          Atualizado em {new Date(x.updated_at).toLocaleString('pt-BR')}
        </p>
      </header>
      <section className="card mt-6 p-6">
        <h2 className="font-semibold">O que os dados mostram</h2>
        <p className="mt-3 leading-relaxed text-slate-600">{x.descricao}</p>
        <div className="mt-6">
          <RecommendationCard action={x.acao_recomendada} />
        </div>
        <div className="mt-6 border-t pt-4 text-xs text-slate-400">
          Regra: {x.tipo} · Referência verificável: {x.referencia}
        </div>
      </section>
    </div>
  )
}
