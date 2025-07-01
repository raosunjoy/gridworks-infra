/** @type {import('next').NextConfig} */
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig = {
  // Performance optimizations for luxury experience
  swcMinify: true,
  compress: true,
  poweredByHeader: false,
  
  // Security headers for Black Portal
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;"
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(self), payment=(self)'
          }
        ]
      }
    ];
  },

  // Redirects for SEO and security
  async redirects() {
    return [
      {
        source: '/index.html',
        destination: '/',
        permanent: true,
      },
      {
        source: '/home',
        destination: '/',
        permanent: true,
      }
    ];
  },

  // Environment variables
  env: {
    CUSTOM_KEY: 'black-portal-production',
    PORTAL_VERSION: '1.0.0',
    LUXURY_MODE: 'true'
  },

  // Image optimization for luxury assets
  images: {
    domains: ['black.trademate.ai', 'assets.trademate.ai'],
    formats: ['image/webp', 'image/avif'],
    quality: 95,
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // Experimental features for premium experience
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
    gzipSize: true
  },

  // Webpack configuration for luxury assets
  webpack: (config, { dev, isServer }) => {
    // Optimize for luxury experience
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          luxury: {
            name: 'luxury-components',
            test: /[\\/]src[\\/](components|lib)[\\/]/,
            priority: 20,
            reuseExistingChunk: true
          },
          threejs: {
            name: 'threejs',
            test: /[\\/]node_modules[\\/](three|@react-three)[\\/]/,
            priority: 30,
            reuseExistingChunk: true
          }
        }
      };
    }

    // Handle GLSL shaders for 3D effects
    config.module.rules.push({
      test: /\.(glsl|vs|fs|vert|frag)$/,
      use: ['raw-loader', 'glslify-loader']
    });

    return config;
  },

  // Output configuration for deployment
  output: 'standalone',
  
  // Disable telemetry for privacy
  telemetry: false,

  // Custom server configuration
  serverRuntimeConfig: {
    PROJECT_ROOT: __dirname
  },

  publicRuntimeConfig: {
    PORTAL_URL: process.env.PORTAL_URL || 'https://black.trademate.ai'
  }
};

module.exports = withBundleAnalyzer(nextConfig);