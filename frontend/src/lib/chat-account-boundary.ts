import type { QueryClient } from '@tanstack/react-query'

import { queryClient } from './query-client'

let generation = 0
const activeSends = new Set<AbortController>()

export const chatAccountGeneration = () => generation

export function registerChatSend(controller: AbortController) {
  activeSends.add(controller)
  return () => activeSends.delete(controller)
}

/**
 * Ends the current identity's server-state lifetime before auth state changes.
 * Invalidate callbacks first, then abort/cancel and clear BOTH cache types.
 * This is account-boundary cleanup, never an ordinary navigation operation;
 * tab drafts and component reset are handled separately by the auth store.
 */
export function resetChatServerState(client: QueryClient = queryClient) {
  generation++
  activeSends.forEach((controller) => controller.abort())
  activeSends.clear()
  void client.cancelQueries().catch(() => {})
  client.clear()
}
