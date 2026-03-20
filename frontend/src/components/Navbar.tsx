import { Brain, Moon, Sun } from 'lucide-react'
import { useThemeStore } from '../store/themeStore'

interface NavbarProps {
  onSignIn?: () => void
  showSignIn?: boolean
}

export default function Navbar({ onSignIn, showSignIn = true }: NavbarProps) {
  const { dark, toggle } = useThemeStore()

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 glass"
      style={{ borderBottom: '1px solid var(--border)', height: 52 }}
    >
      <div className="max-w-6xl mx-auto px-5 h-full flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, var(--blue), var(--purple))' }}>
            <Brain size={15} className="text-white" />
          </div>
          <span className="font-bold text-base tracking-tight" style={{ color: 'var(--text)' }}>
            MindWatch
          </span>
        </div>

        {/* Right */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggle}
            className="w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-200 hover:scale-110 active:scale-95"
            style={{ background: 'var(--bg-3)', color: 'var(--text-2)' }}
            aria-label="Toggle dark mode"
          >
            {dark ? <Sun size={15} /> : <Moon size={15} />}
          </button>

          {showSignIn && onSignIn && (
            <button
              onClick={onSignIn}
              className="text-sm font-semibold px-4 py-2 rounded-pill text-white transition-all duration-200 hover:scale-105 active:scale-95 hover:shadow-glow-blue"
              style={{ background: 'linear-gradient(135deg, var(--blue), #1A8FFF)' }}
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </nav>
  )
}
