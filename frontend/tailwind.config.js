/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'status-processing': '#ffd700',
        'status-done': '#90EE90',
        'status-error': '#ffcccb',
      }
    },
  },
  plugins: [],
}
