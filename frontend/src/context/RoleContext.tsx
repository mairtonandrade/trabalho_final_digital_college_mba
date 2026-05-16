import { createContext, useContext, useState, type ReactNode } from 'react'

export type Role = 'analista' | 'gerente' | 'diretoria' | null

const RoleContext = createContext<{
  role: Role
  setRole: (r: Role) => void
}>({ role: null, setRole: () => {} })

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRoleState] = useState<Role>(() => {
    const saved = localStorage.getItem('mba_role')
    return (saved as Role) || null
  })

  const setRole = (r: Role) => {
    if (r) localStorage.setItem('mba_role', r)
    else localStorage.removeItem('mba_role')
    setRoleState(r)
  }

  return (
    <RoleContext.Provider value={{ role, setRole }}>{children}</RoleContext.Provider>
  )
}

export const useRole = () => useContext(RoleContext)
