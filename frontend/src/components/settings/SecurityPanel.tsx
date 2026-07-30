import { useState } from 'react'
import { ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { authService } from '@/services/auth'
import { useAuth } from '@/context/AuthContext'

export function SecurityPanel() {
  const { logout, logoutAll } = useAuth()
  const [current, setCurrent] = useState('')
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [error, setError] = useState('')
  const change = async (event: React.FormEvent) => {
    event.preventDefault()
    if (password !== confirmation) {
      setError('As novas senhas precisam ser iguais.')
      return
    }
    try {
      await authService.changePassword(current, password)
      await logout()
    } catch {
      setError(
        'Não foi possível alterar a senha. Confira a senha atual e os requisitos.'
      )
    }
  }
  return (
    <section className="card p-6 sm:p-8">
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <ShieldCheck size={19} /> Segurança
      </h2>
      <p className="mt-1 text-sm text-slate-500">
        A sessão encerra após{' '}
        {import.meta.env.VITE_SESSION_IDLE_TIMEOUT_MINUTES ?? 15} minutos sem
        atividade.
      </p>
      <form className="mt-5 grid gap-4 sm:grid-cols-3" onSubmit={change}>
        <Password label="Senha atual" value={current} set={setCurrent} />
        <Password label="Nova senha" value={password} set={setPassword} />
        <Password
          label="Confirmar nova senha"
          value={confirmation}
          set={setConfirmation}
        />
        {error && <p className="text-sm text-red-600 sm:col-span-3">{error}</p>}
        <div className="flex flex-wrap gap-3 sm:col-span-3">
          <Button>Alterar senha e sair</Button>
          <Button
            type="button"
            className="bg-slate-700"
            onClick={() => void logoutAll()}
          >
            Sair de todos os dispositivos
          </Button>
        </div>
      </form>
    </section>
  )
}
function Password({
  label,
  value,
  set,
}: {
  label: string
  value: string
  set: (value: string) => void
}) {
  return (
    <label className="label">
      {label}
      <input
        className="field"
        type="password"
        required
        minLength={8}
        value={value}
        onChange={(event) => set(event.target.value)}
      />
    </label>
  )
}
