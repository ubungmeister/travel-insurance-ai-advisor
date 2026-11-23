import { Box, Typography } from '@mui/material'
import type { PolicySummary } from '../../api'

export function PolicyDetails({ policy }: { policy: PolicySummary }) {
  return (
    <Box sx={{ minWidth: 0, overflowWrap: 'anywhere' }}>
      <Typography variant="body2">
        <strong>{policy.policy_number}</strong> — {policy.plan_name} (version{' '}
        {policy.plan_version}), {policy.territory}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Travel dates: {policy.start_date} to {policy.end_date} · Status:{' '}
        {policy.status}
      </Typography>
    </Box>
  )
}
