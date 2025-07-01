/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/lib/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Black Portal Color Palette
      colors: {
        // Primary blacks for tier hierarchy
        'void-black': '#000000',
        'obsidian': '#0A0A0A',
        'onyx': '#1C1C1C',
        
        // Luxury accent colors
        'void-gold': '#FFD700',
        'obsidian-platinum': '#E5E4E2',
        'onyx-silver': '#C0C0C0',
        
        // Neutral luxury palette
        'luxury-gray': {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0A0A0A'
        },
        
        // Status colors with luxury feel
        'success-luxury': '#10B981',
        'warning-luxury': '#F59E0B',
        'error-luxury': '#EF4444',
        'info-luxury': '#3B82F6',
        
        // Background gradients
        'gradient-void': 'linear-gradient(135deg, #000000 0%, #1C1C1C 100%)',
        'gradient-obsidian': 'linear-gradient(135deg, #0A0A0A 0%, #262626 100%)',
        'gradient-onyx': 'linear-gradient(135deg, #1C1C1C 0%, #404040 100%)'
      },
      
      // Luxury typography
      fontFamily: {
        'luxury-serif': ['Didot', 'serif'],
        'luxury-sans': ['Futura', 'system-ui', 'sans-serif'],
        'luxury-mono': ['Monaco', 'Consolas', 'monospace']
      },
      
      // Premium spacing scale
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
        '144': '36rem'
      },
      
      // Luxury shadows
      boxShadow: {
        'luxury-sm': '0 1px 2px rgba(0, 0, 0, 0.15)',
        'luxury': '0 4px 6px rgba(0, 0, 0, 0.2)',
        'luxury-md': '0 8px 25px rgba(0, 0, 0, 0.25)',
        'luxury-lg': '0 15px 35px rgba(0, 0, 0, 0.3)',
        'luxury-xl': '0 25px 50px rgba(0, 0, 0, 0.4)',
        'void-glow': '0 0 20px rgba(255, 215, 0, 0.3)',
        'obsidian-glow': '0 0 15px rgba(229, 228, 226, 0.2)',
        'onyx-glow': '0 0 10px rgba(192, 192, 192, 0.15)'
      },
      
      // Animation configurations
      animation: {
        'luxury-float': 'luxuryFloat 6s ease-in-out infinite',
        'void-pulse': 'voidPulse 3s ease-in-out infinite',
        'reality-warp': 'realityWarp 2s ease-in-out infinite',
        'gold-shimmer': 'goldShimmer 2s linear infinite',
        'fade-in-luxury': 'fadeInLuxury 1.5s ease-out',
        'slide-up-luxury': 'slideUpLuxury 1s ease-out'
      },
      
      // Custom keyframes
      keyframes: {
        luxuryFloat: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' }
        },
        voidPulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' }
        },
        realityWarp: {
          '0%, 100%': { filter: 'none' },
          '50%': { filter: 'blur(1px) brightness(1.1)' }
        },
        goldShimmer: {
          '0%': { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' }
        },
        fadeInLuxury: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        slideUpLuxury: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      },
      
      // Custom gradients
      backgroundImage: {
        'luxury-radial': 'radial-gradient(circle at center, rgba(255,215,0,0.1) 0%, transparent 70%)',
        'void-gradient': 'linear-gradient(135deg, #000000 0%, #1C1C1C 50%, #000000 100%)',
        'obsidian-gradient': 'linear-gradient(135deg, #0A0A0A 0%, #262626 50%, #0A0A0A 100%)',
        'onyx-gradient': 'linear-gradient(135deg, #1C1C1C 0%, #404040 50%, #1C1C1C 100%)',
        'gold-shimmer': 'linear-gradient(90deg, transparent, rgba(255,215,0,0.4), transparent)'
      },
      
      // Custom filters
      backdropBlur: {
        'luxury': '20px'
      },
      
      // Screen sizes for luxury displays
      screens: {
        '3xl': '1920px',
        '4xl': '2560px',
        '5xl': '3840px'
      },
      
      // Z-index scale for layering
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100'
      }
    }
  },
  plugins: [
    // Custom plugin for luxury components
    function({ addUtilities, addComponents, theme }) {
      // Luxury button styles
      addComponents({
        '.btn-void': {
          '@apply bg-void-black text-void-gold border border-void-gold hover:bg-void-gold hover:text-void-black transition-all duration-300 luxury-shadow-lg': {},
          'font-family': theme('fontFamily.luxury-sans'),
          'text-transform': 'uppercase',
          'letter-spacing': '0.1em',
          'backdrop-filter': 'blur(10px)'
        },
        '.btn-obsidian': {
          '@apply bg-obsidian text-obsidian-platinum border border-obsidian-platinum hover:bg-obsidian-platinum hover:text-obsidian transition-all duration-300': {},
          'font-family': theme('fontFamily.luxury-sans'),
          'text-transform': 'uppercase',
          'letter-spacing': '0.1em'
        },
        '.btn-onyx': {
          '@apply bg-onyx text-onyx-silver border border-onyx-silver hover:bg-onyx-silver hover:text-onyx transition-all duration-300': {},
          'font-family': theme('fontFamily.luxury-sans'),
          'text-transform': 'uppercase',
          'letter-spacing': '0.1em'
        }
      });
      
      // Luxury text styles
      addUtilities({
        '.text-luxury-heading': {
          'font-family': theme('fontFamily.luxury-serif'),
          'font-weight': '300',
          'letter-spacing': '0.02em',
          'line-height': '1.2'
        },
        '.text-luxury-body': {
          'font-family': theme('fontFamily.luxury-sans'),
          'font-weight': '400',
          'letter-spacing': '0.01em',
          'line-height': '1.6'
        },
        '.text-luxury-caption': {
          'font-family': theme('fontFamily.luxury-sans'),
          'font-weight': '300',
          'font-size': '0.875rem',
          'letter-spacing': '0.05em',
          'text-transform': 'uppercase'
        }
      });
    }
  ]
};