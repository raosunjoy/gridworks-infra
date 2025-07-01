import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary, { AsyncErrorBoundary, withErrorBoundary, useAsyncError } from '../ErrorBoundary';

// Test component that throws an error
const ThrowError = ({ shouldThrow = false, errorMessage = 'Test error' }) => {
  if (shouldThrow) {
    throw new Error(errorMessage);
  }
  return <div>No error</div>;
};

// Test component for async errors
const AsyncErrorComponent = () => {
  const throwAsyncError = useAsyncError();
  
  return (
    <button
      onClick={() => throwAsyncError(new Error('Async test error'))}
      data-testid="async-error-button"
    >
      Throw Async Error
    </button>
  );
};

describe('ErrorBoundary', () => {
  // Suppress console.error for these tests
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  afterAll(() => {
    console.error = originalError;
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Normal Operation', () => {
    it('should render children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div data-testid="child">Test content</div>
        </ErrorBoundary>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('should not interfere with normal component lifecycle', () => {
      const mockCallback = jest.fn();
      
      const TestComponent = () => {
        React.useEffect(() => {
          mockCallback();
        }, []);
        return <div data-testid="test-component">Test</div>;
      };

      render(
        <ErrorBoundary>
          <TestComponent />
        </ErrorBoundary>
      );

      expect(screen.getByTestId('test-component')).toBeInTheDocument();
      expect(mockCallback).toHaveBeenCalledTimes(1);
    });
  });

  describe('Error Handling', () => {
    it('should catch and display error fallback UI', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Test error message" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText('We apologize for the inconvenience. An unexpected error occurred.')).toBeInTheDocument();
    });

    it('should display error details when show details button is clicked', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Detailed error message" />
        </ErrorBoundary>
      );

      const showDetailsButton = screen.getByText('Show Error Details');
      fireEvent.click(showDetailsButton);

      expect(screen.getByText('Hide Error Details')).toBeInTheDocument();
      expect(screen.getByText('Detailed error message')).toBeInTheDocument();
    });

    it('should hide error details when hide details button is clicked', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Detailed error message" />
        </ErrorBoundary>
      );

      const showDetailsButton = screen.getByText('Show Error Details');
      fireEvent.click(showDetailsButton);
      
      const hideDetailsButton = screen.getByText('Hide Error Details');
      fireEvent.click(hideDetailsButton);

      expect(screen.getByText('Show Error Details')).toBeInTheDocument();
      expect(screen.queryByText('Detailed error message')).not.toBeInTheDocument();
    });

    it('should call custom onError handler when provided', () => {
      const mockOnError = jest.fn();

      render(
        <ErrorBoundary onError={mockOnError}>
          <ThrowError shouldThrow={true} errorMessage="Custom handler test" />
        </ErrorBoundary>
      );

      expect(mockOnError).toHaveBeenCalledTimes(1);
      expect(mockOnError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String),
        })
      );
    });

    it('should render custom fallback when provided', () => {
      const customFallback = <div data-testid="custom-fallback">Custom error UI</div>;

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
      expect(screen.getByText('Custom error UI')).toBeInTheDocument();
    });
  });

  describe('Error Recovery', () => {
    it('should retry and render children again when try again is clicked', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      const tryAgainButton = screen.getByText('Try Again');
      fireEvent.click(tryAgainButton);

      // Re-render with no error
      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();
    });

    it('should reload page when reload button is clicked', () => {
      const mockReload = jest.fn();
      Object.defineProperty(window, 'location', {
        value: { reload: mockReload },
        writable: true,
      });

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const reloadButton = screen.getByText('Reload Page');
      fireEvent.click(reloadButton);

      expect(mockReload).toHaveBeenCalledTimes(1);
    });

    it('should navigate home when go home button is clicked', () => {
      const mockAssign = jest.fn();
      Object.defineProperty(window, 'location', {
        value: { href: '', assign: mockAssign },
        writable: true,
      });

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const goHomeButton = screen.getByText('Go Home');
      fireEvent.click(goHomeButton);

      expect(window.location.href).toBe('/');
    });
  });

  describe('Error Reporting', () => {
    it('should report error to external service', async () => {
      const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce(new Response(JSON.stringify({ success: true })));

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Reportable error" />
        </ErrorBoundary>
      );

      // Wait for error reporting
      await new Promise(resolve => setTimeout(resolve, 0));

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/errors/report',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: expect.stringContaining('Reportable error'),
        })
      );
    });

    it('should handle error reporting failure gracefully', async () => {
      const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Reporting failure test" />
        </ErrorBoundary>
      );

      // Should not crash when error reporting fails
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });
  });
});

describe('AsyncErrorBoundary', () => {
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  afterAll(() => {
    console.error = originalError;
  });

  it('should handle async errors', () => {
    render(
      <AsyncErrorBoundary>
        <AsyncErrorComponent />
      </AsyncErrorBoundary>
    );

    const button = screen.getByTestId('async-error-button');
    
    expect(() => {
      fireEvent.click(button);
    }).toThrow('Async test error');
  });

  it('should reload page for chunk load errors', () => {
    const mockReload = jest.fn();
    Object.defineProperty(window, 'location', {
      value: { reload: mockReload },
      writable: true,
    });

    const ChunkLoadError = () => {
      const error = new Error('Loading chunk 123 failed');
      error.name = 'ChunkLoadError';
      throw error;
    };

    render(
      <AsyncErrorBoundary>
        <ChunkLoadError />
      </AsyncErrorBoundary>
    );

    expect(mockReload).toHaveBeenCalledTimes(1);
  });
});

describe('withErrorBoundary HOC', () => {
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  afterAll(() => {
    console.error = originalError;
  });

  it('should wrap component with error boundary', () => {
    const TestComponent = ({ shouldThrow }: { shouldThrow: boolean }) => {
      if (shouldThrow) {
        throw new Error('HOC test error');
      }
      return <div data-testid="wrapped-component">Wrapped content</div>;
    };

    const WrappedComponent = withErrorBoundary(TestComponent);

    const { rerender } = render(<WrappedComponent shouldThrow={false} />);
    
    expect(screen.getByTestId('wrapped-component')).toBeInTheDocument();

    rerender(<WrappedComponent shouldThrow={true} />);
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('should use custom fallback when provided', () => {
    const TestComponent = () => {
      throw new Error('Custom fallback test');
    };

    const customFallback = <div data-testid="hoc-custom-fallback">HOC Custom Error</div>;
    const WrappedComponent = withErrorBoundary(TestComponent, customFallback);

    render(<WrappedComponent />);
    
    expect(screen.getByTestId('hoc-custom-fallback')).toBeInTheDocument();
  });

  it('should call custom onError handler', () => {
    const mockOnError = jest.fn();
    const TestComponent = () => {
      throw new Error('HOC onError test');
    };

    const WrappedComponent = withErrorBoundary(TestComponent, undefined, mockOnError);

    render(<WrappedComponent />);
    
    expect(mockOnError).toHaveBeenCalledTimes(1);
  });

  it('should preserve component display name', () => {
    const TestComponent = () => <div>Test</div>;
    TestComponent.displayName = 'TestComponent';

    const WrappedComponent = withErrorBoundary(TestComponent);
    
    expect(WrappedComponent.displayName).toBe('withErrorBoundary(TestComponent)');
  });

  it('should use component name when displayName is not available', () => {
    function NamedComponent() {
      return <div>Test</div>;
    }

    const WrappedComponent = withErrorBoundary(NamedComponent);
    
    expect(WrappedComponent.displayName).toBe('withErrorBoundary(NamedComponent)');
  });
});

describe('useAsyncError', () => {
  it('should throw error when called', () => {
    const TestComponent = () => {
      const throwAsyncError = useAsyncError();
      
      return (
        <button
          onClick={() => throwAsyncError(new Error('useAsyncError test'))}
          data-testid="throw-button"
        >
          Throw Error
        </button>
      );
    };

    render(<TestComponent />);
    
    const button = screen.getByTestId('throw-button');
    
    expect(() => {
      fireEvent.click(button);
    }).toThrow('useAsyncError test');
  });
});