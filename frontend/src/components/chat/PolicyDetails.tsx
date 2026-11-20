import type { PolicySummary } from '../../api'

export function PolicyDetails({ policy }: { policy: PolicySummary }) {
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
