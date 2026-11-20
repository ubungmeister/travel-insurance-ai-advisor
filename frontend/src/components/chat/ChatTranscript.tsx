import type { ChatMessage } from '../../api'

export function ChatTranscript({ messages }: { messages: ChatMessage[] }) {
  return (
    <ol aria-label="Chat messages" aria-live="polite">
      {messages.map((message) => (
        <li key={message.id}>
          <strong>
            {message.role === 'USER' ? 'You' : 'Mock assistant'}:{' '}
          </strong>
          <span style={{ whiteSpace: 'pre-wrap' }}>{message.content}</span>
        </li>
      ))}
    </ol>
  )
}
