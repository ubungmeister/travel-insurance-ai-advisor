import { useContext } from 'react'

import { ChatSessionContext } from './chat-session-context'

/** Reads the existing session; never instantiates another draft/send owner. */
export function useChatSessionContext() {
  const session = useContext(ChatSessionContext)
  if (!session) {
    throw new Error('useChatSessionContext requires ChatSessionProvider')
  }
  return session
}
