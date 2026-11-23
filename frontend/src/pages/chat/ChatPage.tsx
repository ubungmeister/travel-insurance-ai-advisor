import { Box, Stack, Typography } from '@mui/material'
import {
  ChatSession,
  ChatSessionProvider,
  HealthStatus,
  LogoutButton,
} from '../../components'
import { useAuthStore } from '../../store'
import { useNavigate, useParams } from 'react-router-dom'
import type { SxProps, Theme } from '@mui/material/styles'

const chatPageStyles = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100dvh',
    height: { md: '100dvh' },
    bgcolor: 'background.default',
  },
  header: {
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: 1,
    flexShrink: 0,
    px: { xs: 2, md: 3 },
    py: 1,
    borderBottom: 1,
    borderColor: 'divider',
    bgcolor: 'background.paper',
  },
  headerActions: {
    alignItems: 'center',
    typography: 'body2',
    '& p': { m: 0, color: 'text.secondary' },
  },
} as const satisfies Record<string, SxProps<Theme>>

export function ChatPage() {
  const userId = useAuthStore((state) => state.user?.id)
  const draftEpoch = useAuthStore((state) => state.draftEpoch)
  const { conversationId } = useParams()
  const navigate = useNavigate()

  return (
    <Box sx={chatPageStyles.page}>
      <Stack component="header" direction="row" sx={chatPageStyles.header}>
        <Typography component="h1" variant="h6">
          Travel Insurance Advisor
        </Typography>
        <Stack direction="row" spacing={2} sx={chatPageStyles.headerActions}>
          <HealthStatus />
          <LogoutButton />
        </Stack>
      </Stack>
      {userId && (
        <ChatSessionProvider
          accountId={userId}
          target={conversationId}
          draftEpoch={draftEpoch}
          navigate={(path, replace) => navigate(path, { replace })}
        >
          <ChatSession />
        </ChatSessionProvider>
      )}
    </Box>
  )
}
