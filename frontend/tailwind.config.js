/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        jnt: {
          red: '#ED1C24',
          darkRed: '#C81017',
          lightRed: '#FEE2E2',
          black: '#1F2937'
        }
      }
    },
  },
  plugins: [],
}

