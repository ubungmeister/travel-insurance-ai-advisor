import { useQuery } from '@tanstack/react-query'

import { listPolicies } from '../../api'
import { chatKeys } from './chat-query-keys'

export function useChatPolicies(accountId: string, enabled: boolean) {
  return useQuery({
    queryKey: chatKeys.policies(accountId),
    queryFn: ({ signal }) => listPolicies(signal, accountId),
    enabled,
    retry: false,
    staleTime: 0,
    refetchOnWindowFocus: false,
  })
}
