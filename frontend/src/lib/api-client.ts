import { API_URL } from '../config/env'
import { supabase } from './supabase'

export class ApiError extends Error {
  constructor(readonly status: number) {
    super(`Request failed with status ${status}`)
  }
}

/**
 * Sends an API request using the current Supabase session. When a caller
 * supplies an account ID, it is a local guard, not a server parameter: reject
 * the request if the session changed while it was waiting for a token. Check
 * cancellation after retrieving the session so work from an old route is not
 * sent after navigation or logout. The backend still verifies ownership.
 */
export async function apiRequest<TResponse>(
  path: string,
  options?: RequestInit & { accountId?: string },
): Promise<TResponse> {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  options?.signal?.throwIfAborted()
  const { accountId, ...request } = options ?? {}
  if (accountId && session?.user.id !== accountId) throw new ApiError(401)

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(session ? { Authorization: `Bearer ${session.access_token}` } : {}),
    ...options?.headers,
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...request,
    headers,
  })

  if (!response.ok) {
    throw new ApiError(response.status)
  }

  const body = (await response.json()) as TResponse
  request.signal?.throwIfAborted()
  return body
}
