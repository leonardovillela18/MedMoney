import { useEffect, useRef } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { PriorityChip } from '@/components/alerts/PriorityChip'
import { RecommendationCard } from '@/components/alerts/RecommendationCard'
import { alertsService } from '@/services/alerts'
export function AlertDetailPage() {
  const readRequested = useRef(false)
  const { id } = useParams(),
    qc = useQueryClient(),
    navigate = useNavigate()
  const q = useQuery({
      queryKey: ['alert', id],
      queryFn: () => alertsService.get(id!),
    }),
    read = useMutation({
      mutationFn: () => alertsService.read(id!),
      onSuccess: async () => {
        await Promise.all([
          qc.invalidateQueries({ queryKey: ['alerts'] }),
          qc.invalidateQueries({ queryKey: ['alerts-dashboard'] }),
        ])
      },
    }),
    resolve = useMutation({
      mutationFn: () => alertsService.resolve(id!),
      onSuccess: async () => {
        await Promise.all([
          qc.invalidateQueries({ queryKey: ['alerts'] }),
          qc.invalidateQueries({ queryKey: ['alerts-dashboard'] }),
        ])
        navigate('/alertas')
      },
    })
  useEffect(() => {
    if (q.data?.status === 'Novo' && !readRequested.current) {
      readRequested.current = true
      read.mutate()
    }
  }, [q.data?.status, read])
  if (q.isLoading)
    return <div className="h-80 animate-pulse rounded-xl bg-slate-100" />
  const x = q.data!
  return (
    <div className="mx-auto max-w-3xl">
      <header>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-400">{x.categoria}</span>
          <PriorityChip priority={x.prioridade} />
        </div>
        <h1 className="mt-3 text-3xl font-bold">{x.titulo}</h1>
        <p className="mt-2 text-sm text-slate-400">
          {x.origem} · {new Date(x.updated_at).toLocaleString('pt-BR')}
        </p>
      </header>
      <section className="card mt-6 p-6">
        <h2 className="font-semibold">Contexto e impacto</h2>
        <p className="mt-3 leading-relaxed text-slate-600">{x.descricao}</p>
        <div className="mt-6">
          <RecommendationCard action={x.acao} url={x.url_destino} />
        </div>
        {x.status !== 'Resolvido' && (
          <Button
            className="mt-5 bg-emerald-600 hover:bg-emerald-700"
            disabled={resolve.isPending}
            onClick={() => resolve.mutate()}
          >
            Marcar como resolvido
          </Button>
        )}
        <p className="mt-6 border-t pt-4 text-xs text-slate-400">
          Regra: {x.tipo} · Referência: {x.referencia_id}
        </p>
      </section>
    </div>
  )
}
