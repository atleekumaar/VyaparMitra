/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paytm: {
          navy: "#002970",
          midnight: "#001844",
          dark: "#001F54",
          royal: "#003A8C",
          blue: "#00BAF2",
          cyan: "#00BAF2",
          hover: "#009EDB",
          light: "#F0F8FE",
          ice: "#E5F4FD",
          surface: "#FFFFFF",
          border: "#CDE5F7",
          borderStrong: "#9BD0F5",
          text: "#0F2042",
          muted: "#4F6A94",
          green: "#00B970",
          greenLight: "#E8F8F0",
          greenDark: "#008A54",
          orange: "#FF7A00",
          gold: "#FFB800",
          coral: "#FF4D4D",
        },
        fintech: {
          success: "#00B970",
          warning: "#FFB800",
          danger: "#FF4D4D",
          info: "#00BAF2",
        }
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Oxygen',
          'Ubuntu',
          'Cantarell',
          'sans-serif'
        ],
      },
      boxShadow: {
        paytm: '0 4px 20px -2px rgba(0, 41, 112, 0.08), 0 2px 6px -1px rgba(0, 186, 242, 0.08)',
        paytmGlow: '0 0 20px rgba(0, 186, 242, 0.35)',
        soundbox: '0 8px 30px rgba(0, 41, 112, 0.12)',
      }
    },
  },
  plugins: [],
}
