import type { ChatRequest } from '../api/chat/chat-api'

/**
 * The tab's editable text and selected policy, plus a separate pending send.
 * Once submitted, the pending payload must stay unchanged for idempotent retry.
 * A rejection flag belongs to that pending send, not to the editable text.
 */
export interface Draft {
  text: string
  policyId?: number
  pending?: ChatRequest
  rejected?: boolean
}

const prefix = 'ai-advisor:chat-drafts:'
const accountKey = `${prefix}account`
const logoutGenerationKey = `${prefix}logout-generation`
const key = (account: string) => `${prefix}user:${account}`
const logoutKey = (account: string) => `${prefix}logout:${account}`

export function draftStorage() {
  try {
    return globalThis.sessionStorage
  } catch {
    return undefined
  }
}

export function clearChatDrafts(storage = draftStorage()) {
  if (!storage) return
  try {
    for (let i = storage.length - 1; i >= 0; i--) {
      const name = storage.key(i)
      if (name?.startsWith(prefix)) storage.removeItem(name)
    }
  } catch {
    // Storage may be disabled by the browser.
  }
}

function sharedStorage() {
  try {
    return globalThis.localStorage
  } catch {
    return undefined
  }
}

/**
 * Clears a tab's drafts when its account changes or when it missed an explicit
 * logout in another tab. The shared store holds only a logout marker; drafts,
 * including pending payloads, stay in sessionStorage. Callers must not use a
 * missing session alone as a signal to purge, since it can mean token expiry.
 * Returns whether data was cleared so the UI can discard stale in-memory state.
 */
export function syncDraftAccount(
  account: string,
  storage = draftStorage(),
  shared = sharedStorage(),
  beforeClear?: () => void,
) {
  if (!storage) return false
  try {
    const previous = storage.getItem(logoutGenerationKey) ?? ''
    let generation = previous
    try {
      if (shared) generation = shared.getItem(logoutKey(account)) ?? ''
    } catch {
      // Blocking shared storage must not prevent account-change cleanup.
    }
    if (storage.getItem(accountKey) !== account || previous !== generation) {
      beforeClear?.()
      clearChatDrafts(storage)
      storage.setItem(accountKey, account)
      storage.setItem(logoutGenerationKey, generation)
      return true
    }
  } catch {
    // Sending will fail closed if a recovery record cannot be saved.
  }
  return false
}

export function broadcastDraftLogout(
  account: string | undefined,
  storage = draftStorage(),
  shared = sharedStorage(),
) {
  clearChatDrafts(storage)
  if (!account || !shared) return
  try {
    // Only an opaque logout generation is shared. Drafts remain tab-local.
    shared.setItem(logoutKey(account), `${Date.now()}:${Math.random()}`)
  } catch {
    // Local drafts are still cleared if shared browser storage is disabled.
  }
}

export function listenForDraftLogout(
  beforeClear: () => void,
  storage = draftStorage(),
  shared = sharedStorage(),
  events: EventTarget | undefined = typeof window === 'undefined'
    ? undefined
    : window,
) {
  function onStorage(event: Event) {
    const { key: changedKey, storageArea } = event as StorageEvent
    if (
      !storage ||
      !shared ||
      storageArea !== shared ||
      !changedKey?.startsWith(`${prefix}logout:`)
    )
      return
    let account: string | null
    try {
      account = storage.getItem(accountKey)
    } catch {
      return
    }
    if (account && changedKey === logoutKey(account)) {
      syncDraftAccount(account, storage, shared, beforeClear)
    }
  }
  events?.addEventListener('storage', onStorage)
  return () => events?.removeEventListener('storage', onStorage)
}

function readAll(account: string, storage?: Storage): Record<string, Draft> {
  const value = storage?.getItem(key(account))
  return value ? JSON.parse(value) : {}
}

export function readDraft(
  account: string,
  slot: string,
  storage = draftStorage(),
): Draft {
  try {
    return readAll(account, storage)[slot] ?? { text: '' }
  } catch {
    return { text: '' }
  }
}

export function updateDraft(
  account: string,
  slot: string,
  update: (draft: Draft) => Draft,
  storage = draftStorage(),
) {
  if (!storage) throw new Error('Tab storage is unavailable')
  const drafts = readAll(account, storage)
  const next = update(drafts[slot] ?? { text: '' })
  drafts[slot] = next
  storage.setItem(key(account), JSON.stringify(drafts))
  return next
}

/**
 * Clears a confirmed request only if it still matches the pending request in
 * the tab. Read the stored record again so newer typing is not lost. First-send
 * confirmation can move that text to the saved conversation's draft, but must
 * keep both drafts if text already exists at the destination.
 */
export function confirmSend(
  account: string,
  slot: string,
  requestId: string,
  conversationId: number,
  storage = draftStorage(),
) {
  if (!storage) return false
  const drafts = readAll(account, storage)
  const current = drafts[slot]
  if (current?.pending?.request_id !== requestId) return false
  const destination = String(conversationId)
  if (slot === 'new') {
    const saved = drafts[destination]
    if (current.text && !saved?.text) {
      drafts[destination] = { ...saved, text: current.text }
    }
    if (current.text && saved?.text) {
      drafts[slot] = { text: current.text, policyId: current.policyId }
    } else {
      delete drafts[slot]
    }
  } else {
    drafts[slot] = { text: current.text }
  }
  storage.setItem(key(account), JSON.stringify(drafts))
  return true
}
