import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '../auth';
import { Permission } from '@/types';

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      partner: null,
      permissions: [],
      isAuthenticated: false,
      isLoading: false,
      sessionId: null,
      sessionExpiry: null,
      lastActivity: new Date(),
    });
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      expect(result.current.user).toBeNull();
      expect(result.current.partner).toBeNull();
      expect(result.current.permissions).toEqual([]);
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.sessionId).toBeNull();
      expect(result.current.sessionExpiry).toBeNull();
    });
  });

  describe('Authentication', () => {
    const mockCredentials = {
      email: 'test@example.com',
      password: 'password123',
    };

    const mockLoginResponse = {
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'developer',
        partnerId: 'partner1',
        permissions: [Permission.API_READ, Permission.API_WRITE],
      },
      partner: {
        id: 'partner1',
        name: 'Test Partner',
        companyName: 'Test Company',
      },
      sessionId: 'session123',
      sessionExpiry: new Date(Date.now() + 3600000).toISOString(),
      permissions: [Permission.API_READ, Permission.API_WRITE],
    };

    it('should handle successful login', async () => {
      mockFetch.mockResolvedValueOnce(mockApiResponse(mockLoginResponse));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login(mockCredentials);
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockLoginResponse.user);
      expect(result.current.partner).toEqual(mockLoginResponse.partner);
      expect(result.current.permissions).toEqual(mockLoginResponse.permissions);
      expect(result.current.sessionId).toBe(mockLoginResponse.sessionId);
      expect(result.current.isLoading).toBe(false);
    });

    it('should handle login failure', async () => {
      mockFetch.mockResolvedValueOnce(mockApiError(401, 'Unauthorized'));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await expect(result.current.login(mockCredentials)).rejects.toThrow();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.isLoading).toBe(false);
    });

    it('should set loading state during login', async () => {
      // Create a promise that we can control
      let resolveLogin: (value: any) => void;
      const loginPromise = new Promise(resolve => {
        resolveLogin = resolve;
      });
      
      mockFetch.mockReturnValueOnce(loginPromise as any);

      const { result } = renderHook(() => useAuthStore());

      // Start login
      act(() => {
        result.current.login(mockCredentials);
      });

      // Check loading state
      expect(result.current.isLoading).toBe(true);

      // Complete login
      await act(async () => {
        resolveLogin(mockApiResponse(mockLoginResponse));
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Logout', () => {
    it('should handle logout successfully', async () => {
      mockFetch.mockResolvedValueOnce(mockApiResponse({}));

      const { result } = renderHook(() => useAuthStore());

      // Set initial authenticated state
      act(() => {
        useAuthStore.setState({
          user: { id: '1', email: 'test@example.com' } as any,
          isAuthenticated: true,
          sessionId: 'session123',
        });
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.partner).toBeNull();
      expect(result.current.permissions).toEqual([]);
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.sessionId).toBeNull();
      expect(result.current.sessionExpiry).toBeNull();
    });

    it('should handle logout failure gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useAuthStore());

      // Set initial authenticated state
      act(() => {
        useAuthStore.setState({
          user: { id: '1', email: 'test@example.com' } as any,
          isAuthenticated: true,
          sessionId: 'session123',
        });
      });

      await act(async () => {
        await result.current.logout();
      });

      // Should still clear state even if logout request fails
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('Token Refresh', () => {
    it('should refresh token successfully', async () => {
      const refreshResponse = {
        sessionId: 'new_session123',
        sessionExpiry: new Date(Date.now() + 3600000).toISOString(),
      };

      mockFetch.mockResolvedValueOnce(mockApiResponse(refreshResponse));

      const { result } = renderHook(() => useAuthStore());

      // Set initial state
      act(() => {
        useAuthStore.setState({
          sessionId: 'old_session123',
          isAuthenticated: true,
        });
      });

      await act(async () => {
        await result.current.refreshToken();
      });

      expect(result.current.sessionId).toBe(refreshResponse.sessionId);
      expect(result.current.sessionExpiry).toEqual(new Date(refreshResponse.sessionExpiry));
    });

    it('should logout on refresh token failure', async () => {
      mockFetch.mockResolvedValueOnce(mockApiError(401, 'Token expired'));

      const { result } = renderHook(() => useAuthStore());

      // Set initial state
      act(() => {
        useAuthStore.setState({
          sessionId: 'old_session123',
          isAuthenticated: true,
        });
      });

      await act(async () => {
        await result.current.refreshToken();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.sessionId).toBeNull();
    });
  });

  describe('Session Validation', () => {
    it('should validate active session', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        useAuthStore.setState({
          isAuthenticated: true,
          sessionExpiry: new Date(Date.now() + 3600000), // 1 hour from now
        });
      });

      expect(result.current.validateSession()).toBe(true);
    });

    it('should invalidate expired session', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        useAuthStore.setState({
          isAuthenticated: true,
          sessionExpiry: new Date(Date.now() - 3600000), // 1 hour ago
        });
      });

      expect(result.current.validateSession()).toBe(false);
    });

    it('should invalidate session when not authenticated', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        useAuthStore.setState({
          isAuthenticated: false,
          sessionExpiry: new Date(Date.now() + 3600000),
        });
      });

      expect(result.current.validateSession()).toBe(false);
    });

    it('should check if session is expired', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        useAuthStore.setState({
          sessionExpiry: new Date(Date.now() - 1000), // 1 second ago
        });
      });

      expect(result.current.isSessionExpired()).toBe(true);
    });

    it('should handle null session expiry', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        useAuthStore.setState({
          sessionExpiry: null,
        });
      });

      expect(result.current.isSessionExpired()).toBe(true);
    });
  });

  describe('User Management', () => {
    it('should update user data', () => {
      const { result } = renderHook(() => useAuthStore());

      const initialUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
      };

      const userUpdate = {
        name: 'Updated Name',
        avatar: 'avatar.jpg',
      };

      act(() => {
        useAuthStore.setState({ user: initialUser as any });
      });

      act(() => {
        result.current.updateUser(userUpdate);
      });

      expect(result.current.user).toEqual({
        ...initialUser,
        ...userUpdate,
      });
    });

    it('should not update user when user is null', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.updateUser({ name: 'New Name' });
      });

      expect(result.current.user).toBeNull();
    });

    it('should update partner data', () => {
      const { result } = renderHook(() => useAuthStore());

      const initialPartner = {
        id: 'partner1',
        name: 'Test Partner',
        companyName: 'Test Company',
      };

      const partnerUpdate = {
        name: 'Updated Partner',
        website: 'https://example.com',
      };

      act(() => {
        useAuthStore.setState({ partner: initialPartner as any });
      });

      act(() => {
        result.current.updatePartner(partnerUpdate);
      });

      expect(result.current.partner).toEqual({
        ...initialPartner,
        ...partnerUpdate,
      });
    });
  });

  describe('Permission Checks', () => {
    beforeEach(() => {
      act(() => {
        useAuthStore.setState({
          permissions: [Permission.API_READ, Permission.API_WRITE, Permission.USER_READ],
        });
      });
    });

    it('should check if user has permission', () => {
      const { result } = renderHook(() => useAuthStore());

      expect(result.current.hasPermission(Permission.API_READ)).toBe(true);
      expect(result.current.hasPermission(Permission.API_DELETE)).toBe(false);
    });

    it('should check if user has any of the required permissions', () => {
      const { result } = renderHook(() => useAuthStore());

      expect(
        result.current.hasAnyPermission([Permission.API_DELETE, Permission.API_READ])
      ).toBe(true);

      expect(
        result.current.hasAnyPermission([Permission.API_DELETE, Permission.ADMIN_WRITE])
      ).toBe(false);
    });

    it('should check if user has all required permissions', () => {
      const { result } = renderHook(() => useAuthStore());

      expect(
        result.current.hasAllPermissions([Permission.API_READ, Permission.API_WRITE])
      ).toBe(true);

      expect(
        result.current.hasAllPermissions([Permission.API_READ, Permission.API_DELETE])
      ).toBe(false);
    });
  });

  describe('Activity Tracking', () => {
    it('should update last activity', () => {
      const { result } = renderHook(() => useAuthStore());

      const initialTime = new Date(2023, 0, 1);
      act(() => {
        useAuthStore.setState({ lastActivity: initialTime });
      });

      act(() => {
        result.current.updateLastActivity();
      });

      expect(result.current.lastActivity.getTime()).toBeGreaterThan(initialTime.getTime());
    });
  });
});