import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { authService } from '@/services/auth'
import { idleTimeoutMs, lastActivity, recordActivity } from '@/lib/authActivity'

export function IdleSessionManager({
  active,
  logout,
}: {
  active: boolean
  logout: (reason?: 'idle') => Promise<void>
}) {
  const [remaining, setRemaining] = useState<number | null>(null)
  useEffect(() => {
    if (!active) {
      setRemaining(null)
      return
    }
    if (!localStorage.getItem('crmoney_last_activity')) recordActivity()
    let lastRecorded = 0
    const activity = () => {
      if (Date.now() - lastRecorded > 1000) {
        lastRecorded = Date.now()
        recordActivity()
        setRemaining(null)
      }
    }
    const events: (keyof WindowEventMap)[] = [
      'click',
      'keydown',
      'touchstart',
      'popstate',
    ]
    events.forEach((event) =>
      window.addEventListener(event, activity, { passive: true })
    )
    const timer = window.setInterval(() => {
      const milliseconds = idleTimeoutMs - (Date.now() - lastActivity())
      if (milliseconds <= 0) void logout('idle')
      else
        setRemaining(
          milliseconds <= 60_000 ? Math.ceil(milliseconds / 1000) : null
        )
    }, 1000)
    return () => {
      events.forEach((event) => window.removeEventListener(event, activity))
      window.clearInterval(timer)
    }
  }, [active, logout])
  if (remaining === null) return null
  return (
    <div className="fixed inset-0 z-[100] grid place-items-center bg-slate-900/50 p-4">
      <section
        role="alertdialog"
        aria-modal="true"
        className="card w-full max-w-md p-6"
      >
        <h2 className="text-lg font-semibold">
          Sua sessão será encerrada por inatividade
        </h2>
        <p className="mt-2 text-sm text-slate-600">
          Saída automática em {remaining} segundo{remaining === 1 ? '' : 's'}.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Button
            type="button"
            onClick={async () => {
              recordActivity()
              await authService.me()
              setRemaining(null)
            }}
          >
            Continuar conectado
          </Button>
          <Button
            type="button"
            className="bg-slate-700"
            onClick={() => void logout('idle')}
          >
            Sair agora
          </Button>
        </div>
      </section>
    </div>
  )
}
