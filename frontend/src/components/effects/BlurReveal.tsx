import { motion } from 'framer-motion'

interface BlurRevealProps {
  children: React.ReactNode
  delay?: number
  className?: string
  once?: boolean
}

export default function BlurReveal({ children, delay = 0, className = '', once = true }: BlurRevealProps) {
  return (
    <motion.div
      initial={{ opacity: 0, filter: 'blur(12px)', y: 16 }}
      whileInView={{ opacity: 1, filter: 'blur(0px)', y: 0 }}
      viewport={{ once }}
      transition={{
        duration: 0.6,
        delay,
        ease: [0.16, 1, 0.3, 1],
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}
