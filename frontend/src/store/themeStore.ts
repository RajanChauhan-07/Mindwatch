import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ThemeState {
  dark: boolean
  toggle: () => void
  setDark: (v: boolean) => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      dark: false,
      toggle: () => {
        const next = !get().dark
        set({ dark: next })
        document.documentElement.classList.toggle('dark', next)
      },
      setDark: (v) => {
        set({ dark: v })
        document.documentElement.classList.toggle('dark', v)
      },
    }),
    { name: 'mindwatch-theme' }
  )
)

// Sync on app load
export function initTheme() {
  const stored = localStorage.getItem('mindwatch-theme')
  if (stored) {
    try {
      const { state } = JSON.parse(stored)
      if (state?.dark) document.documentElement.classList.add('dark')
    } catch {}
  }
}
