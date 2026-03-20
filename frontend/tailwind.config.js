/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ['Inter', '-apple-system', 'sans-serif'],
      },
      colors: {
        // Semantic surfaces via CSS vars
        canvas:  'var(--canvas)',
        surface: 'var(--surface)',
        raised:  'var(--raised)',
        overlay: 'var(--overlay)',
        // Accent
        accent: {
          blue:   '#0071E3',
          indigo: '#6366F1',
          purple: '#A855F7',
          pink:   '#EC4899',
          green:  '#22C55E',
          amber:  '#F59E0B',
          red:    '#EF4444',
          cyan:   '#06B6D4',
        },
      },
      borderRadius: {
        '3xl':  '24px',
        '4xl':  '32px',
        '5xl':  '40px',
        pill:   '9999px',
      },
      fontSize: {
        '10xl': ['9rem',  { lineHeight: '1',    letterSpacing: '-0.04em' }],
        '9xl':  ['8rem',  { lineHeight: '1',    letterSpacing: '-0.04em' }],
        '8xl':  ['6rem',  { lineHeight: '1.02', letterSpacing: '-0.03em' }],
        '7xl':  ['4.5rem',{ lineHeight: '1.05', letterSpacing: '-0.03em' }],
        '6xl':  ['3.75rem',{lineHeight: '1.08', letterSpacing: '-0.025em'}],
        '5xl':  ['3rem',  { lineHeight: '1.1',  letterSpacing: '-0.02em' }],
      },
      boxShadow: {
        // Light mode layered shadows
        'tile':    '0 1px 2px rgba(0,0,0,.04), 0 4px 12px rgba(0,0,0,.04), 0 0 0 1px rgba(0,0,0,.04)',
        'tile-lg': '0 2px 4px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.06), 0 0 0 1px rgba(0,0,0,.04)',
        'tile-hover':'0 4px 8px rgba(0,0,0,.06), 0 16px 40px rgba(0,0,0,.10), 0 0 0 1px rgba(0,0,0,.06)',
        // Glows
        'glow-blue':  '0 0 0 1px rgba(99,102,241,.3), 0 0 40px rgba(99,102,241,.2)',
        'glow-green': '0 0 0 1px rgba(34,197,94,.3),  0 0 40px rgba(34,197,94,.15)',
        'glow-purple':'0 0 0 1px rgba(168,85,247,.3),  0 0 40px rgba(168,85,247,.2)',
        'glow-amber': '0 0 0 1px rgba(245,158,11,.3),  0 0 40px rgba(245,158,11,.15)',
        'inner-white':'inset 0 1px 0 rgba(255,255,255,.12)',
      },
      animation: {
        'aurora':       'aurora 12s ease infinite alternate',
        'blob-1':       'blob1 8s ease-in-out infinite',
        'blob-2':       'blob2 10s ease-in-out infinite',
        'blob-3':       'blob3 9s ease-in-out infinite',
        'float':        'float 5s ease-in-out infinite',
        'shimmer':      'shimmer 2.5s linear infinite',
        'fade-up':      'fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards',
        'scale-in':     'scaleIn 0.35s cubic-bezier(0.16,1,0.3,1) forwards',
        'count-up':     'countUp 1s cubic-bezier(0.16,1,0.3,1)',
        'spin-slow':    'spin 8s linear infinite',
        'pulse-soft':   'pulseSoft 3s ease-in-out infinite',
      },
      keyframes: {
        aurora: {
          '0%':   { backgroundPosition: '0% 50%' },
          '50%':  { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        blob1: {
          '0%,100%': { transform: 'translate(0,0) scale(1)' },
          '33%':     { transform: 'translate(30px,-50px) scale(1.08)' },
          '66%':     { transform: 'translate(-20px,20px) scale(0.95)' },
        },
        blob2: {
          '0%,100%': { transform: 'translate(0,0) scale(1)' },
          '40%':     { transform: 'translate(-35px,30px) scale(1.1)' },
          '70%':     { transform: 'translate(25px,-15px) scale(0.92)' },
        },
        blob3: {
          '0%,100%': { transform: 'translate(0,0) scale(1)' },
          '30%':     { transform: 'translate(20px,40px) scale(0.96)' },
          '65%':     { transform: 'translate(-30px,-25px) scale(1.06)' },
        },
        float: {
          '0%,100%': { transform: 'translateY(0)' },
          '50%':     { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-500px 0' },
          '100%': { backgroundPosition: '500px 0' },
        },
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%':   { opacity: '0', transform: 'scale(0.94)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulseSoft: {
          '0%,100%': { opacity: '0.7' },
          '50%':     { opacity: '1' },
        },
      },
      backgroundImage: {
        'radial-glow':    'radial-gradient(ellipse at center, var(--tw-gradient-stops))',
        'mesh-light':     'radial-gradient(at 20% 50%, hsla(220,100%,70%,0.06) 0px, transparent 60%), radial-gradient(at 80% 20%, hsla(260,100%,70%,0.06) 0px, transparent 50%), radial-gradient(at 60% 80%, hsla(160,100%,50%,0.04) 0px, transparent 50%)',
        'mesh-dark':      'radial-gradient(at 20% 50%, hsla(220,100%,60%,0.08) 0px, transparent 60%), radial-gradient(at 80% 20%, hsla(260,100%,60%,0.08) 0px, transparent 50%)',
        'gradient-brand': 'linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%)',
        'gradient-blue':  'linear-gradient(135deg, #0071E3 0%, #6366F1 100%)',
        'gradient-green': 'linear-gradient(135deg, #22C55E 0%, #06B6D4 100%)',
        'gradient-warm':  'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)',
      },
    },
  },
  plugins: [],
}
