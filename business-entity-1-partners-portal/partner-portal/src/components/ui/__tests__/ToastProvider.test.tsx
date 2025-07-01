import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { ToastProvider, useErrorToast, useSuccessToast, useToast } from '../ToastProvider';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
    custom: jest.fn(),
    dismiss: jest.fn(),
  },
  Toaster: jest.fn(() => <div data-testid="toaster" />),
}));

// Test component that uses the toast hooks
const TestComponent = () => {
  const showError = useErrorToast();
  const showSuccess = useSuccessToast();
  const toast = useToast();

  return (
    <div>
      <button 
        onClick={() => showError('Error title', 'Error message')}
        data-testid="error-button"
      >
        Show Error
      </button>
      <button 
        onClick={() => showSuccess('Success title', 'Success message')}
        data-testid="success-button"
      >
        Show Success
      </button>
      <button 
        onClick={() => toast.error('Simple error')}
        data-testid="simple-error-button"
      >
        Simple Error
      </button>
      <button 
        onClick={() => toast.success('Simple success')}
        data-testid="simple-success-button"
      >
        Simple Success
      </button>
      <button 
        onClick={() => toast.dismiss()}
        data-testid="dismiss-button"
      >
        Dismiss All
      </button>
    </div>
  );
};

const TestComponentWithProvider = () => (
  <ToastProvider>
    <TestComponent />
  </ToastProvider>
);

describe('ToastProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Provider Rendering', () => {
    it('should render children correctly', () => {
      render(
        <ToastProvider>
          <div data-testid="child">Test child</div>
        </ToastProvider>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
      expect(screen.getByText('Test child')).toBeInTheDocument();
    });

    it('should render Toaster component', () => {
      render(
        <ToastProvider>
          <div>Test content</div>
        </ToastProvider>
      );

      expect(screen.getByTestId('toaster')).toBeInTheDocument();
    });

    it('should provide toast context to children', () => {
      const { container } = render(<TestComponentWithProvider />);

      expect(container).toBeInTheDocument();
      expect(screen.getByTestId('error-button')).toBeInTheDocument();
      expect(screen.getByTestId('success-button')).toBeInTheDocument();
    });
  });

  describe('useErrorToast Hook', () => {
    it('should show error toast with title and message', () => {
      const toast = require('react-hot-toast');
      render(<TestComponentWithProvider />);

      const errorButton = screen.getByTestId('error-button');
      act(() => {
        errorButton.click();
      });

      expect(toast.toast.error).toHaveBeenCalledWith(
        expect.stringContaining('Error title'),
        expect.objectContaining({
          duration: 5000,
          style: expect.objectContaining({
            borderRadius: '8px',
            background: '#FEF2F2',
            color: '#991B1B',
            border: '1px solid #FECACA',
          }),
        })
      );
    });

    it('should show error toast with only title when message is not provided', () => {
      const toast = require('react-hot-toast');
      
      const SingleParamTestComponent = () => {
        const showError = useErrorToast();
        return (
          <button 
            onClick={() => showError('Just title')}
            data-testid="single-param-error"
          >
            Single Param Error
          </button>
        );
      };

      render(
        <ToastProvider>
          <SingleParamTestComponent />
        </ToastProvider>
      );

      const button = screen.getByTestId('single-param-error');
      act(() => {
        button.click();
      });

      expect(toast.toast.error).toHaveBeenCalledWith(
        'Just title',
        expect.objectContaining({
          duration: 5000,
          style: expect.any(Object),
        })
      );
    });

    it('should apply correct error styling', () => {
      const toast = require('react-hot-toast');
      render(<TestComponentWithProvider />);

      const errorButton = screen.getByTestId('error-button');
      act(() => {
        errorButton.click();
      });

      const callArgs = toast.toast.error.mock.calls[0];
      const options = callArgs[1];

      expect(options.style).toEqual({
        borderRadius: '8px',
        background: '#FEF2F2',
        color: '#991B1B',
        border: '1px solid #FECACA',
        fontSize: '14px',
        fontWeight: 500,
      });
    });
  });

  describe('useSuccessToast Hook', () => {
    it('should show success toast with title and message', () => {
      const toast = require('react-hot-toast');
      render(<TestComponentWithProvider />);

      const successButton = screen.getByTestId('success-button');
      act(() => {
        successButton.click();
      });

      expect(toast.toast.success).toHaveBeenCalledWith(
        expect.stringContaining('Success title'),
        expect.objectContaining({
          duration: 4000,
          style: expect.objectContaining({
            borderRadius: '8px',
            background: '#F0FDF4',
            color: '#166534',
            border: '1px solid #BBF7D0',
          }),
        })
      );
    });

    it('should show success toast with only title when message is not provided', () => {
      const toast = require('react-hot-toast');
      
      const SingleParamTestComponent = () => {
        const showSuccess = useSuccessToast();
        return (
          <button 
            onClick={() => showSuccess('Just title')}
            data-testid="single-param-success"
          >
            Single Param Success
          </button>
        );
      };

      render(
        <ToastProvider>
          <SingleParamTestComponent />
        </ToastProvider>
      );

      const button = screen.getByTestId('single-param-success');
      act(() => {
        button.click();
      });

      expect(toast.toast.success).toHaveBeenCalledWith(
        'Just title',
        expect.objectContaining({
          duration: 4000,
          style: expect.any(Object),
        })
      );
    });

    it('should apply correct success styling', () => {
      const toast = require('react-hot-toast');
      render(<TestComponentWithProvider />);

      const successButton = screen.getByTestId('success-button');
      act(() => {
        successButton.click();
      });

      const callArgs = toast.toast.success.mock.calls[0];
      const options = callArgs[1];

      expect(options.style).toEqual({
        borderRadius: '8px',
        background: '#F0FDF4',
        color: '#166534',
        border: '1px solid #BBF7D0',
        fontSize: '14px',
        fontWeight: 500,
      });
    });
  });

  describe('useToast Hook', () => {
    it('should provide access to basic toast methods', () => {
      const toast = require('react-hot-toast');
      render(<TestComponentWithProvider />);

      const simpleErrorButton = screen.getByTestId('simple-error-button');
      const simpleSuccessButton = screen.getByTestId('simple-success-button');
      const dismissButton = screen.getByTestId('dismiss-button');

      act(() => {
        simpleErrorButton.click();
      });

      expect(toast.toast.error).toHaveBeenCalledWith('Simple error');

      act(() => {
        simpleSuccessButton.click();
      });

      expect(toast.toast.success).toHaveBeenCalledWith('Simple success');

      act(() => {
        dismissButton.click();
      });

      expect(toast.toast.dismiss).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should handle hooks being called outside of provider', () => {
      const TestComponentWithoutProvider = () => {
        try {
          const showError = useErrorToast();
          return (
            <button 
              onClick={() => showError('Test')}
              data-testid="outside-provider"
            >
              Outside Provider
            </button>
          );
        } catch (error) {
          return <div data-testid="error">Error: Hook used outside provider</div>;
        }
      };

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => render(<TestComponentWithoutProvider />)).toThrow();

      consoleSpy.mockRestore();
    });

    it('should handle empty string parameters gracefully', () => {
      const toast = require('react-hot-toast');
      
      const EmptyStringTestComponent = () => {
        const showError = useErrorToast();
        const showSuccess = useSuccessToast();
        
        return (
          <div>
            <button 
              onClick={() => showError('', '')}
              data-testid="empty-error"
            >
              Empty Error
            </button>
            <button 
              onClick={() => showSuccess('', '')}
              data-testid="empty-success"
            >
              Empty Success
            </button>
          </div>
        );
      };

      render(
        <ToastProvider>
          <EmptyStringTestComponent />
        </ToastProvider>
      );

      const emptyErrorButton = screen.getByTestId('empty-error');
      const emptySuccessButton = screen.getByTestId('empty-success');

      act(() => {
        emptyErrorButton.click();
      });

      act(() => {
        emptySuccessButton.click();
      });

      expect(toast.toast.error).toHaveBeenCalled();
      expect(toast.toast.success).toHaveBeenCalled();
    });
  });

  describe('Toast Content Formatting', () => {
    it('should format multi-line content correctly for error toasts', () => {
      const toast = require('react-hot-toast');
      
      const MultiLineTestComponent = () => {
        const showError = useErrorToast();
        return (
          <button 
            onClick={() => showError('Error Title', 'Line 1\nLine 2\nLine 3')}
            data-testid="multiline-error"
          >
            Multiline Error
          </button>
        );
      };

      render(
        <ToastProvider>
          <MultiLineTestComponent />
        </ToastProvider>
      );

      const button = screen.getByTestId('multiline-error');
      act(() => {
        button.click();
      });

      expect(toast.toast.error).toHaveBeenCalledWith(
        expect.stringContaining('Error Title'),
        expect.any(Object)
      );
    });

    it('should handle special characters in toast content', () => {
      const toast = require('react-hot-toast');
      
      const SpecialCharsTestComponent = () => {
        const showError = useErrorToast();
        return (
          <button 
            onClick={() => showError('Special: <>&"\'', 'Message with "quotes" & <tags>')}
            data-testid="special-chars"
          >
            Special Characters
          </button>
        );
      };

      render(
        <ToastProvider>
          <SpecialCharsTestComponent />
        </ToastProvider>
      );

      const button = screen.getByTestId('special-chars');
      act(() => {
        button.click();
      });

      expect(toast.toast.error).toHaveBeenCalled();
    });
  });

  describe('Performance and Memory', () => {
    it('should not create new functions on every render', () => {
      let renderCount = 0;
      const renders: any[] = [];

      const PerformanceTestComponent = () => {
        renderCount++;
        const showError = useErrorToast();
        const showSuccess = useSuccessToast();
        const toast = useToast();
        
        renders.push({ showError, showSuccess, toast });
        
        return <div data-testid={`render-${renderCount}`}>Render {renderCount}</div>;
      };

      const { rerender } = render(
        <ToastProvider>
          <PerformanceTestComponent />
        </ToastProvider>
      );

      rerender(
        <ToastProvider>
          <PerformanceTestComponent />
        </ToastProvider>
      );

      expect(renderCount).toBe(2);
      // Functions should be stable across renders
      expect(renders[0].showError).toBe(renders[1].showError);
      expect(renders[0].showSuccess).toBe(renders[1].showSuccess);
      expect(renders[0].toast).toBe(renders[1].toast);
    });
  });

  describe('Multiple Provider Instances', () => {
    it('should handle multiple provider instances independently', () => {
      const Provider1TestComponent = () => {
        const showError = useErrorToast();
        return (
          <button 
            onClick={() => showError('Provider 1 Error')}
            data-testid="provider1-button"
          >
            Provider 1
          </button>
        );
      };

      const Provider2TestComponent = () => {
        const showError = useErrorToast();
        return (
          <button 
            onClick={() => showError('Provider 2 Error')}
            data-testid="provider2-button"
          >
            Provider 2
          </button>
        );
      };

      render(
        <div>
          <ToastProvider>
            <Provider1TestComponent />
          </ToastProvider>
          <ToastProvider>
            <Provider2TestComponent />
          </ToastProvider>
        </div>
      );

      expect(screen.getByTestId('provider1-button')).toBeInTheDocument();
      expect(screen.getByTestId('provider2-button')).toBeInTheDocument();
    });
  });
});