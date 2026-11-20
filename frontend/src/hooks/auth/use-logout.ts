import { useMutation } from '@tanstack/react-query'

import { supabase } from '../../lib/supabase'
import { broadcastDraftLogout } from '../../lib/chat-drafts'
import { useAuthStore } from '../../store'

/**
 * Signs out explicitly and purges chat recovery across the account's tabs.
 * Capture the account before awaiting Supabase, since the auth subscription
 * can clear it before signOut returns. Session expiry follows a different path
 * and must not discard a pending send.
 */
export function useLogout() {
  return useMutation({
    mutationFn: async () => {
      const account = useAuthStore.getState().user?.id
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      broadcastDraftLogout(account)
    },
  })
}
