/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#667eea', dark: '#764ba2' },
        sunrise: { DEFAULT: '#f6d365', dark: '#fda085' },
        knowledge: { DEFAULT: '#11998e', dark: '#38ef7d' },
        sport: { DEFAULT: '#4facfe', dark: '#00f2fe' },
        gold: '#ffd700',
        dark: '#0f0f23',
      }
    }
  },
  plugins: []
}
