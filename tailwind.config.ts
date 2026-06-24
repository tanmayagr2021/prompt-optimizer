import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "Fira Code", "monospace"],
      },
      colors: {
        accent: {
          50:  "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
      },
      animation: {
        shimmer:  "shimmer 1.8s infinite",
        "fade-in":  "fadeIn 0.25s ease-out",
        "slide-up": "slideUp 0.25s ease-out",
      },
      keyframes: {
        shimmer:  { "0%": { backgroundPosition: "200% 0" }, "100%": { backgroundPosition: "-200% 0" } },
        fadeIn:   { from: { opacity: "0" }, to: { opacity: "1" } },
        slideUp:  { from: { transform: "translateY(6px)", opacity: "0" }, to: { transform: "translateY(0)", opacity: "1" } },
      },
    },
  },
  plugins: [],
};

export default config;
