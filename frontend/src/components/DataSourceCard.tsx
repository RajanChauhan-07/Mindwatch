import React from 'react'

interface DataSourceCardProps {
  icon: React.ReactNode
  name: string
  description: string
  connected: boolean
  comingSoon?: boolean
  onConnect?: () => void
  accentColor?: string
}

export default function DataSourceCard({
  icon,
  name,
  description,
  connected,
  comingSoon = false,
  onConnect,
  accentColor = 'var(--blue)',
}: DataSourceCardProps) {
  return (
    <div
      className={`glass-card rounded-2xl p-4 flex items-center gap-3 cursor-default select-none ${
        comingSoon ? 'opacity-50' : ''
      }`}
    >
      <div
        className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center"
        style={{ background: `${accentColor}18`, border: `1px solid ${accentColor}30` }}
      >
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold leading-tight" style={{ color: 'var(--text)' }}>{name}</p>
        <p className="text-xs mt-0.5 truncate" style={{ color: 'var(--text-2)' }}>{description}</p>
      </div>
      {comingSoon ? (
        <span
          className="text-xs font-medium px-2.5 py-1 rounded-full flex-shrink-0"
          style={{ background: 'var(--bg-3)', color: 'var(--text-3)' }}
        >
          Soon
        </span>
      ) : connected ? (
        <span
          className="text-xs font-semibold px-2.5 py-1 rounded-full flex-shrink-0 flex items-center gap-1"
          style={{ background: 'rgba(52,199,89,0.12)', color: 'var(--green)', border: '1px solid rgba(52,199,89,0.25)' }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-current" />
          Live
        </span>
      ) : (
        <button
          onClick={onConnect}
          className="text-xs font-semibold flex-shrink-0 px-3 py-1.5 rounded-full transition-all duration-200 hover:scale-105 active:scale-95"
          style={{
            background: `${accentColor}18`,
            color: accentColor,
            border: `1px solid ${accentColor}30`,
          }}
        >
          Connect
        </button>
      )}
    </div>
  )
}
