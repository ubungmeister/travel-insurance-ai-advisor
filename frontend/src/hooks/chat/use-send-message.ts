import { useMutation } from '@tanstack/react-query'

import { sendMessage } from '../../api'

export function useSendMessage() {
  return useMutation({
    mutationFn: sendMessage,
  })
}
