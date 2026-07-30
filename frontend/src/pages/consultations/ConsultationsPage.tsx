import { useQuery } from '@tanstack/react-query'
import { CalendarDays, Plus, Stethoscope } from 'lucide-react'
import { Link } from 'react-router-dom'
import { shiftsService } from '@/services/shifts'
import { Button } from '@/components/ui/Button'
export function ConsultationsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['consultations'],
    queryFn: () =>
      shiftsService.list({
        type: 'Consulta',
        page: 1,
        page_size: 100,
        order: 'oldest',
      }),
  })
  return (
    <div>
      <div className="mb-8 flex items-end justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">Agenda de atendimentos</p>
          <h1 className="text-2xl font-bold">Consultas</h1>
        </div>
        <Link to="/consultas/nova?type=Consulta">
          <Button>
            <Plus size={17} className="mr-2" />
            Nova consulta
          </Button>
        </Link>
      </div>
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="m-5 h-40 animate-pulse rounded bg-slate-100" />
        ) : !data?.items.length ? (
          <div className="grid min-h-72 place-items-center text-center">
            <div>
              <Stethoscope className="mx-auto text-blue-600" size={42} />
              <p className="mt-4 font-semibold">Nenhuma consulta agendada.</p>
            </div>
          </div>
        ) : (
          <div className="divide-y">
            {data.items.map((x) => (
              <div
                className="flex flex-wrap items-center gap-4 p-5 hover:bg-slate-50"
                key={x.id}
              >
                <span className="grid h-11 w-11 place-items-center rounded-xl bg-blue-50 text-blue-600">
                  <Stethoscope size={20} />
                </span>
                <div className="flex-1">
                  <p className="font-semibold">{x.title || 'Consulta'}</p>
                  <p className="text-sm text-slate-500">
                    {x.hospital_sector || x.city || 'Local não informado'}
                  </p>
                </div>
                <p className="text-sm">
                  <CalendarDays size={15} className="mr-1 inline" />
                  {new Date(`${x.date}T12:00`).toLocaleDateString(
                    'pt-BR'
                  )} às {x.start_time.slice(0, 5)}
                </p>
                <div className="flex gap-3 text-sm font-medium">
                  <Link className="text-blue-600" to={`/plantoes/${x.id}`}>
                    Ver
                  </Link>
                  <Link
                    className="text-blue-600"
                    to={`/plantoes/${x.id}/editar`}
                  >
                    Editar
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
