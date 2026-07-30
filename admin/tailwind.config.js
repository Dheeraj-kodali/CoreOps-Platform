/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        temple: {
          gold: "#D4AF37",
          goldLight: "#F3E5AB",
          goldDark: "#997A15",
          brown: "#2C1A11",
          brownLight: "#3E2723",
          ivory: "#FAF8F5",
          crimson: "#900C3F",
          surface: "#FFFFFF",
        },
      },
      fontFamily: {
        heading: ["Cinzel", "serif"],
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
