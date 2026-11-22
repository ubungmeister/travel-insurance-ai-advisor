import { useEffect } from 'react'

import { ApiError } from '../../lib/api-client'
import { draftStorage } from '../../lib/chat-drafts'
import { chatRoute } from './chat-route'
import { useChatDraft } from './use-chat-draft'
import { useChatPolicies } from './use-chat-policies'
import { useConversation } from './use-conversation'
import { useConversationHistory } from './use-conversation-history'
import { useSendChatMessage } from './use-send-chat-message'

/**
 * Owns one scoped session's query, draft and send composition. Instantiate it
 * only in ChatSessionProvider; descendants consume the shared context rather
 * than creating independent draft refs or mutation observers.
 */
export function useChatSessionController(
  accountId: string,
  target: string | undefined,
  navigate: (path: string, replace?: boolean) => void,
  storage = draftStorage(),
) {
  const route = chatRoute(target)
  const draft = useChatDraft(accountId, route.slot, storage)
  const { selectPolicy } = draft
  const selectedPolicyId = draft.value.policyId
  const localDraft = !!(draft.value.pending || draft.value.text || draft.value.policyId !== undefined)
  const history = useConversationHistory(accountId, route.kind !== 'home' || !localDraft)
  const policies = useChatPolicies(accountId, route.kind === 'new')
  const detail = useConversation(accountId, route.kind === 'saved' ? route.id : undefined)
  const primary = route.kind === 'home' ? history : route.kind === 'new' ? policies : detail
  const unavailable = route.kind === 'unavailable' || (route.kind === 'saved' &&
    detail.error instanceof ApiError && [403, 404].includes(detail.error.status))
  const conversation = route.kind === 'saved' && !detail.isError ? detail.data ?? null : null
  const loading = !unavailable && !(route.kind === 'home' && localDraft) && (primary.isPending || primary.isFetching)
  const loadError = !unavailable && primary.isError
  const policyList = route.kind === 'new' ? policies.data ?? [] : []
  const policyId = policyList.some((policy) => policy.policy_id === draft.value.policyId)
    ? draft.value.policyId : policyList.length === 1 ? policyList[0].policy_id : undefined
  const autoPolicyId = route.kind === 'new' && policies.data?.length === 1
    ? policies.data[0].policy_id : undefined

  useEffect(() => {
    if (route.kind !== 'home') return
    if (localDraft) navigate('/chat/new', true)
    else if (history.isSuccess && !history.isFetching) navigate(history.data.length ? `/chat/${history.data[0].conversation_id}` : '/chat/new', true)
  }, [history.data, history.isFetching, history.isSuccess, localDraft, navigate, route.kind])

  useEffect(() => {
    if (policies.isSuccess && !policies.isFetching && autoPolicyId !== undefined && selectedPolicyId !== autoPolicyId) {
      selectPolicy(autoPolicyId)
    }
  }, [autoPolicyId, selectPolicy, selectedPolicyId, policies.isFetching, policies.isSuccess])

  const reload = () => {
    if (route.kind === 'unavailable') return
    void primary.refetch()
    if (primary !== history) void history.refetch()
  }
  const message = useSendChatMessage({
    accountId, route, draft, policyId, navigate, reload,
    canSend: !loading && !loadError && !unavailable &&
      (route.kind === 'new' ? policyId !== undefined : !!conversation?.selected_policy),
    canRetry: !loading && !unavailable,
  })

  function resolveRejected(action: 'restore' | 'discard') {
    draft.resolveRejected(action)
    if (!draft.getCurrent().pending) message.resetSettled()
  }

  return {
    conversation, history: history.data ?? [], policies: policyList, policyId,
    loading, unavailable, loadError, reload,
    draft: draft.value.text, recovery: draft.value.pending, rejected: draft.value.rejected === true,
    editDraft: draft.edit, selectPolicy, resolveRejected,
    ...message,
    sendError: draft.error || message.sendError,
    reauthenticate: message.reauthenticate || (loadError && primary.error instanceof ApiError && primary.error.status === 401),
  }
}
