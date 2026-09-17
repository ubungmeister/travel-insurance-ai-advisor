import { HealthStatus, LogoutButton } from '../../components'
import { ChatForm } from '../../forms'

export function ChatPage() {
  return (
    <>
      <h1>Travel Insurance Advisor</h1>

      <LogoutButton />
      <HealthStatus />
      <ChatForm />
    </>
  )
}
