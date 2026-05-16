import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { RoleProvider, useRole } from './context/RoleContext'
import Home from './pages/Home'
import Analista from './pages/Analista'
import Gerente from './pages/Gerente'
import Diretoria from './pages/Diretoria'
import Guia from './pages/Guia'

function ProtectedRoute({
  children,
  allowed,
}: {
  children: React.ReactNode
  allowed: 'analista' | 'gerente' | 'diretoria'
}) {
  const { role } = useRole()
  if (!role) return <Navigate to="/" replace />
  if (role !== allowed) return <Navigate to="/" replace />
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
    <RoleProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </RoleProvider>
  )
}
