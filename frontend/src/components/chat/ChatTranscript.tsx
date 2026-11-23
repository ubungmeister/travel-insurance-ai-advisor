import { Paper, Stack, Typography } from '@mui/material'
import type { ChatMessage } from '../../api'

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
            sx={{
              alignSelf: isUser ? 'flex-end' : 'flex-start',
              bgcolor: isUser ? 'primary.dark' : 'background.paper',
              color: isUser ? 'primary.contrastText' : 'text.primary',
              maxWidth: '85%',
              minWidth: 0,
              borderRadius: 2,
              px: 1.5,
              py: 1,
            }}
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
