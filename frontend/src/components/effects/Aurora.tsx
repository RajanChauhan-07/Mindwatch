interface AuroraProps {
  className?: string
  intensity?: 'low' | 'mid' | 'high'
}

export default function Aurora({ className = '', intensity = 'mid' }: AuroraProps) {
  const op = intensity === 'low' ? 0.25 : intensity === 'high' ? 0.55 : 0.38

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none select-none ${className}`} aria-hidden>
      {/* Blob 1 — indigo */}
      <div
        className="absolute rounded-full blur-3xl animate-blob-1"
        style={{
          width: '55%', height: '55%',
          top: '-15%', left: '-10%',
          opacity: op,
          background: 'radial-gradient(circle at 40% 40%, #6366F1 0%, #A855F7 50%, transparent 70%)',
        }}
      />
      {/* Blob 2 — cyan/blue */}
      <div
        className="absolute rounded-full blur-3xl animate-blob-2"
        style={{
          width: '50%', height: '50%',
          top: '5%', right: '-12%',
          opacity: op * 0.85,
          background: 'radial-gradient(circle at 60% 40%, #06B6D4 0%, #0071E3 50%, transparent 70%)',
        }}
      />
      {/* Blob 3 — pink */}
      <div
        className="absolute rounded-full blur-3xl animate-blob-3"
        style={{
          width: '42%', height: '42%',
          bottom: '-10%', left: '25%',
          opacity: op * 0.7,
          background: 'radial-gradient(circle at 50% 60%, #EC4899 0%, #A855F7 50%, transparent 70%)',
        }}
      />
    </div>
  )
}
