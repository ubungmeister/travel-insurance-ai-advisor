import { useChatSessionContext } from '../../hooks/chat/use-chat-session-context'

export function PendingSendRecovery() {
  const {
    recovery: request,
    rejected,
    draft,
    sending: busy,
    loading,
    unavailable,
    retry: onRetry,
    resolveRejected: onResolve,
  } = useChatSessionContext()
  const hasDraft = !!draft
  const canRetry = !loading && !unavailable
  if (!request) return null
  return (
    <section aria-label={rejected ? 'Rejected send' : 'Pending send'}>
      {rejected ? (
        <>
          <p role="alert">
            The server rejected this message. Restore it to make corrections,
            or discard it.
          </p>
          <p>Rejected message: {request.message}</p>
          {hasDraft && (
            <p>
              Clear the composer before restoring, or copy the rejected text
              to keep both.
            </p>
          )}
          <button
            type="button"
            disabled={hasDraft || busy}
            onClick={() => onResolve('restore')}
          >
            Restore rejected text
          </button>{' '}
          <button
            type="button"
            disabled={busy}
            onClick={() => onResolve('discard')}
          >
            Discard rejected send
          </button>
        </>
      ) : (
        <>
          <p>Pending message: {request.message}</p>
          <button
            type="button"
            onClick={() => void onRetry()}
            disabled={busy || !canRetry}
          >
            Retry pending message
          </button>
        </>
      )}
    </section>
  )
}
