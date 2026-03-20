import { useRef, useState } from 'react'

interface MagneticProps {
  children: React.ReactNode
  strength?: number
}

export default function Magnetic({ children, strength = 0.35 }: MagneticProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [pos, setPos] = useState({ x: 0, y: 0 })

  const handleMove = (e: React.MouseEvent) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    setPos({
      x: (e.clientX - cx) * strength,
      y: (e.clientY - cy) * strength,
    })
  }

  const handleLeave = () => setPos({ x: 0, y: 0 })

  return (
    <div
      ref={ref}
      onMouseMove={handleMove}
      onMouseLeave={handleLeave}
      style={{
        transform: `translate(${pos.x}px, ${pos.y}px)`,
        transition: pos.x === 0 && pos.y === 0
          ? 'transform 0.5s cubic-bezier(0.16,1,0.3,1)'
          : 'transform 0.08s ease-out',
        display: 'inline-block',
      }}
    >
      {children}
    </div>
  )
}
