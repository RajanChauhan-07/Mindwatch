interface Props { size?: number; color?: string }

export default function LoadingSpinner({ size = 20, color = 'var(--indigo)' }: Props) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none"
      style={{ animation: 'spin 0.7s linear infinite' }}>
      <circle cx="10" cy="10" r="7.5" stroke="var(--border-2)" strokeWidth="2.5" />
      <circle cx="10" cy="10" r="7.5" stroke={color} strokeWidth="2.5"
        strokeLinecap="round" strokeDasharray="47" strokeDashoffset="35" />
    </svg>
  )
}
