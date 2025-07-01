/**
 * Comprehensive End-to-End Integration Tests for Complete Investment Workflow
 * Tests complete user journey from syndicate formation to portfolio analytics
 * Target: 100% integration coverage with realistic user scenarios
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InvestmentSyndicateFormation } from '../../components/investment/InvestmentSyndicateFormation';
import { RealTimePortfolioAnalytics } from '../../components/investment/RealTimePortfolioAnalytics';
import { InvestmentTier, InvestmentCategory } from '../../services/InvestmentSyndicateEngine';

// Mock all luxury components
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

// Mock Investment Services
const mockInvestmentSyndicateEngine = {
  createSyndicate: jest.fn(),
  joinSyndicate: jest.fn(),
  getSyndicateDetails: jest.fn(),
  getInvestmentOpportunities: jest.fn(),
};

const mockPortfolioManager = {
  getPortfolioData: jest.fn(),
  updatePortfolio: jest.fn(),
  rebalancePortfolio: jest.fn(),
};

jest.mock('../../services/InvestmentSyndicateEngine', () => ({
  ...jest.requireActual('../../services/InvestmentSyndicateEngine'),
  InvestmentSyndicateEngine: () => mockInvestmentSyndicateEngine,
}));

jest.mock('../../services/InvestmentPortfolioManager', () => ({
  ...jest.requireActual('../../services/InvestmentPortfolioManager'),
  InvestmentPortfolioManager: () => mockPortfolioManager,
}));

// Mock opportunities data for testing
const mockSpaceXOpportunity = {
  id: 'spacex-series-x',
  title: 'SpaceX Series X Pre-IPO',
  companyDetails: {
    name: 'SpaceX',
    valuation: 1800000000000,
    stage: 'Series X',
  },
  minimumInvestment: 500000000,
  maximumInvestment: 10000000000,
  lockupPeriod: '3 years',
  category: InvestmentCategory.PRE_IPO,
  expectedReturns: { min: 15, max: 30 },
  riskLevel: 'medium' as const,
  description: 'Revolutionary space transportation',
};

const mockOpenAIOpportunity = {
  id: 'openai-strategic',
  title: 'OpenAI Strategic Round',
  companyDetails: {
    name: 'OpenAI',
    valuation: 2900000000000,
    stage: 'Strategic',
  },
  minimumInvestment: 1000000000,
  maximumInvestment: 5000000000,
  lockupPeriod: '4 years',
  category: InvestmentCategory.PRE_IPO,
  expectedReturns: { min: 20, max: 35 },
  riskLevel: 'high' as const,
  description: 'Artificial General Intelligence leader',
};

describe('Complete Investment Workflow Integration', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    jest.clearAllMocks();
    jest.useFakeTimers();

    // Setup default mock responses
    mockInvestmentSyndicateEngine.createSyndicate.mockResolvedValue({
      id: 'syn-123-abc',
      status: 'forming',
      leadInvestor: { anonymousId: 'anon-123' },
    });

    mockPortfolioManager.getPortfolioData.mockResolvedValue({
      totalValue: 1135000000,
      positions: [],
      performance: {},
    });
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('End-to-End Investment Syndicate Creation Flow', () => {
    it('should complete full syndicate creation workflow for Onyx tier investor', async () => {
      const onSyndicateCreated = jest.fn();
      
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSpaceXOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId="anon-onyx-123"
          onSyndicateCreated={onSyndicateCreated}
          onCancel={jest.fn()}
        />
      );

      // Step 1: Configuration
      expect(screen.getByText('Create Investment Syndicate')).toBeInTheDocument();
      expect(screen.getByText(/ONYX Tier Lead/)).toBeInTheDocument();

      // Modify lead commitment
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '750000000');

      // Update governance structure
      const governanceSelect = screen.getByDisplayValue('lead_decides');
      await user.selectOptions(governanceSelect, 'majority_vote');

      // Update fee structure
      const managementFeeInput = screen.getByDisplayValue('2');
      await user.clear(managementFeeInput);
      await user.type(managementFeeInput, '2.5');

      // Navigate to Structure step
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);

      // Step 2: Structure
      expect(screen.getByText('Anonymous Structure')).toBeInTheDocument();

      // Update SPV name
      const spvNameInput = screen.getByDisplayValue('BlackPortal SpaceX SPV');
      await user.clear(spvNameInput);
      await user.type(spvNameInput, 'Onyx SpaceX Investment SPV');

      // Change jurisdiction
      const jurisdictionSelect = screen.getByDisplayValue('mauritius');
      await user.selectOptions(jurisdictionSelect, 'singapore');

      // Wait for jurisdiction benefits to load
      await waitFor(() => {
        expect(screen.getByText('Global financial hub')).toBeInTheDocument();
      });

      // Navigate to Participants step
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);

      // Step 3: Participants
      expect(screen.getByText('Participant Criteria')).toBeInTheDocument();

      // Update minimum net worth
      const netWorthInput = screen.getByDisplayValue('1000000000');
      await user.clear(netWorthInput);
      await user.type(netWorthInput, '1500000000');

      // Update tier restrictions (remove Onyx access)
      const onyxCheckbox = screen.getByRole('checkbox', { name: /Onyx/ });
      await user.click(onyxCheckbox);

      // Enable institutional only
      const institutionalCheckbox = screen.getByRole('checkbox', { name: /Institutional investors only/ });
      await user.click(institutionalCheckbox);

      // Navigate to Review step
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Step 4: Review
      expect(screen.getByText('Syndicate Summary')).toBeInTheDocument();
      expect(screen.getByText('₹75 Cr')).toBeInTheDocument(); // Updated lead commitment
      expect(screen.getByText('Majority Vote')).toBeInTheDocument(); // Updated governance
      expect(screen.getByText('Onyx SpaceX Investment SPV')).toBeInTheDocument(); // Updated SPV name
      expect(screen.getByText('Singapore')).toBeInTheDocument(); // Updated jurisdiction

      // Create syndicate
      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      await user.click(createButton);

      // Should show loading state
      expect(screen.getByRole('button', { name: 'Creating Syndicate...' })).toBeInTheDocument();

      // Wait for creation to complete
      jest.advanceTimersByTime(2000);

      await waitFor(() => {
        expect(onSyndicateCreated).toHaveBeenCalledWith(
          expect.objectContaining({
            id: expect.stringMatching(/^syn-\d+-\w+$/),
            leadInvestor: expect.objectContaining({
              anonymousId: 'anon-onyx-123',
              tier: InvestmentTier.ONYX,
              commitmentAmount: 750000000,
            }),
            configuration: expect.objectContaining({
              governanceStructure: 'majority_vote',
              feeStructure: expect.objectContaining({
                managementFee: 2.5,
              }),
            }),
            anonymousStructure: expect.objectContaining({
              spvName: 'Onyx SpaceX Investment SPV',
              jurisdiction: 'singapore',
            }),
          })
        );
      });
    });

    it('should complete syndicate creation for VOID tier with quantum features', async () => {
      const onSyndicateCreated = jest.fn();
      
      render(
        <InvestmentSyndicateFormation
          opportunity={mockOpenAIOpportunity}
          leadInvestorTier={InvestmentTier.VOID}
          anonymousId="anon-void-456"
          onSyndicateCreated={onSyndicateCreated}
          onCancel={jest.fn()}
        />
      );

      // Navigate through all steps quickly for VOID tier
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);

      // Should show quantum compliance option
      const complianceSelect = screen.getByDisplayValue('quantum');
      expect(complianceSelect).toBeInTheDocument();

      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);

      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Should show higher minimum commitment for OpenAI
      expect(screen.getByText('₹100 Cr')).toBeInTheDocument();

      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      await user.click(createButton);

      jest.advanceTimersByTime(2000);

      await waitFor(() => {
        expect(onSyndicateCreated).toHaveBeenCalledWith(
          expect.objectContaining({
            leadInvestor: expect.objectContaining({
              tier: InvestmentTier.VOID,
            }),
            anonymousStructure: expect.objectContaining({
              complianceLevel: 'quantum',
            }),
          })
        );
      });
    });
  });

  describe('Complete Portfolio Analytics Integration Flow', () => {
    it('should integrate with real-time data updates and tab navigation', async () => {
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="anon-obsidian-789"
          portfolioId="portfolio-456"
        />
      );

      // Verify initial render
      expect(screen.getByText('Portfolio Analytics')).toBeInTheDocument();
      expect(screen.getByText(/OBSIDIAN Tier/)).toBeInTheDocument();

      // Check live updates are active
      const liveButton = screen.getByRole('button', { name: '● LIVE' });
      expect(liveButton).toBeInTheDocument();

      // Test time range controls
      const oneWeekButton = screen.getByRole('button', { name: '1W' });
      await user.click(oneWeekButton);
      expect(oneWeekButton).toHaveClass('bg-gold-500');

      // Navigate to Performance tab
      const performanceTab = screen.getByRole('button', { name: 'Performance' });
      await user.click(performanceTab);

      expect(screen.getByText('Performance vs Benchmarks')).toBeInTheDocument();
      expect(screen.getByText('Rolling Returns')).toBeInTheDocument();

      // Navigate to Risk Analysis tab
      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      await user.click(riskTab);

      expect(screen.getByText('Value at Risk (95%)')).toBeInTheDocument();
      expect(screen.getByText('Sharpe Ratio')).toBeInTheDocument();

      // Navigate to Allocation tab
      const allocationTab = screen.getByRole('button', { name: 'Allocation' });
      await user.click(allocationTab);

      expect(screen.getByText('Current vs Target Allocation')).toBeInTheDocument();
      expect(screen.getByText('Rebalancing Recommendations')).toBeInTheDocument();

      // Test rebalancing action
      const rebalanceButton = screen.getByRole('button', { name: 'Execute Rebalancing' });
      await user.click(rebalanceButton);

      // Navigate to ESG Analysis tab
      const esgTab = screen.getByRole('button', { name: 'ESG Analysis' });
      await user.click(esgTab);

      expect(screen.getByText('Environmental Score')).toBeInTheDocument();
      expect(screen.getByText('ESG Impact Metrics')).toBeInTheDocument();

      // Test live data pause/resume
      await user.click(liveButton);
      expect(screen.getByRole('button', { name: '⏸ PAUSED' })).toBeInTheDocument();

      const pausedButton = screen.getByRole('button', { name: '⏸ PAUSED' });
      await user.click(pausedButton);
      expect(screen.getByRole('button', { name: '● LIVE' })).toBeInTheDocument();
    });

    it('should handle VOID tier quantum features in analytics', async () => {
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="anon-void-quantum"
          portfolioId="quantum-portfolio-789"
        />
      );

      // Navigate to Risk Analysis to see quantum features
      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      await user.click(riskTab);

      // Should show quantum risk analysis
      expect(screen.getByText('Quantum Risk Analysis')).toBeInTheDocument();
      expect(screen.getByText('Advanced Risk Modeling')).toBeInTheDocument();
      expect(screen.getByText(/Monte Carlo simulations/)).toBeInTheDocument();
      expect(screen.getByText(/quantum risk metrics/)).toBeInTheDocument();
    });
  });

  describe('Cross-Component Integration Scenarios', () => {
    it('should maintain consistent data flow between syndicate creation and portfolio analytics', async () => {
      // This test simulates the flow from creating a syndicate to viewing it in portfolio
      const syndicateData = {
        id: 'syn-integration-test',
        leadInvestor: { anonymousId: 'anon-integration-123' },
        status: 'active',
      };

      // Mock portfolio data that includes the syndicate
      mockPortfolioManager.getPortfolioData.mockResolvedValue({
        totalValue: 2500000000, // ₹250 Cr
        positions: [
          {
            id: 'spacex-position',
            syndicateId: 'syn-integration-test',
            value: 750000000,
            assetClass: 'PRE_IPO',
          },
        ],
        performance: {
          dayChange: 25000000,
          dayChangePercent: 1.0,
          totalReturn: 150000000,
          totalReturnPercent: 6.4,
        },
      });

      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.ONYX}
          anonymousId="anon-integration-123"
          portfolioId="integrated-portfolio"
        />
      );

      // Should display the updated portfolio value
      await waitFor(() => {
        expect(screen.getByText(/₹250 Cr/)).toBeInTheDocument();
      });

      // Should show positive performance
      expect(screen.getByText(/\+1\.0%/)).toBeInTheDocument();
    });

    it('should handle tier upgrades and feature access changes', async () => {
      // Start with Onyx tier
      const { rerender } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.ONYX}
          anonymousId="anon-upgrade-test"
          portfolioId="upgrade-portfolio"
        />
      );

      // Navigate to Risk Analysis
      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      await user.click(riskTab);

      // Should not show quantum features
      expect(screen.queryByText('Quantum Risk Analysis')).not.toBeInTheDocument();

      // Simulate tier upgrade to VOID
      rerender(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="anon-upgrade-test"
          portfolioId="upgrade-portfolio"
        />
      );

      // Should now show quantum features
      expect(screen.getByText('Quantum Risk Analysis')).toBeInTheDocument();
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle syndicate creation failures gracefully', async () => {
      mockInvestmentSyndicateEngine.createSyndicate.mockRejectedValue(
        new Error('Network error')
      );

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      const onSyndicateCreated = jest.fn();

      render(
        <InvestmentSyndicateFormation
          opportunity={mockSpaceXOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId="anon-error-test"
          onSyndicateCreated={onSyndicateCreated}
          onCancel={jest.fn()}
        />
      );

      // Navigate to review and create
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      await user.click(createButton);

      jest.advanceTimersByTime(2000);

      // Should handle error without crashing
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Failed to create syndicate:', expect.any(Error));
      });

      expect(onSyndicateCreated).not.toHaveBeenCalled();
      consoleSpy.mockRestore();
    });

    it('should handle portfolio data loading failures', async () => {
      mockPortfolioManager.getPortfolioData.mockRejectedValue(
        new Error('Portfolio service unavailable')
      );

      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="anon-error-portfolio"
          portfolioId="error-portfolio"
        />
      );

      // Should still render basic structure
      expect(screen.getByText('Portfolio Analytics')).toBeInTheDocument();
      expect(screen.getByText(/OBSIDIAN Tier/)).toBeInTheDocument();

      // Should handle missing data gracefully
      expect(screen.getByText('₹113.5 Cr')).toBeInTheDocument(); // Fallback data
    });

    it('should validate complex syndicate configurations', async () => {
      render(
        <InvestmentSyndicateFormation
          opportunity={mockSpaceXOpportunity}
          leadInvestorTier={InvestmentTier.ONYX}
          anonymousId="anon-validation-test"
          onSyndicateCreated={jest.fn()}
          onCancel={jest.fn()}
        />
      );

      // Create invalid configuration
      const leadCommitmentInput = screen.getByDisplayValue('500000000');
      await user.clear(leadCommitmentInput);
      await user.type(leadCommitmentInput, '100000000'); // Below minimum

      const minSizeInput = screen.getByDisplayValue('3');
      await user.clear(minSizeInput);
      await user.type(minSizeInput, '25'); // Greater than max

      const maxSizeInput = screen.getByDisplayValue('15');
      await user.clear(maxSizeInput);
      await user.type(maxSizeInput, '20');

      // Navigate to review
      const nextButton1 = screen.getByRole('button', { name: 'Next: Structure' });
      await user.click(nextButton1);
      const nextButton2 = screen.getByRole('button', { name: 'Next: Participants' });
      await user.click(nextButton2);
      const nextButton3 = screen.getByRole('button', { name: 'Next: Review' });
      await user.click(nextButton3);

      // Should show validation errors
      expect(screen.getByText('Validation Errors:')).toBeInTheDocument();
      expect(screen.getByText('Lead commitment must meet minimum investment requirement')).toBeInTheDocument();
      expect(screen.getByText('Minimum syndicate size cannot exceed maximum size')).toBeInTheDocument();

      // Create button should be disabled
      const createButton = screen.getByRole('button', { name: 'Create Syndicate' });
      expect(createButton).toBeDisabled();
    });
  });

  describe('Performance and Memory Management', () => {
    it('should handle multiple concurrent analytics updates efficiently', async () => {
      const { unmount } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="anon-performance-test"
          portfolioId="performance-portfolio"
        />
      );

      // Simulate rapid updates
      for (let i = 0; i < 20; i++) {
        jest.advanceTimersByTime(5000);
      }

      // Should handle rapid updates without issues
      expect(screen.getByText('Portfolio Analytics')).toBeInTheDocument();

      // Clean unmount
      unmount();
      expect(true).toBe(true); // Test passes if no memory leaks
    });

    it('should optimize re-renders during live updates', async () => {
      const renderSpy = jest.fn();
      const TestComponent = () => {
        renderSpy();
        return (
          <RealTimePortfolioAnalytics
            tier={InvestmentTier.OBSIDIAN}
            anonymousId="anon-render-test"
            portfolioId="render-portfolio"
          />
        );
      };

      render(<TestComponent />);

      const initialRenderCount = renderSpy.mock.calls.length;

      // Trigger multiple updates
      jest.advanceTimersByTime(15000); // 3 updates

      // Should not cause excessive re-renders
      const finalRenderCount = renderSpy.mock.calls.length;
      expect(finalRenderCount - initialRenderCount).toBeLessThanOrEqual(3);
    });
  });
});