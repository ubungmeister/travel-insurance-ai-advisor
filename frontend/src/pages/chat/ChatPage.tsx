import { ChatSession, HealthStatus, LogoutButton } from '../../components'
import { useAuthStore } from '../../store'

export function ChatPage() {
  const userId = useAuthStore((state) => state.user?.id)

  return (
    <>
      <h1>Travel Insurance Advisor</h1>

      <LogoutButton />
      <HealthStatus />
      {userId && <ChatSession key={userId} />}
    </>
  )
}
