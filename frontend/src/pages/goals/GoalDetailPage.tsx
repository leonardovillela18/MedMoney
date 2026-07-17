import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { GoalChart } from '@/components/goals/GoalChart'
import { GoalProgress } from '@/components/goals/GoalProgress'
import { GoalSimulation } from '@/components/goals/GoalSimulation'
import { GoalTimeline } from '@/components/goals/GoalTimeline'
import { goalsService } from '@/services/goals'
export function GoalDetailPage() {
  const { id } = useParams(),
    navigate = useNavigate(),
    qc = useQueryClient()
  const q = useQuery({
      queryKey: ['goal', id],
      queryFn: () => goalsService.get(id!),
    }),
    remove = useMutation({
      mutationFn: () => goalsService.remove(id!),
      onSuccess: async () => {
        await qc.invalidateQueries({ queryKey: ['goals'] })
        navigate('/metas')
      },
    })
  if (q.isLoading)
    return <div className="h-96 animate-pulse rounded-xl bg-slate-100" />
  const { goal, forecast, history, insight, comparisons } = q.data!
  return (
    <div className="mx-auto max-w-5xl">
      <header className="mb-6 flex flex-wrap justify-between gap-4">
        <div>
          <p className="text-sm text-blue-600">{goal.tipo}</p>
          <h1 className="mt-1 text-3xl font-bold">{goal.titulo}</h1>
          <p className="mt-2 text-sm text-slate-500">{goal.descricao}</p>
        </div>
        <div className="flex gap-2">
          <Link to={`/metas/${id}/editar`}>
            <Button>Editar</Button>
          </Link>
          <Button
            className="bg-red-600 hover:bg-red-700"
            onClick={() => remove.mutate()}
          >
            Excluir
          </Button>
        </div>
      </header>
      <section className="card p-6">
        <div className="grid gap-5 sm:grid-cols-4">
          <div>
            <small>Valor atual</small>
            <p className="text-xl font-bold">
              {goal.valor_atual.toLocaleString('pt-BR')}
            </p>
          </div>
          <div>
            <small>Quanto falta</small>
            <p className="text-xl font-bold">
              {forecast.remaining.toLocaleString('pt-BR')}
            </p>
          </div>
          <div>
            <small>Dias restantes</small>
            <p className="text-xl font-bold">{forecast.days_remaining}</p>
          </div>
          <div>
            <small>Previsão</small>
            <p className="text-xl font-bold">
              {forecast.forecast_date
                ? new Date(
                    `${forecast.forecast_date}T12:00`
                  ).toLocaleDateString('pt-BR')
                : 'Sem ritmo suficiente'}
            </p>
          </div>
        </div>
        <div className="mt-6">
          <GoalProgress percentage={goal.percentual} color={goal.cor} />
        </div>
        <p
          className={`mt-4 text-sm ${forecast.on_track ? 'text-emerald-600' : 'text-amber-600'}`}
        >
          {forecast.on_track
            ? 'Seu ritmo atual é suficiente.'
            : `Ritmo necessário: ${forecast.required_daily_pace.toLocaleString('pt-BR')} por dia.`}
        </p>
        <p className="mt-4 rounded-lg bg-blue-50 p-3 text-sm text-blue-900">
          {insight}
        </p>
      </section>
      <section className="card mt-5 p-5">
        <h2 className="font-semibold">Comparativo</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {comparisons.map((item) => (
            <div className="rounded-lg bg-slate-50 p-3" key={item.label}>
              <p className="text-xs text-slate-400">{item.label}</p>
              <p className="mt-1 font-semibold">
                {item.value.toLocaleString('pt-BR')}
              </p>
            </div>
          ))}
        </div>
      </section>
      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <GoalChart history={history} />
        <GoalSimulation goalId={goal.id} />
      </div>
      <div className="mt-5">
        <GoalTimeline items={history} />
      </div>
    </div>
  )
}
