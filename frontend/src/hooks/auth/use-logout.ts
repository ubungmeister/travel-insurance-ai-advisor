import { useMutation } from '@tanstack/react-query'

import { supabase } from '../../lib/supabase'
import { broadcastDraftLogout } from '../../lib/chat-drafts'
import { useAuthStore } from '../../store'
import { resetChatServerState } from '../../lib/chat-account-boundary'

/**
 * Signs out explicitly and purges chat recovery across the account's tabs.
 * Capture the account before awaiting Supabase, since the auth subscription
 * can clear it before signOut returns. Session expiry follows a different path
 * and must not discard a pending send.
 */
export function useLogout() {
  return useMutation({
    mutationFn: async () => {
      const previous = useAuthStore.getState()
      // Invalidate/abort before hiding the session or clearing draft storage.
      resetChatServerState()
      useAuthStore.setState({ status: 'checking' })
      try {
        const { error } = await supabase.auth.signOut()
        if (error) throw error
        broadcastDraftLogout(previous.user?.id)
      } catch (error) {
        useAuthStore.setState({ status: previous.status, user: previous.user })
        throw error
      }
    },
  })
}
