import { useQuery } from '@tanstack/react-query'

import { getHealth } from '../../api'

export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    retry: false,
  })
}
