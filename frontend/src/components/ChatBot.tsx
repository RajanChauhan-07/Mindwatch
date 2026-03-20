import { useEffect, useRef, useState } from 'react'
import { Sparkles, Send, X, Brain } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../utils/api'

interface Message { id: string; role: 'user' | 'assistant'; content: string }
interface Props {
  spotifyData?: Record<string, unknown> | null
  youtubeData?: Record<string, unknown> | null
  whatsappData?: Record<string, unknown> | null
  externalOpen?: boolean
  onClose?: () => void
}

const STARTERS = [
  'How is my mental wellness looking?',
  'What does my music say about my mood?',
  'Am I showing signs of stress?',
  'How can I improve my score?',
]

export default function ChatBot({ spotifyData, youtubeData, whatsappData, externalOpen, onClose }: Props) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { if (externalOpen) setOpen(true) }, [externalOpen])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  const handleClose = () => { setOpen(false); onClose?.() }

  const send = async (text: string) => {
    if (!text.trim() || loading) return
    setMessages(p => [...p, { id: `${Date.now()}`, role: 'user', content: text.trim() }])
    setInput('')
    setLoading(true)
    try {
      const history = messages.slice(-10).map(m => ({ message: m.role === 'user' ? m.content : '', response: m.role === 'assistant' ? m.content : '' }))
      const { data } = await api.post('/api/chat/message', { message: text.trim(), history, spotify_data: spotifyData || null, youtube_data: youtubeData || null, whatsapp_data: whatsappData || null })
      setMessages(p => [...p, { id: `${Date.now()+1}`, role: 'assistant', content: data.response }])
    } catch {
      setMessages(p => [...p, { id: `${Date.now()+1}`, role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }])
    } finally { setLoading(false) }
  }

  return (
    <>
      <AnimatePresence>
        {!open && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.06 }}
            whileTap={{ scale: 0.94 }}
            onClick={() => setOpen(true)}
            className="fixed bottom-7 right-7 z-50 flex items-center gap-2.5 pl-4 pr-5 py-3.5 rounded-pill text-white font-bold text-sm shadow-glow-purple"
            style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)', boxShadow: '0 4px 32px rgba(99,102,241,0.45)' }}
          >
            <Sparkles size={16} />
            Ask AI
          </motion.button>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 32, scale: 0.94 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 32, scale: 0.94 }}
            transition={{ type: 'spring', stiffness: 380, damping: 32 }}
            className="fixed bottom-7 right-7 z-50 flex flex-col overflow-hidden"
            style={{
              width: 390, height: 580,
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 28,
              boxShadow: '0 8px 64px rgba(0,0,0,0.2), 0 0 0 1px var(--border)',
            }}
          >
            {/* Header */}
            <div className="flex items-center gap-3 px-5 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
              <div className="w-9 h-9 rounded-2xl flex items-center justify-center flex-shrink-0"
                style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)' }}>
                <Brain size={17} className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-bold text-sm" style={{ color: 'var(--tx)' }}>MindWatch AI</p>
                <p className="text-xs flex items-center gap-1.5" style={{ color: 'var(--green)' }}>
                  <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" /> Online
                </p>
              </div>
              <button onClick={handleClose}
                className="w-7 h-7 rounded-xl flex items-center justify-center hover:scale-110 transition-transform"
                style={{ background: 'var(--raised)', color: 'var(--tx-2)' }}>
                <X size={14} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 no-scroll">
              {messages.length === 0 && (
                <div className="space-y-2.5">
                  <p className="text-xs text-center px-4 pt-2" style={{ color: 'var(--tx-2)' }}>
                    Hi! Ask me anything about your wellness data.
                  </p>
                  <div className="grid grid-cols-1 gap-2 pt-1">
                    {STARTERS.map(s => (
                      <button key={s} onClick={() => send(s)}
                        className="text-left text-sm px-4 py-3 rounded-2xl transition-all hover:scale-[1.01] active:scale-[0.99]"
                        style={{ background: 'var(--raised)', border: '1px solid var(--border)', color: 'var(--tx-2)' }}>
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {messages.map(m => (
                <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className="max-w-[82%] px-4 py-3 text-sm leading-relaxed"
                    style={m.role === 'user'
                      ? { background: 'linear-gradient(135deg, #6366F1, #A855F7)', color: '#fff', borderRadius: '20px 20px 6px 20px' }
                      : { background: 'var(--raised)', border: '1px solid var(--border)', color: 'var(--tx)', borderRadius: '20px 20px 20px 6px' }
                    }
                  >
                    {m.content}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="flex gap-1.5 px-4 py-3.5 rounded-3xl"
                    style={{ background: 'var(--raised)', border: '1px solid var(--border)', borderBottomLeftRadius: 6 }}>
                    {[0,1,2].map(i => (
                      <span key={i} className="w-2 h-2 rounded-full animate-bounce"
                        style={{ background: 'var(--tx-3)', animationDelay: `${i*0.14}s` }} />
                    ))}
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="px-4 py-4" style={{ borderTop: '1px solid var(--border)' }}>
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send(input)}
                  placeholder="Ask about your wellness…"
                  className="flex-1 px-4 py-3 rounded-2xl text-sm outline-none"
                  style={{ background: 'var(--raised)', border: '1px solid var(--border)', color: 'var(--tx)' }}
                />
                <button
                  onClick={() => send(input)}
                  disabled={!input.trim() || loading}
                  className="w-11 h-11 rounded-2xl flex items-center justify-center text-white transition-all hover:scale-105 active:scale-95 disabled:opacity-40"
                  style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)' }}>
                  <Send size={15} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
