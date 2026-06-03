/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        ev: {
          bg:      '#080808',
          surface: '#111111',
          card:    '#161616',
          border:  '#252525',
          red:     '#E2231A',
          'red-d': '#B01A13',
          silver:  '#888888',
          white:   '#F0F0F0',
        }
      },
      fontFamily: {
        display: ['"Bebas Neue"', 'sans-serif'],
        body:    ['"Outfit"', '"Noto Sans Thai"', '"Noto Sans"', 'Tahoma', 'sans-serif'],
      },
      animation: {
        'fade-up':   'fadeUp 0.5s ease forwards',
        'fade-up-1': 'fadeUp 0.5s 0.1s ease both',
        'fade-up-2': 'fadeUp 0.5s 0.2s ease both',
        'fade-up-3': 'fadeUp 0.5s 0.3s ease both',
        'fade-up-4': 'fadeUp 0.5s 0.4s ease both',
        'fade-in':   'fadeIn 0.4s ease forwards',
        'sweep':     'sweep 4s ease-in-out infinite',
        'bar-grow':  'barGrow 1s ease forwards',
      },
      keyframes: {
        fadeUp:  { from: { opacity: 0, transform: 'translateY(20px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        fadeIn:  { from: { opacity: 0 }, to: { opacity: 1 } },
        sweep:   { '0%': { left: '-80%' }, '100%': { left: '120%' } },
        barGrow: { from: { width: '0%' }, to: {} },
      }
    }
  },
  plugins: []
}
