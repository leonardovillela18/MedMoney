import { Link, useSearchParams } from 'react-router-dom'
import { useState } from 'react'
import { AuthShell } from './AuthShell'
import { Button } from '@/components/ui/Button'
import { authService } from '@/services/auth'
export function ForgotPasswordPage() {
  const [email, setEmail] = useState(''),
    [sent, setSent] = useState(false),
    [error, setError] = useState('')
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await authService.forgot(email)
      setSent(true)
    } catch {
      setError('Não foi possível enviar o e-mail agora.')
    }
  }
  return (
    <AuthShell
      title="Recuperar senha"
      subtitle="Enviaremos um link seguro para o seu e-mail."
    >
      {sent ? (
        <p className="mt-8 rounded-lg bg-green-50 p-4 text-sm text-green-700">
          Se houver uma conta com este e-mail, você receberá as instruções em
          breve.
        </p>
      ) : (
        <form onSubmit={submit} className="mt-8 space-y-5">
          <div>
            <label className="label">E-mail</label>
            <input
              className="field"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button className="w-full">Enviar instruções</Button>
        </form>
      )}
      <Link
        className="mt-6 block text-center text-sm font-medium text-blue-600"
        to="/login"
      >
        Voltar para entrar
      </Link>
    </AuthShell>
  )
}
export function ResetPasswordPage() {
  const [params] = useSearchParams(),
    [password, setPassword] = useState(''),
    [confirmation, setConfirmation] = useState(''),
    [message, setMessage] = useState(''),
    [success, setSuccess] = useState(false)
  const token = params.get('token')
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirmation) {
      setMessage('As senhas precisam ser iguais.')
      return
    }
    try {
      await authService.reset(token ?? '', password)
      setSuccess(true)
      setMessage('Senha alterada com sucesso. Faça login novamente.')
    } catch {
      setMessage('Não foi possível redefinir sua senha. Solicite um novo link.')
    }
  }
  return (
    <AuthShell
      title="Nova senha"
      subtitle="Escolha uma senha forte para sua conta."
    >
      {!token ? (
        <div className="mt-8">
          <p className="rounded-lg bg-amber-50 p-4 text-sm text-amber-800">
            Link de redefinição inválido.
          </p>
          <Link
            className="mt-5 block text-center font-medium text-blue-600"
            to="/esqueci-senha"
          >
            Solicitar novo link
          </Link>
        </div>
      ) : success ? (
        <div className="mt-8">
          <p className="rounded-lg bg-green-50 p-4 text-sm text-green-700">
            {message}
          </p>
          <Link
            className="mt-5 block text-center font-medium text-blue-600"
            to="/login"
          >
            Ir para login
          </Link>
        </div>
      ) : (
        <form onSubmit={submit} className="mt-8 space-y-5">
          <div>
            <label className="label">Nova senha</label>
            <input
              className="field"
              type="password"
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="label">Confirmar nova senha</label>
            <input
              className="field"
              type="password"
              minLength={8}
              value={confirmation}
              onChange={(e) => setConfirmation(e.target.value)}
              required
            />
          </div>
          <p className="text-xs text-slate-500">
            Use pelo menos 8 caracteres, uma letra maiúscula, um número e um
            caractere especial.
          </p>
          {message && <p className="text-sm text-slate-600">{message}</p>}
          <Button className="w-full">Redefinir senha</Button>
        </form>
      )}
    </AuthShell>
  )
}
