import { apiRequest } from '../../lib/api-client'

export interface HealthResponse {
  status: string
}

export function getHealth() {
  return apiRequest<HealthResponse>('/health')
}
