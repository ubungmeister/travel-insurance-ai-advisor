import type { PropsWithChildren } from 'react'

import { ChatSessionContext } from '../../hooks/chat/chat-session-context'
import { useChatSessionController } from '../../hooks/chat/use-chat-session-controller'

type Props = PropsWithChildren<{
  accountId: string
  target?: string
  draftEpoch?: number
  navigate: (path: string, replace?: boolean) => void
}>

function ChatSessionScope({ accountId, target, navigate, children }: Props) {
  const session = useChatSessionController(accountId, target, navigate)
  return (
    <ChatSessionContext.Provider value={{ ...session, target, navigate }}>
      {children}
    </ChatSessionContext.Provider>
  )
}

/**
 * Creates one controller for all chat consumers. Rekey the inner scope on
 * account, route or logout epoch changes so its local state cannot survive
 * that boundary. Draft storage and query-cache cleanup remain separate owners.
 */
export function ChatSessionProvider(props: Props) {
  const key = JSON.stringify([
    props.accountId,
    props.target ?? null,
    props.draftEpoch ?? 0,
  ])
  return <ChatSessionScope key={key} {...props} />
}
