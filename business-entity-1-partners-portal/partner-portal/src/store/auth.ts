import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { User, Partner, Permission } from '@/types';

interface AuthState {
  // User State
  user: User | null;
  partner: Partner | null;
  permissions: Permission[];
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Session Management
  sessionId: string | null;
  sessionExpiry: Date | null;
  lastActivity: Date;
  
  // Authentication Methods
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateLastActivity: () => void;
  
  // Session Validation
  validateSession: () => boolean;
  isSessionExpired: () => boolean;
  
  // User Management
  updateUser: (user: Partial<User>) => void;
  updatePartner: (partner: Partial<Partner>) => void;
  
  // Permission Checks
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
}

interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    immer((set, get) => ({
      // Initial State
      user: null,
      partner: null,
      permissions: [],
      isAuthenticated: false,
      isLoading: false,
      sessionId: null,
      sessionExpiry: null,
      lastActivity: new Date(),

      // Authentication Methods
      login: async (credentials: LoginCredentials) => {
        set((state) => {
          state.isLoading = true;
        });

        try {
          const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
          });

          if (!response.ok) {
            throw new Error('Login failed');
          }

          const data = await response.json();
          
          set((state) => {
            state.user = data.user;
            state.partner = data.partner;
            state.permissions = data.permissions;
            state.isAuthenticated = true;
            state.sessionId = data.sessionId;
            state.sessionExpiry = new Date(data.sessionExpiry);
            state.lastActivity = new Date();
            state.isLoading = false;
          });

          // Authentication successful
        } catch (error) {
          set((state) => {
            state.isLoading = false;
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${get().sessionId}`,
            },
          });
        } catch (error) {
          console.warn('Logout request failed:', error);
        }

        set((state) => {
          state.user = null;
          state.partner = null;
          state.permissions = [];
          state.isAuthenticated = false;
          state.sessionId = null;
          state.sessionExpiry = null;
        });
      },

      refreshToken: async () => {
        try {
          const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${get().sessionId}`,
            },
          });

          if (!response.ok) {
            throw new Error('Token refresh failed');
          }

          const data = await response.json();
          
          set((state) => {
            state.sessionId = data.sessionId;
            state.sessionExpiry = new Date(data.sessionExpiry);
            state.lastActivity = new Date();
          });
        } catch (error) {
          console.error('Token refresh failed:', error);
          await get().logout();
        }
      },

      updateLastActivity: () => {
        set((state) => {
          state.lastActivity = new Date();
        });
      },

      // Session Validation
      validateSession: () => {
        const { sessionExpiry, isAuthenticated } = get();
        
        if (!isAuthenticated || !sessionExpiry) {
          return false;
        }

        return new Date() < sessionExpiry;
      },

      isSessionExpired: () => {
        const { sessionExpiry } = get();
        
        if (!sessionExpiry) {
          return true;
        }

        return new Date() >= sessionExpiry;
      },

      // User Management
      updateUser: (userData: Partial<User>) => {
        set((state) => {
          if (state.user) {
            state.user = { ...state.user, ...userData };
          }
        });
      },

      updatePartner: (partnerData: Partial<Partner>) => {
        set((state) => {
          if (state.partner) {
            state.partner = { ...state.partner, ...partnerData };
          }
        });
      },

      // Permission Checks
      hasPermission: (permission: Permission) => {
        const { permissions } = get();
        return permissions.includes(permission);
      },

      hasAnyPermission: (requiredPermissions: Permission[]) => {
        const { permissions } = get();
        return requiredPermissions.some(permission => permissions.includes(permission));
      },

      hasAllPermissions: (requiredPermissions: Permission[]) => {
        const { permissions } = get();
        return requiredPermissions.every(permission => permissions.includes(permission));
      },

      // Session Monitoring (Private Method)
      startSessionMonitoring: () => {
        // Auto-refresh token before expiry
        const refreshInterval = setInterval(() => {
          const { validateSession, refreshToken } = get();
          
          if (!validateSession()) {
            clearInterval(refreshInterval);
            return;
          }

          // Refresh token 5 minutes before expiry
          const { sessionExpiry } = get();
          if (sessionExpiry) {
            const timeUntilExpiry = sessionExpiry.getTime() - new Date().getTime();
            if (timeUntilExpiry <= 5 * 60 * 1000) { // 5 minutes
              refreshToken();
            }
          }
        }, 60000); // Check every minute

        // Auto-logout on inactivity
        const inactivityTimeout = 30 * 60 * 1000; // 30 minutes
        let inactivityTimer: NodeJS.Timeout;

        const resetInactivityTimer = () => {
          clearTimeout(inactivityTimer);
          inactivityTimer = setTimeout(() => {
            get().logout();
          }, inactivityTimeout);
        };

        // Listen for user activity
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        events.forEach(event => {
          document.addEventListener(event, () => {
            get().updateLastActivity();
            resetInactivityTimer();
          }, true);
        });

        resetInactivityTimer();
      },
    })),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        partner: state.partner,
        permissions: state.permissions,
        isAuthenticated: state.isAuthenticated,
        sessionId: state.sessionId,
        sessionExpiry: state.sessionExpiry,
        lastActivity: state.lastActivity,
      }),
    }
  )
);