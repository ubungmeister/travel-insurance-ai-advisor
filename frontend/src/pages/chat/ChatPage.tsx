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
    <>
      <h1>Travel Insurance Advisor</h1>

      <LogoutButton />
      <HealthStatus />
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
    </>
  )
}
