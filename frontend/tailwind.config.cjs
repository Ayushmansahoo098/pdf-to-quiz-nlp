/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 0 1px rgba(232, 121, 249, 0.15), 0 20px 40px rgba(139, 92, 246, 0.2)",
      },
      colors: {
        surface: {
          900: "#09090b",
          800: "#18181b",
          700: "#27272a",
        },
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
};
