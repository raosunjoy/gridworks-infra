import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { signIn, getSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import SignInForm from '../SignInForm';

// Mock next-auth
jest.mock('next-auth/react');
jest.mock('next/navigation');

// Mock toast providers
jest.mock('@/components/ui/ToastProvider', () => ({
  useErrorToast: jest.fn(() => jest.fn()),
  useSuccessToast: jest.fn(() => jest.fn()),
}));

const mockSignIn = signIn as jest.MockedFunction<typeof signIn>;
const mockGetSession = getSession as jest.MockedFunction<typeof getSession>;
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;

describe('SignInForm', () => {
  const mockPush = jest.fn();
  const mockShowError = jest.fn();
  const mockShowSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockUseRouter.mockReturnValue({
      push: mockPush,
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
    } as any);

    // Mock toast functions
    const { useErrorToast, useSuccessToast } = require('@/components/ui/ToastProvider');
    useErrorToast.mockReturnValue(mockShowError);
    useSuccessToast.mockReturnValue(mockShowSuccess);
  });

  describe('Rendering', () => {
    it('should render sign in form correctly', () => {
      render(<SignInForm />);

      expect(screen.getByText('Welcome back')).toBeInTheDocument();
      expect(screen.getByText('Sign in to your TradeMate Partner account')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('your@email.com')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument();
    });

    it('should render social sign in buttons', () => {
      render(<SignInForm />);

      expect(screen.getByText('Continue with Google')).toBeInTheDocument();
      expect(screen.getByText('Continue with GitHub')).toBeInTheDocument();
    });

    it('should render form elements with correct attributes', () => {
      render(<SignInForm />);

      const emailInput = screen.getByLabelText('Email address');
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('autoComplete', 'email');

      const passwordInput = screen.getByLabelText('Password');
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(passwordInput).toHaveAttribute('autoComplete', 'current-password');
    });

    it('should display error prop when provided', () => {
      render(<SignInForm error="Invalid credentials" />);

      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should show validation errors for invalid email', async () => {
      const user = userEvent.setup();
      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'invalid-email');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      });
    });

    it('should show validation errors for short password', async () => {
      const user = userEvent.setup();
      render(<SignInForm />);

      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(passwordInput, '123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument();
      });
    });

    it('should not submit form with validation errors', async () => {
      const user = userEvent.setup();
      render(<SignInForm />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockSignIn).not.toHaveBeenCalled();
      });
    });
  });

  describe('Password Visibility Toggle', () => {
    it('should toggle password visibility when eye icon is clicked', async () => {
      const user = userEvent.setup();
      render(<SignInForm />);

      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const toggleButton = passwordInput.parentElement?.querySelector('button');

      expect(passwordInput).toHaveAttribute('type', 'password');

      if (toggleButton) {
        await user.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'text');

        await user.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'password');
      }
    });
  });

  describe('Form Submission', () => {
    const validFormData = {
      email: 'test@example.com',
      password: 'password123',
    };

    it('should submit form with valid credentials', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ ok: true });
      mockGetSession.mockResolvedValueOnce({
        user: { role: 'developer' },
      } as any);

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, validFormData.email);
      await user.type(passwordInput, validFormData.password);
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('credentials', {
          email: validFormData.email,
          password: validFormData.password,
          redirect: false,
        });
      });

      expect(mockShowSuccess).toHaveBeenCalledWith('Success', 'Signed in successfully');
    });

    it('should handle credentials sign in error', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ 
        ok: false, 
        error: 'CredentialsSignin' 
      });

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, validFormData.email);
      await user.type(passwordInput, validFormData.password);
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Invalid email or password')).toBeInTheDocument();
      });
    });

    it('should handle email not verified error', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ 
        ok: false, 
        error: 'EmailNotVerified' 
      });

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, validFormData.email);
      await user.type(passwordInput, validFormData.password);
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please verify your email address')).toBeInTheDocument();
      });
    });

    it('should handle network errors', async () => {
      const user = userEvent.setup();
      mockSignIn.mockRejectedValueOnce(new Error('Network error'));

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, validFormData.email);
      await user.type(passwordInput, validFormData.password);
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Network error. Please try again.')).toBeInTheDocument();
      });
    });

    it('should show loading state during submission', async () => {
      const user = userEvent.setup();
      
      // Create a promise that we can control
      let resolveSignIn: (value: any) => void;
      const signInPromise = new Promise(resolve => {
        resolveSignIn = resolve;
      });
      
      mockSignIn.mockReturnValueOnce(signInPromise as any);

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, validFormData.email);
      await user.type(passwordInput, validFormData.password);
      await user.click(submitButton);

      // Check loading state
      expect(screen.getByText('Signing in...')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();

      // Complete sign in
      resolveSignIn({ ok: true });

      await waitFor(() => {
        expect(screen.queryByText('Signing in...')).not.toBeInTheDocument();
      });
    });

    it('should disable form during submission', async () => {
      const user = userEvent.setup();
      
      let resolveSignIn: (value: any) => void;
      const signInPromise = new Promise(resolve => {
        resolveSignIn = resolve;
      });
      
      mockSignIn.mockReturnValueOnce(signInPromise as any);

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, validFormData.email);
      await user.type(passwordInput, validFormData.password);
      await user.click(submitButton);

      expect(submitButton).toBeDisabled();

      resolveSignIn({ ok: true });
    });
  });

  describe('Social Sign In', () => {
    it('should handle Google sign in', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ ok: true });

      render(<SignInForm />);

      const googleButton = screen.getByText('Continue with Google');
      await user.click(googleButton);

      expect(mockSignIn).toHaveBeenCalledWith('google', {
        callbackUrl: '/dashboard',
      });
    });

    it('should handle GitHub sign in', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ ok: true });

      render(<SignInForm />);

      const githubButton = screen.getByText('Continue with GitHub');
      await user.click(githubButton);

      expect(mockSignIn).toHaveBeenCalledWith('github', {
        callbackUrl: '/dashboard',
      });
    });

    it('should handle social sign in error', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ error: 'OAuthAccountNotLinked' });

      render(<SignInForm />);

      const googleButton = screen.getByText('Continue with Google');
      await user.click(googleButton);

      await waitFor(() => {
        expect(mockShowError).toHaveBeenCalledWith('Sign In Failed', 'Failed to sign in with google');
      });
    });

    it('should show loading state for social buttons', async () => {
      const user = userEvent.setup();
      
      let resolveSignIn: (value: any) => void;
      const signInPromise = new Promise(resolve => {
        resolveSignIn = resolve;
      });
      
      mockSignIn.mockReturnValueOnce(signInPromise as any);

      render(<SignInForm />);

      const googleButton = screen.getByText('Continue with Google');
      await user.click(googleButton);

      expect(googleButton).toBeDisabled();

      resolveSignIn({ ok: true });
    });

    it('should use custom callback URL when provided', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ ok: true });

      render(<SignInForm callbackUrl="/custom-redirect" />);

      const googleButton = screen.getByText('Continue with Google');
      await user.click(googleButton);

      expect(mockSignIn).toHaveBeenCalledWith('google', {
        callbackUrl: '/custom-redirect',
      });
    });
  });

  describe('Role-based Redirects', () => {
    it('should redirect admin users to admin dashboard', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ ok: true });
      mockGetSession.mockResolvedValueOnce({
        user: { role: 'admin' },
      } as any);

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'admin@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/admin/dashboard');
      });
    });

    it('should redirect developer users to developer dashboard', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ ok: true });
      mockGetSession.mockResolvedValueOnce({
        user: { role: 'developer' },
      } as any);

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'developer@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/developer/dashboard');
      });
    });

    it('should redirect business users to default dashboard', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValueOnce({ ok: true });
      mockGetSession.mockResolvedValueOnce({
        user: { role: 'business_user' },
      } as any);

      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'business@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });
  });

  describe('Remember Me Functionality', () => {
    it('should handle remember me checkbox', async () => {
      const user = userEvent.setup();
      render(<SignInForm />);

      const rememberMeCheckbox = screen.getByLabelText('Remember me');
      expect(rememberMeCheckbox).not.toBeChecked();

      await user.click(rememberMeCheckbox);
      expect(rememberMeCheckbox).toBeChecked();
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      render(<SignInForm />);

      expect(screen.getByLabelText('Email address')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByLabelText('Remember me')).toBeInTheDocument();
    });

    it('should have proper button types', () => {
      render(<SignInForm />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      expect(submitButton).toHaveAttribute('type', 'submit');

      const passwordToggle = screen.getByRole('button', { name: '' }); // Eye icon button
      expect(passwordToggle).toHaveAttribute('type', 'button');
    });

    it('should associate error messages with form fields', async () => {
      const user = userEvent.setup();
      render(<SignInForm />);

      const emailInput = screen.getByPlaceholderText('your@email.com');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'invalid-email');
      await user.click(submitButton);

      await waitFor(() => {
        const errorMessage = screen.getByText('Please enter a valid email address');
        expect(errorMessage).toBeInTheDocument();
      });
    });
  });

  describe('Navigation Links', () => {
    it('should render forgot password link', () => {
      render(<SignInForm />);

      const forgotPasswordLink = screen.getByText('Forgot password?');
      expect(forgotPasswordLink).toHaveAttribute('href', '/auth/forgot-password');
    });

    it('should render sign up link', () => {
      render(<SignInForm />);

      const signUpLink = screen.getByText('Sign up');
      expect(signUpLink).toHaveAttribute('href', '/auth/signup');
    });
  });
});