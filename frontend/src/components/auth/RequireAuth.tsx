import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuthStore } from '../../store'

export function RequireAuth() {
  const status = useAuthStore((state) => state.status)
  const location = useLocation()

  if (status === 'checking') return <p>Loading...</p>

  if (status === 'unauthenticated') {
    return (
      <Navigate to="/login" replace state={{ returnTo: location.pathname }} />
    )
  }

  return <Outlet />
}
