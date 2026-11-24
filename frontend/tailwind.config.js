/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563EB',
          dark: '#1D4ED8',
          soft: '#EFF6FF',
          navy: '#0B192C',
          ocean: '#1E3E62',
          ice: '#DBEAFE'
        },
        accent: '#0284C7',
        canvas: '#F5F7FB',
        ink: {
          DEFAULT: '#0B192C',
          muted: '#64748B'
        },
        line: '#E2E8F0'
      }
    },
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif']
    },
  },
  plugins: [],
}
