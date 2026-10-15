import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type AppPreferencesState = {
  language: string
  onboardingComplete: boolean
  setLanguage: (language: string) => void
  completeOnboarding: () => void
}

export const useAppPreferencesStore = create<AppPreferencesState>()(
  persist(
    (set) => ({
      language: 'en',
      onboardingComplete: false,
      setLanguage: (language) => set({ language }),
      completeOnboarding: () => set({ onboardingComplete: true }),
    }),
    { name: 'bharat-yatra-preferences' },
  ),
)
