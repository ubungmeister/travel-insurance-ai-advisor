import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  // placeholder until the backend exposes real auth endpoints
  login: () => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  login: () => set({ isAuthenticated: true }),
  logout: () => set({ isAuthenticated: false }),
}))
