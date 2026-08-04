import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { CalendarDays, Clock, MapPin, Scissors } from 'lucide-react'
import { shiftsService } from '@/services/shifts'
import { Button } from '@/components/ui/Button'

export function SurgeryDetailPage() {
  const { id } = useParams(), navigate = useNavigate(), queryClient = useQueryClient()
  const { data } = useQuery({ queryKey: ['surgery', id], queryFn: () => shiftsService.get(id!) })
  const remove = useMutation({ mutationFn: () => shiftsService.remove(id!), onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ['surgeries'] }); navigate('/cirurgias') } })
  if (!data) return <div className="h-64 animate-pulse rounded-xl bg-slate-100" />
  return <div className="mx-auto max-w-3xl"><div className="mb-8 flex flex-col items-start gap-4 sm:flex-row sm:justify-between"><div><p className="text-sm text-slate-500">Cirurgia</p><h1 className="text-2xl font-bold">{data.title}</h1></div><div className="flex gap-2"><Link to={`/cirurgias/${id}/editar`}><Button>Editar</Button></Link><Button className="bg-red-600 hover:bg-red-700" disabled={remove.isPending} onClick={() => { if (window.confirm('Excluir cirurgia?')) remove.mutate() }}>Excluir</Button></div></div><section className="card p-4 min-[380px]:p-5 sm:p-6"><div className="grid gap-5 sm:grid-cols-2"><Info icon={Scissors} label="Procedimento" value={data.title}/><Info icon={MapPin} label="Hospital / setor" value={data.hospital_sector}/><Info icon={CalendarDays} label="Data" value={new Date(`${data.date}T12:00`).toLocaleDateString('pt-BR')}/><Info icon={Clock} label="Horário e duração" value={`${data.start_time.slice(0,5)} – ${data.end_time.slice(0,5)} (${data.duration_hours}h)`}/></div>{data.notes && <div className="mt-6 border-t pt-5"><p className="text-xs uppercase text-slate-400">Observações</p><p className="mt-2 whitespace-pre-wrap text-sm">{data.notes}</p></div>}</section></div>
}
function Info({icon:Icon,label,value}:{icon:typeof Scissors;label:string;value?:string}) { return <div className="rounded-xl bg-slate-50 p-4"><Icon size={18} className="text-cyan-600"/><p className="mt-3 text-xs text-slate-400">{label}</p><p className="mt-1 font-medium">{value || 'Não informado'}</p></div> }
