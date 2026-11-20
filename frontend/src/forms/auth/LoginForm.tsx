import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { useLogin } from '../../hooks'

export function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  const requestedPath: unknown = useLocation().state?.returnTo
  const returnTo =
    typeof requestedPath === 'string' &&
    /^\/chat\/[^/\\?#]+$/.test(requestedPath)
      ? requestedPath
      : '/'
  const { mutate, isPending, isError, error } = useLogin()

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!email.trim() || !password) return

    mutate(
      { email, password },
      { onSuccess: () => navigate(returnTo, { replace: true }) },
    )
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        placeholder="Email"
        autoComplete="email"
      />

      <input
        type="password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        placeholder="Password"
        autoComplete="current-password"
      />

      <button type="submit" disabled={isPending}>
        {isPending ? 'Signing in...' : 'Sign in'}
      </button>

      {isError && (
        <p>{error instanceof Error ? error.message : 'Unable to sign in.'}</p>
      )}
    </form>
  )
}
