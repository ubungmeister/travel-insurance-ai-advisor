import { Paper, Stack, Typography } from '@mui/material'
import type { ChatMessage } from '../../api'
import { chatMessageStyles } from './chat-styles'

export function ChatTranscript({ messages }: { messages: ChatMessage[] }) {
  return (
    <Stack
      component="ol"
      role="list"
      aria-label="Chat messages"
      aria-live="polite"
      spacing={1.5}
      sx={{ listStyle: 'none', m: 0, p: 0 }}
    >
      {messages.map((message) => {
        const isUser = message.role === 'USER'
        return (
          <Paper
            component="li"
            variant="outlined"
            key={message.id}
            sx={isUser ? chatMessageStyles.user : chatMessageStyles.assistant}
          >
            <Typography
              component="div"
              variant="caption"
              sx={{ fontWeight: 'bold' }}
            >
              {isUser ? 'You' : 'Mock assistant'}:
            </Typography>
            <Typography
              variant="body2"
              sx={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}
            >
              {message.content}
            </Typography>
          </Paper>
        )
      })}
    </Stack>
  )
}
