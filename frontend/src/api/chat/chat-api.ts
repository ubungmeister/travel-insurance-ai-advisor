import { apiRequest } from '../../lib/api-client'

export interface ChatResponse {
  reply: string
}

export function sendMessage(message: string) {
  return apiRequest<ChatResponse>('/api/v1/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}
