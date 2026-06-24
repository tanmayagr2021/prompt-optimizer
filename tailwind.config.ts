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
        // Stitch design system palette
        primary:              "#8f000d",
        "primary-container":  "#b22222",
        "on-primary":         "#ffffff",
        "on-primary-container": "#ffc8c2",
        "primary-fixed":      "#ffdad6",
        "primary-fixed-dim":  "#ffb4ac",
        "inverse-primary":    "#ffb4ac",

        secondary:            "#735c00",
        "secondary-container": "#fed65b",
        "on-secondary":       "#ffffff",
        "on-secondary-container": "#745c00",
        "secondary-fixed":    "#ffe088",

        tertiary:             "#454545",
        "tertiary-container": "#5d5c5c",
        "on-tertiary":        "#ffffff",

        background:           "#fbf9f4",
        surface:              "#fbf9f4",
        "surface-bright":     "#fbf9f4",
        "surface-dim":        "#dbdad5",
        "surface-variant":    "#e4e2de",
        "surface-container-lowest": "#ffffff",
        "surface-container-low":    "#f5f3ee",
        "surface-container":        "#efeee9",
        "surface-container-high":   "#eae8e3",
        "surface-container-highest": "#e4e2de",
        "inverse-surface":    "#30312e",
        "inverse-on-surface": "#f2f1ec",

        "on-background":      "#1b1c19",
        "on-surface":         "#1b1c19",
        "on-surface-variant": "#5a403e",

        outline:              "#8e706d",
        "outline-variant":    "#e2beba",

        error:                "#ba1a1a",
        "error-container":    "#ffdad6",
        "on-error":           "#ffffff",
        "on-error-container": "#93000a",

        // Convenience aliases
        ink:    "#e5e0d5",
        vellum: "#faf6ee",
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
