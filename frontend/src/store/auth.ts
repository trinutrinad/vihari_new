import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { AuthUser, TokenPair } from '@/types/auth'

type AuthState = {
  user: AuthUser | null
  tokens: TokenPair | null
  setSession: (user: AuthUser, tokens: TokenPair) => void
  setUser: (user: AuthUser) => void
  clearSession: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      setSession: (user, tokens) => set({ user, tokens }),
      setUser: (user) => set({ user }),
      clearSession: () => set({ user: null, tokens: null }),
    }),
    { name: 'bharat-yatra-auth' },
  ),
)
