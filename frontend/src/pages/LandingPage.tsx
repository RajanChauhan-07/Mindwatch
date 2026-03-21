import { useRef, useState } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Brain, Music, Youtube, MessageCircle, Activity, Sparkles, TrendingUp, ArrowRight, Shield, Star, Moon, Sun } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import Aurora from '../components/effects/Aurora'
import BlurReveal from '../components/effects/BlurReveal'
import Magnetic from '../components/effects/Magnetic'
import { useThemeStore } from '../store/themeStore'

const API_URL = import.meta.env.VITE_API_URL || ''

const BENTO = [
  {
    icon: Music, color: '#6366F1', size: 'col-span-12 md:col-span-4 row-span-2',
    title: 'Music Intelligence',
    desc: 'BERT emotion AI decodes your Spotify listening — valence, energy, emotional tone across 50+ tracks.',
    stat: '99.9%', statLabel: 'BERT accuracy',
    bg: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(168,85,247,0.08) 100%)',
    border: 'rgba(99,102,241,0.2)',
  },
  {
    icon: Youtube, color: '#EF4444', size: 'col-span-12 md:col-span-4',
    title: 'Content Diet',
    desc: 'ML classifier analyzes your YouTube history across 11 emotional categories.',
    stat: '11', statLabel: 'content categories',
    bg: 'linear-gradient(135deg, rgba(239,68,68,0.1) 0%, rgba(245,158,11,0.06) 100%)',
    border: 'rgba(239,68,68,0.2)',
  },
  {
    icon: MessageCircle, color: '#22C55E', size: 'col-span-12 md:col-span-4',
    title: 'Chat Analysis',
    desc: 'Sentiment & behavioral patterns from your WhatsApp conversations.',
    stat: '200+', statLabel: 'messages analyzed',
    bg: 'linear-gradient(135deg, rgba(34,197,94,0.1) 0%, rgba(6,182,212,0.06) 100%)',
    border: 'rgba(34,197,94,0.2)',
  },
  {
    icon: Sparkles, color: '#A855F7', size: 'col-span-12 md:col-span-8',
    title: 'Mamdani Fuzzy Logic Engine',
    desc: 'A scientifically-grounded Mamdani FIS fuses Linguistic, Consumption and Behavioral scores into one unified wellness output — not just a simple average.',
    stat: 'Fuzzy', statLabel: 'inference system',
    bg: 'linear-gradient(135deg, rgba(168,85,247,0.12) 0%, rgba(99,102,241,0.08) 100%)',
    border: 'rgba(168,85,247,0.25)',
    wide: true,
  },
  {
    icon: Activity, color: '#06B6D4', size: 'col-span-12 md:col-span-4',
    title: 'Google Fit',
    desc: 'Steps, heart rate, and active minutes feed into the wellness score.',
    stat: '7', statLabel: 'days tracked',
    bg: 'linear-gradient(135deg, rgba(6,182,212,0.1) 0%, rgba(0,113,227,0.06) 100%)',
    border: 'rgba(6,182,212,0.2)',
  },
  {
    icon: TrendingUp, color: '#F59E0B', size: 'col-span-12 md:col-span-4',
    title: '7-Day Forecast',
    desc: 'Prophet + moving average forecasts your wellness trajectory.',
    stat: '7 days', statLabel: 'ahead',
    bg: 'linear-gradient(135deg, rgba(245,158,11,0.1) 0%, rgba(239,68,68,0.06) 100%)',
    border: 'rgba(245,158,11,0.2)',
  },
  {
    icon: Brain, color: '#EC4899', size: 'col-span-12 md:col-span-8',
    title: 'Gemini AI Wellness Coach',
    desc: 'Your personal AI assistant powered by Gemini, with full access to your behavioral data — not generic advice, real personalized insights.',
    stat: 'Gemini', statLabel: 'powered',
    bg: 'linear-gradient(135deg, rgba(236,72,153,0.1) 0%, rgba(168,85,247,0.08) 100%)',
    border: 'rgba(236,72,153,0.2)',
    wide: true,
  },
]

export default function LandingPage() {
  const [params] = useSearchParams()
  const { dark, toggle } = useThemeStore()
  const heroRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: heroRef })
  const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '20%'])
  const heroOpacity = useTransform(scrollYProgress, [0, 0.7], [1, 0])

  const handleSignIn = () => { window.location.href = `${API_URL}/api/auth/google` }

  return (
    <div className="min-h-screen overflow-x-hidden" style={{ background: 'var(--canvas)' }}>

      {/* ── NAV ────────────────────────────────────────────────────────── */}
      <header className="fixed top-0 inset-x-0 z-50 glass" style={{ borderBottom: '1px solid var(--border)', height: 56 }}>
        <div className="max-w-6xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)' }}>
              <Brain size={17} className="text-white" />
            </div>
            <span className="font-black text-base tracking-tight" style={{ color: 'var(--tx)' }}>MindWatch</span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={toggle}
              className="w-9 h-9 rounded-xl flex items-center justify-center transition-all hover:scale-110"
              style={{ background: 'var(--raised)', color: 'var(--tx-2)' }}>
              {dark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            <Magnetic strength={0.25}>
              <button onClick={handleSignIn}
                className="px-5 py-2.5 rounded-xl text-sm font-bold text-white transition-all hover:opacity-90"
                style={{ background: 'linear-gradient(135deg, #0071E3, #6366F1)', boxShadow: '0 2px 16px rgba(0,113,227,0.35)' }}>
                Sign In
              </button>
            </Magnetic>
          </div>
        </div>
      </header>

      {/* ── HERO ───────────────────────────────────────────────────────── */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center overflow-hidden pt-14">
        {/* Aurora BG */}
        <Aurora intensity="high" />

        {/* Noise overlay */}
        <div className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
            backgroundSize: '160px',
            opacity: 0.025,
          }}
        />

        <motion.div style={{ y: heroY, opacity: heroOpacity }} className="relative z-10 text-center px-6 max-w-5xl mx-auto">
          {params.get('error') && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
              className="inline-flex items-center gap-2 text-sm px-4 py-2 rounded-pill mb-8"
              style={{ background: 'rgba(239,68,68,0.1)', color: '#EF4444', border: '1px solid rgba(239,68,68,0.2)' }}>
              Authentication failed — please try again.
            </motion.div>
          )}

          {/* Eyebrow */}
          <BlurReveal delay={0.1}>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-pill text-xs font-bold uppercase tracking-widest mb-8"
              style={{ background: 'rgba(99,102,241,0.1)', color: '#6366F1', border: '1px solid rgba(99,102,241,0.2)', letterSpacing: '0.12em' }}>
              <Sparkles size={11} />
              AI · BERT · Fuzzy Logic · Gemini
            </div>
          </BlurReveal>

          {/* Headline */}
          <BlurReveal delay={0.18}>
            <h1 className="font-black leading-none mb-6"
              style={{ fontSize: 'clamp(3.5rem, 9vw, 7rem)', letterSpacing: '-0.04em', color: 'var(--tx)' }}>
              Know your mind.<br />
              <span className="g-text">Before it's too late.</span>
            </h1>
          </BlurReveal>

          {/* Sub */}
          <BlurReveal delay={0.26}>
            <p className="text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed" style={{ color: 'var(--tx-2)' }}>
              MindWatch analyzes your Spotify, YouTube, WhatsApp and Google Fit to reveal hidden mental wellness patterns — powered by BERT, Fuzzy Logic, and Gemini AI.
            </p>
          </BlurReveal>

          {/* CTA */}
          <BlurReveal delay={0.34}>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Magnetic strength={0.3}>
                <button onClick={handleSignIn}
                  className="group relative overflow-hidden flex items-center gap-3 px-8 py-4 rounded-2xl text-white font-black text-base transition-all"
                  style={{ background: 'linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%)', boxShadow: '0 4px 40px rgba(99,102,241,0.5)', minWidth: 200 }}>
                  {/* Shimmer */}
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    style={{ background: 'linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.15) 50%, transparent 60%)', backgroundSize: '200% 100%' }} />
                  Get Started Free
                  <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </button>
              </Magnetic>
              <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--tx-2)' }}>
                <Shield size={14} style={{ color: 'var(--green)' }} />
                Free · Private · No ads
              </div>
            </div>
          </BlurReveal>

          {/* Star rating */}
          <BlurReveal delay={0.42}>
            <div className="flex items-center justify-center gap-2 mt-8 text-xs" style={{ color: 'var(--tx-3)' }}>
              <div className="flex gap-0.5">
                {[...Array(5)].map((_, i) => <Star key={i} size={12} className="fill-current" style={{ color: '#F59E0B' }} />)}
              </div>
              <span style={{ color: 'var(--tx-2)' }}>BERT + Mamdani Fuzzy Inference System</span>
            </div>
          </BlurReveal>

          {/* Hero mock card */}
          <BlurReveal delay={0.5} className="mt-16">
            <div className="animate-float">
              <div className="inline-block tile-lg p-8 text-left relative overflow-hidden noise"
                style={{ minWidth: 340, boxShadow: '0 8px 80px rgba(99,102,241,0.2), 0 0 0 1px var(--border)' }}>
                {/* Ambient */}
                <div className="absolute -top-8 -right-8 w-32 h-32 rounded-full blur-3xl opacity-30"
                  style={{ background: 'radial-gradient(circle, #6366F1, transparent)' }} />

                <div className="flex items-start justify-between mb-6">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest mb-1.5" style={{ color: 'var(--tx-3)', letterSpacing: '0.1em' }}>Overall Wellness</p>
                    <div className="flex items-end gap-2">
                      <span className="font-black leading-none g-text-green"
                        style={{ fontSize: 64, letterSpacing: '-0.04em' }}>72</span>
                      <span className="text-lg mb-2 font-semibold" style={{ color: 'var(--tx-3)' }}>/100</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-pill"
                      style={{ background: 'rgba(34,197,94,0.12)', color: '#22C55E', border: '1px solid rgba(34,197,94,0.25)' }}>
                      <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                      Good
                    </span>
                    <p className="text-xs mt-2" style={{ color: 'var(--tx-3)' }}>Mamdani FIS</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    { label: 'Linguistic (BERT)', v: 68, c: '#6366F1' },
                    { label: 'Consumption (ML)', v: 74, c: '#F59E0B' },
                    { label: 'Behavioral', v: 79, c: '#22C55E' },
                  ].map(({ label, v, c }) => (
                    <div key={label}>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span style={{ color: 'var(--tx-2)' }}>{label}</span>
                        <span className="font-bold tabular-nums" style={{ color: 'var(--tx)' }}>{v}</span>
                      </div>
                      <div className="h-1.5 rounded-full" style={{ background: 'var(--raised)' }}>
                        <div className="h-full rounded-full transition-all duration-1000"
                          style={{ width: `${v}%`, background: `linear-gradient(90deg, ${c}66, ${c})` }} />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex items-center gap-2 mt-5 pt-5" style={{ borderTop: '1px solid var(--border)' }}>
                  <span className="text-xs font-bold" style={{ color: 'var(--green)' }}>↑ 4 pts from last week</span>
                  <span className="text-xs" style={{ color: 'var(--tx-3)' }}>· Powered by Fuzzy Logic AI</span>
                </div>
              </div>
            </div>
          </BlurReveal>
        </motion.div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-2 animate-bounce opacity-40">
          <div className="w-5 h-8 rounded-pill border-2 flex items-center justify-center" style={{ borderColor: 'var(--tx-3)' }}>
            <div className="w-1 h-2 rounded-full" style={{ background: 'var(--tx-3)' }} />
          </div>
        </div>
      </section>

      {/* ── BENTO GRID ─────────────────────────────────────────────────── */}
      <section className="py-28 px-6" style={{ background: 'var(--canvas)' }}>
        <div className="max-w-6xl mx-auto">
          <BlurReveal className="text-center mb-16">
            <p className="text-xs font-black uppercase tracking-widest mb-4" style={{ color: 'var(--indigo)', letterSpacing: '0.15em' }}>Capabilities</p>
            <h2 className="font-black" style={{ fontSize: 'clamp(2.5rem,5vw,4rem)', letterSpacing: '-0.03em', color: 'var(--tx)' }}>
              Six lenses.<br />One wellness score.
            </h2>
          </BlurReveal>

          <div className="grid grid-cols-12 gap-4">
            {BENTO.map((item, i) => (
              <BlurReveal key={item.title} delay={i * 0.06} className={item.size}>
                <motion.div
                  whileHover={{ scale: 1.015, y: -4 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 28 }}
                  className="h-full rounded-3xl p-7 relative overflow-hidden cursor-default noise"
                  style={{ background: item.bg, border: `1px solid ${item.border}`, minHeight: item.wide ? 180 : 200 }}
                >
                  <div className="absolute -right-6 -top-6 w-24 h-24 rounded-full opacity-20 blur-2xl"
                    style={{ background: item.color }} />

                  <div className="w-12 h-12 rounded-2xl flex items-center justify-center mb-5 relative z-10"
                    style={{ background: `${item.color}20`, border: `1px solid ${item.color}35` }}>
                    <item.icon size={22} style={{ color: item.color }} />
                  </div>

                  <h3 className="font-black text-lg mb-2 relative z-10" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>
                    {item.title}
                  </h3>
                  <p className="text-sm leading-relaxed relative z-10" style={{ color: 'var(--tx-2)' }}>{item.desc}</p>

                  <div className="mt-6 flex items-end gap-1.5 relative z-10">
                    <span className="text-3xl font-black" style={{ color: item.color, letterSpacing: '-0.03em' }}>{item.stat}</span>
                    <span className="text-xs font-semibold pb-1" style={{ color: 'var(--tx-3)' }}>{item.statLabel}</span>
                  </div>
                </motion.div>
              </BlurReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ───────────────────────────────────────────────── */}
      <section className="py-24 px-6" style={{ background: 'var(--surface)' }}>
        <div className="max-w-4xl mx-auto">
          <BlurReveal className="text-center mb-16">
            <p className="text-xs font-black uppercase tracking-widest mb-4" style={{ color: 'var(--purple)', letterSpacing: '0.15em' }}>Process</p>
            <h2 className="font-black" style={{ fontSize: 'clamp(2rem,4vw,3.25rem)', letterSpacing: '-0.03em', color: 'var(--tx)' }}>
              Up and running<br />in 2 minutes.
            </h2>
          </BlurReveal>

          <div className="grid md:grid-cols-3 gap-5">
            {[
              { n: '01', title: 'Connect', desc: 'Link Spotify, upload YouTube & WhatsApp exports, connect Google Fit — all in one dashboard.', color: '#6366F1' },
              { n: '02', title: 'Analyze', desc: 'BERT, ML classifiers, behavioral engine and Mamdani FIS process all your data simultaneously.', color: '#A855F7' },
              { n: '03', title: 'Understand', desc: 'View your wellness score, 7-day predictions, and get personalized AI coaching from Gemini.', color: '#EC4899' },
            ].map((s, i) => (
              <BlurReveal key={s.n} delay={i * 0.1}>
                <motion.div whileHover={{ y: -6 }} transition={{ type: 'spring', stiffness: 280, damping: 28 }}
                  className="tile rounded-3xl p-8 h-full cursor-default">
                  <span className="text-5xl font-black g-text leading-none">{s.n}</span>
                  <h3 className="font-black text-xl mt-5 mb-3" style={{ color: 'var(--tx)', letterSpacing: '-0.02em' }}>{s.title}</h3>
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--tx-2)' }}>{s.desc}</p>
                </motion.div>
              </BlurReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ────────────────────────────────────────────────────────── */}
      <section className="py-24 px-6" style={{ background: 'var(--canvas)' }}>
        <BlurReveal>
          <div className="max-w-3xl mx-auto rounded-4xl p-16 text-center relative overflow-hidden noise"
            style={{
              background: 'linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.10), rgba(236,72,153,0.08))',
              border: '1px solid rgba(99,102,241,0.25)',
              boxShadow: '0 8px 80px rgba(99,102,241,0.15)',
            }}>
            <div className="absolute -top-16 -right-16 w-48 h-48 rounded-full blur-3xl opacity-25"
              style={{ background: 'radial-gradient(circle, #6366F1, transparent)' }} />
            <div className="absolute -bottom-16 -left-16 w-48 h-48 rounded-full blur-3xl opacity-20"
              style={{ background: 'radial-gradient(circle, #A855F7, transparent)' }} />

            <div className="relative z-10">
              <div className="w-14 h-14 rounded-3xl flex items-center justify-center mx-auto mb-6"
                style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)' }}>
                <Brain size={26} className="text-white" />
              </div>
              <h2 className="font-black mb-5" style={{ fontSize: 'clamp(2rem,4vw,3rem)', letterSpacing: '-0.03em', color: 'var(--tx)' }}>
                Start understanding<br />yourself today.
              </h2>
              <p className="text-lg mb-8" style={{ color: 'var(--tx-2)' }}>Free forever. No credit card. Just insights.</p>
              <Magnetic>
                <button onClick={handleSignIn}
                  className="group inline-flex items-center gap-3 px-8 py-4 rounded-2xl text-white font-black text-base transition-all"
                  style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)', boxShadow: '0 4px 40px rgba(99,102,241,0.5)' }}>
                  Get Started Free
                  <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </button>
              </Magnetic>
            </div>
          </div>
        </BlurReveal>
      </section>

      {/* ── FOOTER ─────────────────────────────────────────────────────── */}
      <footer className="py-8 px-6" style={{ borderTop: '1px solid var(--border)' }}>
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #6366F1, #A855F7)' }}>
              <Brain size={14} className="text-white" />
            </div>
            <span className="font-black text-sm" style={{ color: 'var(--tx)' }}>MindWatch</span>
            <span className="text-sm" style={{ color: 'var(--tx-3)' }}>© 2026</span>
          </div>
          <p className="text-xs" style={{ color: 'var(--tx-3)' }}>Not a medical device. For wellness awareness only.</p>
        </div>
      </footer>
    </div>
  )
}
