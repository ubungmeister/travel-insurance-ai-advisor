import { Box, Stack, Typography } from '@mui/material'
import {
  ChatSession,
  ChatSessionProvider,
  HealthStatus,
  LogoutButton,
} from '../../components'
import { useAuthStore } from '../../store'
import { useNavigate, useParams } from 'react-router-dom'

export function ChatPage() {
  const userId = useAuthStore((state) => state.user?.id)
  const draftEpoch = useAuthStore((state) => state.draftEpoch)
  const { conversationId } = useParams()
  const navigate = useNavigate()

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100dvh',
        height: { md: '100dvh' },
        bgcolor: 'background.default',
      }}
    >
      <Stack
        component="header"
        direction="row"
        sx={{
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
        }}
      >
        <Typography component="h1" variant="h6">
          Travel Insurance Advisor
        </Typography>
        <Stack
          direction="row"
          spacing={2}
          sx={{
            alignItems: 'center',
            typography: 'body2',
            '& p': { m: 0, color: 'text.secondary' },
          }}
        >
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
