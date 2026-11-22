import { ChatForm } from '../../forms/chat/ChatForm'
import { useChatSessionContext } from '../../hooks/conversation/use-chat-session-context'

/** Connects the generic controlled form to the one shared session draft. */
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
      readOnly={chat.unavailable || chat.target === undefined}
      onChange={chat.editDraft}
      onSend={chat.send}
      disabled={!canSend || chat.sending || !!chat.recovery}
      isPending={chat.sending}
    />
  )
}
