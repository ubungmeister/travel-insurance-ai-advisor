import { createContext } from 'react'

import type { useChatSessionController } from './use-chat-session-controller'

export type ChatSessionContextValue = ReturnType<
  typeof useChatSessionController
> & {
  target?: string
  navigate: (path: string, replace?: boolean) => void
}

export const ChatSessionContext = createContext<ChatSessionContextValue | null>(
  null,
)
