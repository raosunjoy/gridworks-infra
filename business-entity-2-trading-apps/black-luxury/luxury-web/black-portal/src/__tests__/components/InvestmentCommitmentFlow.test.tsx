/**
 * Investment Commitment Flow Test Suite
 * Comprehensive testing for multi-step investment commitment process,
 * anonymous structure setup, KYC verification, and payment orchestration
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { InvestmentCommitmentFlow } from '../../components/investment/InvestmentCommitmentFlow';
import { InvestmentTier, InvestmentCategory } from '../../services/InvestmentSyndicateEngine';

// Mock dependencies
jest.mock('../../services/InvestmentSyndicateEngine');
jest.mock('../../components/ui/LuxuryCard', () => ({
  LuxuryCard: ({ children, className }: any) => (
    <div className={className} data-testid="luxury-card">
      {children}
    </div>
  ),
}));

const mockOpportunity = {
  id: 'preipo-spacex-001',
  title: 'SpaceX Series X Investment',
  category: InvestmentCategory.PRE_IPO,
  minimumInvestment: 500000000, // ₹50 Cr
  maximumInvestment: 5000000000, // ₹500 Cr
  currency: 'INR',
  tierAccess: [InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
  expectedReturns: {
    conservative: '25',
    optimistic: '40% annually',
  },
  riskRating: 'medium',
  availableSlots: 25,
  currentCommitments: 2500000000,
  status: 'active',
  companyDetails: {
    name: 'SpaceX',
    sector: 'Aerospace',
    lastValuation: 180000000000,
    foundedYear: 2002,
    employees: 12000,
    headquarters: 'Hawthorne, CA',
  },
  offeringPeriod: {
    startDate: '2024-06-01',
    endDate: '2024-12-31',
    finalClosing: '2025-01-15',
  },
  lockupPeriod: '3-5 years',
  riskFactors: [
    'Regulatory changes in space industry',
    'Launch failures and technical risks',
    'Competition from other space companies',
  ],
  complianceChecks: {
    sebiApproval: true,
    rbiCompliance: true,
    femaCompliance: true,
    taxImplications: ['LTCG applicable after 3 years', 'Angel tax exemption'],
  },
  createdAt: '2024-06-01T00:00:00Z',
  updatedAt: '2024-06-29T00:00:00Z',
};

describe('InvestmentCommitmentFlow', () => {
  const defaultProps = {
    opportunity: mockOpportunity,
    clientTier: InvestmentTier.OBSIDIAN,
    anonymousId: 'test-anonymous-id',
    onCommitmentComplete: jest.fn(),
    onCancel: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Initialization', () => {
    test('should render commitment flow with opportunity details', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      expect(screen.getByText('Investment Commitment')).toBeInTheDocument();
      expect(screen.getByText('SpaceX Series X Investment')).toBeInTheDocument();
      expect(screen.getByText('Complete your investment commitment in 5 simple steps')).toBeInTheDocument();
    });

    test('should start with step 1 (Investment Details)', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      expect(screen.getByText('Step 1: Investment Details')).toBeInTheDocument();
      expect(screen.getByText('Investment Amount')).toBeInTheDocument();
      expect(screen.getByDisplayValue('500000000')).toBeInTheDocument(); // Default minimum
    });

    test('should display progress indicator with 5 steps', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const progressSteps = screen.getAllByTestId('step-indicator');
      expect(progressSteps).toHaveLength(5);
      
      expect(screen.getByText('Investment Details')).toBeInTheDocument();
      expect(screen.getByText('Anonymous Structure')).toBeInTheDocument();
      expect(screen.getByText('KYC Verification')).toBeInTheDocument();
      expect(screen.getByText('Payment Setup')).toBeInTheDocument();
      expect(screen.getByText('Final Review')).toBeInTheDocument();
    });
  });

  describe('Step 1: Investment Details', () => {
    test('should allow investment amount input within valid range', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const amountInput = screen.getByDisplayValue('500000000');
      fireEvent.change(amountInput, { target: { value: '1000000000' } });
      
      expect(amountInput.value).toBe('1000000000');
    });

    test('should show validation error for amount below minimum', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const amountInput = screen.getByDisplayValue('500000000');
      fireEvent.change(amountInput, { target: { value: '100000000' } }); // Below minimum
      fireEvent.blur(amountInput);
      
      expect(screen.getByText('Minimum investment is ₹50 Cr')).toBeInTheDocument();
    });

    test('should show validation error for amount above maximum', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const amountInput = screen.getByDisplayValue('500000000');
      fireEvent.change(amountInput, { target: { value: '6000000000' } }); // Above maximum
      fireEvent.blur(amountInput);
      
      expect(screen.getByText('Maximum investment is ₹500 Cr')).toBeInTheDocument();
    });

    test('should display investment amount in readable format', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      expect(screen.getByText('₹50 Cr')).toBeInTheDocument(); // Formatted minimum
      expect(screen.getByText('₹500 Cr')).toBeInTheDocument(); // Formatted maximum
    });

    test('should allow selection of investment vehicle type', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      expect(screen.getByText('Investment Vehicle')).toBeInTheDocument();
      expect(screen.getByLabelText('SPV (Special Purpose Vehicle)')).toBeInTheDocument();
      expect(screen.getByLabelText('Direct Investment')).toBeInTheDocument();
      expect(screen.getByLabelText('Trust Structure')).toBeInTheDocument();
    });

    test('should proceed to next step when details are valid', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const nextButton = screen.getByText('Next: Anonymous Structure');
      fireEvent.click(nextButton);
      
      expect(screen.getByText('Step 2: Anonymous Structure')).toBeInTheDocument();
    });

    test('should disable next button when amount is invalid', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const amountInput = screen.getByDisplayValue('500000000');
      fireEvent.change(amountInput, { target: { value: '0' } });
      
      const nextButton = screen.getByText('Next: Anonymous Structure');
      expect(nextButton).toBeDisabled();
    });
  });

  describe('Step 2: Anonymous Structure', () => {
    beforeEach(() => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      const nextButton = screen.getByText('Next: Anonymous Structure');
      fireEvent.click(nextButton);
    });

    test('should display anonymous structure options', () => {
      expect(screen.getByText('Step 2: Anonymous Structure')).toBeInTheDocument();
      expect(screen.getByText('Holding Company Structure')).toBeInTheDocument();
      expect(screen.getByText('Jurisdiction Selection')).toBeInTheDocument();
      expect(screen.getByText('Beneficial Ownership')).toBeInTheDocument();
    });

    test('should show recommended holding company name', () => {
      expect(screen.getByText(/BlackPortal SPV/)).toBeInTheDocument();
    });

    test('should allow jurisdiction selection', () => {
      const mauritiusOption = screen.getByLabelText('Mauritius');
      const singaporeOption = screen.getByLabelText('Singapore');
      const caymanOption = screen.getByLabelText('Cayman Islands');
      
      expect(mauritiusOption).toBeInTheDocument();
      expect(singaporeOption).toBeInTheDocument();
      expect(caymanOption).toBeInTheDocument();
      
      fireEvent.click(mauritiusOption);
      expect(mauritiusOption).toBeChecked();
    });

    test('should display tax optimization features', () => {
      expect(screen.getByText('Tax Optimization')).toBeInTheDocument();
      expect(screen.getByText('Treaty benefits available')).toBeInTheDocument();
      expect(screen.getByText('DTAA advantages')).toBeInTheDocument();
    });

    test('should allow proceeding to KYC step', () => {
      const nextButton = screen.getByText('Next: KYC Verification');
      fireEvent.click(nextButton);
      
      expect(screen.getByText('Step 3: KYC Verification')).toBeInTheDocument();
    });

    test('should allow going back to previous step', () => {
      const backButton = screen.getByText('Back');
      fireEvent.click(backButton);
      
      expect(screen.getByText('Step 1: Investment Details')).toBeInTheDocument();
    });
  });

  describe('Step 3: KYC Verification', () => {
    beforeEach(() => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      // Navigate to step 3
      fireEvent.click(screen.getByText('Next: Anonymous Structure'));
      fireEvent.click(screen.getByText('Next: KYC Verification'));
    });

    test('should display KYC verification requirements', () => {
      expect(screen.getByText('Step 3: KYC Verification')).toBeInTheDocument();
      expect(screen.getByText('Identity Verification')).toBeInTheDocument();
      expect(screen.getByText('Source of Funds')).toBeInTheDocument();
      expect(screen.getByText('Compliance Checks')).toBeInTheDocument();
    });

    test('should show document upload sections', () => {
      expect(screen.getByText('Upload Identity Documents')).toBeInTheDocument();
      expect(screen.getByText('Upload Source of Funds Documentation')).toBeInTheDocument();
      expect(screen.getByText('Upload Bank Statements (Last 6 months)')).toBeInTheDocument();
    });

    test('should handle document upload', () => {
      const fileInput = screen.getByLabelText('Upload Passport/ID');
      const mockFile = new File(['test'], 'passport.pdf', { type: 'application/pdf' });
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } });
      
      expect(screen.getByText('passport.pdf')).toBeInTheDocument();
    });

    test('should validate required documents before proceeding', () => {
      const nextButton = screen.getByText('Next: Payment Setup');
      
      // Should be disabled initially
      expect(nextButton).toBeDisabled();
      
      // Upload required documents
      const idInput = screen.getByLabelText('Upload Passport/ID');
      const mockFile = new File(['test'], 'id.pdf', { type: 'application/pdf' });
      fireEvent.change(idInput, { target: { files: [mockFile] } });
      
      // Should still be disabled until all required docs are uploaded
      expect(nextButton).toBeDisabled();
    });

    test('should show compliance status indicators', () => {
      expect(screen.getByText('SEBI Compliance')).toBeInTheDocument();
      expect(screen.getByText('RBI Guidelines')).toBeInTheDocument();
      expect(screen.getByText('FEMA Compliance')).toBeInTheDocument();
    });
  });

  describe('Step 4: Payment Setup', () => {
    beforeEach(() => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      // Navigate to step 4
      fireEvent.click(screen.getByText('Next: Anonymous Structure'));
      fireEvent.click(screen.getByText('Next: KYC Verification'));
      fireEvent.click(screen.getByText('Next: Payment Setup'));
    });

    test('should display payment setup options', () => {
      expect(screen.getByText('Step 4: Payment Setup')).toBeInTheDocument();
      expect(screen.getByText('Payment Method')).toBeInTheDocument();
      expect(screen.getByText('Payment Schedule')).toBeInTheDocument();
    });

    test('should show payment method options', () => {
      expect(screen.getByLabelText('Bank Transfer (RTGS/NEFT)')).toBeInTheDocument();
      expect(screen.getByLabelText('Wire Transfer (International)')).toBeInTheDocument();
      expect(screen.getByLabelText('Cryptocurrency (Stable Coins)')).toBeInTheDocument();
    });

    test('should display payment schedule with installments', () => {
      expect(screen.getByText('3 Installments Recommended')).toBeInTheDocument();
      expect(screen.getByText('1st Installment: ₹16.67 Cr (33%)')).toBeInTheDocument();
      expect(screen.getByText('2nd Installment: ₹16.67 Cr (33%)')).toBeInTheDocument();
      expect(screen.getByText('3rd Installment: ₹16.66 Cr (34%)')).toBeInTheDocument();
    });

    test('should allow custom payment schedule', () => {
      const customScheduleButton = screen.getByText('Customize Schedule');
      fireEvent.click(customScheduleButton);
      
      expect(screen.getByText('Custom Payment Schedule')).toBeInTheDocument();
    });

    test('should validate bank account details', () => {
      const bankAccountInput = screen.getByLabelText('Bank Account Number');
      fireEvent.change(bankAccountInput, { target: { value: 'invalid' } });
      fireEvent.blur(bankAccountInput);
      
      expect(screen.getByText('Please enter a valid bank account number')).toBeInTheDocument();
    });

    test('should show encryption and security features', () => {
      expect(screen.getByText('Bank-Grade Encryption')).toBeInTheDocument();
      expect(screen.getByText('Anonymous Payment Processing')).toBeInTheDocument();
      expect(screen.getByText('Multi-Signature Authorization')).toBeInTheDocument();
    });
  });

  describe('Step 5: Final Review', () => {
    beforeEach(() => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      // Navigate to final step
      fireEvent.click(screen.getByText('Next: Anonymous Structure'));
      fireEvent.click(screen.getByText('Next: KYC Verification'));
      fireEvent.click(screen.getByText('Next: Payment Setup'));
      fireEvent.click(screen.getByText('Next: Final Review'));
    });

    test('should display final review summary', () => {
      expect(screen.getByText('Step 5: Final Review')).toBeInTheDocument();
      expect(screen.getByText('Investment Summary')).toBeInTheDocument();
      expect(screen.getByText('Anonymous Structure Summary')).toBeInTheDocument();
      expect(screen.getByText('Payment Summary')).toBeInTheDocument();
    });

    test('should show complete investment details', () => {
      expect(screen.getByText('SpaceX Series X Investment')).toBeInTheDocument();
      expect(screen.getByText('₹50 Cr')).toBeInTheDocument(); // Investment amount
      expect(screen.getByText('SPV Structure')).toBeInTheDocument();
      expect(screen.getByText('3 Installments')).toBeInTheDocument();
    });

    test('should display legal disclaimers and terms', () => {
      expect(screen.getByText('Terms & Conditions')).toBeInTheDocument();
      expect(screen.getByText('Risk Disclosures')).toBeInTheDocument();
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    });

    test('should require agreement to terms before commitment', () => {
      const commitButton = screen.getByText('Complete Investment Commitment');
      expect(commitButton).toBeDisabled();
      
      const termsCheckbox = screen.getByLabelText('I agree to the Terms & Conditions');
      fireEvent.click(termsCheckbox);
      
      const riskCheckbox = screen.getByLabelText('I acknowledge the risk disclosures');
      fireEvent.click(riskCheckbox);
      
      expect(commitButton).not.toBeDisabled();
    });

    test('should complete commitment when all requirements are met', async () => {
      // Accept all terms
      fireEvent.click(screen.getByLabelText('I agree to the Terms & Conditions'));
      fireEvent.click(screen.getByLabelText('I acknowledge the risk disclosures'));
      fireEvent.click(screen.getByLabelText('I confirm the investment details'));
      
      const commitButton = screen.getByText('Complete Investment Commitment');
      fireEvent.click(commitButton);
      
      await waitFor(() => {
        expect(defaultProps.onCommitmentComplete).toHaveBeenCalledWith(
          expect.objectContaining({
            opportunityId: mockOpportunity.id,
            investmentAmount: 500000000,
            anonymousId: 'test-anonymous-id',
          })
        );
      });
    });
  });

  describe('Navigation and Progress', () => {
    test('should update progress indicator when navigating steps', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      // Step 1 should be active
      const step1Indicator = screen.getAllByTestId('step-indicator')[0];
      expect(step1Indicator).toHaveClass('bg-gold-500'); // Active state
      
      fireEvent.click(screen.getByText('Next: Anonymous Structure'));
      
      // Step 2 should now be active
      const step2Indicator = screen.getAllByTestId('step-indicator')[1];
      expect(step2Indicator).toHaveClass('bg-gold-500');
    });

    test('should allow canceling at any step', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);
      
      expect(defaultProps.onCancel).toHaveBeenCalled();
    });

    test('should show confirmation dialog before canceling', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);
      
      expect(screen.getByText('Are you sure you want to cancel this investment commitment?')).toBeInTheDocument();
    });

    test('should save progress for later completion', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const saveButton = screen.getByText('Save & Continue Later');
      fireEvent.click(saveButton);
      
      expect(screen.getByText('Progress saved successfully')).toBeInTheDocument();
    });
  });

  describe('Tier-Specific Features', () => {
    test('should show enhanced features for VOID tier', () => {
      const voidProps = { ...defaultProps, clientTier: InvestmentTier.VOID };
      render(<InvestmentCommitmentFlow {...voidProps} />);
      
      fireEvent.click(screen.getByText('Next: Anonymous Structure'));
      
      expect(screen.getByText('Quantum-Level Anonymity')).toBeInTheDocument();
      expect(screen.getByText('Zero-Knowledge Verification')).toBeInTheDocument();
    });

    test('should limit features for ONYX tier', () => {
      const onyxProps = { ...defaultProps, clientTier: InvestmentTier.ONYX };
      render(<InvestmentCommitmentFlow {...onyxProps} />);
      
      fireEvent.click(screen.getByText('Next: Anonymous Structure'));
      
      expect(screen.queryByText('Quantum-Level Anonymity')).not.toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('should handle API errors gracefully', async () => {
      // Mock API error
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      // Navigate to final step and try to commit
      fireEvent.click(screen.getByText('Next: Anonymous Structure'));
      fireEvent.click(screen.getByText('Next: KYC Verification'));
      fireEvent.click(screen.getByText('Next: Payment Setup'));
      fireEvent.click(screen.getByText('Next: Final Review'));
      
      fireEvent.click(screen.getByLabelText('I agree to the Terms & Conditions'));
      fireEvent.click(screen.getByLabelText('I acknowledge the risk disclosures'));
      fireEvent.click(screen.getByLabelText('I confirm the investment details'));
      
      // Simulate API error by making onCommitmentComplete throw
      defaultProps.onCommitmentComplete.mockImplementation(() => {
        throw new Error('API Error');
      });
      
      const commitButton = screen.getByText('Complete Investment Commitment');
      fireEvent.click(commitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to complete commitment. Please try again.')).toBeInTheDocument();
      });
      
      consoleSpy.mockRestore();
    });

    test('should validate all steps before allowing commitment', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      // Try to navigate directly to final step without completing previous steps
      // This should not be possible in normal UI flow
      const commitButton = screen.queryByText('Complete Investment Commitment');
      expect(commitButton).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('should have proper ARIA labels and roles', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      expect(screen.getByRole('tablist')).toBeInTheDocument(); // Progress indicator
      expect(screen.getByLabelText('Investment commitment progress')).toBeInTheDocument();
    });

    test('should support keyboard navigation', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      const nextButton = screen.getByText('Next: Anonymous Structure');
      expect(nextButton).toHaveAttribute('tabIndex', '0');
    });

    test('should provide screen reader announcements for step changes', () => {
      render(<InvestmentCommitmentFlow {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Next: Anonymous Structure'));
      
      expect(screen.getByText('Step 2 of 5: Anonymous Structure')).toBeInTheDocument();
    });
  });
});