import { useMutation } from '@tanstack/react-query'
import { useCallback, useEffect, useRef, useState } from 'react'

import { createConversation } from '../../api'
import type { ConversationCreateResponse } from '../../api'

export function useCreateConversation() {
  const [result, setResult] = useState<ConversationCreateResponse>()
  const initialized = useRef(false)
  const submitting = useRef(false)
  const { mutate, isPending, isError } = useMutation({
    mutationFn: createConversation,
    retry: false,
    onSuccess: setResult,
    onSettled: () => {
      submitting.current = false
    },
  })

  const selectPolicy = useCallback(
    (policyId?: number) => {
      if (submitting.current || result?.status === 'ready') return
      submitting.current = true
      mutate(policyId)
    },
    [mutate, result?.status],
  )

  useEffect(() => {
    // Resolve once on login/mount, including React StrictMode effect replay.
    if (initialized.current) return
    initialized.current = true
    selectPolicy()
  }, [selectPolicy])

  return { result, selectPolicy, isPending, isError }
}
