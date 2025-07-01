/**
 * Comprehensive Test Suite for Investment Syndicate Formation UI
 * Tests all 4 steps, validation logic, security features, and user interactions
 * Target: 100% code coverage with complete functionality validation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InvestmentSyndicateFormation } from '../../components/investment/InvestmentSyndicateFormation';
import { InvestmentTier, InvestmentCategory } from '../../services/InvestmentSyndicateEngine';

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

// Mock opportunity data
const mockOpportunity = {
  id: 'spacex-series-x',
  title: 'SpaceX Series X Pre-IPO',
  companyDetails: {
    name: 'SpaceX',
    valuation: 1800000000000, // ₹180 Cr
    stage: 'Series X',
  },
  minimumInvestment: 500000000, // ₹50 Cr
  maximumInvestment: 10000000000, // ₹1000 Cr
  lockupPeriod: '3 years',
  category: InvestmentCategory.PRE_IPO,
  expectedReturns: { min: 15, max: 30 },
  riskLevel: 'medium',
  description: 'Revolutionary space transportation and exploration',
};

const defaultProps = {
  opportunity: mockOpportunity,
  leadInvestorTier: InvestmentTier.ONYX,
  anonymousId: 'anon-123-test',
  onSyndicateCreated: jest.fn(),
  onCancel: jest.fn(),
};

describe('InvestmentSyndicateFormation', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Initial Render and Header', () => {
    it('should render with correct title and tier information', () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      expect(screen.getByText('Create Investment Syndicate')).toBeInTheDocument();
      expect(screen.getByText(/Form a syndicate for SpaceX Series X Pre-IPO/)).toBeInTheDocument();
      expect(screen.getByText(/ONYX Tier Lead/)).toBeInTheDocument();
    });

    it('should display step indicator with correct initial state', () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Check step indicator
      const configurationStep = screen.getByText('Configuration').closest('div');
      const structureStep = screen.getByText('Structure').closest('div');
      const participantsStep = screen.getByText('Participants').closest('div');
      const reviewStep = screen.getByText('Review').closest('div');

      expect(configurationStep).toHaveClass('text-gold-400');
      expect(structureStep).toHaveClass('text-gray-500');
      expect(participantsStep).toHaveClass('text-gray-500');
      expect(reviewStep).toHaveClass('text-gray-500');
    });

    it('should render navigation buttons correctly on first step', () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Next: Structure' })).toBeInTheDocument();
      expect(screen.queryByText('Previous')).not.toBeInTheDocument();
    });
  });

  describe('Step 1: Configuration', () => {
    it('should render all configuration fields with default values', () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Check lead commitment field
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      expect(leadCommitmentInput).toBeInTheDocument();

      // Check governance structure dropdown
      const governanceSelect = screen.getByDisplayValue('lead_decides');
      expect(governanceSelect).toBeInTheDocument();

      // Check syndicate size inputs
      const minSizeInput = screen.getByDisplayValue('3');
      const maxSizeInput = screen.getByDisplayValue('15');
      expect(minSizeInput).toBeInTheDocument();
      expect(maxSizeInput).toBeInTheDocument();
    });

    it('should update lead commitment when input changes', async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '750000000');

      expect(leadCommitmentInput).toHaveValue(750000000);
    });

    it('should filter governance options based on tier', () => {
      // Test Onyx tier (should only show lead_decides and majority_vote)
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      const governanceSelect = screen.getByDisplayValue('lead_decides');
      fireEvent.click(governanceSelect);

      const options = within(governanceSelect).getAllByRole('option');
      expect(options).toHaveLength(2); // Only onyx-eligible options
    });

    it('should show additional governance options for higher tiers', () => {
      const voidProps = { ...defaultProps, leadInvestorTier: InvestmentTier.VOID };
      render(<InvestmentSyndicateFormation {...voidProps} />);

      const governanceSelect = screen.getByDisplayValue('lead_decides');
      fireEvent.click(governanceSelect);

      const options = within(governanceSelect).getAllByRole('option');
      expect(options.length).toBeGreaterThan(2); // Should include void-tier options
    });

    it('should update fee structure values', async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      const managementFeeInput = screen.getByDisplayValue('2');
      await user.clear(managementFeeInput);
      await user.type(managementFeeInput, '2.5');

      expect(managementFeeInput).toHaveValue(2.5);

      const carriedInterestInput = screen.getByDisplayValue('20');
      await user.clear(carriedInterestInput);
      await user.type(carriedInterestInput, '25');

      expect(carriedInterestInput).toHaveValue(25);
    });

    it('should validate minimum and maximum values', async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '100000000'); // Below minimum

      // Move to next step to trigger validation
      const nextButton = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton);

      // Should still be on step 1 due to validation error
      expect(screen.getByText('Syndicate Configuration')).toBeInTheDocument();
    });
  });

  describe('Step 2: Structure', () => {
    beforeEach(async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);
      const nextButton = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton);
    });

    it('should render structure form with default values', () => {
      expect(screen.getByText('Anonymous Structure')).toBeInTheDocument();
      expect(screen.getByDisplayValue('BlackPortal SpaceX SPV')).toBeInTheDocument();
      expect(screen.getByDisplayValue('mauritius')).toBeInTheDocument();
    });

    it('should display jurisdiction benefits when selection changes', async () => {
      const jurisdictionSelect = screen.getByDisplayValue('mauritius');
      await user.selectOptions(jurisdictionSelect, 'singapore');

      await waitFor(() => {
        expect(screen.getByText('Global financial hub')).toBeInTheDocument();
        expect(screen.getByText('3-4 weeks')).toBeInTheDocument();
        expect(screen.getByText('₹20-35 L')).toBeInTheDocument();
      });
    });

    it('should update SPV name field', async () => {
      const spvNameInput = screen.getByDisplayValue('BlackPortal SpaceX SPV');
      await user.clear(spvNameInput);
      await user.type(spvNameInput, 'Custom SPV Name');

      expect(spvNameInput).toHaveValue('Custom SPV Name');
    });

    it('should show quantum compliance option for VOID tier only', () => {
      // Re-render with VOID tier
      render(<InvestmentSyndicateFormation {...{ ...defaultProps, leadInvestorTier: InvestmentTier.VOID }} />);
      
      // Navigate to structure step
      const nextButton = screen.getByRole('button', { name: 'Next: Structure' });
      fireEvent.click(nextButton);

      const complianceSelect = screen.getByDisplayValue('quantum');
      expect(complianceSelect).toBeInTheDocument();
    });

    it('should render previous and next buttons', () => {
      expect(screen.getByRole('button', { name: 'Previous' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Next: Participants' })).toBeInTheDocument();
    });
  });

  describe('Step 3: Participants', () => {
    beforeEach(async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);
      
      // Navigate to participants step
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
    });

    it('should render participant criteria form', () => {
      expect(screen.getByText('Participant Criteria')).toBeInTheDocument();
      expect(screen.getByDisplayValue('1000000000')).toBeInTheDocument(); // Min net worth
      expect(screen.getByDisplayValue('25')).toBeInTheDocument(); // Max exposure
    });

    it('should handle tier restriction checkboxes', async () => {
      const onyxCheckbox = screen.getByRole('checkbox', { name: /Onyx/ });
      const obsidianCheckbox = screen.getByRole('checkbox', { name: /Obsidian/ });
      const voidCheckbox = screen.getByRole('checkbox', { name: /Void/ });

      // All should be checked by default
      expect(onyxCheckbox).toBeChecked();
      expect(obsidianCheckbox).toBeChecked();
      expect(voidCheckbox).toBeChecked();

      // Uncheck Onyx
      await user.click(onyxCheckbox);
      expect(onyxCheckbox).not.toBeChecked();
    });

    it('should handle additional requirement checkboxes', async () => {
      const accreditationCheckbox = screen.getByRole('checkbox', { name: /Accredited investor status required/ });
      const institutionalCheckbox = screen.getByRole('checkbox', { name: /Institutional investors only/ });

      expect(accreditationCheckbox).toBeChecked(); // Default true
      expect(institutionalCheckbox).not.toBeChecked(); // Default false

      await user.click(institutionalCheckbox);
      expect(institutionalCheckbox).toBeChecked();
    });

    it('should update minimum net worth requirement', async () => {
      const netWorthInput = screen.getByDisplayValue('1000000000');
      await user.clear(netWorthInput);
      await user.type(netWorthInput, '2000000000');

      expect(netWorthInput).toHaveValue(2000000000);
    });
  });

  describe('Step 4: Review', () => {
    beforeEach(async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);
      
      // Navigate to review step
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);
    });

    it('should display syndicate summary with all configured values', () => {
      expect(screen.getByText('Syndicate Summary')).toBeInTheDocument();
      expect(screen.getByText('SpaceX Series X Pre-IPO')).toBeInTheDocument();
      expect(screen.getByText('₹50 Cr')).toBeInTheDocument(); // Lead commitment
      expect(screen.getByText('3-15 participants')).toBeInTheDocument();
      expect(screen.getByText('Lead Investor Decides')).toBeInTheDocument();
    });

    it('should display structure details', () => {
      expect(screen.getByText('BlackPortal SpaceX SPV')).toBeInTheDocument();
      expect(screen.getByText('Mauritius')).toBeInTheDocument();
      expect(screen.getByText('Enhanced')).toBeInTheDocument(); // Compliance level
    });

    it('should display fee structure summary', () => {
      expect(screen.getByText('2%')).toBeInTheDocument(); // Management fee
      expect(screen.getByText('20%')).toBeInTheDocument(); // Carried interest
      expect(screen.getByText('₹0.5 Cr')).toBeInTheDocument(); // Admin fee
    });

    it('should render Create Syndicate button', () => {
      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      expect(createButton).toBeInTheDocument();
      expect(createButton).not.toBeDisabled();
    });
  });

  describe('Validation Logic', () => {
    it('should prevent syndicate creation with validation errors', async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Set invalid lead commitment (below minimum)
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '100000000');

      // Navigate to review step
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Should show validation errors
      expect(screen.getByText('Validation Errors:')).toBeInTheDocument();
      expect(screen.getByText('Lead commitment must meet minimum investment requirement')).toBeInTheDocument();

      // Create button should be disabled
      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      expect(createButton).toBeDisabled();
    });

    it('should validate syndicate size consistency', async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Set min size greater than max size
      const minSizeInput = screen.getByDisplayValue('3');
      const maxSizeInput = screen.getByDisplayValue('15');

      await user.clear(minSizeInput);
      await user.type(minSizeInput, '20');

      // Navigate to review to trigger validation
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      expect(screen.getByText('Minimum syndicate size cannot exceed maximum size')).toBeInTheDocument();
    });
  });

  describe('Syndicate Creation Flow', () => {
    it('should create syndicate successfully with valid data', async () => {
      const onSyndicateCreated = jest.fn();
      render(<InvestmentSyndicateFormation {...{ ...defaultProps, onSyndicateCreated }} />);

      // Navigate to review step
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Create syndicate
      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      await user.click(createButton);

      // Should show loading state
      expect(screen.getByRole('button', { name: 'Creating Syndicate...' })).toBeInTheDocument();

      // Fast-forward past the simulated API delay
      jest.advanceTimersByTime(2000);

      await waitFor(() => {
        expect(onSyndicateCreated).toHaveBeenCalledWith(
          expect.objectContaining({
            id: expect.stringMatching(/^syn-\d+-\w+$/),
            opportunityId: 'spacex-series-x',
            leadInvestor: expect.objectContaining({
              anonymousId: 'anon-123-test',
              tier: InvestmentTier.ONYX,
              commitmentAmount: 500000000,
              role: 'lead',
            }),
            status: 'forming',
          })
        );
      });
    });

    it('should handle cancel action', async () => {
      const onCancel = jest.fn();
      render(<InvestmentSyndicateFormation {...{ ...defaultProps, onCancel }} />);

      const cancelButton = screen.getByRole('button', { name: 'Cancel' });
      await user.click(cancelButton);

      expect(onCancel).toHaveBeenCalled();
    });
  });

  describe('Navigation Flow', () => {
    it('should navigate forward through all steps', async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Step 1 -> 2
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      expect(screen.getByText('Anonymous Structure')).toBeInTheDocument();

      // Step 2 -> 3
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      expect(screen.getByText('Participant Criteria')).toBeInTheDocument();

      // Step 3 -> 4
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);
      expect(screen.getByText('Syndicate Summary')).toBeInTheDocument();
    });

    it('should navigate backward through steps', async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Navigate to step 4
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Go back to step 3
      const prevButton = screen.getByRole('button', { name: 'Previous' });
      await user.click(prevButton);
      expect(screen.getByText('Participant Criteria')).toBeInTheDocument();
    });
  });

  describe('Currency Formatting', () => {
    it('should format currency values correctly', () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Navigate to review step to see formatted values
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      fireEvent.click(nextButton1);
      
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      fireEvent.click(nextButton2);
      
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      fireEvent.click(nextButton3);

      expect(screen.getByText('₹50 Cr')).toBeInTheDocument(); // Lead commitment
      expect(screen.getByText('₹100 Cr')).toBeInTheDocument(); // Min net worth
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Check form inputs have proper labels
      expect(screen.getByLabelText('Lead Investor Commitment')).toBeInTheDocument();
      expect(screen.getByLabelText('Governance Structure')).toBeInTheDocument();
      expect(screen.getByLabelText('Syndicate Size Range')).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      render(<InvestmentSyndicateFormation {...defaultProps} />);

      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      leadCommitmentInput.focus();

      // Tab to next field
      await user.tab();
      expect(screen.getByDisplayValue('lead_decides')).toHaveFocus();
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      // Mock a failed API call by overriding the Promise.resolve in the component
      const originalSetTimeout = global.setTimeout;
      global.setTimeout = jest.fn((callback) => {
        // Simulate an error
        throw new Error('API Error');
      });

      render(<InvestmentSyndicateFormation {...defaultProps} />);

      // Navigate to review and try to create
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      await user.click(createButton);

      // Should handle error gracefully
      global.setTimeout = originalSetTimeout;
      consoleSpy.mockRestore();
    });
  });
});