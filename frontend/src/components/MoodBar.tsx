interface MoodBarProps {
  label?: string
  value: number
  max?: number
  color?: string
  unit?: string
  showLabel?: boolean
  thick?: boolean
}

export default function MoodBar({
  label, value, max = 100, color = 'var(--indigo)',
  unit = '%', showLabel = true, thick = false,
}: MoodBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  const display = unit === '%' ? `${Math.round(value)}%` : `${value}${unit}`

  return (
    <div className="space-y-1.5">
      {showLabel && label && (
        <div className="flex justify-between items-center">
          <span className="text-sm" style={{ color: 'var(--tx-2)' }}>{label}</span>
          <span className="text-sm font-bold tabular-nums" style={{ color: 'var(--tx)' }}>{display}</span>
        </div>
      )}
      <div
        className={`rounded-full overflow-hidden ${thick ? 'h-2.5' : 'h-1.5'}`}
        style={{ background: 'var(--raised)' }}
      >
        <div
          className="h-full rounded-full"
          style={{
            width: `${pct}%`,
            background: `linear-gradient(90deg, ${color}80, ${color})`,
            transition: 'width 0.8s cubic-bezier(0.16,1,0.3,1)',
          }}
        />
      </div>
    </div>
  )
}
