import { Button, List, ListItem, Paper, Typography } from '@mui/material'
import { useChatSessionContext } from '../../hooks/chat/use-chat-session-context'
import { PolicyDetails } from './PolicyDetails'

/** Renders policy controls from the session without owning or auto-selecting a policy. */
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
      {isNew && visible && policies.length === 0 && (
        <Paper
          component="section"
          variant="outlined"
          aria-label="Chat policy"
          sx={{ p: 1.5 }}
        >
          <Typography component="h2" variant="subtitle2">
            Chat policy
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No policies linked. Sign in with the account linked to your policy
            or contact support.
          </Typography>
        </Paper>
      )}
      {isNew && visible && policies.length > 1 && (
        <Paper
          component="section"
          variant="outlined"
          aria-label="Chat policy"
          sx={{ p: 1.5 }}
        >
          <Typography component="h2" variant="subtitle2">
            Choose a policy
          </Typography>
          <List aria-label="Available policies" disablePadding>
            {policies.map((item) => {
              const selected = policyId === item.policy_id
              return (
                <ListItem
                  key={item.policy_id}
                  disableGutters
                  sx={{
                    gap: 1,
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                  }}
                >
                  <PolicyDetails policy={item} />
                  <Button
                    type="button"
                    size="small"
                    variant={selected ? 'contained' : 'outlined'}
                    disabled={disabled}
                    aria-pressed={selected}
                    onClick={() => onSelect(item.policy_id)}
                  >
                    Choose {item.policy_number}
                  </Button>
                </ListItem>
              )
            })}
          </List>
        </Paper>
      )}
      {policy && (
        <Paper
          component="section"
          variant="outlined"
          aria-label="Selected policy"
          sx={{ p: 1.5 }}
        >
          <Typography component="h2" variant="caption" color="text.secondary">
            Selected policy
          </Typography>
          <PolicyDetails policy={policy} />
        </Paper>
      )}
    </>
  )
}
