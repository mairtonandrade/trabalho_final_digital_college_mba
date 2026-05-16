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
  const segment = location.pathname.replace(/^\//, '')
  const roleFromPath = PATH_TO_ROLE[segment]

  useEffect(() => {
    if (!role && roleFromPath) setRole(roleFromPath)
  }, [role, roleFromPath, setRole])

  const effective = role || roleFromPath
  if (!effective) return <Navigate to="/" replace />
  if (effective !== allowed) return <Navigate to="/" replace />
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
