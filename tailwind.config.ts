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
        sans:    ["var(--font-geist)", "Geist", "system-ui", "sans-serif"],
        serif:   ["var(--font-literata)", "Literata", "Georgia", "serif"],
        mono:    ["var(--font-geist-mono)", "monospace"],
      },
      colors: {
        // All semantic tokens reference CSS variables defined in globals.css.
        // The .dark class swaps those variables → every Tailwind class adapts automatically.
        // The `rgb(var(...) / <alpha-value>)` pattern lets opacity modifiers work (e.g. text-on-surface/70).
        primary:              "rgb(var(--c-primary) / <alpha-value>)",
        "primary-container":  "rgb(var(--c-primary-container) / <alpha-value>)",
        "on-primary":         "rgb(var(--c-on-primary) / <alpha-value>)",
        "on-primary-container": "rgb(var(--c-on-primary-container) / <alpha-value>)",
        "primary-fixed":      "rgb(var(--c-primary-fixed) / <alpha-value>)",
        "primary-fixed-dim":  "rgb(var(--c-primary-fixed-dim) / <alpha-value>)",
        "inverse-primary":    "rgb(var(--c-inverse-primary) / <alpha-value>)",

        secondary:            "rgb(var(--c-secondary) / <alpha-value>)",
        "secondary-container": "rgb(var(--c-secondary-container) / <alpha-value>)",
        "on-secondary":       "rgb(var(--c-on-secondary) / <alpha-value>)",
        "on-secondary-container": "rgb(var(--c-on-secondary-container) / <alpha-value>)",
        "secondary-fixed":    "rgb(var(--c-secondary-fixed) / <alpha-value>)",
        "on-secondary-fixed": "rgb(var(--c-on-secondary-fixed) / <alpha-value>)",

        tertiary:             "rgb(var(--c-tertiary) / <alpha-value>)",
        "tertiary-container": "rgb(var(--c-tertiary-container) / <alpha-value>)",
        "on-tertiary":        "rgb(var(--c-on-tertiary) / <alpha-value>)",

        background:           "rgb(var(--c-background) / <alpha-value>)",
        surface:              "rgb(var(--c-surface) / <alpha-value>)",
        "surface-bright":     "rgb(var(--c-surface-bright) / <alpha-value>)",
        "surface-dim":        "rgb(var(--c-surface-dim) / <alpha-value>)",
        "surface-variant":    "rgb(var(--c-surface-variant) / <alpha-value>)",
        "surface-container-lowest": "rgb(var(--c-surface-container-lowest) / <alpha-value>)",
        "surface-container-low":    "rgb(var(--c-surface-container-low) / <alpha-value>)",
        "surface-container":        "rgb(var(--c-surface-container) / <alpha-value>)",
        "surface-container-high":   "rgb(var(--c-surface-container-high) / <alpha-value>)",
        "surface-container-highest": "rgb(var(--c-surface-container-highest) / <alpha-value>)",
        "inverse-surface":    "rgb(var(--c-inverse-surface) / <alpha-value>)",
        "inverse-on-surface": "rgb(var(--c-inverse-on-surface) / <alpha-value>)",

        "on-background":      "rgb(var(--c-on-surface) / <alpha-value>)",
        "on-surface":         "rgb(var(--c-on-surface) / <alpha-value>)",
        "on-surface-variant": "rgb(var(--c-on-surface-variant) / <alpha-value>)",

        outline:              "rgb(var(--c-outline) / <alpha-value>)",
        "outline-variant":    "rgb(var(--c-outline-variant) / <alpha-value>)",

        error:                "rgb(var(--c-error) / <alpha-value>)",
        "error-container":    "rgb(var(--c-error-container) / <alpha-value>)",
        "on-error":           "rgb(var(--c-on-error) / <alpha-value>)",
        "on-error-container": "rgb(var(--c-on-error-container) / <alpha-value>)",

        ink:    "rgb(var(--c-ink) / <alpha-value>)",
        vellum: "rgb(var(--c-vellum) / <alpha-value>)",
      },
      spacing: {
        "container-max": "1280px",
        gutter:          "24px",
        "margin-mobile": "20px",
        "margin-desktop":"64px",
        unit:            "8px",
      },
      borderRadius: {
        DEFAULT: "0.5rem",
        lg:      "0.75rem",
        xl:      "1rem",
        "2xl":   "1.5rem",
        full:    "9999px",
      },
      fontSize: {
        "display-lg":  ["64px", { lineHeight: "1.1",  letterSpacing: "-0.02em", fontWeight: "700" }],
        "display-mob": ["40px", { lineHeight: "1.2",  letterSpacing: "-0.01em", fontWeight: "700" }],
        "headline-lg": ["32px", { lineHeight: "1.3",  fontWeight: "600" }],
        "headline-md": ["24px", { lineHeight: "1.4",  fontWeight: "600" }],
        "body-lg":     ["18px", { lineHeight: "1.6",  fontWeight: "400" }],
        "body-md":     ["16px", { lineHeight: "1.5",  fontWeight: "400" }],
        "label-sm":    ["12px", { lineHeight: "1",    letterSpacing: "0.05em", fontWeight: "600" }],
      },
      animation: {
        shimmer:   "shimmer 1.8s infinite",
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up":"slideUp 0.3s ease-out",
      },
      keyframes: {
        shimmer:  { "0%": { backgroundPosition: "200% 0" }, "100%": { backgroundPosition: "-200% 0" } },
        fadeIn:   { from: { opacity: "0", transform: "translateY(8px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        slideUp:  { from: { transform: "translateY(6px)", opacity: "0" }, to: { transform: "translateY(0)", opacity: "1" } },
      },
      boxShadow: {
        paper: "0 4px 20px -2px rgba(27, 28, 25, 0.06)",
        card:  "0 20px 40px rgba(27, 28, 25, 0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
