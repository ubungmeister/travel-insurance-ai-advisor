import { useEffect, useRef, useState } from 'react'

import {
  getConversation,
  listConversations,
  listPolicies,
  sendMessage,
} from '../../api'
import type {
  ChatRequest,
  ConversationDetail,
  ConversationSummary,
  PolicySummary,
} from '../../api'
import { ApiError } from '../../lib/api-client'
import {
  confirmSend,
  draftStorage,
  readDraft,
  updateDraft,
} from '../../lib/chat-drafts'
import type { Draft } from '../../lib/chat-drafts'

/**
 * Owns chat state for one account and route. The home route resumes a tab
 * draft or the latest saved chat; an explicit saved URL never falls back to
 * another conversation. The new-chat route reads policies but does not write
 * to the server until the first send.
 *
 * The editable draft and its pending request are separate. Save the exact
 * payload and UUID before sending, never auto-send on mount, and reuse that
 * payload only for a manual retry. A confirmed response must not erase text
 * typed after submission. Keep the session keyed by account, route, and logout
 * epoch so navigation or logout cancels stale work instead of reusing it.
 */
export function useChatSession(
  accountId: string,
  target: string | undefined,
  navigate: (path: string, replace?: boolean) => void,
  storage = draftStorage(),
) {
  const isNew = target === 'new'
  const id = target && /^[1-9]\d*$/.test(target) ? Number(target) : NaN
  const validId = Number.isSafeInteger(id) && id <= 2147483647
  const slot = isNew ? 'new' : validId ? String(id) : 'unavailable'
  const [draft, setDraft] = useState(() => readDraft(accountId, slot, storage))
  const draftRef = useRef(draft)
  const [history, setHistory] = useState<ConversationSummary[]>([])
  const [historyVersion, setHistoryVersion] = useState(0)
  const [policies, setPolicies] = useState<PolicySummary[]>([])
  const [conversation, setConversation] = useState<ConversationDetail | null>(
    null,
  )
  const [loading, setLoading] = useState(true)
  const [unavailable, setUnavailable] = useState(false)
  const [loadError, setLoadError] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState('')
  const [reauthenticate, setReauthenticate] = useState(false)
  const sendingRef = useRef<AbortController | null>(null)
  const navigateRef = useRef(navigate)
  useEffect(() => {
    navigateRef.current = navigate
  }, [navigate])
  useEffect(
    () => () => {
      const activeSend = sendingRef.current
      sendingRef.current = null
      activeSend?.abort()
    },
    [],
  )

  useEffect(() => {
    if (target === undefined) return
    const controller = new AbortController()
    void listConversations(controller.signal, accountId).then(
      (items) => {
        if (!controller.signal.aborted) setHistory(items)
      },
      // History is ancillary; a failed refresh does not unconfirm a send.
      () => {},
    )
    return () => controller.abort()
  }, [accountId, attempt, historyVersion, target])

  useEffect(() => {
    const controller = new AbortController()
    const { signal } = controller
    setLoadError(false)
    setUnavailable(false)
    setLoading(true)

    async function load() {
      try {
        if (target === undefined) {
          const local = readDraft(accountId, 'new', storage)
          if (local.pending || local.text || local.policyId !== undefined) {
            if (!signal.aborted) navigateRef.current('/chat/new', true)
            return
          }
          const items = await listConversations(signal, accountId)
          if (!signal.aborted) {
            navigateRef.current(
              items.length ? `/chat/${items[0].conversation_id}` : '/chat/new',
              true,
            )
          }
          return
        }
        if (isNew) {
          const items = await listPolicies(signal, accountId)
          if (!signal.aborted) {
            setPolicies(items)
            const current = draftRef.current
            if (items.length === 1 && current.policyId !== items[0].policy_id) {
              try {
                const next = updateDraft(
                  accountId,
                  slot,
                  () => ({
                    ...current,
                    policyId: items[0].policy_id,
                  }),
                  storage,
                )
                draftRef.current = next
                setDraft(next)
              } catch {
                // The policy is still visible; Send requires writable storage.
              }
            }
          }
        } else if (validId) {
          const detail = await getConversation(id, signal, accountId)
          if (!signal.aborted) setConversation(detail)
        } else {
          setUnavailable(true)
        }
      } catch (error) {
        if (signal.aborted) return
        if (
          validId &&
          error instanceof ApiError &&
          [403, 404].includes(error.status)
        ) {
          setUnavailable(true)
          setConversation(null)
        } else {
          setLoadError(true)
          if (error instanceof ApiError && error.status === 401)
            setReauthenticate(true)
        }
      } finally {
        if (!signal.aborted) setLoading(false)
      }
    }
    void load()
    return () => controller.abort()
  }, [accountId, attempt, id, isNew, slot, storage, target, validId])

  function changeDraft(update: (value: Draft) => Draft) {
    try {
      const next = updateDraft(
        accountId,
        slot,
        () => update(draftRef.current),
        storage,
      )
      draftRef.current = next
      setDraft(next)
      return true
    } catch {
      setSendError(
        'Tab storage is unavailable. Sending is disabled until recovery data can be saved.',
      )
      return false
    }
  }

  function editDraft(text: string) {
    if (!isNew && !validId) return
    if (!changeDraft((current) => ({ ...current, text }))) {
      const next = { ...draftRef.current, text }
      draftRef.current = next
      setDraft(next)
    }
  }

  const policyId = policies.some(
    (policy) => policy.policy_id === draft.policyId,
  )
    ? draft.policyId
    : policies.length === 1
      ? policies[0].policy_id
      : undefined

  /**
   * Sends a payload already saved for recovery. A timeout leaves the outcome
   * uncertain, so retry must reuse the UUID. A definitive rejection instead
   * leaves the text available to restore or discard. Only a matching success
   * clears recovery and updates the transcript; merging by message ID makes
   * replay safe.
   */
  async function submit(payload: ChatRequest) {
    const controller = new AbortController()
    sendingRef.current = controller
    setSending(true)
    setSendError('')
    setReauthenticate(false)
    const timeout = setTimeout(() => controller.abort(), 15000)
    try {
      const result = await sendMessage(payload, controller.signal, accountId)
      controller.signal.throwIfAborted()
      if (
        !Number.isSafeInteger(result.conversation_id) ||
        result.conversation_id <= 0 ||
        (payload.conversation_id !== undefined &&
          result.conversation_id !== payload.conversation_id) ||
        !Array.isArray(result.messages)
      ) {
        throw new Error('Invalid chat confirmation')
      }
      if (
        !confirmSend(
          accountId,
          slot,
          payload.request_id,
          result.conversation_id,
          storage,
        )
      )
        return
      const next = readDraft(accountId, slot, storage)
      draftRef.current = next
      setDraft(next)
      if (isNew) {
        navigateRef.current(`/chat/${result.conversation_id}`, true)
      } else {
        setConversation((current) => {
          if (!current) return current
          const messages = new Map(
            current.messages.map((message) => [message.id, message]),
          )
          result.messages.forEach((message) =>
            messages.set(message.id, message),
          )
          return {
            ...current,
            messages: [...messages.values()].sort((a, b) => a.id - b.id),
          }
        })
        setHistoryVersion((version) => version + 1)
      }
    } catch (error) {
      if (sendingRef.current !== controller) return
      if (error instanceof ApiError && error.status === 401) {
        setReauthenticate(true)
        setSendError(
          'Sign in to the same account, then retry the pending message.',
        )
      } else if (
        error instanceof ApiError &&
        [404, 409, 422].includes(error.status)
      ) {
        if (
          readDraft(accountId, slot, storage).pending?.request_id ===
          payload.request_id
        ) {
          changeDraft((current) => ({ ...current, rejected: true }))
          if (error.status === 404) setAttempt((value) => value + 1)
        }
      } else {
        setSendError(
          'Send could not be confirmed. Retry the original message to recover it safely.',
        )
      }
    } finally {
      clearTimeout(timeout)
      if (sendingRef.current === controller) {
        sendingRef.current = null
        setSending(false)
      }
    }
  }

  function online() {
    if (globalThis.navigator?.onLine !== false) return true
    setSendError('You are offline. Nothing was sent or queued.')
    return false
  }

  async function send() {
    const current = draftRef.current
    if (
      sendingRef.current ||
      current.pending ||
      loading ||
      loadError ||
      unavailable ||
      !current.text.trim()
    )
      return
    if (!online()) return
    if (typeof globalThis.crypto?.randomUUID !== 'function') {
      setSendError('A secure browser context is required to send messages.')
      return
    }
    const base = { request_id: crypto.randomUUID(), message: current.text }
    const payload =
      isNew && policyId !== undefined
        ? { ...base, policy_id: policyId }
        : conversation?.selected_policy
          ? { ...base, conversation_id: conversation.conversation_id }
          : null
    if (
      payload &&
      changeDraft((value) => ({
        ...value,
        text: '',
        pending: payload,
        rejected: undefined,
      }))
    ) {
      await submit(payload)
    }
  }

  async function retry() {
    const { pending: payload, rejected } = draftRef.current
    const sameTarget = isNew
      ? payload?.policy_id !== undefined
      : payload?.conversation_id === id
    if (
      !sendingRef.current &&
      payload &&
      !rejected &&
      sameTarget &&
      !loading &&
      !unavailable &&
      online()
    ) {
      await submit(payload)
    }
  }

  function resolveRejected(action: 'restore' | 'discard') {
    const current = draftRef.current
    const pending = current.pending
    if (sendingRef.current || !current.rejected || !pending) return
    const stored = readDraft(accountId, slot, storage)
    if (!stored.rejected || stored.pending?.request_id !== pending.request_id)
      return
    // Keep the rejected text available until the user can restore it safely.
    if (action === 'restore' && (current.text || stored.text)) return
    if (
      changeDraft((value) => ({
        policyId: value.policyId,
        text: action === 'restore' ? pending.message : value.text,
      }))
    )
      setSendError('')
  }

  return {
    conversation,
    history,
    policies,
    policyId,
    loading,
    unavailable,
    loadError,
    sending,
    draft: draft.text,
    recovery: draft.pending,
    rejected: draft.rejected === true,
    sendError,
    reauthenticate,
    editDraft,
    send,
    retry,
    resolveRejected,
    reload: () => setAttempt((value) => value + 1),
    selectPolicy: (value: number) =>
      changeDraft((current) => ({ ...current, policyId: value })),
  }
}
