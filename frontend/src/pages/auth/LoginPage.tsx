import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { AuthShell } from './AuthShell'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/context/AuthContext'

const schema = z.object({
  email: z.string().email('Informe um e-mail válido'),
  password: z.string().min(1, 'Informe sua senha'),
  keep: z.boolean(),
})
type Data = z.infer<typeof schema>

export function LoginPage() {
  const { login } = useAuth()
  const nav = useNavigate()
  const [error, setError] = useState('')
  const [notice] = useState(() => {
    const value = sessionStorage.getItem('crmoney_auth_notice') ?? ''
    sessionStorage.removeItem('crmoney_auth_notice')
    return value
  })
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Data>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: import.meta.env.DEV ? 'admin@crmoney.com' : '',
      password: import.meta.env.DEV ? 'Admin@123' : '',
      keep: true,
    },
  })

  const submit = async (data: Data) => {
    try {
      setError('')
      await login(data.email, data.password, data.keep)
      nav('/dashboard')
    } catch {
      setError(
        'Não conseguimos realizar o login agora. Verifique seus dados e tente novamente.'
      )
    }
  }

  return (
    <AuthShell
      title="Boas-vindas"
      subtitle="Entre para acompanhar sua vida financeira."
      darkForm
    >
      {import.meta.env.DEV && (
        <div className="mt-6 rounded-lg border border-cyan-700/60 bg-cyan-950/50 p-3 text-sm text-cyan-100">
          <p className="font-semibold">
            Acesso administrativo de desenvolvimento
          </p>
          <p>E-mail: admin@crmoney.com</p>
          <p>Senha: Admin@123</p>
        </div>
      )}
      <form onSubmit={handleSubmit(submit)} className="mt-8 space-y-5">
        {notice && (
          <p className="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
            {notice}
          </p>
        )}
        <div>
          <label className="label">E-mail</label>
          <input
            className="field"
            autoComplete="email"
            placeholder="voce@email.com"
            {...register('email')}
          />
          {errors.email && (
            <p className="mt-1 text-xs text-red-300">{errors.email.message}</p>
          )}
        </div>
        <div>
          <div className="flex justify-between">
            <label className="label">Senha</label>
            <Link
              className="text-xs font-medium text-cyan-300 hover:text-cyan-200"
              to="/esqueci-senha"
            >
              Esqueci minha senha
            </Link>
          </div>
          <input
            className="field"
            type="password"
            autoComplete="current-password"
            {...register('password')}
          />
          {errors.password && (
            <p className="mt-1 text-xs text-red-300">
              {errors.password.message}
            </p>
          )}
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input
            type="checkbox"
            className="rounded border-slate-300 text-blue-600"
            {...register('keep')}
          />
          Manter conectado
        </label>
        {error && (
          <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
            {error}
          </p>
        )}
        <Button className="w-full" disabled={isSubmitting}>
          {isSubmitting ? 'Entrando...' : 'Entrar'}
        </Button>
      </form>
      <p className="mt-7 text-center text-sm text-slate-300">
        Ainda não tem conta?{' '}
        <Link
          className="font-semibold text-cyan-300 hover:text-cyan-200"
          to="/cadastro"
        >
          Criar conta
        </Link>
      </p>
    </AuthShell>
  )
}
