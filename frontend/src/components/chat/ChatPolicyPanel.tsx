import { useChatSessionContext } from '../../hooks/conversation/use-chat-session-context'
import { PolicyDetails } from './PolicyDetails'

export function ChatPolicyPanel() {
  const chat = useChatSessionContext()
  const { policies, policyId, selectPolicy: onSelect } = chat
  const isNew = chat.target === 'new'
  const visible = !chat.loading && !chat.loadError
  const disabled = chat.sending || !!chat.recovery
  const policy =
    chat.conversation?.selected_policy ??
    policies.find((item) => item.policy_id === policyId)
  return (
    <>
      {isNew && visible && (
        <section aria-label="Chat policy">
          {policies.length === 0 && (
            <p>
              No policies linked. Sign in with the account linked to your policy
              or contact support.
            </p>
          )}
          {policies.length > 1 && (
            <>
              <h2>Choose a policy</h2>
              <ul>
                {policies.map((item) => (
                  <li key={item.policy_id}>
                    <PolicyDetails policy={item} />
                    <button
                      type="button"
                      disabled={disabled}
                      aria-pressed={policyId === item.policy_id}
                      onClick={() => onSelect(item.policy_id)}
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
    </>
  )
}
