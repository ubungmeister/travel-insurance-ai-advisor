import type { User } from '@supabase/supabase-js'
import { create } from 'zustand'

import { supabase } from '../../lib/supabase'

export type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated'

interface AuthState {
  status: AuthStatus
  user: User | null
}

export const useAuthStore = create<AuthState>(() => ({
  status: 'checking',
  user: null,
}))

// Fires immediately with the persisted session (if any), then on every sign-in/out/refresh
supabase.auth.onAuthStateChange((_event, session) => {
  useAuthStore.setState({
    status: session ? 'authenticated' : 'unauthenticated',
    user: session?.user ?? null,
  })
})
