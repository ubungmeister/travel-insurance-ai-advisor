import { useCallback, useRef, useState } from 'react'

import type { ChatRequest } from '../../api'
import {
  confirmSend,
  draftStorage,
  readDraft,
  updateDraft,
} from '../../lib/chat-drafts'
import type { Draft } from '../../lib/chat-drafts'

/**
 * Owns the tab's editable text and immutable pending request. Synchronous refs
 * protect same-tick actions; confirmation carries the latest in-memory text
 * into receipt cleanup so a quota-failed edit is not replaced by stale storage.
 * It never sends or caches a transcript.
 */
export function useChatDraft(
  accountId: string,
  slot: string,
  storage = draftStorage(),
) {
  const [value, setValue] = useState(() => readDraft(accountId, slot, storage))
  const current = useRef(value)
  const [error, setError] = useState('')

  const change = useCallback(
    (update: (draft: Draft) => Draft) => {
      try {
        const next = updateDraft(
          accountId,
          slot,
          () => update(current.current),
          storage,
        )
        current.current = next
        setValue(next)
        setError('')
        return true
      } catch {
        setError(
          'Tab storage is unavailable. Sending is disabled until recovery data can be saved.',
        )
        return false
      }
    },
    [accountId, slot, storage],
  )

  function edit(text: string) {
    if (!change((draft) => ({ ...draft, text }))) {
      current.current = { ...current.current, text }
      setValue(current.current)
    }
  }

  const selectPolicy = useCallback(
    (policyId: number) => change((draft) => ({ ...draft, policyId })),
    [change],
  )

  function stage(payload: ChatRequest) {
    return change((draft) => ({
      ...draft,
      text: '',
      pending: payload,
      rejected: undefined,
    }))
  }

  function confirm(requestId: string, conversationId: number) {
    if (
      !confirmSend(
        accountId,
        slot,
        requestId,
        conversationId,
        storage,
        current.current,
      )
    )
      return false
    current.current = readDraft(accountId, slot, storage)
    setValue(current.current)
    setError('')
    return true
  }

  function reject(requestId: string) {
    if (readDraft(accountId, slot, storage).pending?.request_id !== requestId)
      return false
    return change((draft) => ({ ...draft, rejected: true }))
  }

  function resolveRejected(action: 'restore' | 'discard') {
    const draft = current.current
    const saved = readDraft(accountId, slot, storage)
    if (
      !draft.rejected ||
      !saved.rejected ||
      !draft.pending ||
      saved.pending?.request_id !== draft.pending.request_id
    )
      return
    if (action === 'restore' && (draft.text || saved.text)) return
    const message = draft.pending.message
    change((value) => ({
      policyId: value.policyId,
      text: action === 'restore' ? message : value.text,
    }))
  }

  return {
    value,
    error,
    getCurrent: () => current.current,
    edit,
    selectPolicy,
    stage,
    confirm,
    reject,
    resolveRejected,
  }
}
