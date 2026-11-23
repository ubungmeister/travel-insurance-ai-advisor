import type { SxProps, Theme } from '@mui/material/styles'

export const chatSessionStyles = {
  layout: {
    display: 'grid',
    gridTemplateColumns: {
      xs: 'minmax(0, 1fr)',
      md: '17rem minmax(0, 1fr)',
    },
    gridTemplateRows: { md: 'minmax(0, 1fr)' },
    flex: 1,
    minHeight: 0,
  },
  history: {
    overflowY: 'auto',
    maxHeight: { xs: '30dvh', md: 'none' },
    borderRight: { md: 1 },
    borderBottom: { xs: 1, md: 0 },
    borderColor: 'divider',
    bgcolor: 'background.paper',
    p: 2,
  },
  transcript: {
    flex: 1,
    minHeight: { xs: 120, md: 0 },
    overflowY: 'auto',
    p: { xs: 2, md: 3 },
  },
  controls: {
    // Long recovery text or policy lists must not crowd out the transcript.
    maxHeight: { md: '65%' },
    overflowY: 'auto',
    borderTop: 1,
    borderColor: 'divider',
    bgcolor: 'background.paper',
    px: { xs: 2, md: 3 },
    py: 2,
  },
} as const satisfies Record<string, SxProps<Theme>>

const message = {
  maxWidth: '85%',
  minWidth: 0,
  borderRadius: 2,
  px: 1.5,
  py: 1,
} as const satisfies SxProps<Theme>

export const chatMessageStyles = {
  user: {
    ...message,
    alignSelf: 'flex-end',
    bgcolor: 'primary.dark',
    color: 'primary.contrastText',
  },
  assistant: {
    ...message,
    alignSelf: 'flex-start',
    bgcolor: 'background.paper',
    color: 'text.primary',
  },
} as const satisfies Record<string, SxProps<Theme>>
