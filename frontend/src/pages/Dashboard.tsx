import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, Music, Youtube, MessageCircle, Activity, LogOut, Upload, RefreshCw, TrendingUp, Clock, Zap, Sparkles, Sun, Moon, Bell, BarChart3 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { useAuthStore } from '../store/authStore'
import { useThemeStore } from '../store/themeStore'
import api from '../utils/api'
import ScoreCard from '../components/ScoreCard'
import InsightCard from '../components/InsightCard'
import MoodBar from '../components/MoodBar'
import ChatBot from '../components/ChatBot'
import LoadingSpinner from '../components/LoadingSpinner'
import Aurora from '../components/effects/Aurora'
import BlurReveal from '../components/effects/BlurReveal'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
type Tab = 'overview' | 'music' | 'youtube' | 'whatsapp' | 'googlefit' | 'predictions'

interface SpotifyData {
  mood_score: number; emotional_tone: string; avg_valence: number; avg_energy: number
  avg_tempo: number; avg_danceability: number; late_night_ratio: number; total_tracks_analyzed: number
  recently_played: Array<{ name: string; artist: string; album: string; album_art: string; played_at: string }>
  top_tracks: Array<{ name: string; artist: string; album_art: string }>
}
interface YoutubeData {
  emotional_diet_score: number; category_breakdown: Record<string, number>; dark_content_percentage: number
  recovery_score: number; rumination_score: number; content_mood: string; total_videos: number; insights: string[]
}
interface WhatsappData {
  total_messages: number; unique_senders: number; sentiment_score: number; emotional_tone: string
  late_night_ratio: number; avg_messages_per_day: number; most_active_hours: string[]
  top_words: Array<{ word: string; count: number }>; isolation_score: number
  message_frequency_trend: string; total_days_active: number; insights: string[]
}
interface GoogleFitData {
  fitness_score: number; steps_score: number; active_minutes_score: number; heart_rate_score: number
  avg_daily_steps: number; avg_active_minutes: number; avg_calories: number; avg_heart_rate: number
  activity_trend: string; steps_data: Array<{ date: string; value: number }>
  active_minutes_data: Array<{ date: string; value: number }>; calories_data: Array<{ date: string; value: number }>
  heart_rate_data: Array<{ date: string; value: number }>; days_analyzed: number
  insights: Array<{ type: string; message: string }>
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'; if (h < 17) return 'Good afternoon'; return 'Good evening'
}
function computeScore(s: SpotifyData | null, y: YoutubeData | null, w: WhatsappData | null) {
  const sc: number[] = []
  if (s) sc.push(s.mood_score); if (y) sc.push(y.emotional_diet_score); if (w) sc.push(w.sentiment_score)
  return sc.length ? Math.round(sc.reduce((a, b) => a + b) / sc.length) : null
}
function riskInfo(s: number | null) {
  if (s === null) return { label: 'Unknown', color: 'var(--tx-3)', glow: 'transparent' }
  if (s >= 65) return { label: 'Low Risk', color: '#22C55E', glow: 'rgba(34,197,94,0.25)' }
  if (s >= 40) return { label: 'Moderate', color: '#F59E0B', glow: 'rgba(245,158,11,0.2)' }
  return { label: 'High Risk', color: '#EF4444', glow: 'rgba(239,68,68,0.25)' }
}

function Tile({ children, className = '', style = {}, onClick }: { children: React.ReactNode; className?: string; style?: React.CSSProperties; onClick?: () => void }) {
  return <div className={`tile rounded-3xl overflow-hidden ${className}`} style={style} onClick={onClick}>{children}</div>
}

function UploadZone({ label, fileName, accept, inputRef, onFileChange, color }: {
  label: string; fileName: string | null; accept: string
  inputRef: React.RefObject<HTMLInputElement>; onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void; color: string
}) {
  return (
    <div>
      <p className="text-xs font-bold mb-2 uppercase tracking-wider" style={{ color: 'var(--tx-3)' }}>{label}</p>
      <div className="rounded-2xl p-5 text-center cursor-pointer transition-all"
        style={{ border: `2px dashed ${fileName ? color : 'var(--border-2)'}`, background: fileName ? `${color}08` : 'var(--raised)' }}
        onClick={() => inputRef.current?.click()}>
        <Upload size={20} className="mx-auto mb-2" style={{ color: fileName ? color : 'var(--tx-3)' }} />
        <p className="text-sm font-medium" style={{ color: fileName ? color : 'var(--tx-2)' }}>
          {fileName ? `✓ ${fileName}` : 'Click to upload'}
        </p>
        <input ref={inputRef} type="file" accept={accept} className="hidden" onChange={onFileChange} />
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user, token, logout, setUser } = useAuthStore()
  const { dark, toggle: toggleTheme } = useThemeStore()
  const navigate = useNavigate()

  const [tab, setTab] = useState<Tab>('overview')
  const [spotifyData, setSpotifyData] = useState<SpotifyData | null>(null)
  const [youtubeData, setYoutubeData] = useState<YoutubeData | null>(null)
  const [whatsappData, setWhatsappData] = useState<WhatsappData | null>(null)
  const [googleFitData, setGoogleFitData] = useState<GoogleFitData | null>(null)
  const [loadingSpotify, setLoadingSpotify] = useState(false)
  const [loadingYoutube, setLoadingYoutube] = useState(false)
  const [loadingWhatsapp, setLoadingWhatsapp] = useState(false)
  const [loadingFit, setLoadingFit] = useState(false)
  const [loadingAnalysis, setLoadingAnalysis] = useState(false)
  const [ytError, setYtError] = useState<string | null>(null)
  const [waError, setWaError] = useState<string | null>(null)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [spotifyConnected, setSpotifyConnected] = useState(user?.spotify_connected ?? false)
  const [fitConnected, setFitConnected] = useState(user?.google_fit_connected ?? false)
  const [mlResult, setMlResult] = useState<Record<string, unknown> | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [ytFileName, setYtFileName] = useState<string | null>(null)
  const [waFileName, setWaFileName] = useState<string | null>(null)

  const watchRef = useRef<HTMLInputElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)
  const waRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const p = new URLSearchParams(window.location.search)
    if (p.get('spotify_connected') === '1' || p.get('fit_connected') === '1') {
      if (p.get('spotify_connected') === '1') setSpotifyConnected(true)
      if (p.get('fit_connected') === '1') setFitConnected(true)
      window.history.replaceState({}, '', '/dashboard')
      api.get('/api/auth/me').then(({ data }) => setUser(data)).catch(() => {})
    }
  }, [])

  useEffect(() => { if (spotifyConnected) fetchSpotify() }, [spotifyConnected])
  useEffect(() => { if (fitConnected) fetchFit() }, [fitConnected])
  // Auto-fetch Spotify when switching to Music tab
  useEffect(() => {
    if (tab === 'music' && spotifyConnected && !spotifyData && !loadingSpotify) fetchSpotify()
  }, [tab])

  const [spotifyError, setSpotifyError] = useState<string | null>(null)
  const fetchSpotify = useCallback(async () => {
    setLoadingSpotify(true)
    setSpotifyError(null)
    try { const { data } = await api.get('/api/connectors/spotify/analysis'); setSpotifyData(data) }
    catch (e: unknown) {
      const status = (e as { response?: { status?: number; data?: { detail?: string } } })?.response?.status
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      if (status === 401) {
        // Token expired — mark disconnected so tile shows reconnect
        setSpotifyConnected(false)
        setSpotifyError('Spotify session expired. Please reconnect.')
      } else {
        setSpotifyError(msg || 'Failed to load Spotify data. Try reconnecting.')
      }
    } finally { setLoadingSpotify(false) }
  }, [])

  const fetchFit = useCallback(async () => {
    setLoadingFit(true)
    try { const { data } = await api.get('/api/connectors/googlefit/analysis'); setGoogleFitData(data) }
    catch {} finally { setLoadingFit(false) }
  }, [])

  const connectSpotify = () => { window.location.href = `${API_URL}/api/connectors/spotify/connect?token=${token}` }
  const connectFit = () => { window.location.href = `${API_URL}/api/connectors/googlefit/connect?token=${token}` }

  const handleYtUpload = async () => {
    const f = watchRef.current?.files?.[0]
    if (!f) { setYtError('Select watch-history.html'); return }
    setLoadingYoutube(true); setYtError(null)
    const fd = new FormData(); fd.append('watch_history', f)
    const sf = searchRef.current?.files?.[0]; if (sf) fd.append('search_history', sf)
    try {
      const { data } = await api.post('/api/connectors/youtube/analyze', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setYoutubeData(data); setTab('youtube')
    } catch (e: unknown) {
      setYtError((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Analysis failed')
    } finally { setLoadingYoutube(false) }
  }

  const handleWaUpload = async () => {
    const f = waRef.current?.files?.[0]
    if (!f) { setWaError('Select _chat.txt'); return }
    setLoadingWhatsapp(true); setWaError(null)
    const fd = new FormData(); fd.append('chat_file', f)
    try {
      const { data } = await api.post('/api/connectors/whatsapp/analyze', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setWhatsappData(data); setTab('whatsapp')
    } catch (e: unknown) {
      setWaError((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Analysis failed')
    } finally { setLoadingWhatsapp(false) }
  }

  const showToast = (msg: string) => { setToast(msg); setTimeout(() => setToast(null), 3500) }

  const runAnalysis = async () => {
    setLoadingAnalysis(true); setAnalysisError(null)
    try {
      const { data } = await api.post('/api/analysis/run', { spotify_data: spotifyData, youtube_data: youtubeData, whatsapp_data: whatsappData })
      setMlResult(data); setTab('overview'); showToast(`AI Score: ${data.overall_wellness_score} · ${data.risk_level}`)
    } catch (e: unknown) {
      setAnalysisError((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Analysis failed')
    } finally { setLoadingAnalysis(false) }
  }

  const simpleScore = computeScore(spotifyData, youtubeData, whatsappData)
  const overallScore = mlResult ? (mlResult.overall_wellness_score as number) : simpleScore
  const { label: riskLabel, color: riskColor, glow: riskGlow } = riskInfo(overallScore)
  const scoreColor = overallScore === null ? 'var(--tx-3)' : overallScore >= 65 ? '#22C55E' : overallScore >= 40 ? '#F59E0B' : '#EF4444'
  const chartGrid = dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'
  const chartTick = 'var(--tx-3)'
  const chartTooltip = { background: dark ? '#161616' : '#fff', border: '1px solid var(--border)', borderRadius: 16, fontSize: 12, color: 'var(--tx)' }

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 size={13} /> },
    { id: 'music', label: 'Music', icon: <Music size={13} /> },
    { id: 'youtube', label: 'YouTube', icon: <Youtube size={13} /> },
    { id: 'whatsapp', label: 'WhatsApp', icon: <MessageCircle size={13} /> },
    { id: 'googlefit', label: 'Google Fit', icon: <Activity size={13} /> },
    { id: 'predictions', label: 'Predictions', icon: <TrendingUp size={13} /> },
  ]

  return (
    <div className="min-h-screen" style={{ background: 'var(--canvas)' }}>
      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div initial={{ opacity: 0, y: -20, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -20 }}
            transition={{ type: 'spring', stiffness: 380, damping: 32 }}
            className="fixed top-16 left-1/2 z-50 flex items-center gap-3 px-5 py-3 rounded-2xl text-sm font-bold -translate-x-1/2 whitespace-nowrap"
            style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--tx)', boxShadow: 'var(--sh-xl)' }}>
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />{toast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Nav */}
      <nav className="sticky top-0 z-40 glass" style={{ borderBottom: '1px solid var(--border)', height: 56 }}>
        <div className="max-w-6xl mx-auto px-5 h-full flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)' }}>
              <Brain size={16} className="text-white" />
            </div>
            <span className="font-black text-base" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>MindWatch</span>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setChatOpen(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold text-white transition-all hover:opacity-90 hover:scale-105 active:scale-95"
              style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)', boxShadow: '0 2px 16px rgba(99,102,241,0.35)' }}>
              <Sparkles size={13} />Ask AI
            </button>
            <button onClick={toggleTheme} className="w-9 h-9 rounded-xl flex items-center justify-center transition-all hover:scale-110"
              style={{ background: 'var(--raised)', color: 'var(--tx-2)' }}>
              {dark ? <Sun size={15} /> : <Moon size={15} />}
            </button>
            <Bell size={15} style={{ color: 'var(--tx-3)', cursor: 'pointer' }} />
            {user?.picture
              ? <img src={user.picture} alt="" className="w-8 h-8 rounded-full object-cover" />
              : <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-black text-white" style={{ background: 'linear-gradient(135deg,#6366F1,#A855F7)' }}>{user?.name?.[0]?.toUpperCase()}</div>
            }
            <button onClick={() => { logout(); navigate('/') }} className="w-9 h-9 rounded-xl flex items-center justify-center transition-all hover:scale-110" style={{ background: 'var(--raised)', color: 'var(--tx-2)' }}>
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-5 py-8 space-y-5">
        {/* Welcome + Run Button */}
        <BlurReveal>
          <div className="flex items-end justify-between flex-wrap gap-4">
            <div>
              <p className="text-sm font-medium mb-1" style={{ color: 'var(--tx-3)' }}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</p>
              <h1 className="font-black leading-tight" style={{ fontSize: 'clamp(1.75rem,3vw,2.5rem)', letterSpacing: '-0.03em', color: 'var(--tx)' }}>
                {getGreeting()}, {user?.name?.split(' ')[0]}. 👋
              </h1>
            </div>
            <div className="flex flex-col items-end gap-1">
              <button onClick={runAnalysis} disabled={loadingAnalysis || (!spotifyData && !youtubeData && !whatsappData)}
                className="flex items-center gap-2.5 px-6 py-3 rounded-2xl text-white font-bold transition-all hover:scale-105 active:scale-95 disabled:opacity-40"
                style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)', boxShadow: '0 4px 24px rgba(99,102,241,0.4)' }}>
                {loadingAnalysis ? <><LoadingSpinner size={16} color="#fff" />Running AI...</> : <><Sparkles size={15} />Run Full AI Analysis</>}
              </button>
              {analysisError && <p className="text-xs" style={{ color: '#EF4444' }}>{analysisError}</p>}
            </div>
          </div>
        </BlurReveal>

        {/* Score + Sources Grid */}
        <div className="grid grid-cols-12 gap-4">
          {/* Score Hero */}
          <BlurReveal delay={0.05} className="col-span-12 md:col-span-5">
            <div className="tile-lg rounded-4xl p-8 h-full relative overflow-hidden noise" style={{ minHeight: 340 }}>
              <Aurora intensity="low" />
              <div className="relative z-10 flex flex-col items-center justify-center h-full gap-5 py-4">
                <ScoreCard score={overallScore} size={200} strokeWidth={14} />
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 flex-wrap mb-3">
                    <span className="font-black text-xl" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Overall Wellness</span>
                    {mlResult && (
                      <span className="text-xs font-bold px-2.5 py-1 rounded-pill" style={{ background: 'rgba(99,102,241,0.12)', color: '#6366F1', border: '1px solid rgba(99,102,241,0.25)' }}>
                        <Sparkles size={9} className="inline mr-1" />{(mlResult.fuzzy_method as string) === 'fuzzy_mamdani' ? 'Mamdani FIS' : 'AI'}
                      </span>
                    )}
                  </div>
                  <span className="inline-flex items-center gap-1.5 text-sm font-bold px-4 py-2 rounded-pill"
                    style={{ background: `${riskColor}15`, color: riskColor, border: `1px solid ${riskColor}30`, boxShadow: `0 0 20px ${riskGlow}` }}>
                    {riskLabel}
                  </span>
                </div>
                <div className="flex gap-6">
                  {[
                    { icon: Music, label: 'Music', val: mlResult ? (mlResult.scores as Record<string,number>).linguistic : spotifyData?.mood_score, color: '#6366F1' },
                    { icon: Youtube, label: 'Content', val: mlResult ? (mlResult.scores as Record<string,number>).consumption : youtubeData?.emotional_diet_score, color: '#EF4444' },
                    { icon: MessageCircle, label: 'Chat', val: mlResult ? (mlResult.scores as Record<string,number>).behavioral : whatsappData?.sentiment_score, color: '#22C55E' },
                  ].map(({ icon: Icon, label, val, color }) => (
                    <div key={label} className="flex flex-col items-center gap-1">
                      <Icon size={13} style={{ color }} />
                      <span className="font-black tabular-nums" style={{ color, fontSize: 20, letterSpacing: '-0.02em' }}>{val ?? '–'}</span>
                      <span className="text-xs" style={{ color: 'var(--tx-3)' }}>{label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </BlurReveal>

          {/* Source Tiles */}
          <div className="col-span-12 md:col-span-7 grid grid-cols-2 gap-4">
            {[
              { icon: <Music size={20} style={{ color: '#6366F1' }} />, name: 'Spotify', desc: 'Music & emotion AI', connected: spotifyConnected, onConnect: connectSpotify, ac: '#6366F1', bg: 'linear-gradient(135deg,rgba(99,102,241,0.08),rgba(168,85,247,0.05))' },
              { icon: <Youtube size={20} style={{ color: '#EF4444' }} />, name: 'YouTube', desc: 'Content diet analysis', connected: youtubeData !== null, onConnect: () => setTab('youtube'), ac: '#EF4444', bg: 'linear-gradient(135deg,rgba(239,68,68,0.08),rgba(245,158,11,0.05))' },
              { icon: <MessageCircle size={20} style={{ color: '#22C55E' }} />, name: 'WhatsApp', desc: 'Sentiment & behavior', connected: whatsappData !== null, onConnect: () => setTab('whatsapp'), ac: '#22C55E', bg: 'linear-gradient(135deg,rgba(34,197,94,0.08),rgba(6,182,212,0.05))' },
              { icon: <Activity size={20} style={{ color: '#06B6D4' }} />, name: 'Google Fit', desc: 'Physical wellness', connected: fitConnected, onConnect: connectFit, ac: '#06B6D4', bg: 'linear-gradient(135deg,rgba(6,182,212,0.08),rgba(0,113,227,0.05))' },
            ].map((s, i) => (
              <BlurReveal key={s.name} delay={0.07 + i * 0.04}>
                <motion.div whileHover={{ scale: 1.015, y: -3 }} transition={{ type: 'spring', stiffness: 300, damping: 28 }}
                  className="tile rounded-3xl p-6 relative overflow-hidden cursor-default noise h-full" style={{ background: s.bg }}>
                  <div className="absolute -right-4 -top-4 w-16 h-16 rounded-full blur-2xl opacity-20" style={{ background: s.ac }} />
                  <div className="flex items-start justify-between mb-4 relative z-10">
                    <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ background: `${s.ac}20`, border: `1px solid ${s.ac}30` }}>{s.icon}</div>
                    {s.connected
                      ? <span className="text-xs font-bold px-2.5 py-1.5 rounded-pill flex items-center gap-1.5" style={{ background: 'rgba(34,197,94,0.12)', color: '#22C55E', border: '1px solid rgba(34,197,94,0.25)' }}>
                          <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />Live
                        </span>
                      : <button onClick={s.onConnect} className="text-xs font-bold px-3 py-1.5 rounded-xl text-white transition-all hover:scale-105" style={{ background: s.ac, boxShadow: `0 2px 12px ${s.ac}55` }}>Connect</button>
                    }
                  </div>
                  <p className="font-black text-base relative z-10" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>{s.name}</p>
                  <p className="text-xs mt-1 relative z-10" style={{ color: 'var(--tx-2)' }}>{s.desc}</p>
                </motion.div>
              </BlurReveal>
            ))}
          </div>
        </div>

        {/* ML Result Banner */}
        <AnimatePresence>
          {mlResult && (
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="tile rounded-3xl p-6 relative overflow-hidden noise"
              style={{ background: 'linear-gradient(135deg,rgba(99,102,241,0.1),rgba(168,85,247,0.08))' }}>
              <div className="absolute -right-8 -top-8 w-32 h-32 rounded-full blur-3xl opacity-25" style={{ background: 'radial-gradient(circle,#6366F1,transparent)' }} />
              <div className="flex flex-col sm:flex-row sm:items-center gap-4 relative z-10">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles size={15} style={{ color: '#6366F1' }} />
                    <span className="font-black text-sm" style={{ color: 'var(--tx)' }}>Fuzzy Logic AI Result</span>
                    <span className="text-xs font-bold px-2.5 py-1 rounded-pill" style={{ background: 'rgba(99,102,241,0.15)', color: '#6366F1' }}>
                      {(mlResult.fuzzy_method as string) === 'fuzzy_mamdani' ? 'Mamdani FIS' : 'Weighted Avg'}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--tx-2)' }}>{mlResult.explanation as string}</p>
                </div>
                <div className="flex gap-2 flex-wrap">
                  {(mlResult.data_sources_used as string[]).map(src => (
                    <span key={src} className="text-xs font-bold px-3 py-1.5 rounded-xl capitalize" style={{ background: 'var(--raised)', color: 'var(--tx-2)', border: '1px solid var(--border)' }}>{src}</span>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tabs */}
        <div className="flex gap-1 overflow-x-auto no-scroll p-1 rounded-2xl w-fit" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-bold whitespace-nowrap transition-all"
              style={tab === t.id ? { background: 'linear-gradient(135deg,#6366F1,#A855F7)', color: '#fff', boxShadow: '0 2px 12px rgba(99,102,241,0.4)' } : { color: 'var(--tx-2)', background: 'transparent' }}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div key={tab}
            initial={{ opacity: 0, y: 12, filter: 'blur(4px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -8, filter: 'blur(2px)' }}
            transition={{ duration: 0.2, ease: [0.16,1,0.3,1] }}>

            {tab === 'overview' && (
              <div className="grid grid-cols-12 gap-4">
                <Tile className="col-span-12 md:col-span-6 p-7">
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-9 h-9 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(99,102,241,0.1)' }}><Music size={17} style={{ color: '#6366F1' }} /></div>
                      <span className="font-black" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Music Mood</span>
                    </div>
                    {spotifyConnected && !loadingSpotify && <button onClick={fetchSpotify}><RefreshCw size={13} style={{ color: 'var(--tx-3)' }} /></button>}
                    {loadingSpotify && <LoadingSpinner size={14} />}
                  </div>
                  {spotifyData ? (
                    <>
                      <div className="flex items-end gap-3 mb-6">
                        <span className="font-black leading-none" style={{ fontSize: 56, color: '#6366F1', letterSpacing: '-0.04em' }}>{spotifyData.mood_score}</span>
                        <div className="pb-2"><p className="font-bold text-sm" style={{ color: 'var(--tx)' }}>{spotifyData.emotional_tone}</p><p className="text-xs" style={{ color: 'var(--tx-3)' }}>{spotifyData.total_tracks_analyzed} tracks</p></div>
                      </div>
                      <div className="space-y-3">
                        <MoodBar label="Happiness" value={spotifyData.avg_valence*100} color="#6366F1" thick />
                        <MoodBar label="Energy" value={spotifyData.avg_energy*100} color="#F59E0B" thick />
                        <MoodBar label="Danceability" value={spotifyData.avg_danceability*100} color="#22C55E" thick />
                      </div>
                    </>
                  ) : (
                    <div className="flex flex-col items-center py-6 gap-3">
                      {loadingSpotify ? (
                        <LoadingSpinner size={24} />
                      ) : spotifyConnected ? (
                        <>
                          {spotifyError && <p className="text-xs text-center" style={{ color: '#EF4444' }}>{spotifyError}</p>}
                          <button onClick={fetchSpotify} className="text-sm font-bold px-4 py-2.5 rounded-xl text-white" style={{ background: '#6366F1' }}>
                            Retry Load
                          </button>
                          <button onClick={connectSpotify} className="text-xs underline" style={{ color: 'var(--tx-3)' }}>Reconnect Spotify</button>
                        </>
                      ) : (
                        <>
                          <p className="text-sm text-center" style={{ color: 'var(--tx-2)' }}>Connect Spotify to see your music mood analysis</p>
                          <button onClick={connectSpotify} className="text-sm font-bold px-4 py-2 rounded-xl text-white" style={{ background: '#6366F1' }}>Connect Spotify</button>
                        </>
                      )}
                    </div>
                  )}
                </Tile>

                <Tile className="col-span-12 md:col-span-6 p-7">
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-9 h-9 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(239,68,68,0.1)' }}><Youtube size={17} style={{ color: '#EF4444' }} /></div>
                      <span className="font-black" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Content Diet</span>
                    </div>
                  </div>
                  {youtubeData ? (
                    <>
                      <div className="flex items-end gap-3 mb-6">
                        <span className="font-black leading-none" style={{ fontSize: 56, color: '#EF4444', letterSpacing: '-0.04em' }}>{youtubeData.emotional_diet_score}</span>
                        <div className="pb-2"><p className="font-bold text-sm" style={{ color: 'var(--tx)' }}>{youtubeData.content_mood}</p><p className="text-xs" style={{ color: 'var(--tx-3)' }}>{youtubeData.total_videos} videos</p></div>
                      </div>
                      <div className="space-y-3">
                        <MoodBar label="Positive" value={youtubeData.recovery_score} color="#22C55E" thick />
                        <MoodBar label="Dark Content" value={youtubeData.dark_content_percentage} color="#EF4444" thick />
                      </div>
                    </>
                  ) : (
                    <div className="flex flex-col items-center py-6 gap-3">
                      <p className="text-sm text-center" style={{ color: 'var(--tx-2)' }}>Upload YouTube history to analyze content patterns</p>
                      <button onClick={() => setTab('youtube')} className="text-sm font-bold px-4 py-2 rounded-xl text-white" style={{ background: '#EF4444' }}>Upload History</button>
                    </div>
                  )}
                </Tile>

                <Tile className="col-span-12 md:col-span-5 p-7">
                  <div className="flex items-center gap-2.5 mb-5">
                    <div className="w-9 h-9 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(6,182,212,0.1)' }}><Clock size={17} style={{ color: '#06B6D4' }} /></div>
                    <span className="font-black" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Recently Played</span>
                  </div>
                  {spotifyData?.recently_played.length ? (
                    <div className="space-y-3.5">
                      {spotifyData.recently_played.slice(0,6).map((t,i) => (
                        <div key={i} className="flex items-center gap-3">
                          {t.album_art ? <img src={t.album_art} alt="" className="w-11 h-11 rounded-xl object-cover flex-shrink-0" />
                            : <div className="w-11 h-11 rounded-xl flex-shrink-0 flex items-center justify-center" style={{ background: 'var(--raised)' }}><Music size={14} style={{ color: 'var(--tx-3)' }} /></div>}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-bold truncate" style={{ color: 'var(--tx)' }}>{t.name}</p>
                            <p className="text-xs truncate" style={{ color: 'var(--tx-2)' }}>{t.artist}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : <p className="text-sm" style={{ color: 'var(--tx-2)' }}>No recent tracks.</p>}
                </Tile>

                <Tile className="col-span-12 md:col-span-7 p-7">
                  <div className="flex items-center gap-2.5 mb-5">
                    <div className="w-9 h-9 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(245,158,11,0.1)' }}><Zap size={17} style={{ color: '#F59E0B' }} /></div>
                    <span className="font-black" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Quick Insights</span>
                  </div>
                  <div className="space-y-2.5">
                    {[
                      ...(spotifyData ? [`Music tone: ${spotifyData.emotional_tone}`] : []),
                      ...(youtubeData?.insights?.slice(0,2) ?? []),
                      ...(whatsappData?.insights?.slice(0,2) ?? []),
                    ].length > 0
                      ? [...(spotifyData ? [`Music tone: ${spotifyData.emotional_tone}`] : []), ...(youtubeData?.insights?.slice(0,2)??[]), ...(whatsappData?.insights?.slice(0,2)??[])].map((ins,i) => (
                          <InsightCard key={i} text={ins} type={ins.toLowerCase().includes('high')||ins.toLowerCase().includes('concerning')?'warning':'info'} />
                        ))
                      : <p className="text-sm" style={{ color: 'var(--tx-2)' }}>Connect your data sources to see personalized insights here.</p>
                    }
                  </div>
                </Tile>

                {mlResult && (() => {
                  const pred = mlResult.predictions as { available: boolean; predictions: Array<{ date: string; predicted_score: number }>; overall_trend: string; method: string }
                  if (!pred?.available || !pred.predictions?.length) return null
                  const cd = pred.predictions.map(p => ({ date: new Date(p.date).toLocaleDateString('en-US',{month:'short',day:'numeric'}), score: p.predicted_score }))
                  const tC = pred.overall_trend==='improving'?'#22C55E':pred.overall_trend==='declining'?'#EF4444':'#F59E0B'
                  return (
                    <Tile className="col-span-12 p-7">
                      <div className="flex items-center justify-between mb-5">
                        <div className="flex items-center gap-2.5">
                          <div className="w-9 h-9 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(99,102,241,0.1)' }}><TrendingUp size={17} style={{ color: '#6366F1' }} /></div>
                          <span className="font-black" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>7-Day Forecast</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold px-3 py-1.5 rounded-pill" style={{ background: `${tC}15`, color: tC, border: `1px solid ${tC}30` }}>{pred.overall_trend}</span>
                          <span className="text-xs" style={{ color: 'var(--tx-3)' }}>{pred.method}</span>
                        </div>
                      </div>
                      <ResponsiveContainer width="100%" height={220}>
                        <AreaChart data={cd} margin={{ top:5, right:5, bottom:0, left:-25 }}>
                          <defs>
                            <linearGradient id="fg3" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#6366F1" stopOpacity={0.25} />
                              <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke={chartGrid} />
                          <XAxis dataKey="date" tick={{ fontSize:11, fill:chartTick }} tickLine={false} axisLine={false} />
                          <YAxis domain={[0,100]} tick={{ fontSize:11, fill:chartTick }} tickLine={false} axisLine={false} />
                          <Tooltip contentStyle={chartTooltip} formatter={(v: number) => [`${v}`, 'Score']} />
                          <ReferenceLine y={65} stroke="#22C55E" strokeDasharray="4 4" />
                          <ReferenceLine y={40} stroke="#F59E0B" strokeDasharray="4 4" />
                          <Area type="monotone" dataKey="score" stroke="#6366F1" strokeWidth={2.5} fill="url(#fg3)" dot={{ r:5, fill:'#6366F1', strokeWidth:0 }} activeDot={{ r:7 }} />
                        </AreaChart>
                      </ResponsiveContainer>
                    </Tile>
                  )
                })()}
              </div>
            )}

            {tab === 'music' && (
              <div className="grid grid-cols-12 gap-4">
                {!spotifyConnected ? (
                  <Tile className="col-span-12 p-16 text-center">
                    <div className="w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-6" style={{ background: 'rgba(99,102,241,0.1)' }}><Music size={36} style={{ color: '#6366F1' }} /></div>
                    <h3 className="font-black text-2xl mb-3" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Connect Spotify</h3>
                    <p className="text-base mb-8 max-w-sm mx-auto" style={{ color: 'var(--tx-2)' }}>BERT emotion AI analyzes your listening patterns.</p>
                    <button onClick={connectSpotify} className="px-8 py-4 rounded-2xl font-black text-white text-base transition-all hover:scale-105" style={{ background: 'linear-gradient(135deg,#6366F1,#A855F7)' }}>Connect Spotify</button>
                  </Tile>
                ) : loadingSpotify ? (
                  <Tile className="col-span-12 p-20 flex justify-center"><LoadingSpinner size={48} /></Tile>
                ) : spotifyData ? (
                  <>
                    <Tile className="col-span-12 md:col-span-6 p-8">
                      <h3 className="font-black text-xl mb-6" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Audio Profile</h3>
                      <div className="space-y-5">
                        <MoodBar label="Happiness (Valence)" value={spotifyData.avg_valence*100} color="#6366F1" thick />
                        <MoodBar label="Energy" value={spotifyData.avg_energy*100} color="#F59E0B" thick />
                        <MoodBar label="Danceability" value={spotifyData.avg_danceability*100} color="#22C55E" thick />
                        <MoodBar label="Late Night Listening" value={spotifyData.late_night_ratio*100} color="#EF4444" thick />
                      </div>
                      <div className="grid grid-cols-2 gap-4 mt-7">
                        {[{label:'Avg BPM',val:spotifyData.avg_tempo,color:'#06B6D4'},{label:'Mood Score',val:spotifyData.mood_score,color:'#6366F1'}].map(s => (
                          <div key={s.label} className="rounded-2xl p-5 text-center" style={{ background: 'var(--raised)' }}>
                            <p className="font-black text-3xl leading-none mb-1" style={{ color: s.color, letterSpacing: '-0.03em' }}>{s.val}</p>
                            <p className="text-xs font-medium" style={{ color: 'var(--tx-2)' }}>{s.label}</p>
                          </div>
                        ))}
                      </div>
                    </Tile>
                    <Tile className="col-span-12 md:col-span-6 p-8">
                      <h3 className="font-black text-xl mb-6" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Recently Played</h3>
                      <div className="space-y-4">
                        {spotifyData.recently_played.map((t,i) => (
                          <div key={i} className="flex items-center gap-4">
                            {t.album_art ? <img src={t.album_art} alt="" className="w-12 h-12 rounded-2xl object-cover flex-shrink-0" />
                              : <div className="w-12 h-12 rounded-2xl flex-shrink-0 flex items-center justify-center" style={{ background: 'var(--raised)' }}><Music size={16} style={{ color: 'var(--tx-3)' }} /></div>}
                            <div className="flex-1 min-w-0">
                              <p className="font-bold truncate" style={{ color: 'var(--tx)' }}>{t.name}</p>
                              <p className="text-sm truncate" style={{ color: 'var(--tx-2)' }}>{t.artist}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </Tile>
                  </>
                ) : (
                  <Tile className="col-span-12 p-10 text-center">
                    {spotifyError && <p className="text-sm mb-4" style={{ color: '#EF4444' }}>{spotifyError}</p>}
                    <p className="text-sm mb-5" style={{ color: 'var(--tx-2)' }}>Spotify data couldn't be loaded. Your token may have expired.</p>
                    <div className="flex items-center justify-center gap-3">
                      <button onClick={fetchSpotify} className="px-6 py-3 rounded-2xl font-bold text-white" style={{ background: '#6366F1' }}>
                        Retry
                      </button>
                      <button onClick={connectSpotify} className="px-6 py-3 rounded-2xl font-bold" style={{ background: 'var(--raised)', color: 'var(--tx-2)', border: '1px solid var(--border)' }}>
                        Reconnect Spotify
                      </button>
                    </div>
                  </Tile>
                )}
              </div>
            )}

            {tab === 'youtube' && (
              <div className="grid grid-cols-12 gap-4">
                {!youtubeData ? (
                  <Tile className="col-span-12 p-10">
                    <div className="max-w-lg mx-auto">
                      <div className="flex items-center gap-4 mb-7">
                        <div className="w-14 h-14 rounded-3xl flex items-center justify-center" style={{ background: 'rgba(239,68,68,0.1)' }}><Youtube size={28} style={{ color: '#EF4444' }} /></div>
                        <div>
                          <h3 className="font-black text-xl" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Analyze YouTube History</h3>
                          <p className="text-sm" style={{ color: 'var(--tx-2)' }}>Google Takeout → YouTube → watch-history.html</p>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <UploadZone label="Watch History (required)" fileName={ytFileName} accept=".html" inputRef={watchRef} onFileChange={e => setYtFileName(e.target.files?.[0]?.name || null)} color="#EF4444" />
                        <UploadZone label="Search History (optional)" fileName={null} accept=".html" inputRef={searchRef} onFileChange={() => {}} color="#EF4444" />
                        {ytError && <p className="text-sm" style={{ color: '#EF4444' }}>{ytError}</p>}
                        <button onClick={handleYtUpload} disabled={loadingYoutube}
                          className="w-full py-4 rounded-2xl font-black text-white flex items-center justify-center gap-2 text-base disabled:opacity-50 transition-all hover:scale-[1.01]"
                          style={{ background: 'linear-gradient(135deg,#EF4444,#F59E0B)' }}>
                          {loadingYoutube ? <><LoadingSpinner size={18} color="#fff" />Analyzing...</> : <><Upload size={17} />Analyze History</>}
                        </button>
                      </div>
                    </div>
                  </Tile>
                ) : (
                  <>
                    <Tile className="col-span-12 md:col-span-5 p-8">
                      <h3 className="font-black text-xl mb-6" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Emotional Diet</h3>
                      <div className="flex items-end gap-3 mb-6">
                        <span className="font-black leading-none" style={{ fontSize:72, color:youtubeData.emotional_diet_score>=60?'#22C55E':youtubeData.emotional_diet_score>=40?'#F59E0B':'#EF4444', letterSpacing:'-0.04em' }}>{youtubeData.emotional_diet_score}</span>
                        <div className="pb-3"><p className="font-bold text-sm" style={{ color: 'var(--tx)' }}>{youtubeData.content_mood}</p><p className="text-xs" style={{ color: 'var(--tx-3)' }}>{youtubeData.total_videos} videos</p></div>
                      </div>
                      <div className="space-y-4">
                        <MoodBar label="Positive Content" value={youtubeData.recovery_score} color="#22C55E" thick />
                        <MoodBar label="Dark Content" value={youtubeData.dark_content_percentage} color="#EF4444" thick />
                        <MoodBar label="Rumination" value={youtubeData.rumination_score} color="#F59E0B" thick />
                      </div>
                    </Tile>
                    <Tile className="col-span-12 md:col-span-7 p-8">
                      <h3 className="font-black text-xl mb-6" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Category Breakdown</h3>
                      <div className="space-y-3.5">
                        {Object.entries(youtubeData.category_breakdown).sort(([,a],[,b])=>b-a).slice(0,7).map(([cat,pct]) => (
                          <MoodBar key={cat} label={cat.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())} value={pct} thick
                            color={cat==='dark_content'?'#EF4444':cat==='motivational'?'#22C55E':cat==='educational'?'#6366F1':'#06B6D4'} />
                        ))}
                      </div>
                    </Tile>
                    <Tile className="col-span-12 p-8">
                      <h3 className="font-black text-xl mb-5" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Insights</h3>
                      <div className="grid md:grid-cols-2 gap-3">
                        {youtubeData.insights.map((ins,i) => <InsightCard key={i} text={ins} type={ins.includes('high')||ins.includes('elevated')?'warning':ins.includes('good')||ins.includes('strong')?'success':'info'} />)}
                      </div>
                      <button onClick={() => { setYoutubeData(null); if (watchRef.current) watchRef.current.value='' }} className="text-xs mt-4 underline" style={{ color: 'var(--tx-3)' }}>Upload new file</button>
                    </Tile>
                  </>
                )}
              </div>
            )}

            {tab === 'whatsapp' && (
              <div className="grid grid-cols-12 gap-4">
                {!whatsappData ? (
                  <Tile className="col-span-12 p-10">
                    <div className="max-w-lg mx-auto">
                      <div className="flex items-center gap-4 mb-7">
                        <div className="w-14 h-14 rounded-3xl flex items-center justify-center" style={{ background: 'rgba(34,197,94,0.1)' }}><MessageCircle size={28} style={{ color: '#22C55E' }} /></div>
                        <div>
                          <h3 className="font-black text-xl" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Analyze WhatsApp</h3>
                          <p className="text-sm" style={{ color: 'var(--tx-2)' }}>Open chat → ··· → More → Export Chat → Without Media</p>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <UploadZone label="WhatsApp Export (.txt)" fileName={waFileName} accept=".txt" inputRef={waRef} onFileChange={e => setWaFileName(e.target.files?.[0]?.name || null)} color="#22C55E" />
                        {waError && <p className="text-sm" style={{ color: '#EF4444' }}>{waError}</p>}
                        <button onClick={handleWaUpload} disabled={loadingWhatsapp}
                          className="w-full py-4 rounded-2xl font-black text-white flex items-center justify-center gap-2 text-base disabled:opacity-50 transition-all hover:scale-[1.01]"
                          style={{ background: 'linear-gradient(135deg,#22C55E,#06B6D4)' }}>
                          {loadingWhatsapp ? <><LoadingSpinner size={18} color="#fff" />Analyzing...</> : <><Upload size={17} />Analyze Chat</>}
                        </button>
                      </div>
                    </div>
                  </Tile>
                ) : (
                  <>
                    <Tile className="col-span-12 md:col-span-5 p-8">
                      <h3 className="font-black text-xl mb-6" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Sentiment</h3>
                      <div className="flex items-end gap-3 mb-6">
                        <span className="font-black leading-none" style={{ fontSize:72, color:whatsappData.sentiment_score>=60?'#22C55E':whatsappData.sentiment_score>=40?'#F59E0B':'#EF4444', letterSpacing:'-0.04em' }}>{whatsappData.sentiment_score}</span>
                        <div className="pb-3"><p className="font-bold text-sm" style={{ color: 'var(--tx)' }}>{whatsappData.emotional_tone}</p><p className="text-xs" style={{ color: 'var(--tx-3)' }}>{whatsappData.total_messages} messages</p></div>
                      </div>
                      <div className="space-y-4">
                        <MoodBar label="Late Night Messaging" value={whatsappData.late_night_ratio*100} color="#F59E0B" thick />
                        <MoodBar label="Isolation Score" value={whatsappData.isolation_score} color="#EF4444" thick />
                      </div>
                      <div className="grid grid-cols-3 gap-3 mt-5">
                        {[{l:'Avg/day',v:whatsappData.avg_messages_per_day},{l:'People',v:whatsappData.unique_senders},{l:'Days',v:whatsappData.total_days_active}].map(s => (
                          <div key={s.l} className="rounded-2xl p-4 text-center" style={{ background: 'var(--raised)' }}>
                            <p className="font-black text-2xl" style={{ color: 'var(--tx)', letterSpacing: '-0.03em' }}>{s.v}</p>
                            <p className="text-xs mt-0.5" style={{ color: 'var(--tx-2)' }}>{s.l}</p>
                          </div>
                        ))}
                      </div>
                    </Tile>
                    <Tile className="col-span-12 md:col-span-7 p-8">
                      <h3 className="font-black text-xl mb-5" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Top Words</h3>
                      <div className="flex flex-wrap gap-2 mb-5">
                        {whatsappData.top_words.slice(0,20).map(w => (
                          <span key={w.word} className="px-3.5 py-1.5 rounded-2xl font-medium" style={{ fontSize:Math.max(11,Math.min(16,11+w.count/4)), background:'var(--raised)', border:'1px solid var(--border)', color:'var(--tx-2)' }}>{w.word}</span>
                        ))}
                      </div>
                      <div className="text-sm space-y-1">
                        <p style={{ color: 'var(--tx-2)' }}>Trend: <span className="font-bold" style={{ color:whatsappData.message_frequency_trend==='increasing'?'#22C55E':whatsappData.message_frequency_trend==='decreasing'?'#EF4444':'var(--tx)' }}>{whatsappData.message_frequency_trend}</span></p>
                        <p style={{ color: 'var(--tx-2)' }}>Most active: {whatsappData.most_active_hours.join(', ')}</p>
                      </div>
                    </Tile>
                    <Tile className="col-span-12 p-8">
                      <h3 className="font-black text-xl mb-5" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Insights</h3>
                      <div className="grid md:grid-cols-2 gap-3">
                        {whatsappData.insights.map((ins,i) => <InsightCard key={i} text={ins} type={ins.includes('high')||ins.includes('declining')?'warning':ins.includes('healthy')||ins.includes('positive')?'success':'info'} />)}
                      </div>
                      <button onClick={() => { setWhatsappData(null); if (waRef.current) waRef.current.value='' }} className="text-xs mt-4 underline" style={{ color: 'var(--tx-3)' }}>Upload new file</button>
                    </Tile>
                  </>
                )}
              </div>
            )}

            {tab === 'googlefit' && (
              <div className="grid grid-cols-12 gap-4">
                {!fitConnected ? (
                  <Tile className="col-span-12 p-16 text-center">
                    <div className="w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-6" style={{ background: 'rgba(6,182,212,0.1)' }}><Activity size={36} style={{ color: '#06B6D4' }} /></div>
                    <h3 className="font-black text-2xl mb-3" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>Connect Google Fit</h3>
                    <p className="text-base mb-3 max-w-sm mx-auto" style={{ color: 'var(--tx-2)' }}>Steps, heart rate, active minutes and sleep.</p>
                    <p className="text-xs mb-8 max-w-md mx-auto px-5 py-3 rounded-2xl inline-block" style={{ color: 'var(--tx-2)', background: 'var(--raised)' }}>
                      Enable Google Fit API and add redirect URI <code>http://localhost:8000/api/connectors/googlefit/callback</code>
                    </p><br />
                    <button onClick={connectFit} className="px-8 py-4 rounded-2xl font-black text-white text-base transition-all hover:scale-105" style={{ background: 'linear-gradient(135deg,#06B6D4,#0071E3)' }}>Connect Google Fit</button>
                  </Tile>
                ) : loadingFit ? (
                  <Tile className="col-span-12 p-20 flex justify-center"><LoadingSpinner size={48} /></Tile>
                ) : googleFitData ? (
                  <>
                    <div className="col-span-12 grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        {label:'Fitness Score',val:googleFitData.fitness_score,color:'#06B6D4',unit:''},
                        {label:'Daily Steps',val:googleFitData.avg_daily_steps.toLocaleString(),color:'#22C55E',unit:''},
                        {label:'Active Min/Day',val:googleFitData.avg_active_minutes,color:'#F59E0B',unit:' min'},
                        {label:'Heart Rate',val:googleFitData.avg_heart_rate||'–',color:'#EF4444',unit:googleFitData.avg_heart_rate?' bpm':''},
                      ].map(s => (
                        <Tile key={s.label} className="p-7 text-center">
                          <p className="font-black text-4xl mb-1" style={{ color:s.color, letterSpacing:'-0.03em' }}>{s.val}{s.unit}</p>
                          <p className="text-sm font-medium" style={{ color:'var(--tx-2)' }}>{s.label}</p>
                        </Tile>
                      ))}
                    </div>
                    <Tile className="col-span-12 md:col-span-5 p-8">
                      <h3 className="font-black text-xl mb-6" style={{ color:'var(--tx)', letterSpacing:'-0.02em' }}>Daily Activity</h3>
                      <div className="space-y-5">
                        <div><MoodBar label="Steps Progress" value={Math.min(100,(googleFitData.avg_daily_steps/10000)*100)} color="#22C55E" thick /><p className="text-xs mt-1" style={{ color:'var(--tx-3)' }}>Goal: 10,000 steps/day</p></div>
                        <div><MoodBar label="Activity Goal" value={Math.min(100,(googleFitData.avg_active_minutes/30)*100)} color="#F59E0B" thick /><p className="text-xs mt-1" style={{ color:'var(--tx-3)' }}>Goal: 30 min/day</p></div>
                      </div>
                      <p className="text-sm mt-5" style={{ color:'var(--tx-2)' }}>Trend: <span className="font-bold" style={{ color:googleFitData.activity_trend==='improving'?'#22C55E':googleFitData.activity_trend==='declining'?'#EF4444':'var(--tx)' }}>{googleFitData.activity_trend==='improving'?'📈':googleFitData.activity_trend==='declining'?'📉':'➡️'} {googleFitData.activity_trend}</span></p>
                    </Tile>
                    {googleFitData.steps_data.length > 0 && (
                      <Tile className="col-span-12 md:col-span-7 p-8">
                        <h3 className="font-black text-xl mb-6" style={{ color:'var(--tx)', letterSpacing:'-0.02em' }}>Steps — Last 7 Days</h3>
                        <ResponsiveContainer width="100%" height={220}>
                          <AreaChart data={googleFitData.steps_data} margin={{ top:5, right:5, bottom:0, left:-25 }}>
                            <defs><linearGradient id="sg3" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#22C55E" stopOpacity={0.3}/><stop offset="95%" stopColor="#22C55E" stopOpacity={0}/></linearGradient></defs>
                            <CartesianGrid strokeDasharray="3 3" stroke={chartGrid} />
                            <XAxis dataKey="date" tick={{ fontSize:11, fill:chartTick }} tickLine={false} axisLine={false} tickFormatter={v=>new Date(v).toLocaleDateString('en-US',{month:'short',day:'numeric'})} />
                            <YAxis tick={{ fontSize:11, fill:chartTick }} tickLine={false} axisLine={false} />
                            <Tooltip formatter={(v: number) => [v.toLocaleString(),'Steps']} contentStyle={chartTooltip} />
                            <ReferenceLine y={10000} stroke="#22C55E" strokeDasharray="4 4" />
                            <Area type="monotone" dataKey="value" stroke="#22C55E" strokeWidth={2.5} fill="url(#sg3)" dot={{ r:5, fill:'#22C55E', strokeWidth:0 }} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </Tile>
                    )}
                    <Tile className="col-span-12 p-8">
                      <h3 className="font-black text-xl mb-5" style={{ color:'var(--tx)', letterSpacing:'-0.02em' }}>Insights</h3>
                      <div className="grid md:grid-cols-2 gap-3">
                        {googleFitData.insights.map((ins,i) => <InsightCard key={i} text={ins.message} type={ins.type==='warning'?'warning':ins.type==='positive'?'success':'info'} />)}
                      </div>
                      <button onClick={fetchFit} disabled={loadingFit} className="flex items-center gap-1.5 mt-4 text-xs" style={{ color:'var(--tx-3)' }}><RefreshCw size={11}/>Refresh data</button>
                    </Tile>
                  </>
                ) : (
                  <Tile className="col-span-12 p-10 text-center">
                    <button onClick={fetchFit} className="px-8 py-4 rounded-2xl font-black text-white" style={{ background:'linear-gradient(135deg,#06B6D4,#0071E3)' }}>Load Google Fit Data</button>
                  </Tile>
                )}
              </div>
            )}

            {tab === 'predictions' && (
              <div className="grid grid-cols-12 gap-4">
                <Tile className="col-span-12 md:col-span-4 p-8">
                  <h3 className="font-black text-xl mb-6" style={{ color:'var(--tx)', letterSpacing:'-0.02em' }}>Wellness Dimensions</h3>
                  {overallScore !== null ? (
                    <div className="space-y-5">
                      {[
                        { label:'Emotional (BERT)', score:mlResult?(mlResult.scores as Record<string,number>).linguistic:(spotifyData?.mood_score??50), color:'#6366F1' },
                        { label:'Content (ML)', score:mlResult?(mlResult.scores as Record<string,number>).consumption:(youtubeData?.emotional_diet_score??50), color:'#EF4444' },
                        { label:'Behavioral', score:mlResult?(mlResult.scores as Record<string,number>).behavioral:(spotifyData?Math.round(100-spotifyData.late_night_ratio*150):50), color:'#06B6D4' },
                        { label:'Physical', score:googleFitData?.fitness_score??50, color:'#22C55E' },
                        { label:'Overall', score:overallScore, color:scoreColor },
                      ].map(d => (
                        <div key={d.label}>
                          <div className="flex justify-between text-sm mb-2"><span style={{ color:'var(--tx-2)' }}>{d.label}</span><span className="font-black" style={{ color:d.color }}>{Math.max(0,Math.round(d.score))}</span></div>
                          <MoodBar label="" value={Math.max(0,d.score)} color={d.color} thick />
                        </div>
                      ))}
                      <div className="mt-6 pt-6" style={{ borderTop:'1px solid var(--border)' }}>
                        <span className="inline-flex items-center gap-2 text-sm font-bold px-4 py-2.5 rounded-2xl" style={{ background:`${riskColor}15`, color:riskColor, border:`1px solid ${riskColor}30` }}>{riskLabel}</span>
                      </div>
                    </div>
                  ) : <p className="text-sm" style={{ color:'var(--tx-2)' }}>Connect at least one data source.</p>}
                </Tile>
                <Tile className="col-span-12 md:col-span-8 p-8">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-black text-xl" style={{ color:'var(--tx)', letterSpacing:'-0.02em' }}>AI Analysis Summary</h3>
                    {mlResult && <span className="text-xs font-bold px-3 py-1.5 rounded-pill" style={{ background:'rgba(99,102,241,0.12)', color:'#6366F1' }}><Sparkles size={10} className="inline mr-1"/>{(mlResult.fuzzy_method as string)==='fuzzy_mamdani'?'Mamdani FIS':'AI'}</span>}
                  </div>
                  <p className="text-base leading-relaxed mb-8" style={{ color:'var(--tx-2)' }}>
                    {mlResult ? mlResult.explanation as string
                      : overallScore !== null
                      ? overallScore>=65 ? 'Your wellness trajectory looks positive. Keep up your current habits and maintain social connections.'
                        : overallScore>=40 ? 'Mixed signals detected. Reduce dark content consumption and maintain regular social connections.'
                        : 'Wellness indicators suggest support may help. Consider reaching out to someone you trust.'
                      : 'Run the AI analysis to get a detailed prediction summary.'}
                  </p>
                  {!mlResult && overallScore !== null && (
                    <button onClick={runAnalysis} disabled={loadingAnalysis} className="flex items-center gap-2 px-6 py-3 rounded-2xl font-bold text-white transition-all hover:scale-105" style={{ background:'linear-gradient(135deg,#6366F1,#A855F7)' }}>
                      {loadingAnalysis ? <LoadingSpinner size={16} color="#fff" /> : <Sparkles size={15} />}
                      {loadingAnalysis ? 'Running…' : 'Run Full AI Analysis'}
                    </button>
                  )}
                  <div className="mt-8 pt-6" style={{ borderTop:'1px solid var(--border)' }}>
                    <p className="text-xs px-4 py-3 rounded-2xl" style={{ color:'var(--tx-2)', background:'rgba(245,158,11,0.07)', border:'1px solid rgba(245,158,11,0.15)' }}>
                      ⚠️ AI predictions are for wellness awareness only. Not a clinical assessment.
                    </p>
                  </div>
                </Tile>
              </div>
            )}

          </motion.div>
        </AnimatePresence>
      </div>

      <ChatBot
        spotifyData={spotifyData as Record<string,unknown> | null}
        youtubeData={youtubeData as Record<string,unknown> | null}
        whatsappData={whatsappData as Record<string,unknown> | null}
        externalOpen={chatOpen}
        onClose={() => setChatOpen(false)}
      />
    </div>
  )
}
