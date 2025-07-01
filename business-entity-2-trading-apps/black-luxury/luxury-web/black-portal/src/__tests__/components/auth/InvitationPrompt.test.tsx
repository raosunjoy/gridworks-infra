import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { InvitationPrompt } from '../../../components/auth/InvitationPrompt';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    input: ({ children, ...props }: any) => <input {...props}>{children}</input>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Shield: () => <div data-testid="shield-icon">Shield</div>,
  Eye: () => <div data-testid="eye-icon">Eye</div>,
  EyeOff: () => <div data-testid="eye-off-icon">EyeOff</div>,
  Sparkles: () => <div data-testid="sparkles-icon">Sparkles</div>,
  Crown: () => <div data-testid="crown-icon">Crown</div>,
  Zap: () => <div data-testid="zap-icon">Zap</div>,
  Fingerprint: () => <div data-testid="fingerprint-icon">Fingerprint</div>,
  Lock: () => <div data-testid="lock-icon">Lock</div>,
}));

// Mock audio
global.Audio = jest.fn().mockImplementation(() => ({
  play: jest.fn(),
  pause: jest.fn(),
  load: jest.fn(),
}));

describe('InvitationPrompt Component', () => {
  const mockOnValidCode = jest.fn();
  const mockOnInvalidAttempt = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  const renderInvitationPrompt = (props = {}) => {
    const defaultProps = {
      onValidCode: mockOnValidCode,
      onInvalidAttempt: mockOnInvalidAttempt,
    };
    return render(<InvitationPrompt {...defaultProps} {...props} />);
  };

  describe('Rendering', () => {
    test('renders invitation prompt with correct title', () => {
      renderInvitationPrompt();
      expect(screen.getByText('Exclusive Access Required')).toBeInTheDocument();
    });

    test('renders invitation code input field', () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'password');
    });

    test('renders verify access button', () => {
      renderInvitationPrompt();
      expect(screen.getByText('Verify Access')).toBeInTheDocument();
    });

    test('displays security features', () => {
      renderInvitationPrompt();
      expect(screen.getByText('Quantum-Level Security')).toBeInTheDocument();
      expect(screen.getByText('Biometric Verification')).toBeInTheDocument();
      expect(screen.getByText('Device Fingerprinting')).toBeInTheDocument();
    });

    test('renders all required icons', () => {
      renderInvitationPrompt();
      expect(screen.getByTestId('shield-icon')).toBeInTheDocument();
      expect(screen.getByTestId('eye-off-icon')).toBeInTheDocument();
      expect(screen.getByTestId('sparkles-icon')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    test('toggles password visibility when eye icon is clicked', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const toggleButton = screen.getByRole('button', { name: /toggle/i });

      // Initially password type
      expect(input).toHaveAttribute('type', 'password');

      // Click to show password
      fireEvent.click(toggleButton);
      expect(input).toHaveAttribute('type', 'text');

      // Click to hide password
      fireEvent.click(toggleButton);
      expect(input).toHaveAttribute('type', 'password');
    });

    test('updates input value when typing', () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      
      fireEvent.change(input, { target: { value: 'TEST123' } });
      expect(input).toHaveValue('TEST123');
    });

    test('enables verify button when code is entered', () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      // Initially disabled
      expect(button).toBeDisabled();

      // Enter code
      fireEvent.change(input, { target: { value: 'TEST123' } });
      expect(button).not.toBeDisabled();
    });
  });

  describe('Code Validation', () => {
    test('calls onValidCode with correct tier for VOID_ACCESS code', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: 'VOID_ACCESS' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnValidCode).toHaveBeenCalledWith('void');
      });
    });

    test('calls onValidCode with correct tier for OBSIDIAN_ELITE code', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: 'OBSIDIAN_ELITE' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnValidCode).toHaveBeenCalledWith('obsidian');
      });
    });

    test('calls onValidCode with correct tier for ONYX_PREMIUM code', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: 'ONYX_PREMIUM' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnValidCode).toHaveBeenCalledWith('onyx');
      });
    });

    test('calls onInvalidAttempt for invalid code', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: 'INVALID_CODE' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnInvalidAttempt).toHaveBeenCalled();
      });
    });

    test('shows error message for invalid code', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: 'INVALID_CODE' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Invalid invitation code. Access denied.')).toBeInTheDocument();
      });
    });

    test('clears error message when typing new code', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      // Enter invalid code
      fireEvent.change(input, { target: { value: 'INVALID_CODE' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Invalid invitation code. Access denied.')).toBeInTheDocument();
      });

      // Start typing new code
      fireEvent.change(input, { target: { value: 'V' } });
      expect(screen.queryByText('Invalid invitation code. Access denied.')).not.toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    test('shows verifying state when validating code', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: 'VOID_ACCESS' } });
      fireEvent.click(button);

      // Should show verifying state briefly
      expect(screen.getByText('Verifying...')).toBeInTheDocument();
    });

    test('disables input and button during verification', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: 'VOID_ACCESS' } });
      fireEvent.click(button);

      expect(input).toBeDisabled();
      expect(button).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels', () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      expect(input).toHaveAttribute('aria-label', 'Invitation code input');
    });

    test('supports keyboard navigation', () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      // Tab to input
      input.focus();
      expect(input).toHaveFocus();

      // Enter to submit
      fireEvent.change(input, { target: { value: 'VOID_ACCESS' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
      
      expect(mockOnValidCode).toHaveBeenCalledWith('void');
    });
  });

  describe('Security Features Display', () => {
    test('renders security features with correct styling', () => {
      renderInvitationPrompt();
      
      const securitySection = screen.getByText('Security Features').closest('div');
      expect(securitySection).toBeInTheDocument();
      
      expect(screen.getByText('Quantum-Level Security')).toBeInTheDocument();
      expect(screen.getByText('Military-grade encryption')).toBeInTheDocument();
      expect(screen.getByText('Biometric Verification')).toBeInTheDocument();
      expect(screen.getByText('Face & fingerprint auth')).toBeInTheDocument();
    });

    test('renders luxury features section', () => {
      renderInvitationPrompt();
      
      expect(screen.getByText('Exclusive Features')).toBeInTheDocument();
      expect(screen.getByText('Butler AI Assistant')).toBeInTheDocument();
      expect(screen.getByText('Emergency Services')).toBeInTheDocument();
      expect(screen.getByText('Private Banking')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('handles empty code submission', async () => {
      renderInvitationPrompt();
      const button = screen.getByText('Verify Access');

      // Button should be disabled for empty input
      expect(button).toBeDisabled();
    });

    test('handles whitespace-only code', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: '   ' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnInvalidAttempt).toHaveBeenCalled();
      });
    });

    test('handles case sensitivity in codes', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      // Test lowercase version of valid code
      fireEvent.change(input, { target: { value: 'void_access' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnValidCode).toHaveBeenCalledWith('void');
      });
    });

    test('handles multiple rapid submissions', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      fireEvent.change(input, { target: { value: 'VOID_ACCESS' } });
      
      // Rapid clicks should not cause multiple calls
      fireEvent.click(button);
      fireEvent.click(button);
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnValidCode).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Error Recovery', () => {
    test('allows retry after invalid attempt', async () => {
      renderInvitationPrompt();
      const input = screen.getByPlaceholderText('Enter your invitation code');
      const button = screen.getByText('Verify Access');

      // First invalid attempt
      fireEvent.change(input, { target: { value: 'INVALID' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnInvalidAttempt).toHaveBeenCalled();
      });

      // Clear and try valid code
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.change(input, { target: { value: 'VOID_ACCESS' } });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnValidCode).toHaveBeenCalledWith('void');
      });
    });
  });
});