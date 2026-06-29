/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        vazir: ['Vazirmatn', 'sans-serif'],
      },
      colors: {
        bg:       '#080b14',
        surface:  '#0f1623',
        card:     '#141c2e',
        accent:   '#4f7bff',
        accent2:  '#a259ff',
        sgold:    '#f5c842',
        sgreen:   '#22d87a',
        sred:     '#ff4f6a',
        muted:    '#6b7a99',
      },
      borderRadius: { sector: '18px' },
    },
  },
  plugins: [],
}
