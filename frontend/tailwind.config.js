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
        fintech: {
          bg: "#F8FAFC",
          card: "#FFFFFF",
          border: "#E2E8F0",
          primary: "#2563EB",
          primaryHover: "#1D4ED8",
          primaryLight: "#EFF6FF",
          text: "#0F172A",
          muted: "#64748B",
          copilot: "#6D45D8",
          copilotHover: "#5B37B8",
          copilotLight: "#F5F3FF",
          success: "#16A34A",
          successLight: "#F0FDF4",
          warning: "#D97706",
          warningLight: "#FFFBEB",
          danger: "#DC2626",
          dangerLight: "#FEF2F2",
          darkBg: "#0B0F19",
          darkCard: "#111827",
          darkBorder: "#1E293B",
          darkMuted: "#94A3B8",
        },
        // Mapped for backwards-compatibility with existing page templates
        paytm: {
          navy: "#0F172A",
          midnight: "#0B0F19",
          dark: "#0F172A",
          royal: "#1E3A8A",
          blue: "#2563EB",
          cyan: "#2563EB",
          hover: "#1D4ED8",
          light: "#F8FAFC",
          ice: "#EFF6FF",
          surface: "#FFFFFF",
          border: "#E2E8F0",
          borderStrong: "#CBD5E1",
          text: "#0F172A",
          muted: "#64748B",
          green: "#16A34A",
          greenLight: "#F0FDF4",
          greenDark: "#15803D",
          orange: "#D97706",
          gold: "#D97706",
          coral: "#DC2626",
        }
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif'
        ],
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
