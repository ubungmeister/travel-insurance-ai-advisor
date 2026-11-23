import { useQuery } from '@tanstack/react-query'

import { listConversations } from '../../api'
import { chatKeys } from './chat-query-keys'

export function useConversationHistory(accountId: string, enabled = true) {
  return useQuery({
    queryKey: chatKeys.history(accountId),
    queryFn: ({ signal }) => listConversations(signal, accountId),
    enabled,
    retry: false,
    staleTime: 0,
    refetchOnWindowFocus: false,
  })
}
