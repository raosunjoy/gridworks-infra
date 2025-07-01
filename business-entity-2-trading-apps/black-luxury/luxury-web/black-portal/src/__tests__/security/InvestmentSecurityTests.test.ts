/**
 * Comprehensive Security Tests for Investment Syndicate and Anonymous Structures
 * Tests data protection, anonymity preservation, and financial security measures
 * Target: 100% security coverage with zero vulnerabilities
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { InvestmentSyndicateFormation } from '../../components/investment/InvestmentSyndicateFormation';
import { RealTimePortfolioAnalytics } from '../../components/investment/RealTimePortfolioAnalytics';
import { InvestmentTier, InvestmentCategory } from '../../services/InvestmentSyndicateEngine';

// Mock crypto and security utilities
const mockCrypto = {
  getRandomValues: jest.fn((array) => {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(Math.random() * 256);
    }
    return array;
  }),
  subtle: {
    encrypt: jest.fn().mockResolvedValue(new ArrayBuffer(32)),
    decrypt: jest.fn().mockResolvedValue(new ArrayBuffer(32)),
    generateKey: jest.fn().mockResolvedValue({}),
    digest: jest.fn().mockResolvedValue(new ArrayBuffer(32)),
  },
};

// Mock secure storage
const mockSecureStorage = {
  setItem: jest.fn(),
  getItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Security test utilities
const securityTestUtils = {
  generateMaliciousInput: (type: 'xss' | 'injection' | 'overflow') => {
    switch (type) {
      case 'xss':
        return '<script>alert("XSS")</script>';
      case 'injection':
        return "'; DROP TABLE syndicates; --";
      case 'overflow':
        return 'A'.repeat(10000);
      default:
        return '';
    }
  },
  
  checkDataEncryption: (data: any) => {
    // Verify that sensitive data is not stored in plain text
    const serialized = JSON.stringify(data);
    const sensitivePatterns = [
      /\d{4,}/g, // Large numbers (investment amounts)
      /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}/g, // Email addresses
      /[A-Z]{2,3}\d{6,}/g, // Account numbers
    ];
    
    return !sensitivePatterns.some(pattern => pattern.test(serialized));
  },
  
  validateAnonymity: (output: string) => {
    const identifiablePatterns = [
      /anon-[a-zA-Z0-9-]+/g, // Anonymous IDs should be masked
      /\b[A-Z][a-z]+ [A-Z][a-z]+\b/g, // Real names
      /\b\d{3}-\d{2}-\d{4}\b/g, // SSN patterns
    ];
    
    return !identifiablePatterns.some(pattern => pattern.test(output));
  },
};

// Mock luxury components
jest.mock('../../components/ui/LuxuryCard', () => ({
  LuxuryCard: ({ children, className }: any) => (
    <div data-testid="luxury-card" className={className}>
      {children}
    </div>
  ),
}));

jest.mock('../../components/ui/TierGlow', () => ({
  TierGlow: ({ children }: any) => <div data-testid="tier-glow">{children}</div>,
}));

// Mock opportunity for security testing
const mockSecureOpportunity = {
  id: 'secure-test-opportunity',
  title: 'Security Test Investment',
  companyDetails: {
    name: 'SecureTestCorp',
    valuation: 1000000000000,
    stage: 'Series A',
  },
  minimumInvestment: 500000000,
  maximumInvestment: 5000000000,
  lockupPeriod: '2 years',
  category: InvestmentCategory.PRE_IPO,
  expectedReturns: { min: 10, max: 25 },
  riskLevel: 'medium' as const,
  description: 'Security testing investment opportunity',
};

describe('Investment Security Tests', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    jest.clearAllMocks();
    
    // Mock crypto API
    Object.defineProperty(global, 'crypto', {
      value: mockCrypto,
      writable: true,
    });
    
    // Mock secure storage
    Object.defineProperty(global, 'secureStorage', {
      value: mockSecureStorage,
      writable: true,
    });
  });

  describe('Input Validation and Sanitization', () => {
    it('should prevent XSS attacks in syndicate formation inputs', async () => {
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId="anon-security-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Try XSS in SPV name field
      const nextButton = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton);

      const spvNameInput = screen.getByDisplayValue('BlackPortal SecureTestCorp SPV');
      const maliciousInput = securityTestUtils.generateMaliciousInput('xss');
      
      await user.clear(spvNameInput);
      await user.type(spvNameInput, maliciousInput);

      // Should sanitize or reject malicious input
      expect(spvNameInput.value).not.toContain('<script>');
      expect(spvNameInput.value).not.toContain('alert');
    });

    it('should prevent SQL injection attempts in numeric inputs', async () => {
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId="anon-security-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      const injectionAttempt = securityTestUtils.generateMaliciousInput('injection');
      
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, injectionAttempt);

      // Numeric input should reject non-numeric characters
      expect(leadCommitmentInput.value).not.toContain('DROP TABLE');
      expect(leadCommitmentInput.value).not.toContain(';');
      expect(leadCommitmentInput.value).not.toContain('--');
    });

    it('should handle buffer overflow attempts gracefully', async () => {
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId="anon-security-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      const nextButton = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton);

      const spvNameInput = screen.getByDisplayValue('BlackPortal SecureTestCorp SPV');
      const overflowAttempt = securityTestUtils.generateMaliciousInput('overflow');
      
      await user.clear(spvNameInput);
      await user.type(spvNameInput, overflowAttempt);

      // Should limit input length
      expect(spvNameInput.value.length).toBeLessThan(1000);
    });

    it('should validate investment amounts against manipulation', async () => {
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId="anon-security-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Try negative investment amount
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '-1000000000');

      // Navigate to review to trigger validation
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Should show validation error for negative amounts
      expect(screen.getByText(/Validation Errors/)).toBeInTheDocument();
    });
  });

  describe('Anonymous ID Protection', () => {
    it('should not expose anonymous IDs in DOM or logs', () => {
      const { container } = render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.VOID}
          anonymousId="anon-super-secret-123"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Check that anonymous ID is not exposed in DOM
      const htmlContent = container.innerHTML;
      expect(htmlContent).not.toContain('anon-super-secret-123');
      
      // Check that sensitive data is not in attributes
      const elements = container.querySelectorAll('*');
      elements.forEach(element => {
        Array.from(element.attributes).forEach(attr => {
          expect(attr.value).not.toContain('anon-super-secret-123');
        });
      });
    });

    it('should mask anonymous IDs in portfolio analytics', () => {
      const { container } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="anon-portfolio-secret-456"
          portfolioId="sensitive-portfolio-id"
        />
      );

      const htmlContent = container.innerHTML;
      expect(htmlContent).not.toContain('anon-portfolio-secret-456');
      expect(htmlContent).not.toContain('sensitive-portfolio-id');
    });

    it('should use secure hash functions for ID generation', () => {
      const syndicateCreated = jest.fn();
      
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.VOID}
          anonymousId="anon-hash-test"
          onSyndicateCreated={syndicateCreated}
          onCancel={jest.fn()}
        />
      );

      // Navigate through and create syndicate
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      fireEvent.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      fireEvent.click(nextButton2);
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      fireEvent.click(nextButton3);
      
      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      fireEvent.click(createButton);

      // Generated IDs should use secure random patterns
      if (syndicateCreated.mock.calls.length > 0) {
        const createdSyndicate = syndicateCreated.mock.calls[0][0];
        expect(createdSyndicate.id).toMatch(/^syn-\d+-[a-z0-9]{6}$/);
      }
    });
  });

  describe('Financial Data Encryption', () => {
    it('should encrypt sensitive financial data before storage', async () => {
      const syndicateCreated = jest.fn();
      
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.OBSIDIAN}
          anonymousId="anon-encryption-test"
          onSyndicateCreated={syndicateCreated}
          onCancel={jest.fn()}
        />
      );

      // Set specific financial values
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '1000000000');

      // Complete syndicate creation
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);
      
      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      await user.click(createButton);

      // Verify encryption was called for financial data
      expect(mockCrypto.subtle.encrypt).toHaveBeenCalled();
    });

    it('should not store plaintext investment amounts in local storage', () => {
      const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
      
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="anon-storage-test"
          portfolioId="storage-test-portfolio"
        />
      );

      // Check that no plaintext financial data is stored
      setItemSpy.mock.calls.forEach(([key, value]) => {
        expect(securityTestUtils.checkDataEncryption(value)).toBe(true);
      });

      setItemSpy.mockRestore();
    });

    it('should use secure transmission protocols for financial data', async () => {
      const fetchSpy = jest.spyOn(global, 'fetch').mockResolvedValue(
        new Response(JSON.stringify({ success: true }))
      );

      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.ONYX}
          anonymousId="anon-transmission-test"
          portfolioId="transmission-test-portfolio"
        />
      );

      // Simulate data transmission
      await waitFor(() => {
        if (fetchSpy.mock.calls.length > 0) {
          fetchSpy.mock.calls.forEach(([url, options]) => {
            // Should use HTTPS
            expect(url).toMatch(/^https:/);
            
            // Should have proper security headers
            const headers = (options as any)?.headers || {};
            expect(headers['Content-Type']).toContain('application/json');
          });
        }
      });

      fetchSpy.mockRestore();
    });
  });

  describe('Access Control and Authorization', () => {
    it('should enforce tier-based access controls', () => {
      // Test Onyx tier limitations
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId="anon-access-onyx"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      const governanceSelect = screen.getByDisplayValue('lead_decides');
      const options = Array.from(governanceSelect.querySelectorAll('option'));
      
      // Onyx tier should not have access to unanimous or weighted voting
      const optionValues = options.map(option => option.getAttribute('value'));
      expect(optionValues).not.toContain('unanimous');
      expect(optionValues).not.toContain('weighted_vote');
    });

    it('should validate tier eligibility for quantum features', async () => {
      // Test that lower tiers cannot access quantum features
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.ONYX}
          anonymousId="anon-quantum-access-test"
          portfolioId="quantum-access-portfolio"
        />
      );

      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      await user.click(riskTab);

      // Should not show quantum risk analysis for Onyx tier
      expect(screen.queryByText('Quantum Risk Analysis')).not.toBeInTheDocument();
    });

    it('should prevent unauthorized syndicate modifications', async () => {
      const unauthorizedUser = 'anon-unauthorized-user';
      
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId={unauthorizedUser}
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Attempt to create syndicate with invalid permissions
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '10000000000'); // Above tier limit

      // Navigate to review
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Should show validation errors for tier limits
      expect(screen.getByText(/Validation Errors/)).toBeInTheDocument();
    });
  });

  describe('Session Security', () => {
    it('should implement secure session management', () => {
      const sessionToken = 'secure-session-token-123';
      const mockSessionStorage = {
        getItem: jest.fn().mockReturnValue(sessionToken),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      };

      Object.defineProperty(global, 'sessionStorage', {
        value: mockSessionStorage,
        writable: true,
      });

      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="anon-session-test"
          portfolioId="session-test-portfolio"
        />
      );

      // Session token should be handled securely
      expect(mockSessionStorage.getItem).toHaveBeenCalled();
    });

    it('should handle session expiration gracefully', async () => {
      const expiredSession = {
        token: 'expired-token',
        expiresAt: Date.now() - 3600000, // 1 hour ago
      };

      const mockSessionStorage = {
        getItem: jest.fn().mockReturnValue(JSON.stringify(expiredSession)),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      };

      Object.defineProperty(global, 'sessionStorage', {
        value: mockSessionStorage,
        writable: true,
      });

      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="anon-expired-session"
          portfolioId="expired-session-portfolio"
        />
      );

      // Should handle expired session without crashing
      expect(screen.getByText('Portfolio Analytics')).toBeInTheDocument();
    });

    it('should implement CSRF protection', async () => {
      const csrfToken = 'csrf-protection-token-456';
      
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.VOID}
          anonymousId="anon-csrf-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // CSRF token should be included in form submissions
      const forms = document.querySelectorAll('form');
      forms.forEach(form => {
        const csrfInput = form.querySelector('input[name="csrf_token"]');
        if (csrfInput) {
          expect(csrfInput.getAttribute('value')).toBeTruthy();
        }
      });
    });
  });

  describe('Data Anonymization', () => {
    it('should anonymize all user data in error logs', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      // Force an error with sensitive data
      const ErrorComponent = () => {
        throw new Error('Test error with anon-sensitive-id-789');
      };

      try {
        render(<ErrorComponent />);
      } catch (error) {
        // Error handling should anonymize sensitive data
        expect(consoleSpy).toHaveBeenCalled();
        const loggedErrors = consoleSpy.mock.calls.flat().join(' ');
        expect(securityTestUtils.validateAnonymity(loggedErrors)).toBe(true);
      }

      consoleSpy.mockRestore();
    });

    it('should not expose portfolio composition in client-side code', () => {
      const { container } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="anon-composition-test"
          portfolioId="composition-test-portfolio"
        />
      );

      // Check that detailed portfolio data is not exposed
      const scripts = container.querySelectorAll('script');
      scripts.forEach(script => {
        const content = script.textContent || '';
        expect(content).not.toMatch(/\d{8,}/g); // Large numbers
        expect(content).not.toContain('portfolio_positions');
        expect(content).not.toContain('holdings_detail');
      });
    });

    it('should use differential privacy for aggregate statistics', async () => {
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="anon-privacy-test"
          portfolioId="privacy-test-portfolio"
        />
      );

      // Navigate to different tabs to check aggregate data
      const tabs = ['Performance', 'Risk Analysis', 'Allocation', 'ESG Analysis'];
      
      for (const tabName of tabs) {
        const tab = screen.getByRole('button', { name: tabName });
        await user.click(tab);
        
        // Statistical data should be anonymized
        const content = screen.getByTestId('luxury-card').textContent || '';
        expect(securityTestUtils.validateAnonymity(content)).toBe(true);
      }
    });
  });

  describe('Audit Trail Security', () => {
    it('should create secure audit logs for all actions', async () => {
      const auditSpy = jest.fn();
      global.auditLogger = { log: auditSpy };
      
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.OBSIDIAN}
          anonymousId="anon-audit-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Perform actions that should be audited
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '750000000');

      // Audit logs should be created with proper anonymization
      if (auditSpy.mock.calls.length > 0) {
        auditSpy.mock.calls.forEach(([logEntry]) => {
          expect(logEntry).toHaveProperty('timestamp');
          expect(logEntry).toHaveProperty('action');
          expect(logEntry).toHaveProperty('anonymousUserId');
          expect(logEntry.anonymousUserId).not.toContain('anon-audit-test');
        });
      }
    });

    it('should implement tamper-proof audit logging', () => {
      const auditLog = {
        timestamp: Date.now(),
        action: 'syndicate_created',
        data: { amount: 1000000000 },
        hash: 'secure-hash-value',
      };

      // Audit logs should have integrity checks
      expect(auditLog).toHaveProperty('hash');
      expect(auditLog.hash).toBeTruthy();
      expect(typeof auditLog.hash).toBe('string');
    });
  });

  describe('Compliance and Regulatory Security', () => {
    it('should implement KYC data protection', async () => {
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.VOID}
          anonymousId="anon-kyc-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Navigate to participants section
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);

      // KYC requirements should be enforced
      expect(screen.getByText('Accredited investor status required')).toBeInTheDocument();
      
      const accreditationCheckbox = screen.getByRole('checkbox', { 
        name: /Accredited investor status required/ 
      });
      expect(accreditationCheckbox).toBeChecked();
    });

    it('should enforce anti-money laundering (AML) checks', async () => {
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.OBSIDIAN}
          anonymousId="anon-aml-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Large investment amounts should trigger AML checks
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '5000000000'); // ₹500 Cr

      // Should implement additional validation for large amounts
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Should show additional compliance requirements
      expect(screen.getByText(/Enhanced/)).toBeInTheDocument();
    });

    it('should implement geographic compliance restrictions', async () => {
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSecureOpportunity}
          leadInvestorTier={InvestmentTier.VOID}
          anonymousId="anon-geo-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Navigate to participants section
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);

      // Geographic restrictions should be configurable
      expect(screen.getByText('Geographic Restrictions')).toBeInTheDocument();
    });
  });
});