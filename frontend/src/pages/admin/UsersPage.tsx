import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Pencil, Plus, Search, ShieldCheck, X } from 'lucide-react'
import { adminUsersService } from '@/services/adminUsers'
import { Button } from '@/components/ui/Button'
import type { AdminUser, AdminUserPayload } from '@/types/adminUser'

const empty: AdminUserPayload = { name: '', email: '', password: '', crm: '', crm_uf: '', cnpj: '', phone: '', city: '', state: '', specialty: '' }

export function UsersPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<AdminUser | null | undefined>(undefined)
  const [form, setForm] = useState<AdminUserPayload>(empty)
  const [error, setError] = useState('')
  const { data = [], isLoading } = useQuery({ queryKey: ['admin-users'], queryFn: adminUsersService.list })
  const mutation = useMutation({
    mutationFn: () => editing ? adminUsersService.update(editing.id, form) : adminUsersService.create(form),
    onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ['admin-users'] }); setEditing(undefined); setForm(empty) },
    onError: () => setError('Não foi possível salvar. Verifique os dados, e-mail, CNPJ e a força da senha.'),
  })
  const openCreate = () => { setEditing(null); setForm(empty); setError('') }
  const openEdit = (user: AdminUser) => {
    setEditing(user)
    setForm({ name: user.name, email: user.email, password: '', crm: user.crm, crm_uf: user.crm_uf, cnpj: user.cnpj, phone: user.phone, city: user.city, state: user.state, specialty: user.specialty })
    setError('')
  }
  const filtered = data.filter(user => `${user.name} ${user.email} ${user.crm}`.toLowerCase().includes(search.toLowerCase()))

  return <div>
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div><p className="flex items-center gap-2 text-sm text-slate-500"><ShieldCheck size={16}/>Área exclusiva do administrador</p><h1 className="mt-1 text-2xl font-bold">Usuários</h1></div>
      <Button onClick={openCreate}><Plus size={17} className="mr-2"/>Novo usuário</Button>
    </div>
    <section className="card overflow-hidden">
      <div className="border-b p-4"><div className="relative max-w-sm"><Search className="absolute left-3 top-3 text-slate-400" size={17}/><input className="field mt-0 pl-9" placeholder="Buscar nome, e-mail ou CRM" value={search} onChange={event => setSearch(event.target.value)}/></div></div>
      {isLoading ? <div className="m-5 h-40 animate-pulse rounded bg-slate-100"/> : <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr>{['Usuário','CRM','Especialidade','Cidade','Perfil','Cadastro',''].map(item => <th className="px-5 py-3 font-medium" key={item}>{item}</th>)}</tr></thead><tbody>{filtered.map(user => <tr className="border-t" key={user.id}>
          <td className="px-5 py-4"><div className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">{user.name.slice(0,2).toUpperCase()}</span><div><p className="font-medium">{user.name}</p><p className="text-xs text-slate-500">{user.email}</p></div></div></td>
          <td className="px-5 py-4">{user.crm}/{user.crm_uf}</td><td className="px-5 py-4">{user.specialty}</td><td className="px-5 py-4">{user.city}/{user.state}</td>
          <td className="px-5 py-4"><span className={user.role === 'ADMIN' ? 'rounded-full bg-cyan-50 px-2 py-1 text-xs font-semibold text-cyan-700' : 'rounded-full bg-slate-100 px-2 py-1 text-xs'}>{user.role}</span></td>
          <td className="px-5 py-4 text-slate-500">{new Date(user.created_at).toLocaleDateString('pt-BR')}</td><td className="px-5 py-4"><button onClick={() => openEdit(user)} title="Editar" className="text-blue-600"><Pencil size={17}/></button></td>
        </tr>)}</tbody></table>
        {!filtered.length && <div className="p-10 text-center text-sm text-slate-400">Nenhum usuário encontrado.</div>}
      </div>}
    </section>
    {editing !== undefined && <div className="fixed inset-0 z-[80] grid place-items-center bg-slate-950/50 p-2 sm:p-4" onClick={() => setEditing(undefined)}>
      <form onSubmit={event => { event.preventDefault(); mutation.mutate() }} className="card max-h-[calc(100svh-1rem)] w-full max-w-3xl overflow-y-auto p-4 sm:max-h-[92vh] sm:p-6" onClick={event => event.stopPropagation()}>
        <div className="flex items-center justify-between gap-3"><div><p className="text-sm text-slate-500">{editing ? 'Editar acesso' : 'Novo acesso'}</p><h2 className="text-xl font-bold">{editing?.name || 'Cadastrar usuário'}</h2></div><button type="button" onClick={() => setEditing(undefined)}><X/></button></div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2"><Field label="Nome completo" name="name" form={form} set={setForm}/><Field label="E-mail de login" name="email" type="email" form={form} set={setForm}/><Field label={editing ? 'Nova senha (deixe vazio para manter)' : 'Senha'} name="password" type="password" required={!editing} form={form} set={setForm}/><Field label="CRM" name="crm" form={form} set={setForm}/><Field label="UF do CRM" name="crm_uf" form={form} set={setForm}/><Field label="Especialidade" name="specialty" form={form} set={setForm}/><Field label="CNPJ" name="cnpj" form={form} set={setForm}/><Field label="Telefone" name="phone" form={form} set={setForm}/><Field label="Cidade" name="city" form={form} set={setForm}/><Field label="Estado" name="state" form={form} set={setForm}/></div>
        <p className="mt-4 text-xs text-slate-500">A senha deve ter pelo menos 8 caracteres, letra maiúscula, número e caractere especial. Senhas existentes não podem ser visualizadas.</p>
        {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        <div className="mt-6 flex flex-wrap justify-end gap-3"><button type="button" onClick={() => setEditing(undefined)} className="px-4 text-sm">Cancelar</button><Button disabled={mutation.isPending}>{mutation.isPending ? 'Salvando...' : 'Salvar usuário'}</Button></div>
      </form>
    </div>}
  </div>
}

function Field({ label, name, type = 'text', required = true, form, set }: { label: string; name: keyof AdminUserPayload; type?: string; required?: boolean; form: AdminUserPayload; set: React.Dispatch<React.SetStateAction<AdminUserPayload>> }) {
  return <label className="label">{label}<input required={required} className="field" type={type} value={String(form[name] ?? '')} onChange={event => set({ ...form, [name]: event.target.value })}/></label>
}
