/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: '#F7F7F3',
          raised: '#FFFFFF',
    },
    ink: {
      900: '#152520',
      700: '#33443C',
      600: '#56675F',
      400: '#8A968F',
      200: '#D8DDD9',
      100: '#E9ECE9',
    },
    fiber: {
      teal: '#1F6F5C',
      amber: '#B9791F',
      moss: '#4C7A46',
      rust: '#B23B2E',
    },
  },
  boxShadow: {
    'card': '0 1px 2px rgba(21,37,32,0.04), 0 8px 24px -12px rgba(21,37,32,0.12)',
    'card-hover': '0 1px 2px rgba(21,37,32,0.05), 0 16px 36px -14px rgba(31,111,92,0.22)',
  },
},
  },
  plugins: [],
};

