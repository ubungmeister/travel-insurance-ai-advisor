import { ChatSession, HealthStatus, LogoutButton } from '../../components'
import { useAuthStore } from '../../store'
import { useNavigate, useParams } from 'react-router-dom'

export function ChatPage() {
  const userId = useAuthStore((state) => state.user?.id)
  const draftEpoch = useAuthStore((state) => state.draftEpoch)
  const { conversationId } = useParams()
  const navigate = useNavigate()

  console.log('conversationId', conversationId, 'draftEpoch.', draftEpoch)

  return (
    <>
      <h1>Travel Insurance Advisor</h1>

      <LogoutButton />
      <HealthStatus />
      {userId && (
        <ChatSession
          key={`${userId}:${conversationId ?? 'home'}:${draftEpoch}`}
          accountId={userId}
          target={conversationId}
          navigate={(path, replace) => navigate(path, { replace })}
        />
      )}
    </>
  )
}
