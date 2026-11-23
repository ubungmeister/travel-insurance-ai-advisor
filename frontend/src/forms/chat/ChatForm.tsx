import { Button, Stack, TextField } from '@mui/material'

interface ChatFormProps {
  value: string
  onChange: (value: string) => void
  disabled?: boolean
  readOnly?: boolean
  isPending?: boolean
  onSend: () => Promise<void>
}

/** Keeps draft editing separate from the send lock so later typing is preserved. */
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
    <Stack component="form" direction="row" spacing={1} onSubmit={handleSubmit}>
      <TextField
        fullWidth
        size="small"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask about your travel insurance"
        slotProps={{
          input: { readOnly },
          htmlInput: { 'aria-label': 'Message', maxLength: 2000 },
        }}
      />
      <Button
        type="submit"
        variant="contained"
        disabled={disabled || isPending || !value.trim()}
      >
        {isPending ? 'Sending...' : 'Send'}
      </Button>
    </Stack>
  )
}
