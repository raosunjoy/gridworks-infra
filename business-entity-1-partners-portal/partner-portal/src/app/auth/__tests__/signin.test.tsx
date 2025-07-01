import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { signIn, getSession } from 'next-auth/react';
import SignInPage from '../signin/page';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock NextAuth
jest.mock('next-auth/react', () => ({
  signIn: jest.fn(),
  getSession: jest.fn(),
}));

const mockPush = jest.fn();
const mockGet = jest.fn();

const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;
const mockUseSearchParams = useSearchParams as jest.MockedFunction<typeof useSearchParams>;
const mockSignIn = signIn as jest.MockedFunction<typeof signIn>;
const mockGetSession = getSession as jest.MockedFunction<typeof getSession>;

describe('SignInPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    } as any);
    
    mockUseSearchParams.mockReturnValue({
      get: mockGet,
      getAll: jest.fn(),
      has: jest.fn(),
      keys: jest.fn(),
      values: jest.fn(),
      entries: jest.fn(),
      forEach: jest.fn(),
      toString: jest.fn(),
      size: 0,
      [Symbol.iterator]: jest.fn(),
    } as any);
    
    mockGet.mockImplementation((key) => {
      if (key === 'callbackUrl') return '/dashboard';
      if (key === 'error') return null;
      return null;
    });
  });

  describe('Rendering', () => {
    it('should render sign in form correctly', () => {
      render(<SignInPage />);

      expect(screen.getByText('TradeMate')).toBeInTheDocument();
      expect(screen.getByText('Welcome back')).toBeInTheDocument();
      expect(screen.getByText('Sign in to your partner account')).toBeInTheDocument();
      expect(screen.getByLabelText('Email address')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });

    it('should render social sign in buttons', () => {
      render(<SignInPage />);

      expect(screen.getByRole('button', { name: /google/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /github/i })).toBeInTheDocument();
    });

    it('should render navigation links', () => {
      render(<SignInPage />);

      expect(screen.getByText('Forgot password?')).toBeInTheDocument();
      expect(screen.getByText('Sign up for free')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when error param is present', () => {
      mockGet.mockImplementation((key) => {
        if (key === 'error') return 'CredentialsSignin';
        return null;
      });

      render(<SignInPage />);

      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });

    it('should display custom error messages for different error types', () => {
      mockGet.mockImplementation((key) => {
        if (key === 'error') return 'OAuthAccountNotLinked';
        return null;
      });

      render(<SignInPage />);

      expect(screen.getByText(/account not linked/i)).toBeInTheDocument();
    });

    it('should display form error when credentials sign in fails', async () => {
      mockSignIn.mockResolvedValueOnce({ error: 'CredentialsSignin' } as any);

      render(<SignInPage />);

      const emailInput = screen.getByLabelText('Email address');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Interactions', () => {
    it('should handle email and password input changes', () => {
      render(<SignInPage />);

      const emailInput = screen.getByLabelText('Email address') as HTMLInputElement;
      const passwordInput = screen.getByLabelText('Password') as HTMLInputElement;

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      expect(emailInput.value).toBe('test@example.com');
      expect(passwordInput.value).toBe('password123');
    });

    it('should toggle password visibility', () => {
      render(<SignInPage />);

      const passwordInput = screen.getByLabelText('Password') as HTMLInputElement;
      const toggleButton = screen.getByRole('button', { name: '' }); // Eye icon button

      expect(passwordInput.type).toBe('password');

      fireEvent.click(toggleButton);
      expect(passwordInput.type).toBe('text');

      fireEvent.click(toggleButton);
      expect(passwordInput.type).toBe('password');
    });
  });

  describe('Form Submission', () => {
    it('should submit form with credentials and redirect on success', async () => {
      mockSignIn.mockResolvedValueOnce({ error: null } as any);
      mockGetSession.mockResolvedValueOnce({ user: { email: 'test@example.com' } } as any);

      render(<SignInPage />);

      const emailInput = screen.getByLabelText('Email address');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('credentials', {
          email: 'test@example.com',
          password: 'password123',
          redirect: false,
        });
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should disable form during submission', async () => {
      mockSignIn.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      render(<SignInPage />);

      const emailInput = screen.getByLabelText('Email address');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      expect(submitButton).toBeDisabled();
      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
    });
  });

  describe('Social Sign In', () => {
    it('should handle Google sign in', async () => {
      mockSignIn.mockResolvedValueOnce(undefined);

      render(<SignInPage />);

      const googleButton = screen.getByRole('button', { name: /google/i });
      fireEvent.click(googleButton);

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('google', { callbackUrl: '/dashboard' });
      });
    });

    it('should handle GitHub sign in', async () => {
      mockSignIn.mockResolvedValueOnce(undefined);

      render(<SignInPage />);

      const githubButton = screen.getByRole('button', { name: /github/i });
      fireEvent.click(githubButton);

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('github', { callbackUrl: '/dashboard' });
      });
    });

    it('should handle social sign in errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      mockSignIn.mockRejectedValueOnce(new Error('OAuth failed'));

      render(<SignInPage />);

      const googleButton = screen.getByRole('button', { name: /google/i });
      fireEvent.click(googleButton);

      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith('google sign in error:', expect.any(Error));
      });

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels and structure', () => {
      render(<SignInPage />);

      expect(screen.getByLabelText('Email address')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    it('should have proper ARIA attributes for form validation', () => {
      render(<SignInPage />);

      const emailInput = screen.getByLabelText('Email address');
      const passwordInput = screen.getByLabelText('Password');

      expect(emailInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('required');
      expect(emailInput).toHaveAttribute('type', 'email');
    });
  });

  describe('Navigation', () => {
    it('should use custom callback URL when provided', () => {
      mockGet.mockImplementation((key) => {
        if (key === 'callbackUrl') return '/custom-redirect';
        return null;
      });

      render(<SignInPage />);

      const googleButton = screen.getByRole('button', { name: /google/i });
      fireEvent.click(googleButton);

      expect(mockSignIn).toHaveBeenCalledWith('google', { callbackUrl: '/custom-redirect' });
    });

    it('should handle navigation to forgot password page', () => {
      render(<SignInPage />);

      const forgotPasswordLink = screen.getByText('Forgot password?');
      expect(forgotPasswordLink.closest('a')).toHaveAttribute('href', '/auth/forgot-password');
    });

    it('should handle navigation to sign up page', () => {
      render(<SignInPage />);

      const signUpLink = screen.getByText('Sign up for free');
      expect(signUpLink.closest('a')).toHaveAttribute('href', '/auth/signup');
    });
  });
});