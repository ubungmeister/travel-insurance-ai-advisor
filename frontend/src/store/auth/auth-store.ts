import type { User } from '@supabase/supabase-js'
import { create } from 'zustand'

import { supabase } from '../../lib/supabase'
import { listenForDraftLogout, syncDraftAccount } from '../../lib/chat-drafts'
import { resetChatServerState } from '../../lib/chat-account-boundary'

export type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated'

interface AuthState {
  status: AuthStatus
  user: User | null
  draftEpoch: number
}

export const useAuthStore = create<AuthState>(() => ({
  status: 'checking',
  user: null,
  draftEpoch: 0,
}))

listenForDraftLogout(() => {
  resetChatServerState()
  // Remount the chat if the auth change event has not arrived yet, so
  // in-memory drafts cannot write the cleared data back to sessionStorage.
  useAuthStore.setState((state) => ({ draftEpoch: state.draftEpoch + 1 }))
})

// Fires immediately with the persisted session (if any), then on every sign-in/out/refresh
supabase.auth.onAuthStateChange((_event, session) => {
  // A null session can mean expiry; only a different authenticated account
  // or an explicit logout should purge recovery data.
  if (useAuthStore.getState().user?.id !== session?.user?.id) {
    resetChatServerState()
  }
  const cleared = session?.user
    ? syncDraftAccount(session.user.id, undefined, undefined, resetChatServerState)
    : false
  useAuthStore.setState((state) => ({
    status: session ? 'authenticated' : 'unauthenticated',
    user: session?.user ?? null,
    draftEpoch: state.draftEpoch + Number(cleared),
  }))
})
