import { Navigate, Outlet } from 'react-router-dom'

import { useAuthStore } from '../../store'

export function RequireAuth() {
  const status = useAuthStore((state) => state.status)

  if (status === 'checking') return <p>Loading...</p>

  if (status === 'unauthenticated') return <Navigate to="/login" replace />

  return <Outlet />
}
