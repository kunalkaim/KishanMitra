/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#F2F7F4',
          100: '#E1ECE4',
          200: '#C1D9CA',
          300: '#94BEA3',
          400: '#5F9E75',
          500: '#3D8054', // Agricultural Green
          600: '#2D6B44',
          700: '#235737',
          800: '#1C4B30',
          900: '#174B35', // Deep Forest Green (Primary)
          950: '#0C261A',
        },
        saffron: {
          50: '#FEFAF0',
          100: '#FDF2D8',
          200: '#FBE4AE',
          300: '#F7D07E',
          400: '#F0BA51',
          500: '#E8AD45', // Warm Saffron (Accent)
          600: '#CF8E26',
          700: '#A4681A',
          800: '#7F4F19',
          900: '#5E3B16',
        },
        charcoal: {
          50: '#F6F8F7',
          100: '#EBF0ED',
          200: '#D5DFD9',
          300: '#B4C3BA',
          400: '#758279', // Secondary Text
          500: '#546359',
          600: '#3F4D44',
          700: '#2F3C34',
          800: '#232F28',
          900: '#1E2922', // Main Text
        },
        'kisan-bg': '#F8F8F2',
        'kisan-card': '#FFFFFF',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 10px rgba(23, 75, 53, 0.04), 0 10px 25px rgba(23, 75, 53, 0.06)',
        'soft-lg': '0 10px 30px rgba(23, 75, 53, 0.08), 0 20px 40px rgba(23, 75, 53, 0.04)',
        'glow': '0 0 25px rgba(232, 173, 69, 0.25)',
      }
    },
  },
  plugins: [],
}
