import { Link } from 'react-router-dom'

import { ChatForm } from '../../forms'
import { useChatSession } from '../../hooks'
import { ChatTranscript } from './ChatTranscript'
import { ConversationHistory } from './ConversationHistory'
import { PolicyDetails } from './PolicyDetails'

interface Props {
  accountId: string
  target?: string
  navigate: (path: string, replace?: boolean) => void
}

/**
 * Presents the current chat, with history and policy controls alongside the
 * composer. The hook owns all reads and sends; the UI distinguishes an
 * uncertain request the user can retry from a rejected one they can restore
 * or discard. Keep the composer editable while a send is pending, but block
 * a second submission until the pending request is resolved.
 */
export function ChatSession({ accountId, target, navigate }: Props) {
  const chat = useChatSession(accountId, target, navigate)
  const policy =
    chat.conversation?.selected_policy ??
    chat.policies.find((item) => item.policy_id === chat.policyId)
  const canSend =
    !chat.loading && !chat.loadError && !chat.unavailable && !!policy

  return (
    <>
      <ConversationHistory
        history={chat.history}
        conversationId={chat.conversation?.conversation_id}
        disabled={false}
        onSelect={(id) => navigate(`/chat/${id}`)}
        onNew={() => navigate('/chat/new')}
      />
      {chat.loading && <p role="status">Loading chat…</p>}
      {chat.unavailable && (
        <p role="alert">This conversation is unavailable.</p>
      )}
      {chat.loadError && (
        <p role="alert">
          Unable to load chat.{' '}
          <button type="button" onClick={chat.reload}>
            Try again
          </button>
        </p>
      )}
      {target === 'new' && !chat.loading && !chat.loadError && (
        <section aria-label="Chat policy">
          {chat.policies.length === 0 && (
            <p>
              No policies linked. Sign in with the account linked to your policy
              or contact support.
            </p>
          )}
          {chat.policies.length > 1 && (
            <>
              <h2>Choose a policy</h2>
              <ul>
                {chat.policies.map((item) => (
                  <li key={item.policy_id}>
                    <PolicyDetails policy={item} />
                    <button
                      type="button"
                      disabled={chat.sending || !!chat.recovery}
                      aria-pressed={chat.policyId === item.policy_id}
                      onClick={() => chat.selectPolicy(item.policy_id)}
                    >
                      Choose {item.policy_number}
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      )}
      {policy && (
        <section aria-label="Selected policy">
          <PolicyDetails policy={policy} />
        </section>
      )}
      <ChatTranscript messages={chat.conversation?.messages ?? []} />
      {chat.reauthenticate && (
        <Link
          to="/login"
          state={{ returnTo: target ? `/chat/${target}` : '/' }}
        >
          Sign in again
        </Link>
      )}
      {chat.sendError && <p role="alert">{chat.sendError}</p>}
      {chat.recovery && (
        <section aria-label={chat.rejected ? 'Rejected send' : 'Pending send'}>
          {chat.rejected ? (
            <>
              <p role="alert">
                The server rejected this message. Restore it to make
                corrections, or discard it.
              </p>
              <p>Rejected message: {chat.recovery.message}</p>
              {chat.draft && (
                <p>
                  Clear the composer before restoring, or copy the rejected text
                  to keep both.
                </p>
              )}
              <button
                type="button"
                disabled={!!chat.draft || chat.sending}
                onClick={() => chat.resolveRejected('restore')}
              >
                Restore rejected text
              </button>{' '}
              <button
                type="button"
                disabled={chat.sending}
                onClick={() => chat.resolveRejected('discard')}
              >
                Discard rejected send
              </button>
            </>
          ) : (
            <>
              <p>Pending message: {chat.recovery.message}</p>
              <button
                type="button"
                onClick={() => void chat.retry()}
                disabled={chat.loading || chat.sending || chat.unavailable}
              >
                Retry pending message
              </button>
            </>
          )}
        </section>
      )}
      <ChatForm
        value={chat.draft}
        readOnly={chat.unavailable || target === undefined}
        onChange={chat.editDraft}
        onSend={chat.send}
        disabled={!canSend || chat.sending || !!chat.recovery}
        isPending={chat.sending}
      />
    </>
  )
}
