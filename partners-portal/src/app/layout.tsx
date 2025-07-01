import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import AiChatWidget from '@/components/ai/AiChatWidget'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'GridWorks Partners Portal',
  description: 'Enterprise B2B Infrastructure Services Portal',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          {children}
        </div>
        <AiChatWidget />
      </body>
    </html>
  )
}