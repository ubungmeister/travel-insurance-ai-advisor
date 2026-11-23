import { useChatSessionContext } from '../../hooks/conversation/use-chat-session-context'
import { ChatTranscript } from './ChatTranscript'

export function ChatMessages() {
  const { conversation } = useChatSessionContext()
  return <ChatTranscript messages={conversation?.messages ?? []} />
}
