/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        "background-subtle": "hsl(var(--background-subtle))",
        card: "hsl(var(--card))",
        popover: "hsl(var(--popover))",
        foreground: "hsl(var(--foreground))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        secondary: "hsl(var(--secondary))",
        border: "hsl(var(--border))",
        "border-subtle": "hsl(var(--border-subtle))",
        input: "hsl(var(--input))",
        primary: "hsl(var(--primary))",
        "primary-foreground": "hsl(var(--primary-foreground))",
        destructive: "hsl(var(--destructive))",
        "accent-1": "hsl(var(--accent-1))",
        "accent-1-vivid": "hsl(var(--accent-1-vivid))",
        "accent-2": "hsl(var(--accent-2))",
        "accent-2-vivid": "hsl(var(--accent-2-vivid))",
        "accent-3": "hsl(var(--accent-3))",
        "accent-3-vivid": "hsl(var(--accent-3-vivid))",
      },
      fontFamily: {
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      boxShadow: {
        sm: "0 1px 2px 0 hsl(0 0% 0% / 0.03)",
        md: "0 4px 6px -1px hsl(0 0% 0% / 0.05), 0 2px 4px -2px hsl(0 0% 0% / 0.03)",
        lg: "0 10px 15px -3px hsl(0 0% 0% / 0.05), 0 4px 6px -4px hsl(0 0% 0% / 0.03)",
        soft: "0 20px 40px -15px hsl(0 0% 0% / 0.08)",
      },
      screens: {
        "2xl": "1400px",
      },
    },
  },
  plugins: [],
}
