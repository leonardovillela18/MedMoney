import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { shiftsService } from '@/services/shifts'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/context/AuthContext'

export function ShiftDetailPage() {
  const { id } = useParams(), { user } = useAuth(), assistant = !!user?.is_assistant
  const navigate = useNavigate(), queryClient = useQueryClient()
  const { data: shift } = useQuery({ queryKey: ['shift', id], queryFn: () => shiftsService.get(id!) })
  const remove = useMutation({
    mutationFn: () => shiftsService.remove(id!),
    onSuccess: async () => {
      await Promise.all([queryClient.invalidateQueries({ queryKey: ['shifts'] }), queryClient.invalidateQueries({ queryKey: ['consultations'] })])
      navigate(shift?.type === 'Consulta' ? '/consultas' : '/plantoes')
    },
  })
  if (!shift) return <div className="h-64 animate-pulse bg-slate-100" />
  const details = [['Data', shift.date], ['Horário', `${shift.start_time} – ${shift.end_time}`], ['Duração', `${shift.duration_hours} horas`], ['Status', shift.status], ['Local', shift.hospital_sector || shift.city]]
  if (!assistant) details.splice(3, 0, ['Valor', `R$ ${shift.gross_value}`], ['Pagamento previsto', shift.expected_payment_date || '—'])
  return <div className="mx-auto max-w-3xl"><div className="mb-8 flex items-end justify-between gap-4"><div><p className="text-sm text-slate-500">{shift.type}</p><h1 className="text-2xl font-bold">{shift.title || shift.type}</h1></div><div className="flex gap-2"><Link to={`/plantoes/${id}/editar`}><Button>Editar</Button></Link><Button className="bg-red-600 hover:bg-red-700" disabled={remove.isPending} onClick={() => { if (window.confirm(`Excluir ${shift.type.toLowerCase()}?`)) remove.mutate() }}>Excluir</Button></div></div><section className="card p-5"><h2 className="font-semibold">Detalhes do compromisso</h2><div className="mt-5 grid gap-4 sm:grid-cols-2">{details.map(([label, value]) => <div key={label}><p className="text-xs text-slate-500">{label}</p><p className="font-medium">{value || '—'}</p></div>)}</div>{shift.notes && <div className="mt-5 border-t pt-4"><p className="text-xs text-slate-500">Observações</p><p className="mt-1 whitespace-pre-wrap">{shift.notes}</p></div>}</section>{!assistant && <section className="card mt-5 p-5"><h2 className="font-semibold">Acompanhamento financeiro</h2><p className="mt-2 text-sm text-slate-500">Informações de recebimento, nota fiscal e impostos ficam disponíveis somente para o médico.</p></section>}</div>
}
