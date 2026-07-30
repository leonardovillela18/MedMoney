import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '@/context/AuthContext'
import { App } from '@/routes/App'
import { AppErrorBoundary } from '@/components/common/AppErrorBoundary'
import { NetworkStatus } from '@/components/common/NetworkStatus'
import { applyInitialPreferences } from '@/lib/preferences'
import '@/index.css'
import '@/styles/themes/light/theme.css'
import '@/styles/themes/dark/theme.css'

applyInitialPreferences()
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnReconnect: true,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
    mutations: { retry: 0 },
  },
})
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <NetworkStatus />
        <BrowserRouter>
          <AuthProvider>
            <App />
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </AppErrorBoundary>
  </StrictMode>
)
