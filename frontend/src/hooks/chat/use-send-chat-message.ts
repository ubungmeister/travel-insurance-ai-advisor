import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'

import { sendMessage } from '../../api'
import type { ChatRequest, ConversationDetail } from '../../api'
import { ApiError } from '../../lib/api-client'
import { chatAccountGeneration, registerChatSend } from '../../lib/chat-account-boundary'
import { chatKeys } from './chat-query-keys'
import { mergeChatTurn, validateChatConfirmation } from './chat-reconciliation'
import type { ChatRoute } from './chat-route'
import type { useChatDraft } from './use-chat-draft'

interface SendOptions {
  accountId: string
  route: ChatRoute
  draft: ReturnType<typeof useChatDraft>
  policyId?: number
  canSend: boolean
  canRetry: boolean
  navigate: (path: string, replace?: boolean) => void
  reload: () => void
}

/**
 * React Query owns POST status; tab storage owns recovery. Guard both entry
 * points offline, disable automatic retry/queueing, and gate every callback by
 * the account generation and active controller. Cache reset cannot cancel a
 * committed server write, so aborted sends keep their original recovery data.
 */
export function useSendChatMessage(options: SendOptions) {
  const { accountId, route, draft } = options
  const client = useQueryClient()
  const active = useRef<AbortController | null>(null)
  const [guardError, setGuardError] = useState('')
  const mutation = useMutation({
    mutationKey: chatKeys.send(accountId),
    mutationFn: (payload: ChatRequest) => sendMessage(payload, active.current!.signal, accountId),
    networkMode: 'always',
    retry: false,
    gcTime: 0,
  })

  useEffect(() => () => {
    const controller = active.current
    active.current = null
    controller?.abort()
  }, [])

  function online() {
    if (globalThis.navigator?.onLine !== false) return true
    setGuardError('You are offline. Nothing was sent or queued.')
    return false
  }

  async function submit(payload: ChatRequest) {
    if (active.current || !online()) return
    const controller = new AbortController()
    const generation = chatAccountGeneration()
    const release = registerChatSend(controller)
    active.current = controller
    setGuardError('')
    const timeout = setTimeout(() => controller.abort(), 15000)
    const isCurrent = () => active.current === controller && generation === chatAccountGeneration()
    try {
      const result = await mutation.mutateAsync(payload)
      controller.signal.throwIfAborted()
      if (!isCurrent()) return
      validateChatConfirmation(payload, result)
      const key = chatKeys.conversation(accountId, result.conversation_id)
      await client.cancelQueries({ queryKey: key, exact: true })
      if (!isCurrent()) return
      if (!draft.confirm(payload.request_id, result.conversation_id)) return
      client.setQueryData<ConversationDetail>(key, (current) => mergeChatTurn(current, result))
      if (!client.getQueryData(key) && route.kind === 'saved') {
        // Recovery can succeed despite an earlier detail-read failure. A turn
        // is not a full detail response, so reload this exact conversation.
        void client.invalidateQueries({ queryKey: key, exact: true }).catch(() => {})
      }
      // Refresh is best effort and never part of the send's success/failure.
      void client.invalidateQueries({ queryKey: chatKeys.history(accountId), exact: true }).catch(() => {})
      mutation.reset()
      if (route.kind === 'new') options.navigate(`/chat/${result.conversation_id}`, true)
    } catch (error) {
      if (!isCurrent()) return
      if (error instanceof ApiError && [404, 409, 422].includes(error.status)) {
        if (draft.reject(payload.request_id) && error.status === 404) options.reload()
      } else if (mutation.error !== error && !(error instanceof ApiError)) {
        // Validation or storage failure after a 200 is still unconfirmed.
        setGuardError('Send could not be confirmed. Retry the original message to recover it safely.')
      }
    } finally {
      clearTimeout(timeout)
      release()
      if (active.current === controller) active.current = null
    }
  }

  async function send() {
    const value = draft.getCurrent()
    if (active.current || value.pending || !options.canSend || !value.text.trim() || !online()) return
    if (typeof globalThis.crypto?.randomUUID !== 'function') {
      setGuardError('A secure browser context is required to send messages.')
      return
    }
    const base = { request_id: crypto.randomUUID(), message: value.text }
    const payload: ChatRequest | null = route.kind === 'new' && options.policyId !== undefined
      ? { ...base, policy_id: options.policyId }
      : route.kind === 'saved' ? { ...base, conversation_id: route.id } : null
    if (payload && draft.stage(payload)) await submit(payload)
  }

  async function retry() {
    const value = draft.getCurrent()
    const payload = value.pending
    const sameTarget = route.kind === 'new' ? payload?.policy_id !== undefined
      : route.kind === 'saved' && payload?.conversation_id === route.id
    if (!value.rejected && options.canRetry && payload && sameTarget && online()) await submit(payload)
  }

  const error = mutation.error
  const reauthenticate = !!draft.value.pending && error instanceof ApiError && error.status === 401
  const sendError = guardError || (reauthenticate
    ? 'Sign in to the same account, then retry the pending message.'
    : error && draft.value.pending && !draft.value.rejected ? 'Send could not be confirmed. Retry the original message to recover it safely.' : '')

  function resetSettled() {
    if (active.current) return
    mutation.reset()
    setGuardError('')
  }

  return { send, retry, sending: mutation.isPending, sendError, reauthenticate, resetSettled }
}
