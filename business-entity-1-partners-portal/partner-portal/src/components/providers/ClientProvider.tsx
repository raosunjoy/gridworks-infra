'use client';

import { ReactNode } from 'react';
import { QueryProvider } from '@/lib/react-query';
import { ToastProvider } from '@/components/ui/ToastProvider';
import { SessionProvider } from '@/components/providers/SessionProvider';
import ErrorBoundary from '@/components/ErrorBoundary';

interface ClientProviderProps {
  children: ReactNode;
}

export function ClientProvider({ children }: ClientProviderProps) {
  return (
    <ErrorBoundary>
      <SessionProvider>
        <QueryProvider>
          <ToastProvider>
            {children}
          </ToastProvider>
        </QueryProvider>
      </SessionProvider>
    </ErrorBoundary>
  );
}