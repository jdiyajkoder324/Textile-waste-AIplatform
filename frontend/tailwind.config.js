/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: '#EAF4EF',
          raised: '#FFFFFF',
        },
        ink: {
          900: '#1B2B24',
          700: '#33453C',
          600: '#54655C',
          400: '#8B978F',
          200: '#D6E0DA',
          100: '#E8EEEA',
        },
        fiber: {
          teal: '#1E9E6B',
          amber: '#E8A33D',
          moss: '#4C8DBF',
          rust: '#C97B72',
        },
      },
      boxShadow: {
        'card': '0 1px 2px rgba(27,43,36,0.05), 0 8px 24px -12px rgba(27,43,36,0.12)',
        'card-hover': '0 1px 2px rgba(27,43,36,0.06), 0 16px 36px -14px rgba(30,158,107,0.22)',
      },
    },
  },
  plugins: [],
};