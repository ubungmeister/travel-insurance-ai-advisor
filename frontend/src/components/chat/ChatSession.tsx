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
      <p>Mock chat only — replies are not coverage advice. Messages are saved.</p>
      <ChatSessionStatus />
      <ChatPolicyPanel />
      <ChatMessages />
      <PendingSendRecovery />
      <ChatComposer />
    </>
  )
}
