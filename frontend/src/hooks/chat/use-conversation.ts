import { useQuery } from '@tanstack/react-query'

import { getConversation } from '../../api'
import { chatKeys } from './chat-query-keys'

/** Queries one exact ID; consumers must hide cached data when this read fails. */
export function useConversation(accountId: string, id?: number) {
  return useQuery({
    queryKey: chatKeys.conversation(accountId, id),
    queryFn: ({ signal }) => {
      if (id === undefined) throw new Error('No conversation selected')
      return getConversation(id, signal, accountId)
    },
    enabled: id !== undefined,
    retry: false,
    staleTime: 0,
    refetchOnWindowFocus: false,
  })
}
