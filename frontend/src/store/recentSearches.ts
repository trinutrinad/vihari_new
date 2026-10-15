import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const MAX_RECENT = 8

type RecentSearchState = {
  recent: string[]
  addRecent: (query: string) => void
  clearRecent: () => void
}

export const useRecentSearchesStore = create<RecentSearchState>()(
  persist(
    (set, get) => ({
      recent: [],
      addRecent: (query) => {
        const cleaned = query.trim()
        if (!cleaned) return
        const next = [cleaned, ...get().recent.filter((item) => item.toLowerCase() !== cleaned.toLowerCase())]
        set({ recent: next.slice(0, MAX_RECENT) })
      },
      clearRecent: () => set({ recent: [] }),
    }),
    { name: 'bharat-yatra-recent-searches' },
  ),
)
