import { ChatComposer } from './ChatComposer'
import { ChatHistory } from './ChatHistory'
import { ChatMessages } from './ChatMessages'
import { ChatPolicyPanel } from './ChatPolicyPanel'
import { ChatSessionStatus } from './ChatSessionStatus'
import { PendingSendRecovery } from './PendingSendRecovery'

export function ChatSession() {
  return (
    <>
      <ChatHistory />
      <ChatSessionStatus /> //TODO: remove later PR
      <ChatPolicyPanel />
      <ChatMessages />
      <PendingSendRecovery /> //TODO: remove later PR, React query will handle
      retries
      <ChatComposer />
    </>
  )
}
