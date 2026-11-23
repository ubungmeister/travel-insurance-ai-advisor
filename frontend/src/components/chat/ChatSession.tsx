import { Box, Stack, Typography } from '@mui/material'
import { ChatComposer } from './ChatComposer'
import { ChatHistory } from './ChatHistory'
import { ChatMessages } from './ChatMessages'
import { ChatPolicyPanel } from './ChatPolicyPanel'
import { ChatSessionStatus } from './ChatSessionStatus'
import { PendingSendRecovery } from './PendingSendRecovery'

/** Lays out the shared session without taking ownership of any chat state. */
export function ChatSession() {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: {
          xs: 'minmax(0, 1fr)',
          md: '17rem minmax(0, 1fr)',
        },
        gridTemplateRows: { md: 'minmax(0, 1fr)' },
        flex: 1,
        minHeight: 0,
      }}
    >
      <Box
        component="aside"
        aria-label="Chat history"
        sx={{
          overflowY: 'auto',
          maxHeight: { xs: '30dvh', md: 'none' },
          borderRight: { md: 1 },
          borderBottom: { xs: 1, md: 0 },
          borderColor: 'divider',
          bgcolor: 'background.paper',
          p: 2,
        }}
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
          sx={{
            flex: 1,
            minHeight: { xs: 120, md: 0 },
            overflowY: 'auto',
            p: { xs: 2, md: 3 },
          }}
        >
          <Box sx={{ maxWidth: '50rem', mx: 'auto' }}>
            <ChatMessages />
          </Box>
        </Box>
        <Box
          sx={{
            // Long recovery text or policy lists must not crowd out the transcript.
            maxHeight: { md: '65%' },
            overflowY: 'auto',
            borderTop: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
            px: { xs: 2, md: 3 },
            py: 2,
          }}
        >
          <Stack
            spacing={1.5}
            sx={{ maxWidth: '50rem', mx: 'auto', overflowWrap: 'anywhere' }}
          >
            <Typography variant="caption" color="text.secondary">
              Mock chat only — replies are not coverage advice. Messages are
              saved.
            </Typography>
            <ChatSessionStatus />
            <PendingSendRecovery />
            <ChatPolicyPanel />
            <ChatComposer />
          </Stack>
        </Box>
      </Box>
    </Box>
  )
}
