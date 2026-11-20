import type { ConversationSummary } from '../../api'

interface ConversationHistoryProps {
  history: ConversationSummary[]
  conversationId?: number
  disabled: boolean
  onSelect: (id: number) => void
  onNew: () => void
}

export function ConversationHistory({
  history,
  conversationId,
  disabled,
  onSelect,
  onNew,
}: ConversationHistoryProps) {
  return (
    <nav aria-label="Conversation history">
      <label htmlFor="conversation-history">Conversation history</label>{' '}
      <select
        id="conversation-history"
        value={conversationId ?? ''}
        disabled={disabled || history.length === 0}
        onChange={(event) => onSelect(Number(event.target.value))}
      >
        <option value="" disabled>
          Select a conversation
        </option>
        {history.map((item) => (
          <option key={item.conversation_id} value={item.conversation_id}>
            #{item.conversation_id} ·{' '}
            {item.selected_policy?.policy_number ?? 'No policy'} ·{' '}
            {item.last_activity_at}
          </option>
        ))}
      </select>{' '}
      <button type="button" disabled={disabled} onClick={onNew}>
        New chat
      </button>
    </nav>
  )
}
