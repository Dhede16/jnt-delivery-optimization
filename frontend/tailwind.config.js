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
          DEFAULT: '#3366FF',
          dark: '#2B4FD8',
          soft: '#E8EEFB'
        },
        accent: '#00C9A7',
        canvas: '#F5F7FB',
        ink: {
          DEFAULT: '#2B3A67',
          muted: '#8A94A8'
        },
        line: '#E3E8F2',
        jnt: {
          red: '#ED1C24',
          darkRed: '#C81017',
          lightRed: '#FEE2E2',
          black: '#1F2937'
        }
      }
    },
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif']
    },
  },
  plugins: [],
}
