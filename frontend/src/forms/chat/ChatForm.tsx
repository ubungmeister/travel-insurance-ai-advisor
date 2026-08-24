import { useState } from 'react'

import { useSendMessage } from '../../hooks'

export function ChatForm() {
  const [message, setMessage] = useState('')
  const { mutate, data, isPending, isError } = useSendMessage()

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!message.trim()) return

    mutate(message)
  }

  const reply = isError ? 'Unable to reach the advisor.' : data?.reply

  return (
    <>
      <form onSubmit={handleSubmit}>
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask about your travel insurance"
        />

        <button type="submit" disabled={isPending}>
          {isPending ? 'Sending...' : 'Send'}
        </button>
      </form>

      {reply && <p>{reply}</p>}
    </>
  )
}
