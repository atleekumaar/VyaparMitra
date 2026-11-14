/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Unified Semantic Token System (CSS variables with alpha support)
        surface: {
          DEFAULT: 'rgb(var(--surface) / <alpha-value>)',
          muted: 'rgb(var(--surface-muted) / <alpha-value>)',
          card: 'rgb(var(--surface-card) / <alpha-value>)',
          elevated: 'rgb(var(--surface-elevated) / <alpha-value>)',
        },
        border: {
          DEFAULT: 'rgb(var(--border) / <alpha-value>)',
          subtle: 'rgb(var(--border-subtle) / <alpha-value>)',
          strong: 'rgb(var(--border-strong) / <alpha-value>)',
        },
        text: {
          DEFAULT: 'rgb(var(--text) / <alpha-value>)',
          muted: 'rgb(var(--text-muted) / <alpha-value>)',
          subtle: 'rgb(var(--text-subtle) / <alpha-value>)',
        },
        brand: {
          DEFAULT: 'rgb(var(--brand) / <alpha-value>)',
          hover: 'rgb(var(--brand-hover) / <alpha-value>)',
          soft: 'rgb(var(--brand-soft) / <alpha-value>)',
          border: 'rgb(var(--brand-border) / <alpha-value>)',
        },
        success: {
          DEFAULT: 'rgb(var(--success) / <alpha-value>)',
          soft: 'rgb(var(--success-soft) / <alpha-value>)',
        },
        warning: {
          DEFAULT: 'rgb(var(--warning) / <alpha-value>)',
          soft: 'rgb(var(--warning-soft) / <alpha-value>)',
        },
        danger: {
          DEFAULT: 'rgb(var(--danger) / <alpha-value>)',
          soft: 'rgb(var(--danger-soft) / <alpha-value>)',
        },
        info: {
          DEFAULT: 'rgb(var(--info) / <alpha-value>)',
          soft: 'rgb(var(--info-soft) / <alpha-value>)',
        },

        // Backward compatibility mappings - smoothly pointing to semantic variables
        fintech: {
          bg: 'rgb(var(--surface) / <alpha-value>)',
          card: 'rgb(var(--surface-card) / <alpha-value>)',
          border: 'rgb(var(--border) / <alpha-value>)',
          primary: 'rgb(var(--brand) / <alpha-value>)',
          primaryHover: 'rgb(var(--brand-hover) / <alpha-value>)',
          primaryLight: 'rgb(var(--brand-soft) / <alpha-value>)',
          text: 'rgb(var(--text) / <alpha-value>)',
          muted: 'rgb(var(--text-muted) / <alpha-value>)',
          copilot: '#6D45D8',
          copilotHover: '#5B37B8',
          copilotLight: '#F5F3FF',
          success: 'rgb(var(--success) / <alpha-value>)',
          successLight: 'rgb(var(--success-soft) / <alpha-value>)',
          warning: 'rgb(var(--warning) / <alpha-value>)',
          warningLight: 'rgb(var(--warning-soft) / <alpha-value>)',
          danger: 'rgb(var(--danger) / <alpha-value>)',
          dangerLight: 'rgb(var(--danger-soft) / <alpha-value>)',
          darkBg: 'rgb(var(--surface) / <alpha-value>)',
          darkCard: 'rgb(var(--surface-card) / <alpha-value>)',
          darkBorder: 'rgb(var(--border) / <alpha-value>)',
          darkMuted: 'rgb(var(--text-muted) / <alpha-value>)',
        },
        paytm: {
          navy: 'rgb(var(--text) / <alpha-value>)',
          midnight: 'rgb(var(--surface) / <alpha-value>)',
          dark: 'rgb(var(--text) / <alpha-value>)',
          royal: 'rgb(var(--brand) / <alpha-value>)',
          blue: 'rgb(var(--brand) / <alpha-value>)',
          cyan: 'rgb(var(--brand) / <alpha-value>)',
          hover: 'rgb(var(--brand-hover) / <alpha-value>)',
          light: 'rgb(var(--surface) / <alpha-value>)',
          ice: 'rgb(var(--brand-soft) / <alpha-value>)',
          surface: 'rgb(var(--surface-card) / <alpha-value>)',
          border: 'rgb(var(--border) / <alpha-value>)',
          borderStrong: 'rgb(var(--border-strong) / <alpha-value>)',
          text: 'rgb(var(--text) / <alpha-value>)',
          muted: 'rgb(var(--text-muted) / <alpha-value>)',
          green: 'rgb(var(--success) / <alpha-value>)',
          greenLight: 'rgb(var(--success-soft) / <alpha-value>)',
          greenDark: '#15803D',
          orange: 'rgb(var(--warning) / <alpha-value>)',
          gold: 'rgb(var(--warning) / <alpha-value>)',
          coral: 'rgb(var(--danger) / <alpha-value>)',
        }
      },
      fontFamily: {
        sans: [
          'Inter',
          'Noto Sans Devanagari',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif'
        ],
      },
      borderRadius: {
        'xl': '0.75rem',    /* 12px for inputs & buttons */
        '2xl': '1rem',      /* 16px for fintech cards */
        '3xl': '1.5rem',    /* 24px for modals & hero containers */
      },
      boxShadow: {
        fintech: '0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)',
        'fintech-md': '0 4px 6px -1px rgba(15, 23, 42, 0.06), 0 2px 4px -2px rgba(15, 23, 42, 0.04)',
        'fintech-lg': '0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04)',
        paytm: '0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)',
        paytmGlow: '0 0 15px rgba(37, 99, 235, 0.2)',
        soundbox: '0 4px 20px rgba(15, 23, 42, 0.08)',
      }
    },
  },
  plugins: [],
}
