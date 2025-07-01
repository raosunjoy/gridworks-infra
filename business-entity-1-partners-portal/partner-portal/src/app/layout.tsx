import './globals.css';
import { Inter } from 'next/font/google';
import { Metadata } from 'next';
import { ClientProvider } from '@/components/providers/ClientProvider';

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: {
    default: 'TradeMate Partner Portal',
    template: '%s | TradeMate Partner Portal',
  },
  description: 'Enterprise-grade AI support, Zero-Knowledge privacy, and WhatsApp integration for fintech companies across India.',
  keywords: [
    'fintech',
    'API',
    'AI support',
    'WhatsApp integration',
    'Zero-Knowledge privacy',
    'vernacular languages',
    'India',
    'partner portal',
  ],
  authors: [{ name: 'TradeMate Team' }],
  creator: 'TradeMate',
  publisher: 'TradeMate',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://partners.trademate.ai',
    siteName: 'TradeMate Partner Portal',
    title: 'TradeMate Partner Portal - AI-Powered Fintech Solutions',
    description: 'Transform your fintech business with enterprise-grade AI support, Zero-Knowledge privacy, and WhatsApp integration in 11 Indian languages.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'TradeMate Partner Portal',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TradeMate Partner Portal - AI-Powered Fintech Solutions',
    description: 'Transform your fintech business with enterprise-grade AI support, Zero-Knowledge privacy, and WhatsApp integration in 11 Indian languages.',
    images: ['/og-image.png'],
    creator: '@TradeMateAI',
  },
  verification: {
    google: 'your-google-verification-code',
  },
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#3b82f6" />
        
        {/* Preconnect to external domains */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        
        {/* Security headers */}
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
        <meta httpEquiv="Referrer-Policy" content="strict-origin-when-cross-origin" />
        
        {/* Performance hints */}
        <link rel="dns-prefetch" href="//api.trademate.ai" />
        
        {/* Sentry initialization */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if (typeof window !== 'undefined') {
                window.addEventListener('error', function(e) {
                  console.error('Global error:', e.error);
                });
                
                window.addEventListener('unhandledrejection', function(e) {
                  console.error('Unhandled promise rejection:', e.reason);
                });
              }
            `,
          }}
        />
      </head>
      <body className={`${inter.className} antialiased bg-gray-50 text-gray-900`}>
        <ClientProvider>
          <div id="root">
            {children}
          </div>
        </ClientProvider>
        
        {/* Portal for modals */}
        <div id="modal-root" />
        
        {/* Loading indicator */}
        <div id="loading-indicator" />
        
        {/* Service worker registration */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                      console.log('SW registered: ', registration);
                    })
                    .catch(function(registrationError) {
                      console.log('SW registration failed: ', registrationError);
                    });
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}