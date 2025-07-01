import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { signIn } from 'next-auth/react';
import SignUpPage from '../signup/page';
import { apiClient } from '@/lib/react-query';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock NextAuth
jest.mock('next-auth/react', () => ({
  signIn: jest.fn(),
}));

// Mock API client
jest.mock('@/lib/react-query', () => ({
  apiClient: {
    post: jest.fn(),
  },
}));

const mockPush = jest.fn();
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;
const mockSignIn = signIn as jest.MockedFunction<typeof signIn>;
const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('SignUpPage', () => {
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
  });

  describe('Rendering', () => {
    it('should render sign up form correctly', () => {
      render(<SignUpPage />);

      expect(screen.getByText('TradeMate')).toBeInTheDocument();
      expect(screen.getByText('Create your account')).toBeInTheDocument();
      expect(screen.getByText('Join the TradeMate partner ecosystem')).toBeInTheDocument();
      expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Email address')).toBeInTheDocument();
      expect(screen.getByLabelText('Company Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
    });

    it('should render social sign up buttons', () => {
      render(<SignUpPage />);

      expect(screen.getByRole('button', { name: /google/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /github/i })).toBeInTheDocument();
    });

    it('should render terms agreement checkbox', () => {
      render(<SignUpPage />);

      expect(screen.getByText(/I agree to the/)).toBeInTheDocument();
      expect(screen.getByText('Terms of Service')).toBeInTheDocument();
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    });
  });

  describe('Form Interactions', () => {
    it('should handle input changes', () => {
      render(<SignUpPage />);

      const nameInput = screen.getByLabelText('Full Name') as HTMLInputElement;
      const emailInput = screen.getByLabelText('Email address') as HTMLInputElement;
      const companyInput = screen.getByLabelText('Company Name') as HTMLInputElement;
      const passwordInput = screen.getByLabelText('Password') as HTMLInputElement;
      const confirmPasswordInput = screen.getByLabelText('Confirm Password') as HTMLInputElement;

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(companyInput, { target: { value: 'Test Company' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'StrongPassword123!' } });

      expect(nameInput.value).toBe('John Doe');
      expect(emailInput.value).toBe('john@example.com');
      expect(companyInput.value).toBe('Test Company');
      expect(passwordInput.value).toBe('StrongPassword123!');
      expect(confirmPasswordInput.value).toBe('StrongPassword123!');
    });

    it('should toggle password visibility', () => {
      render(<SignUpPage />);

      const passwordInput = screen.getByLabelText('Password') as HTMLInputElement;
      const confirmPasswordInput = screen.getByLabelText('Confirm Password') as HTMLInputElement;
      const toggleButtons = screen.getAllByRole('button', { name: '' }); // Eye icon buttons

      expect(passwordInput.type).toBe('password');
      expect(confirmPasswordInput.type).toBe('password');

      fireEvent.click(toggleButtons[0]); // Toggle password field
      expect(passwordInput.type).toBe('text');

      fireEvent.click(toggleButtons[1]); // Toggle confirm password field
      expect(confirmPasswordInput.type).toBe('text');
    });

    it('should handle terms agreement checkbox', () => {
      render(<SignUpPage />);

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      const submitButton = screen.getByRole('button', { name: /create account/i });

      expect(checkbox.checked).toBe(false);
      expect(submitButton).toBeDisabled();

      fireEvent.click(checkbox);
      expect(checkbox.checked).toBe(true);
      expect(submitButton).not.toBeDisabled();
    });
  });

  describe('Password Strength Validation', () => {
    it('should show password strength indicator', () => {
      render(<SignUpPage />);

      const passwordInput = screen.getByLabelText('Password');
      
      fireEvent.change(passwordInput, { target: { value: 'weak' } });
      expect(screen.getByText('Weak')).toBeInTheDocument();

      fireEvent.change(passwordInput, { target: { value: 'StrongPassword123!' } });
      expect(screen.getByText('Strong')).toBeInTheDocument();
    });

    it('should show password match indicator', () => {
      render(<SignUpPage />);

      const passwordInput = screen.getByLabelText('Password');
      const confirmPasswordInput = screen.getByLabelText('Confirm Password');
      
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      
      expect(screen.getByText('Passwords match')).toBeInTheDocument();

      fireEvent.change(confirmPasswordInput, { target: { value: 'different' } });
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should show error when passwords do not match', async () => {
      render(<SignUpPage />);

      const passwordInput = screen.getByLabelText('Password');
      const confirmPasswordInput = screen.getByLabelText('Confirm Password');
      const checkbox = screen.getByRole('checkbox');
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'different' } });
      fireEvent.click(checkbox);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match.')).toBeInTheDocument();
      });
    });

    it('should show error when password is too weak', async () => {
      render(<SignUpPage />);

      const passwordInput = screen.getByLabelText('Password');
      const confirmPasswordInput = screen.getByLabelText('Confirm Password');
      const checkbox = screen.getByRole('checkbox');
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(passwordInput, { target: { value: 'weak' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'weak' } });
      fireEvent.click(checkbox);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please choose a stronger password.')).toBeInTheDocument();
      });
    });

    it('should show error when terms are not agreed', async () => {
      render(<SignUpPage />);

      const submitButton = screen.getByRole('button', { name: /create account/i });

      // Submit without agreeing to terms
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please agree to the Terms of Service and Privacy Policy.')).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    const fillValidForm = () => {
      const nameInput = screen.getByLabelText('Full Name');
      const emailInput = screen.getByLabelText('Email address');
      const companyInput = screen.getByLabelText('Company Name');
      const passwordInput = screen.getByLabelText('Password');
      const confirmPasswordInput = screen.getByLabelText('Confirm Password');
      const checkbox = screen.getByRole('checkbox');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(companyInput, { target: { value: 'Test Company' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'StrongPassword123!' } });
      fireEvent.click(checkbox);
    };

    it('should submit form and auto sign in on success', async () => {
      mockApiClient.post.mockResolvedValueOnce({ success: true });
      mockSignIn.mockResolvedValueOnce({ error: null } as any);

      render(<SignUpPage />);
      fillValidForm();

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockApiClient.post).toHaveBeenCalledWith('/auth/register', {
          name: 'John Doe',
          email: 'john@example.com',
          password: 'StrongPassword123!',
          companyName: 'Test Company',
        });
      });

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('credentials', {
          email: 'john@example.com',
          password: 'StrongPassword123!',
          redirect: false,
        });
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should handle registration failure', async () => {
      mockApiClient.post.mockResolvedValueOnce({ 
        success: false, 
        message: 'Email already exists' 
      });

      render(<SignUpPage />);
      fillValidForm();

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeInTheDocument();
      });
    });

    it('should handle auto sign in failure after successful registration', async () => {
      mockApiClient.post.mockResolvedValueOnce({ success: true });
      mockSignIn.mockResolvedValueOnce({ error: 'SignInError' } as any);

      render(<SignUpPage />);
      fillValidForm();

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Account created but sign in failed/)).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/auth/signin');
      });
    });

    it('should disable form during submission', async () => {
      mockApiClient.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      render(<SignUpPage />);
      fillValidForm();

      const submitButton = screen.getByRole('button', { name: /create account/i });
      fireEvent.click(submitButton);

      expect(submitButton).toBeDisabled();
    });
  });

  describe('Social Sign Up', () => {
    it('should handle Google sign up', async () => {
      mockSignIn.mockResolvedValueOnce(undefined);

      render(<SignUpPage />);

      const googleButton = screen.getByRole('button', { name: /google/i });
      fireEvent.click(googleButton);

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('google', { callbackUrl: '/dashboard' });
      });
    });

    it('should handle GitHub sign up', async () => {
      mockSignIn.mockResolvedValueOnce(undefined);

      render(<SignUpPage />);

      const githubButton = screen.getByRole('button', { name: /github/i });
      fireEvent.click(githubButton);

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('github', { callbackUrl: '/dashboard' });
      });
    });

    it('should handle social sign up errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      mockSignIn.mockRejectedValueOnce(new Error('OAuth failed'));

      render(<SignUpPage />);

      const googleButton = screen.getByRole('button', { name: /google/i });
      fireEvent.click(googleButton);

      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith('google sign up error:', expect.any(Error));
      });

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels and structure', () => {
      render(<SignUpPage />);

      expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Email address')).toBeInTheDocument();
      expect(screen.getByLabelText('Company Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
    });

    it('should have proper ARIA attributes for form validation', () => {
      render(<SignUpPage />);

      const inputs = [
        screen.getByLabelText('Full Name'),
        screen.getByLabelText('Email address'),
        screen.getByLabelText('Company Name'),
        screen.getByLabelText('Password'),
        screen.getByLabelText('Confirm Password'),
      ];

      inputs.forEach(input => {
        expect(input).toHaveAttribute('required');
      });

      expect(screen.getByLabelText('Email address')).toHaveAttribute('type', 'email');
    });
  });

  describe('Navigation', () => {
    it('should handle navigation to sign in page', () => {
      render(<SignUpPage />);

      const signInLink = screen.getByText('Sign in');
      expect(signInLink.closest('a')).toHaveAttribute('href', '/auth/signin');
    });

    it('should handle navigation to terms and privacy pages', () => {
      render(<SignUpPage />);

      const termsLink = screen.getByText('Terms of Service');
      const privacyLink = screen.getByText('Privacy Policy');
      
      expect(termsLink.closest('a')).toHaveAttribute('href', '/terms');
      expect(privacyLink.closest('a')).toHaveAttribute('href', '/privacy');
    });
  });
});