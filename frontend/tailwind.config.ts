/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#145DA0',
        'primary-light': '#3B82F6',
        'primary-dark': '#0F4C81',
        gpu: '#6C5CE7',
        success: '#168A62',
        warning: '#C47B12',
        danger: '#C2414B',
        bg: '#F5F7FA',
        surface: '#FFFFFF',
        'text-primary': '#172033',
        'text-secondary': '#667085',
        border: '#E4E7EC',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}