import { useChatSessionContext } from '../../hooks/chat/use-chat-session-context'
import { ChatTranscript } from './ChatTranscript'

export function ChatMessages() {
  const { conversation } = useChatSessionContext()
  return <ChatTranscript messages={conversation?.messages ?? []} />
}
