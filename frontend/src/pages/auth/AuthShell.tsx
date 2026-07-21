type AuthShellProps = {
  title: string
  subtitle: string
  children: React.ReactNode
  darkForm?: boolean
}

export function AuthShell({ title, subtitle, children, darkForm = false }: AuthShellProps) {
  return <main className="min-h-screen bg-slate-100 p-4 sm:p-8">
    <div className="mx-auto grid min-h-[calc(100vh-2rem)] max-w-6xl overflow-hidden rounded-2xl border bg-white shadow-xl sm:min-h-[calc(100vh-4rem)] lg:grid-cols-[1.08fr_.92fr]">
      <section className="hidden bg-white p-12 lg:flex lg:flex-col">
        <div className="flex flex-1 flex-col items-center justify-center text-center">
          <img src="/img/logo_vazado.png" alt="MedFinance" className="w-full max-w-[29rem] object-contain" />
          <div className="mt-14 max-w-md">
            <p className="text-4xl font-semibold leading-tight text-slate-900">Seu financeiro,<br />mais tranquilo.</p>
            <p className="mt-5 text-slate-500">Clareza para que você foque no que importa: cuidar das pessoas.</p>
          </div>
        </div>
        <p className="text-sm text-slate-400">Feito para médicos PJ.</p>
      </section>

      <section className={`flex items-center justify-center p-6 sm:p-12 ${darkForm ? 'bg-slate-950' : 'bg-white'}`}>
        <div className={`w-full max-w-sm ${darkForm ? 'auth-dark' : ''}`}>
          <div className="mb-9 w-fit rounded-xl bg-white px-4 py-3 shadow-sm lg:hidden">
            <img src="/img/logo_vazado.png" alt="MedFinance" className="h-auto w-52" />
          </div>
          <h1 className={`text-2xl font-bold ${darkForm ? 'text-white' : 'text-slate-900'}`}>{title}</h1>
          <p className={`mt-2 text-sm ${darkForm ? 'text-slate-300' : 'text-slate-500'}`}>{subtitle}</p>
          {children}
        </div>
      </section>
    </div>
  </main>
}
