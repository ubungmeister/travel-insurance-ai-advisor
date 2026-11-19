import type { ConversationCreateResponse, PolicySummary } from '../../api'

interface PolicySelectionProps {
  result?: ConversationCreateResponse
  isPending: boolean
  isError: boolean
  onStart: (policyId?: number) => void
}

function PolicyDetails({ policy }: { policy: PolicySummary }) {
  return (
    <p>
      <strong>{policy.policy_number}</strong> — {policy.plan_name} (version{' '}
      {policy.plan_version}), {policy.territory}
      <br />
      Travel dates: {policy.start_date} to {policy.end_date} · Status:{' '}
      {policy.status}
    </p>
  )
}

export function PolicySelection({
  result,
  isPending,
  isError,
  onStart,
}: PolicySelectionProps) {
  if (result?.status === 'ready') {
    return (
      <section aria-label="Chat policy">
        <h2>Selected policy</h2>
        <PolicyDetails policy={result.selected_policy} />
      </section>
    )
  }

  return (
    <section aria-label="Chat policy" aria-busy={isPending}>
      {isError && (
        <p role="alert">
          Unable to start chat. Please try again. If a policy is no longer
          available, refresh the page to reload your choices.
        </p>
      )}
      {(isPending || (!result && !isError)) && (
        <p role="status">Loading your chat policy…</p>
      )}
      {result?.status === 'selection_required' ? (
        <>
          <h2>Choose a policy</h2>
          <p>Select the policy for this chat.</p>
          <ul>
            {result.policy_choices.map((policy) => (
              <li key={policy.policy_id}>
                <PolicyDetails policy={policy} />
                <button
                  type="button"
                  disabled={isPending}
                  onClick={() => onStart(policy.policy_id)}
                >
                  Choose {policy.policy_number}
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : result?.status === 'no_policies' ? (
        <>
          <h2>No policies linked</h2>
          <p>
            No travel insurance policies are linked to your account. Sign in
            with the account linked to your policy or contact support. No
            conversation has been created.
          </p>
          <button type="button" disabled={isPending} onClick={() => onStart()}>
            Check again
          </button>
        </>
      ) : isError ? (
        <button type="button" disabled={isPending} onClick={() => onStart()}>
          Try again
        </button>
      ) : null}
    </section>
  )
}
