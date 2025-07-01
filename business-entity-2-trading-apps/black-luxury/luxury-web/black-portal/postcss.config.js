module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    // CSS optimization for luxury performance
    cssnano: process.env.NODE_ENV === 'production' ? {
      preset: ['default', {
        discardComments: {
          removeAll: true,
        },
        normalizeWhitespace: false,
      }]
    } : false,
  },
};