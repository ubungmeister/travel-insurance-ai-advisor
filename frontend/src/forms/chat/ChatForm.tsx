interface ChatFormProps {
  value: string
  onChange: (value: string) => void
  disabled?: boolean
  readOnly?: boolean
  isPending?: boolean
  onSend: () => Promise<void>
}

export function ChatForm({
  value,
  onChange,
  disabled = false,
  readOnly = false,
  isPending = false,
  onSend,
}: ChatFormProps) {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!disabled && !isPending && value.trim()) void onSend()
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        aria-label="Message"
        maxLength={2000}
        readOnly={readOnly}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask about your travel insurance"
      />
      <button type="submit" disabled={disabled || isPending || !value.trim()}>
        {isPending ? 'Sending...' : 'Send'}
      </button>
    </form>
  )
}
