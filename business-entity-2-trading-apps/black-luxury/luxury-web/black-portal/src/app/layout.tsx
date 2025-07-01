import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { BlackPortalProvider } from '@/lib/providers/BlackPortalProvider';
import { SecurityProvider } from '@/lib/providers/SecurityProvider';
import { DeviceFingerprint } from '@/components/security/DeviceFingerprint';
import { LuxuryToastProvider } from '@/components/ui/LuxuryToastProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'GridWorks Black Portal - For Those Who Trade Beyond Charts',
  description: 'Ultra-exclusive trading platform for billionaires and ultra-HNI individuals. Invitation only.',
  keywords: ['luxury trading', 'billionaire trading', 'ultra-premium', 'invitation only', 'black portal'],
  authors: [{ name: 'GridWorks Black Team' }],
  robots: 'noindex, nofollow', // Keep portal mysterious
  openGraph: {
    title: 'GridWorks Black Portal',
    description: 'For Those Who Trade Beyond Charts',
    type: 'website',
    url: 'https://black.gridworks.ai',
    siteName: 'GridWorks Black Portal',
    images: [
      {
        url: 'https://black.gridworks.ai/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'GridWorks Black Portal'
      }
    ]
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GridWorks Black Portal',
    description: 'For Those Who Trade Beyond Charts',
    images: ['https://black.gridworks.ai/twitter-image.jpg']
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false
  },
  themeColor: '#000000',
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png'
  }
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang=\"en\" className=\"dark\">
      <head>
        <meta name=\"format-detection\" content=\"telephone=no\" />
        <meta name=\"msapplication-TileColor\" content=\"#000000\" />
        <meta name=\"msapplication-config\" content=\"/browserconfig.xml\" />
        
        {/* Preload critical luxury fonts */}
        <link rel=\"preload\" href=\"/fonts/didot.woff2\" as=\"font\" type=\"font/woff2\" crossOrigin=\"anonymous\" />
        <link rel=\"preload\" href=\"/fonts/futura.woff2\" as=\"font\" type=\"font/woff2\" crossOrigin=\"anonymous\" />
        
        {/* Security headers via meta tags */}
        <meta httpEquiv=\"X-Content-Type-Options\" content=\"nosniff\" />
        <meta httpEquiv=\"X-Frame-Options\" content=\"DENY\" />
        <meta httpEquiv=\"Referrer-Policy\" content=\"strict-origin-when-cross-origin\" />
        
        {/* Prevent right-click and text selection for mystery */}
        <style dangerouslySetInnerHTML={{
          __html: `
            * {
              -webkit-touch-callout: none;
              -webkit-user-select: none;
              -khtml-user-select: none;
              -moz-user-select: none;
              -ms-user-select: none;
              user-select: none;
            }
            input, textarea {
              -webkit-user-select: text;
              -moz-user-select: text;
              -ms-user-select: text;
              user-select: text;
            }
          `
        }} />
      </head>
      
      <body className={`${inter.className} bg-void-black text-white antialiased`}>
        {/* Security layer - tracks device from first visit */}
        <SecurityProvider>
          <DeviceFingerprint />
          
          {/* Black Portal context and state management */}
          <BlackPortalProvider>
            {/* Luxury toast notifications */}
            <LuxuryToastProvider>
              
              {/* Reality distortion background effects */}
              <div className=\"fixed inset-0 bg-void-gradient opacity-50 pointer-events-none\" />
              <div className=\"fixed inset-0 bg-luxury-radial opacity-30 pointer-events-none\" />
              
              {/* Main portal content */}
              <main className=\"relative z-10 min-h-screen\">
                {children}
              </main>
              
              {/* Luxury loading overlay for interactions */}
              <div id=\"luxury-loader\" className=\"hidden fixed inset-0 bg-void-black/80 backdrop-blur-luxury z-100 flex items-center justify-center\">
                <div className=\"luxury-spinner\">
                  <div className=\"animate-void-pulse w-8 h-8 border-2 border-void-gold rounded-full border-t-transparent\" />
                </div>
              </div>
              
            </LuxuryToastProvider>
          </BlackPortalProvider>
        </SecurityProvider>
        
        {/* Disable dev tools in production */}
        {process.env.NODE_ENV === 'production' && (
          <script dangerouslySetInnerHTML={{
            __html: `
              // Disable F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U
              document.addEventListener('keydown', function (e) {
                if (e.keyCode == 123 || // F12
                    (e.ctrlKey && e.shiftKey && e.keyCode == 73) || // Ctrl+Shift+I
                    (e.ctrlKey && e.shiftKey && e.keyCode == 74) || // Ctrl+Shift+J
                    (e.ctrlKey && e.keyCode == 85)) { // Ctrl+U
                  e.preventDefault();
                  return false;
                }
              });
              
              // Disable right-click
              document.addEventListener('contextmenu', function (e) {
                e.preventDefault();
                return false;
              });
              
              // Detect dev tools
              let devtools = {open: false, orientation: null};
              (function() {
                setInterval(function() {
                  if (window.outerHeight - window.innerHeight > 200 || window.outerWidth - window.innerWidth > 200) {
                    if (!devtools.open) {
                      devtools.open = true;
                      // Redirect to mystery page if dev tools detected
                      window.location.href = '/mystery';
                    }
                  } else {
                    devtools.open = false;
                  }
                }, 500);
              })();
            `
          }} />
        )}
      </body>
    </html>
  );
}