import {
  Box,
  Button,
  List,
  ListItem,
  ListItemButton,
  Typography,
} from '@mui/material'
import type { ConversationSummary } from '../../api'

const historyItemStyle = {
  borderRadius: 1,
  flexDirection: 'column',
  alignItems: 'flex-start',
  textAlign: 'left',
  overflowWrap: 'anywhere',
  minWidth: 0,
} as const

interface ConversationHistoryProps {
  history: ConversationSummary[]
  conversationId?: number
  disabled: boolean
  onSelect: (id: number) => void
  onNew: () => void
}

export function ConversationHistory({
  history,
  conversationId,
  disabled,
  onSelect,
  onNew,
}: ConversationHistoryProps) {
  return (
    <Box component="nav" aria-label="Conversation history">
      <Typography component="h2" variant="subtitle1" sx={{ mb: 1 }}>
        Conversation history
      </Typography>
      <Button
        type="button"
        fullWidth
        variant="outlined"
        disabled={disabled}
        onClick={onNew}
      >
        New chat
      </Button>
      {history.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          No conversations yet.
        </Typography>
      )}
      <List aria-label="Saved conversations" sx={{ mt: 1 }} disablePadding>
        {history.map((item) => {
          const active = item.conversation_id === conversationId
          return (
            <ListItem
              key={item.conversation_id}
              disablePadding
              sx={{ mb: 0.5 }}
            >
              <ListItemButton
                component="button"
                type="button"
                selected={active}
                aria-current={active ? 'page' : undefined}
                disabled={disabled}
                onClick={() => onSelect(item.conversation_id)}
                sx={historyItemStyle}
              >
                <Typography component="span" variant="subtitle2">
                  Conversation #{item.conversation_id}
                </Typography>
                <Typography
                  component="span"
                  variant="body2"
                  color="text.secondary"
                >
                  {item.selected_policy?.policy_number ?? 'No policy'} ·{' '}
                  <time dateTime={item.last_activity_at}>
                    {new Date(item.last_activity_at).toLocaleDateString(
                      undefined,
                      {
                        dateStyle: 'medium',
                      },
                    )}
                  </time>
                </Typography>
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>
    </Box>
  )
}
