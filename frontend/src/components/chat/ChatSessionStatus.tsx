import { Link } from 'react-router-dom'
import { useChatSessionContext } from '../../hooks/conversation/use-chat-session-context'

export function ChatSessionStatus() {
  const {
    loading,
    unavailable,
    loadError,
    sendError,
    reauthenticate,
    target,
    reload: onReload,
  } = useChatSessionContext()
  const returnTo = target ? `/chat/${target}` : '/'
  return (
    <>
      {loading && <p role="status">Loading chat…</p>}
      {unavailable && <p role="alert">This conversation is unavailable.</p>}
      {loadError && (
        <p role="alert">
          Unable to load chat.{' '}
          <button type="button" onClick={onReload}>
            Try again
          </button>
        </p>
      )}
      {reauthenticate && (
        <Link to="/login" state={{ returnTo }}>
          Sign in again
        </Link>
      )}
      {sendError && <p role="alert">{sendError}</p>}
    </>
  )
}
