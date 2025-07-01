import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { AppError } from '@/types';

interface ErrorState {
  // Error Storage
  errors: AppError[];
  globalError: AppError | null;
  
  // Notification State
  notifications: ErrorNotification[];
  
  // Error Handling Methods
  addError: (error: Omit<AppError, 'timestamp'>) => void;
  removeError: (index: number) => void;
  clearErrors: () => void;
  setGlobalError: (error: AppError | null) => void;
  
  // Notification Methods
  showNotification: (notification: Omit<ErrorNotification, 'id' | 'timestamp'>) => void;
  hideNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // Error Recovery
  retryOperation: (operationId: string) => Promise<void>;
  reportError: (error: AppError) => Promise<void>;
}

interface ErrorNotification {
  id: string;
  type: 'error' | 'warning' | 'info' | 'success';
  title: string;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  autoHide?: boolean;
  duration?: number;
  timestamp: Date;
}

export const useErrorStore = create<ErrorState>()(
  immer((set, get) => ({
    // Initial State
    errors: [],
    globalError: null,
    notifications: [],

    // Error Handling Methods
    addError: (error: Omit<AppError, 'timestamp'>) => {
      const newError: AppError = {
        ...error,
        timestamp: new Date(),
      };

      set((state) => {
        state.errors.unshift(newError);
        
        // Keep only last 50 errors
        if (state.errors.length > 50) {
          state.errors = state.errors.slice(0, 50);
        }
      });

      // Auto-report critical errors
      if (error.code.startsWith('CRITICAL_')) {
        get().reportError(newError);
      }

      // Show notification for user-facing errors
      if (error.code.startsWith('USER_')) {
        get().showNotification({
          type: 'error',
          title: 'Error',
          message: error.message,
          autoHide: true,
          duration: 5000,
        });
      }
    },

    removeError: (index: number) => {
      set((state) => {
        state.errors.splice(index, 1);
      });
    },

    clearErrors: () => {
      set((state) => {
        state.errors = [];
      });
    },

    setGlobalError: (error: AppError | null) => {
      set((state) => {
        state.globalError = error;
      });
    },

    // Notification Methods
    showNotification: (notification: Omit<ErrorNotification, 'id' | 'timestamp'>) => {
      const newNotification: ErrorNotification = {
        ...notification,
        id: generateNotificationId(),
        timestamp: new Date(),
      };

      set((state) => {
        state.notifications.unshift(newNotification);
      });

      // Auto-hide notification if specified
      if (notification.autoHide !== false) {
        const duration = notification.duration || 5000;
        setTimeout(() => {
          get().hideNotification(newNotification.id);
        }, duration);
      }
    },

    hideNotification: (id: string) => {
      set((state) => {
        state.notifications = state.notifications.filter(n => n.id !== id);
      });
    },

    clearNotifications: () => {
      set((state) => {
        state.notifications = [];
      });
    },

    // Error Recovery
    retryOperation: async (operationId: string) => {
      try {
        const response = await fetch(`/api/retry/${operationId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Retry failed: ${response.statusText}`);
        }

        get().showNotification({
          type: 'success',
          title: 'Success',
          message: 'Operation retried successfully',
          autoHide: true,
        });
      } catch (error: any) {
        get().addError({
          code: 'RETRY_FAILED',
          message: `Failed to retry operation: ${error?.message || 'Unknown error'}`,
          details: { operationId },
        });
      }
    },

    reportError: async (error: AppError) => {
      try {
        await fetch('/api/errors/report', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(error),
        });
      } catch (reportError) {
        console.error('Failed to report error:', reportError);
      }
    },
  }))
);

// Helper Functions
function generateNotificationId(): string {
  return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Error Handler Hook
export function useErrorHandler() {
  const { addError, showNotification } = useErrorStore();

  const handleError = (error: any, context?: string) => {
    console.error('Error caught by handler:', error, context);

    // Extract error details
    const errorCode = error.code || error.name || 'UNKNOWN_ERROR';
    const errorMessage = error.message || 'An unknown error occurred';
    
    // Create structured error
    const structuredError: Omit<AppError, 'timestamp'> = {
      code: errorCode,
      message: errorMessage,
      details: {
        context,
        stack: error.stack,
        originalError: error,
      },
    };

    addError(structuredError);

    // Show user-friendly notification
    showNotification({
      type: 'error',
      title: 'Something went wrong',
      message: getUserFriendlyMessage(errorCode, errorMessage),
      action: {
        label: 'Retry',
        onClick: () => window.location.reload(),
      },
      autoHide: true,
      duration: 8000,
    });
  };

  return { handleError };
}

// Error Recovery Hook
export function useErrorRecovery() {
  const { retryOperation, showNotification } = useErrorStore();

  const withRetry = async <T>(
    operation: () => Promise<T>,
    options: {
      maxRetries?: number;
      delay?: number;
      backoff?: boolean;
      onRetry?: (attempt: number) => void;
    } = {}
  ): Promise<T> => {
    const { maxRetries = 3, delay = 1000, backoff = true, onRetry } = options;
    
    let lastError: Error = new Error('Operation failed');
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt < maxRetries) {
          const waitTime = backoff ? delay * Math.pow(2, attempt) : delay;
          
          if (onRetry) {
            onRetry(attempt + 1);
          }
          
          showNotification({
            type: 'warning',
            title: 'Retrying...',
            message: `Attempt ${attempt + 1} failed, retrying in ${waitTime}ms`,
            autoHide: true,
            duration: 2000,
          });
          
          await new Promise(resolve => setTimeout(resolve, waitTime));
        }
      }
    }
    
    throw lastError;
  };

  return { withRetry, retryOperation };
}

// User-friendly error messages
function getUserFriendlyMessage(code: string, originalMessage: string): string {
  const friendlyMessages: Record<string, string> = {
    NETWORK_ERROR: 'Please check your internet connection and try again.',
    TIMEOUT_ERROR: 'The request took too long. Please try again.',
    AUTHENTICATION_ERROR: 'Please log in again to continue.',
    PERMISSION_ERROR: 'You don\'t have permission to perform this action.',
    VALIDATION_ERROR: 'Please check your input and try again.',
    RATE_LIMIT_ERROR: 'Too many requests. Please wait a moment and try again.',
    SERVER_ERROR: 'Our servers are experiencing issues. Please try again later.',
    NOT_FOUND_ERROR: 'The requested resource was not found.',
  };

  return friendlyMessages[code] || originalMessage || 'An unexpected error occurred.';
}