import { Box, Stack, Typography } from '@mui/material'
import { ChatComposer } from './ChatComposer'
import { ChatHistory } from './ChatHistory'
import { ChatMessages } from './ChatMessages'
import { ChatPolicyPanel } from './ChatPolicyPanel'
import { ChatSessionStatus } from './ChatSessionStatus'
import { PendingSendRecovery } from './PendingSendRecovery'
import { chatSessionStyles } from './chat-styles'

/** Lays out the shared session without taking ownership of any chat state. */
export function ChatSession() {
  return (
    <Box sx={chatSessionStyles.layout}>
      <Box
        component="aside"
        aria-label="Chat history"
        sx={chatSessionStyles.history}
      >
        <ChatHistory />
      </Box>
      <Box
        component="main"
        sx={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}
      >
        <Box
          role="region"
          aria-label="Transcript"
          tabIndex={0}
          sx={chatSessionStyles.transcript}
        >
          <Box sx={{ maxWidth: '50rem', mx: 'auto' }}>
            <ChatMessages />
          </Box>
        </Box>
        <Box sx={chatSessionStyles.controls}>
          <Stack
            spacing={1.5}
            sx={{ maxWidth: '50rem', mx: 'auto', overflowWrap: 'anywhere' }}
          >
            <Typography variant="caption" color="text.secondary">
              Mock chat only — replies are not coverage advice. Messages are
              saved.
            </Typography>
            <ChatSessionStatus /> //TODO: Implement actual session status handling
            <PendingSendRecovery /> //TODO: Implement actual pending send recovery handling
            <ChatPolicyPanel />
            <ChatComposer />
          </Stack>
        </Box>
      </Box>
    </Box>
  )
}
