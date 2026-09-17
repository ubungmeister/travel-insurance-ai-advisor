import { useMutation } from '@tanstack/react-query'

import { supabase } from '../../lib/supabase'

interface LoginCredentials {
  email: string
  password: string
}

export function useLogin() {
  return useMutation({
    mutationFn: async ({ email, password }: LoginCredentials) => {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error

      return data
    },
  })
}
