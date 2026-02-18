import type { Config } from "tailwindcss"

const config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Alchmai brand colors
        alchmai: {
          purple: "#9333EA",
          blue: "#3B82F6",
          dark: "#0F0F23",
          darker: "#050510",
          glow: "rgba(147, 51, 234, 0.3)",
          "text-primary": "#FFFFFF",
          "text-secondary": "#A0A0B0",
          success: "#10B981",
          danger: "#EF4444",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "pulse-slow": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
        glow: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(147, 51, 234, 0.3)" },
          "50%": { boxShadow: "0 0 30px rgba(147, 51, 234, 0.5)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "pulse-slow": "pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        glow: "glow 2s ease-in-out infinite",
      },
      boxShadow: {
        "glow-purple": "0 0 20px rgba(147, 51, 234, 0.3)",
        "glow-blue": "0 0 20px rgba(59, 130, 246, 0.3)",
        "glow-purple-lg": "0 0 30px rgba(147, 51, 234, 0.5)",
        "glow-blue-lg": "0 0 30px rgba(59, 130, 246, 0.5)",
      },
    },
  },
  plugins: [
    require("tailwindcss-animate"),
    function ({ addUtilities }: any) {
      addUtilities({
        ".glow-purple": {
          boxShadow: "0 0 20px rgba(147, 51, 234, 0.3)",
        },
        ".glow-blue": {
          boxShadow: "0 0 20px rgba(59, 130, 246, 0.3)",
        },
        ".glow-purple-lg": {
          boxShadow: "0 0 30px rgba(147, 51, 234, 0.5)",
        },
        ".glow-blue-lg": {
          boxShadow: "0 0 30px rgba(59, 130, 246, 0.5)",
        },
        ".bg-grid-pattern": {
          backgroundImage: `
            linear-gradient(to right, rgba(147, 51, 234, 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(147, 51, 234, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: "20px 20px",
        },
      });
    },
  ],
} satisfies Config

export default config
