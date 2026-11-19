import { apiRequest } from '../../lib/api-client'

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

export function createConversation(policyId?: number) {
  return apiRequest<ConversationCreateResponse>('/api/v1/conversations', {
    method: 'POST',
    body: JSON.stringify(policyId === undefined ? {} : { policy_id: policyId }),
  })
}
