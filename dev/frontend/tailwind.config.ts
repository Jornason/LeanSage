import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#6366F1",
          dark: "#4338CA",
          light: "#818CF8",
        },
        secondary: "#8B5CF6",
        success: "#22C55E",
        error: "#EF4444",
        warning: "#F59E0B",
        bg: {
          dark: "#0F172A",
          surface: "#1E293B",
          elevated: "#334155",
        },
        text: {
          primary: "#F8FAFC",
          secondary: "#94A3B8",
          muted: "#64748B",
        },
        border: {
          DEFAULT: "#334155",
          focus: "#6366F1",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      animation: {
        "spin-slow": "spin 3s linear infinite",
        "pulse-fast": "pulse 1s ease-in-out infinite",
        "fade-in": "fadeIn 0.3s ease-in",
        "slide-up": "slideUp 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-hero":
          "linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%)",
        "gradient-card":
          "linear-gradient(135deg, #1E293B 0%, #1E1B4B 100%)",
      },
      boxShadow: {
        "glow-primary": "0 0 20px rgba(99, 102, 241, 0.3)",
        "glow-success": "0 0 20px rgba(34, 197, 94, 0.3)",
        "glow-error": "0 0 20px rgba(239, 68, 68, 0.3)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
