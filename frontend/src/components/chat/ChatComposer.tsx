import { ChatForm } from '../../forms/chat/ChatForm'
import { useChatSessionContext } from '../../hooks/chat/use-chat-session-context'

/**
 * Connects the generic form to the shared draft. A rejected send keeps the
 * composer editable so newer text can be cleared for restoration; unavailable
 * chats still disable sending.
 */
export function ChatComposer() {
  const chat = useChatSessionContext()
  const policy =
    chat.conversation?.selected_policy ??
    chat.policies.find((item) => item.policy_id === chat.policyId)
  const canSend =
    !chat.loading && !chat.loadError && !chat.unavailable && !!policy

  return (
    <ChatForm
      value={chat.draft}
      readOnly={chat.target === undefined || (chat.unavailable && !chat.rejected)}
      onChange={chat.editDraft}
      onSend={chat.send}
      disabled={!canSend || chat.sending || !!chat.recovery}
      isPending={chat.sending}
    />
  )
}
