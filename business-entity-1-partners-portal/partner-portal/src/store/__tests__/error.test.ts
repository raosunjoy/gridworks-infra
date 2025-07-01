import { renderHook, act } from '@testing-library/react';
import { useErrorStore } from '../error';
import { ErrorSeverity } from '@/types';

// Mock console methods to avoid noise in tests
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeAll(() => {
  console.error = jest.fn();
  console.warn = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});

describe('Error Store', () => {
  beforeEach(() => {
    // Reset the store before each test
    const { result } = renderHook(() => useErrorStore());
    act(() => {
      result.current.clearErrors();
    });
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useErrorStore());
      
      expect(result.current.errors).toEqual([]);
      expect(result.current.lastError).toBeNull();
    });
  });

  describe('Adding Errors', () => {
    it('should add error with all required fields', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Test error message',
          code: 'TEST_ERROR',
          severity: ErrorSeverity.ERROR,
        });
      });

      expect(result.current.errors).toHaveLength(1);
      expect(result.current.errors[0]).toMatchObject({
        message: 'Test error message',
        code: 'TEST_ERROR',
        severity: ErrorSeverity.ERROR,
      });
      expect(result.current.errors[0].id).toBeDefined();
      expect(result.current.errors[0].timestamp).toBeInstanceOf(Date);
    });

    it('should add error with optional details', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Test error with details',
          code: 'DETAILED_ERROR',
          severity: ErrorSeverity.ERROR,
          details: { userId: '123', action: 'login' },
          stack: 'Error stack trace',
        });
      });

      expect(result.current.errors[0]).toMatchObject({
        message: 'Test error with details',
        code: 'DETAILED_ERROR',
        severity: ErrorSeverity.ERROR,
        details: { userId: '123', action: 'login' },
        stack: 'Error stack trace',
      });
    });

    it('should set lastError when adding error', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Latest error',
          code: 'LATEST_ERROR',
          severity: ErrorSeverity.CRITICAL,
        });
      });

      expect(result.current.lastError).toMatchObject({
        message: 'Latest error',
        code: 'LATEST_ERROR',
        severity: ErrorSeverity.CRITICAL,
      });
    });

    it('should generate unique IDs for multiple errors', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Error 1',
          code: 'ERROR_1',
          severity: ErrorSeverity.ERROR,
        });
        
        result.current.addError({
          message: 'Error 2',
          code: 'ERROR_2',
          severity: ErrorSeverity.WARNING,
        });
      });

      expect(result.current.errors).toHaveLength(2);
      expect(result.current.errors[0].id).not.toBe(result.current.errors[1].id);
    });

    it('should update lastError with most recent error', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'First error',
          code: 'FIRST_ERROR',
          severity: ErrorSeverity.ERROR,
        });
      });

      const firstErrorId = result.current.lastError?.id;

      act(() => {
        result.current.addError({
          message: 'Second error',
          code: 'SECOND_ERROR',
          severity: ErrorSeverity.CRITICAL,
        });
      });

      expect(result.current.lastError?.message).toBe('Second error');
      expect(result.current.lastError?.id).not.toBe(firstErrorId);
    });
  });

  describe('Removing Errors', () => {
    it('should remove error by ID', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Error to remove',
          code: 'REMOVE_ERROR',
          severity: ErrorSeverity.ERROR,
        });
      });

      const errorId = result.current.errors[0].id;

      act(() => {
        result.current.removeError(errorId);
      });

      expect(result.current.errors).toHaveLength(0);
    });

    it('should not affect other errors when removing specific error', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Error 1',
          code: 'ERROR_1',
          severity: ErrorSeverity.ERROR,
        });
        
        result.current.addError({
          message: 'Error 2',
          code: 'ERROR_2',
          severity: ErrorSeverity.WARNING,
        });
      });

      const errorToRemove = result.current.errors[0].id;

      act(() => {
        result.current.removeError(errorToRemove);
      });

      expect(result.current.errors).toHaveLength(1);
      expect(result.current.errors[0].message).toBe('Error 2');
    });

    it('should handle removal of non-existent error gracefully', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Existing error',
          code: 'EXISTING_ERROR',
          severity: ErrorSeverity.ERROR,
        });
      });

      act(() => {
        result.current.removeError('non-existent-id');
      });

      expect(result.current.errors).toHaveLength(1);
      expect(result.current.errors[0].message).toBe('Existing error');
    });
  });

  describe('Clearing Errors', () => {
    it('should clear all errors', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Error 1',
          code: 'ERROR_1',
          severity: ErrorSeverity.ERROR,
        });
        
        result.current.addError({
          message: 'Error 2',
          code: 'ERROR_2',
          severity: ErrorSeverity.WARNING,
        });
      });

      expect(result.current.errors).toHaveLength(2);

      act(() => {
        result.current.clearErrors();
      });

      expect(result.current.errors).toHaveLength(0);
      expect(result.current.lastError).toBeNull();
    });

    it('should reset lastError when clearing', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Error to clear',
          code: 'CLEAR_ERROR',
          severity: ErrorSeverity.ERROR,
        });
      });

      expect(result.current.lastError).not.toBeNull();

      act(() => {
        result.current.clearErrors();
      });

      expect(result.current.lastError).toBeNull();
    });
  });

  describe('Error Severity Handling', () => {
    it('should handle all severity levels', () => {
      const { result } = renderHook(() => useErrorStore());
      
      const severities = [
        ErrorSeverity.INFO,
        ErrorSeverity.WARNING,
        ErrorSeverity.ERROR,
        ErrorSeverity.CRITICAL,
      ];

      severities.forEach((severity, index) => {
        act(() => {
          result.current.addError({
            message: `Error ${index}`,
            code: `ERROR_${index}`,
            severity,
          });
        });
      });

      expect(result.current.errors).toHaveLength(4);
      
      severities.forEach((severity, index) => {
        expect(result.current.errors[index].severity).toBe(severity);
      });
    });

    it('should preserve severity in lastError', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Critical error',
          code: 'CRITICAL_ERROR',
          severity: ErrorSeverity.CRITICAL,
        });
      });

      expect(result.current.lastError?.severity).toBe(ErrorSeverity.CRITICAL);
    });
  });

  describe('Error Filtering and Querying', () => {
    beforeEach(() => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Info message',
          code: 'INFO_ERROR',
          severity: ErrorSeverity.INFO,
        });
        
        result.current.addError({
          message: 'Warning message',
          code: 'WARNING_ERROR',
          severity: ErrorSeverity.WARNING,
        });
        
        result.current.addError({
          message: 'Error message',
          code: 'ERROR_ERROR',
          severity: ErrorSeverity.ERROR,
        });
        
        result.current.addError({
          message: 'Critical message',
          code: 'CRITICAL_ERROR',
          severity: ErrorSeverity.CRITICAL,
        });
      });
    });

    it('should allow filtering by severity', () => {
      const { result } = renderHook(() => useErrorStore());
      
      const criticalErrors = result.current.errors.filter(
        error => error.severity === ErrorSeverity.CRITICAL
      );
      
      expect(criticalErrors).toHaveLength(1);
      expect(criticalErrors[0].message).toBe('Critical message');
    });

    it('should allow filtering by code', () => {
      const { result } = renderHook(() => useErrorStore());
      
      const warningErrors = result.current.errors.filter(
        error => error.code === 'WARNING_ERROR'
      );
      
      expect(warningErrors).toHaveLength(1);
      expect(warningErrors[0].message).toBe('Warning message');
    });

    it('should maintain chronological order', () => {
      const { result } = renderHook(() => useErrorStore());
      
      const messages = result.current.errors.map(error => error.message);
      expect(messages).toEqual([
        'Info message',
        'Warning message',
        'Error message',
        'Critical message',
      ]);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty message', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: '',
          code: 'EMPTY_MESSAGE',
          severity: ErrorSeverity.ERROR,
        });
      });

      expect(result.current.errors[0].message).toBe('');
    });

    it('should handle very long messages', () => {
      const { result } = renderHook(() => useErrorStore());
      const longMessage = 'A'.repeat(10000);
      
      act(() => {
        result.current.addError({
          message: longMessage,
          code: 'LONG_MESSAGE',
          severity: ErrorSeverity.ERROR,
        });
      });

      expect(result.current.errors[0].message).toBe(longMessage);
    });

    it('should handle special characters in message and code', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Error with special chars: <>&"\'',
          code: 'SPECIAL_CHARS_CODE_123!@#',
          severity: ErrorSeverity.ERROR,
        });
      });

      expect(result.current.errors[0].message).toBe('Error with special chars: <>&"\'');
      expect(result.current.errors[0].code).toBe('SPECIAL_CHARS_CODE_123!@#');
    });

    it('should handle null/undefined details gracefully', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        result.current.addError({
          message: 'Error with null details',
          code: 'NULL_DETAILS',
          severity: ErrorSeverity.ERROR,
          details: null as any,
        });
      });

      expect(result.current.errors[0].details).toBeNull();
    });
  });

  describe('Store Persistence', () => {
    it('should maintain state across multiple hook calls', () => {
      const { result: result1 } = renderHook(() => useErrorStore());
      
      act(() => {
        result1.current.addError({
          message: 'Persistent error',
          code: 'PERSISTENT_ERROR',
          severity: ErrorSeverity.ERROR,
        });
      });

      const { result: result2 } = renderHook(() => useErrorStore());
      
      expect(result2.current.errors).toHaveLength(1);
      expect(result2.current.errors[0].message).toBe('Persistent error');
    });

    it('should maintain lastError across hook instances', () => {
      const { result: result1 } = renderHook(() => useErrorStore());
      
      act(() => {
        result1.current.addError({
          message: 'Last error test',
          code: 'LAST_ERROR_TEST',
          severity: ErrorSeverity.ERROR,
        });
      });

      const { result: result2 } = renderHook(() => useErrorStore());
      
      expect(result2.current.lastError?.message).toBe('Last error test');
    });
  });

  describe('Performance', () => {
    it('should handle large number of errors efficiently', () => {
      const { result } = renderHook(() => useErrorStore());
      
      const startTime = performance.now();
      
      act(() => {
        for (let i = 0; i < 1000; i++) {
          result.current.addError({
            message: `Error ${i}`,
            code: `ERROR_${i}`,
            severity: ErrorSeverity.ERROR,
          });
        }
      });
      
      const endTime = performance.now();
      
      expect(result.current.errors).toHaveLength(1000);
      expect(endTime - startTime).toBeLessThan(1000); // Should complete in less than 1 second
    });

    it('should handle rapid error additions and removals', () => {
      const { result } = renderHook(() => useErrorStore());
      
      act(() => {
        // Add many errors
        for (let i = 0; i < 100; i++) {
          result.current.addError({
            message: `Rapid error ${i}`,
            code: `RAPID_ERROR_${i}`,
            severity: ErrorSeverity.ERROR,
          });
        }
        
        // Remove every other error
        const idsToRemove = result.current.errors
          .filter((_, index) => index % 2 === 0)
          .map(error => error.id);
        
        idsToRemove.forEach(id => {
          result.current.removeError(id);
        });
      });
      
      expect(result.current.errors).toHaveLength(50);
    });
  });
});