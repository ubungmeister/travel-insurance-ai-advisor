import { useHealthCheck } from '../../hooks'

export function HealthStatus() {
  const { data, isLoading, isError } = useHealthCheck()

  const status = isLoading
    ? 'checking...'
    : isError
      ? 'unreachable'
      : data?.status

  return (
    <p>
      Backend status: <strong>{status}</strong>
    </p>
  )
}
