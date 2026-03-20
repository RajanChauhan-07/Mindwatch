interface GlowBorderProps {
  children: React.ReactNode
  color?: string
  className?: string
}

export default function GlowBorder({ children, color = '#6366F1', className = '' }: GlowBorderProps) {
  return (
    <div
      className={`relative p-[1px] rounded-3xl ${className}`}
      style={{
        background: `linear-gradient(135deg, ${color}66, transparent 40%, ${color}44)`,
      }}
    >
      <div className="relative rounded-3xl overflow-hidden" style={{ background: 'var(--surface)' }}>
        {children}
      </div>
    </div>
  )
}
