import { useEffect, useState } from 'react'

interface ScoreCardProps {
  score: number | null
  size?: number
  strokeWidth?: number
}

export default function ScoreCard({ score, size = 180, strokeWidth = 12 }: ScoreCardProps) {
  const [animated, setAnimated] = useState(0)

  useEffect(() => {
    if (score === null) { setAnimated(0); return }
    let frame = 0
    const total = 60
    const timer = setInterval(() => {
      frame++
      const t = frame / total
      const ease = 1 - Math.pow(1 - t, 4)
      setAnimated(Math.round(ease * score))
      if (frame >= total) clearInterval(timer)
    }, 16)
    return () => clearInterval(timer)
  }, [score])

  const r = (size - strokeWidth * 2) / 2
  const circ = 2 * Math.PI * r
  const pct = score !== null ? Math.max(0, Math.min(100, score)) : 0
  const dash = (pct / 100) * circ
  const offset = circ - dash

  const color = score === null ? '#4A4A4A'
    : score >= 65 ? '#22C55E'
    : score >= 40 ? '#F59E0B'
    : '#EF4444'

  const gradId = `sg-${size}`

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {/* Ambient glow */}
      {score !== null && (
        <div
          className="absolute rounded-full blur-2xl opacity-30"
          style={{
            width: size * 0.7, height: size * 0.7,
            background: `radial-gradient(circle, ${color}, transparent)`,
          }}
        />
      )}

      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <defs>
          <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={color} stopOpacity="0.5" />
            <stop offset="100%" stopColor={color} />
          </linearGradient>
        </defs>
        {/* Track */}
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke="var(--raised)" strokeWidth={strokeWidth}
        />
        {/* Progress */}
        {score !== null && (
          <circle
            cx={size / 2} cy={size / 2} r={r}
            fill="none"
            stroke={`url(#${gradId})`}
            strokeWidth={strokeWidth}
            strokeDasharray={circ}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1.4s cubic-bezier(0.16,1,0.3,1)' }}
          />
        )}
      </svg>

      {/* Label */}
      <div className="absolute flex flex-col items-center justify-center">
        <span
          className="font-black tabular-nums leading-none"
          style={{ fontSize: size * 0.24, color, letterSpacing: '-0.03em' }}
        >
          {score !== null ? animated : '–'}
        </span>
        <span className="text-xs font-semibold mt-0.5" style={{ color: 'var(--tx-3)' }}>/ 100</span>
      </div>
    </div>
  )
}
