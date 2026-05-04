import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: '#007aff',
          hover: '#0062cc',
        },
        surface: {
          DEFAULT: '#ffffff',
          secondary: '#fafafa',
        },
        border: '#e5e5e5',
        'text-primary': '#1d1d1f',
        'text-secondary': '#6e6e73',
        'text-tertiary': '#aeaeb2',
        easy: '#34c759',
        medium: '#ff9500',
        hard: '#ff3b30',
        solved: '#30b0c7',
      },
      boxShadow: {
        soft: '0 1px 3px rgba(0,0,0,0.06)',
        'soft-lg': '0 4px 12px rgba(0,0,0,0.08)',
      },
      borderRadius: {
        pill: '9999px',
      },
    },
  },
  plugins: [],
};
export default config;
