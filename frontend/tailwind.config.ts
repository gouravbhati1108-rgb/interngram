/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: "#4f46e5", foreground: "#ffffff" },
        muted: "#f1f5f9",
        border: "#e2e8f0",
      },
    },
  },
  plugins: [],
};
