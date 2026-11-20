import { apiRequest } from '../../lib/api-client'
import type { ChatMessage } from '../chat/chat-api'

export interface PolicySummary {
  policy_id: number
  policy_number: string
  plan_name: string
  plan_version: number
  territory: 'CZECH_REPUBLIC' | 'EUROPE' | 'WORLD'
  trip_purpose: 'VACATION' | 'WORK_MANUAL' | 'WORK_NON_MANUAL'
  sport_category: 'RECREATIONAL' | 'WINTER' | 'RISKY'
  start_date: string
  end_date: string
  status: 'ISSUED' | 'CANCELLED'
}

export type ConversationCreateResponse =
  | {
      status: 'ready'
      conversation_id: number
      selected_policy: PolicySummary
      policy_choices: []
    }
  | {
      status: 'no_policies' | 'selection_required'
      conversation_id: null
      selected_policy: null
      policy_choices: PolicySummary[]
    }

export function createConversation(policyId?: number, signal?: AbortSignal) {
  return apiRequest<ConversationCreateResponse>('/api/v1/conversations', {
    method: 'POST',
    signal,
    body: JSON.stringify(policyId === undefined ? {} : { policy_id: policyId }),
  })
}

export interface ConversationSummary {
  conversation_id: number
  selected_policy: PolicySummary | null
  created_at: string
  last_activity_at: string
}

export interface ConversationDetail {
  conversation_id: number
  selected_policy: PolicySummary | null
  created_at: string
  messages: ChatMessage[]
}

export function listConversations(signal?: AbortSignal, accountId?: string) {
  return apiRequest<ConversationSummary[]>('/api/v1/conversations', {
    signal,
    accountId,
    cache: 'no-store',
  })
}

export function getConversation(
  id: number,
  signal?: AbortSignal,
  accountId?: string,
) {
  return apiRequest<ConversationDetail>(`/api/v1/conversations/${id}`, {
    signal,
    accountId,
    cache: 'no-store',
  })
}

export function listPolicies(signal?: AbortSignal, accountId?: string) {
  return apiRequest<PolicySummary[]>('/api/v1/policies', {
    signal,
    accountId,
    cache: 'no-store',
  })
}
