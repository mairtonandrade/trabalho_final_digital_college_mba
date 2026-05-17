import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import { RoleProvider, useRole, type Role } from './context/RoleContext'
import Home from './pages/Home'
import Analista from './pages/Analista'
import Gerente from './pages/Gerente'
import Diretoria from './pages/Diretoria'
import Guia from './pages/Guia'

const PATH_TO_ROLE: Record<string, Role> = {
  analista: 'analista',
  gerente: 'gerente',
  diretoria: 'diretoria',
}

function ProtectedRoute({
  children,
  allowed,
}: {
  children: React.ReactNode
  allowed: 'analista' | 'gerente' | 'diretoria'
}) {
  const { role, setRole } = useRole()
  const location = useLocation()
  const segment = location.pathname.replace(/^\//, '').split('/')[0] ?? ''
  const pathRole = PATH_TO_ROLE[segment]

  // URL do painel tem prioridade (links diretos, F5 e deploy Netlify)
  useEffect(() => {
    if (pathRole === allowed) setRole(allowed)
  }, [pathRole, allowed, setRole])

  if (pathRole === allowed) return <>{children}</>

  if (!role) return <Navigate to="/" replace state={{ from: location }} />
  if (role !== allowed) return <Navigate to={`/${role}`} replace />
  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/guia" element={<Guia />} />
      <Route
        path="/analista"
        element={
          <ProtectedRoute allowed="analista">
            <Analista />
          </ProtectedRoute>
        }
      />
      <Route
        path="/gerente"
        element={
          <ProtectedRoute allowed="gerente">
            <Gerente />
          </ProtectedRoute>
        }
      />
      <Route
        path="/diretoria"
        element={
          <ProtectedRoute allowed="diretoria">
            <Diretoria />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <RoleProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </RoleProvider>
    </ErrorBoundary>
  )
}
