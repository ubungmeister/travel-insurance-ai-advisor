import { useChatSessionContext } from '../../hooks/conversation/use-chat-session-context'
import { ConversationHistory } from './ConversationHistory'

export function ChatHistory() {
  const { history, conversation, navigate } = useChatSessionContext()
  return (
    <ConversationHistory
      history={history}
      conversationId={conversation?.conversation_id}
      disabled={false}
      onSelect={(id) => navigate(`/chat/${id}`)}
      onNew={() => navigate('/chat/new')}
    />
  )
}
