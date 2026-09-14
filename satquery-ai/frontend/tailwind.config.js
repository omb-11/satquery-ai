/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Deep Black + Command Green system
        'space': {
          950: '#030504', // true near-black base
          900: '#070a08', // primary dark surface
          850: '#0c120e', // panel surface
          800: '#111813', // card surface
          750: '#17221b', // elevated surface
          700: '#1f2d24', // borders & dividers
          600: '#2b3d32', // interactive borders
        },
        'emerald': {
          DEFAULT: '#00ff87',
          glow: '#00e676',
          dark: '#059669',
          muted: '#10b981',
        },
        'telemetry': {
          green: '#00ff87',
          lime: '#4ade80',
          amber: '#fbbf24',
          red: '#f87171',
          cyan: '#22d3ee',
        },
        'hud': {
          text: '#f1f5f2',
          muted: '#788f82',
          subtle: '#43554a',
          border: 'rgba(0, 255, 135, 0.15)',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'glow-sm': '0 0 8px rgba(0, 255, 135, 0.25)',
        'glow-md': '0 0 16px rgba(0, 255, 135, 0.35)',
        'glow-lg': '0 0 24px rgba(0, 255, 135, 0.45)',
        'glow-amber': '0 0 12px rgba(251, 191, 36, 0.3)',
      }
    }
  },
  plugins: []
}
