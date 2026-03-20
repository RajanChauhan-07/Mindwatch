interface InsightCardProps {
  text: string
  type?: 'info' | 'warning' | 'success' | 'danger'
}

const cfg = {
  info:    { bg: 'rgba(99,102,241,0.07)',  border: 'rgba(99,102,241,0.2)',  dot: '#6366F1' },
  warning: { bg: 'rgba(245,158,11,0.07)', border: 'rgba(245,158,11,0.2)', dot: '#F59E0B' },
  success: { bg: 'rgba(34,197,94,0.07)',  border: 'rgba(34,197,94,0.2)',  dot: '#22C55E' },
  danger:  { bg: 'rgba(239,68,68,0.07)',  border: 'rgba(239,68,68,0.2)',  dot: '#EF4444' },
}

export default function InsightCard({ text, type = 'info' }: InsightCardProps) {
  const c = cfg[type]
  return (
    <div
      className="flex items-start gap-3 px-4 py-3 rounded-2xl text-sm leading-relaxed"
      style={{ background: c.bg, border: `1px solid ${c.border}` }}
    >
      <div className="mt-1.5 w-2 h-2 rounded-full flex-shrink-0 animate-pulse-soft"
        style={{ background: c.dot, boxShadow: `0 0 8px ${c.dot}` }} />
      <span style={{ color: 'var(--tx-2)' }}>{text}</span>
    </div>
  )
}
