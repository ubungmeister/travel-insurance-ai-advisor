import { apiRequest } from '../../lib/api-client'

export interface ChatMessage {
  id: number
  role: 'USER' | 'ASSISTANT'
  content: string
  created_at: string
}

export interface ChatResponse {
  conversation_id: number
  reply: string
  messages: ChatMessage[]
}

export type ChatRequest = Readonly<
  {
    request_id: string
    message: string
  } & (
    | { conversation_id: number; policy_id?: never }
    | { policy_id: number; conversation_id?: never }
  )
>

export function sendMessage(
  request: ChatRequest,
  signal?: AbortSignal,
  accountId?: string,
) {
  return apiRequest<ChatResponse>('/api/v1/chat', {
    method: 'POST',
    signal,
    accountId,
    body: JSON.stringify(request),
  })
}
