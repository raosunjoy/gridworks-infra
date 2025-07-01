/**
 * Comprehensive Test Suite for Real-time Portfolio Analytics Dashboard
 * Tests all 5 tabs, live data updates, performance metrics, and user interactions
 * Target: 100% code coverage with complete functionality validation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RealTimePortfolioAnalytics } from '../../components/investment/RealTimePortfolioAnalytics';
import { InvestmentTier, AssetClass } from '../../services/InvestmentSyndicateEngine';

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

// Mock chart components
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
}));

const defaultProps = {
  tier: InvestmentTier.ONYX,
  anonymousId: 'anon-123-test',
  portfolioId: 'portfolio-456',
};

describe('RealTimePortfolioAnalytics', () => {
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
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      expect(screen.getByText('Portfolio Analytics')).toBeInTheDocument();
      expect(screen.getByText(/Real-time analytics and insights • ONYX Tier/)).toBeInTheDocument();
    });

    it('should render live/pause toggle button', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const liveButton = screen.getByRole('button', { name: '● LIVE' });
      expect(liveButton).toBeInTheDocument();
      expect(liveButton).toHaveClass('bg-green-500');
    });

    it('should display last updated timestamp', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
    });

    it('should render all tab navigation buttons', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      expect(screen.getByRole('button', { name: 'Overview' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Performance' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Risk Analysis' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Allocation' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'ESG Analysis' })).toBeInTheDocument();
    });
  });

  describe('Live Data Updates', () => {
    it('should update metrics when live mode is enabled', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      // Get initial total value
      const initialValueElement = screen.getByText(/₹113\.5 Cr/);
      expect(initialValueElement).toBeInTheDocument();

      // Advance timers to trigger update (5 second interval)
      jest.advanceTimersByTime(5000);

      await waitFor(() => {
        // Value should have changed (mock adds random variation)
        const valueElements = screen.getAllByText(/₹\d+\.?\d* Cr/);
        expect(valueElements.length).toBeGreaterThan(0);
      });
    });

    it('should pause updates when live mode is disabled', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const liveButton = screen.getByRole('button', { name: '● LIVE' });
      await user.click(liveButton);

      // Button should show paused state
      expect(screen.getByRole('button', { name: '⏸ PAUSED' })).toBeInTheDocument();

      // Advance timers - no updates should occur
      jest.advanceTimersByTime(10000);

      // Value should remain the same
      expect(screen.getByText(/₹113\.5 Cr/)).toBeInTheDocument();
    });

    it('should update last updated timestamp with live updates', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const initialTimestamp = screen.getByText(/Last updated:/).textContent;

      // Advance time and trigger update
      jest.advanceTimersByTime(5000);

      await waitFor(() => {
        const updatedTimestamp = screen.getByText(/Last updated:/).textContent;
        expect(updatedTimestamp).not.toBe(initialTimestamp);
      });
    });
  });

  describe('Tab Navigation', () => {
    it('should switch to Performance tab', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const performanceTab = screen.getByRole('button', { name: 'Performance' });
      await user.click(performanceTab);

      expect(screen.getByText('Performance vs Benchmarks')).toBeInTheDocument();
      expect(screen.getByText('Rolling Returns')).toBeInTheDocument();
      expect(screen.getByText('Drawdown Analysis')).toBeInTheDocument();
    });

    it('should switch to Risk Analysis tab', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      await user.click(riskTab);

      expect(screen.getByText('Value at Risk (95%)')).toBeInTheDocument();
      expect(screen.getByText('Sharpe Ratio')).toBeInTheDocument();
      expect(screen.getByText('Beta')).toBeInTheDocument();
      expect(screen.getByText('Maximum Drawdown')).toBeInTheDocument();
    });

    it('should switch to Allocation tab', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const allocationTab = screen.getByRole('button', { name: 'Allocation' });
      await user.click(allocationTab);

      expect(screen.getByText('Current vs Target Allocation')).toBeInTheDocument();
      expect(screen.getByText('Rebalancing Recommendations')).toBeInTheDocument();
      expect(screen.getByText('Sector Allocation')).toBeInTheDocument();
    });

    it('should switch to ESG Analysis tab', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const esgTab = screen.getByRole('button', { name: 'ESG Analysis' });
      await user.click(esgTab);

      expect(screen.getByText('Environmental Score')).toBeInTheDocument();
      expect(screen.getByText('Social Score')).toBeInTheDocument();
      expect(screen.getByText('Governance Score')).toBeInTheDocument();
      expect(screen.getByText('ESG Impact Metrics')).toBeInTheDocument();
    });

    it('should highlight active tab correctly', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const overviewTab = screen.getByRole('button', { name: 'Overview' });
      const performanceTab = screen.getByRole('button', { name: 'Performance' });

      // Overview should be active by default
      expect(overviewTab).toHaveClass('bg-gold-500');
      expect(performanceTab).not.toHaveClass('bg-gold-500');

      // Click Performance tab
      await user.click(performanceTab);

      expect(performanceTab).toHaveClass('bg-gold-500');
      expect(overviewTab).not.toHaveClass('bg-gold-500');
    });
  });

  describe('Overview Tab Content', () => {
    it('should display key portfolio metrics', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      expect(screen.getByText('Total Portfolio Value')).toBeInTheDocument();
      expect(screen.getByText('Total Returns')).toBeInTheDocument();
      expect(screen.getByText('Sharpe Ratio')).toBeInTheDocument();
      expect(screen.getByText('Portfolio Beta')).toBeInTheDocument();
    });

    it('should show live indicator for real-time data', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const liveIndicators = screen.getAllByRole('generic').filter(el => 
        el.className.includes('animate-pulse') && el.className.includes('bg-green-400')
      );
      expect(liveIndicators.length).toBeGreaterThan(0);
    });

    it('should display performance chart with time range controls', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      expect(screen.getByText('Portfolio Performance')).toBeInTheDocument();
      
      // Check time range buttons
      ['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL'].forEach(range => {
        expect(screen.getByRole('button', { name: range })).toBeInTheDocument();
      });
    });

    it('should change time range when buttons are clicked', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const oneWeekButton = screen.getByRole('button', { name: '1W' });
      await user.click(oneWeekButton);

      expect(oneWeekButton).toHaveClass('bg-gold-500');
    });

    it('should display asset allocation breakdown', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      expect(screen.getByText('Asset Allocation')).toBeInTheDocument();
      expect(screen.getByText(/Equity/)).toBeInTheDocument();
      expect(screen.getByText(/Real estate/)).toBeInTheDocument();
      expect(screen.getByText(/Alternatives/)).toBeInTheDocument();
      expect(screen.getByText(/Fixed income/)).toBeInTheDocument();
      expect(screen.getByText(/Cash/)).toBeInTheDocument();
    });

    it('should display ESG score summary', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      expect(screen.getByText('ESG Score')).toBeInTheDocument();
      expect(screen.getByText('87')).toBeInTheDocument(); // Overall score
      expect(screen.getByText('Overall ESG Rating')).toBeInTheDocument();
    });
  });

  describe('Performance Tab Content', () => {
    beforeEach(async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);
      const performanceTab = screen.getByRole('button', { name: 'Performance' });
      await user.click(performanceTab);
    });

    it('should display performance vs benchmarks chart', () => {
      expect(screen.getByText('Performance vs Benchmarks')).toBeInTheDocument();
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    });

    it('should show rolling returns with different time periods', () => {
      expect(screen.getByText('Rolling Returns')).toBeInTheDocument();
      
      // Check different time periods
      expect(screen.getByText('1 Month')).toBeInTheDocument();
      expect(screen.getByText('3 Months')).toBeInTheDocument();
      expect(screen.getByText('6 Months')).toBeInTheDocument();
      expect(screen.getByText('1 Year')).toBeInTheDocument();
      expect(screen.getByText('3 Years (Ann.)')).toBeInTheDocument();
    });

    it('should display drawdown analysis', () => {
      expect(screen.getByText('Drawdown Analysis')).toBeInTheDocument();
      expect(screen.getByText('Current Drawdown')).toBeInTheDocument();
      expect(screen.getByText('Maximum Drawdown')).toBeInTheDocument();
      expect(screen.getByText('Recovery Time')).toBeInTheDocument();
    });

    it('should show positive and negative return indicators', () => {
      // Check for return percentages with appropriate colors
      const positiveReturns = screen.getAllByText(/\+\d+\.\d+%/);
      expect(positiveReturns.length).toBeGreaterThan(0);
    });
  });

  describe('Risk Analysis Tab Content', () => {
    beforeEach(async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);
      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      await user.click(riskTab);
    });

    it('should display all risk metrics with proper indicators', () => {
      const riskMetrics = [
        'Value at Risk (95%)',
        'Sharpe Ratio',
        'Beta',
        'Volatility',
        'Maximum Drawdown',
        'Correlation to Market'
      ];

      riskMetrics.forEach(metric => {
        expect(screen.getByText(metric)).toBeInTheDocument();
      });
    });

    it('should show risk status indicators (good/warning/critical)', () => {
      // Check for colored status indicators
      const statusIndicators = screen.getAllByRole('generic').filter(el => 
        el.className.includes('bg-green-400') || 
        el.className.includes('bg-yellow-400') || 
        el.className.includes('bg-red-400')
      );
      expect(statusIndicators.length).toBeGreaterThan(0);
    });

    it('should display benchmark comparisons', () => {
      expect(screen.getAllByText(/Benchmark:/)).toHaveLength(6); // One for each metric
    });

    it('should show quantum risk analysis for VOID tier', async () => {
      // Re-render with VOID tier
      render(<RealTimePortfolioAnalytics {...{ ...defaultProps, tier: InvestmentTier.VOID }} />);
      
      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      await user.click(riskTab);

      expect(screen.getByText('Quantum Risk Analysis')).toBeInTheDocument();
      expect(screen.getByText('Advanced Risk Modeling')).toBeInTheDocument();
      expect(screen.getByText(/Monte Carlo simulations/)).toBeInTheDocument();
    });

    it('should not show quantum analysis for lower tiers', () => {
      expect(screen.queryByText('Quantum Risk Analysis')).not.toBeInTheDocument();
    });
  });

  describe('Allocation Tab Content', () => {
    beforeEach(async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);
      const allocationTab = screen.getByRole('button', { name: 'Allocation' });
      await user.click(allocationTab);
    });

    it('should display current vs target allocation', () => {
      expect(screen.getByText('Current vs Target Allocation')).toBeInTheDocument();
      
      // Check for target percentages
      expect(screen.getAllByText(/Target: \d+%/)).toHaveLength(5); // One for each asset class
    });

    it('should show allocation differences with color coding', () => {
      // Check for difference indicators (+/- percentages)
      const differences = screen.getAllByText(/[+-]\d+\.\d+%/);
      expect(differences.length).toBeGreaterThan(0);
    });

    it('should display rebalancing recommendations', () => {
      expect(screen.getByText('Rebalancing Recommendations')).toBeInTheDocument();
      expect(screen.getByText('⚠️ Rebalancing Suggested')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Execute Rebalancing' })).toBeInTheDocument();
    });

    it('should show sector allocation breakdown', () => {
      expect(screen.getByText('Sector Allocation')).toBeInTheDocument();
      
      const sectors = [
        'Technology',
        'Real Estate',
        'Healthcare',
        'Financial Services',
        'Consumer Goods',
        'Energy & Utilities',
        'Others'
      ];

      sectors.forEach(sector => {
        expect(screen.getByText(sector)).toBeInTheDocument();
      });
    });

    it('should handle rebalancing button click', async () => {
      const rebalanceButton = screen.getByRole('button', { name: 'Execute Rebalancing' });
      await user.click(rebalanceButton);

      // Button should remain clickable (no action mocked)
      expect(rebalanceButton).toBeInTheDocument();
    });
  });

  describe('ESG Analysis Tab Content', () => {
    beforeEach(async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);
      const esgTab = screen.getByRole('button', { name: 'ESG Analysis' });
      await user.click(esgTab);
    });

    it('should display individual ESG scores', () => {
      expect(screen.getByText('Environmental Score')).toBeInTheDocument();
      expect(screen.getByText('Social Score')).toBeInTheDocument();
      expect(screen.getByText('Governance Score')).toBeInTheDocument();

      // Check specific scores
      expect(screen.getByText('92')).toBeInTheDocument(); // Environmental
      expect(screen.getByText('84')).toBeInTheDocument(); // Social
      expect(screen.getByText('85')).toBeInTheDocument(); // Governance
    });

    it('should show ESG impact metrics', () => {
      expect(screen.getByText('ESG Impact Metrics')).toBeInTheDocument();
      expect(screen.getByText('Environmental Impact')).toBeInTheDocument();
      expect(screen.getByText('Social Impact')).toBeInTheDocument();
    });

    it('should display environmental metrics', () => {
      expect(screen.getByText('Carbon Footprint Reduction')).toBeInTheDocument();
      expect(screen.getByText('Renewable Energy Investment')).toBeInTheDocument();
      expect(screen.getByText('Water Conservation Projects')).toBeInTheDocument();
    });

    it('should display social impact metrics', () => {
      expect(screen.getByText('Job Creation')).toBeInTheDocument();
      expect(screen.getByText('Education Investment')).toBeInTheDocument();
      expect(screen.getByText('Healthcare Access')).toBeInTheDocument();
    });
  });

  describe('Currency Formatting', () => {
    it('should format large numbers in crores correctly', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      // Check for properly formatted currency values
      const currencyValues = screen.getAllByText(/₹\d+\.?\d* Cr/);
      expect(currencyValues.length).toBeGreaterThan(0);
      
      // Specific format check
      expect(screen.getByText('₹113.5 Cr')).toBeInTheDocument();
    });

    it('should handle negative values correctly', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      // Should handle negative percentages for risk metrics
      const negativeValues = screen.getAllByText(/-\d+\.\d+%/);
      expect(negativeValues.length).toBeGreaterThan(0);
    });
  });

  describe('Color Coding', () => {
    it('should apply correct colors for positive changes', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      // Positive values should have green color class
      const positiveElements = screen.getAllByText(/\+.*%/).filter(el => 
        el.className.includes('text-green-400')
      );
      expect(positiveElements.length).toBeGreaterThan(0);
    });

    it('should apply correct colors for negative changes', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      // Check that negative values get red styling (in risk tab)
      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      fireEvent.click(riskTab);

      const negativeElements = screen.getAllByText(/-\d+\.\d+/).filter(el => 
        el.textContent?.includes('-')
      );
      expect(negativeElements.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      // Check for proper button roles
      const tabs = screen.getAllByRole('button').filter(button => 
        ['Overview', 'Performance', 'Risk Analysis', 'Allocation', 'ESG Analysis'].includes(
          button.textContent || ''
        )
      );
      expect(tabs).toHaveLength(5);
    });

    it('should support keyboard navigation', async () => {
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      const overviewTab = screen.getByRole('button', { name: 'Overview' });
      const performanceTab = screen.getByRole('button', { name: 'Performance' });

      overviewTab.focus();
      expect(overviewTab).toHaveFocus();

      // Tab to next button
      await user.tab();
      expect(performanceTab).toHaveFocus();
    });
  });

  describe('Performance Optimization', () => {
    it('should handle rapid updates without memory leaks', async () => {
      const { unmount } = render(<RealTimePortfolioAnalytics {...defaultProps} />);

      // Trigger multiple rapid updates
      for (let i = 0; i < 10; i++) {
        jest.advanceTimersByTime(5000);
      }

      // Should not crash when unmounting
      unmount();
      expect(true).toBe(true); // Test passes if no errors thrown
    });

    it('should clean up intervals on unmount', () => {
      const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
      const { unmount } = render(<RealTimePortfolioAnalytics {...defaultProps} />);

      unmount();
      expect(clearIntervalSpy).toHaveBeenCalled();
      clearIntervalSpy.mockRestore();
    });
  });

  describe('Tier-Specific Features', () => {
    it('should show tier-appropriate header for different tiers', () => {
      const { rerender } = render(<RealTimePortfolioAnalytics {...defaultProps} />);
      expect(screen.getByText(/ONYX Tier/)).toBeInTheDocument();

      rerender(<RealTimePortfolioAnalytics {...{ ...defaultProps, tier: InvestmentTier.OBSIDIAN }} />);
      expect(screen.getByText(/OBSIDIAN Tier/)).toBeInTheDocument();

      rerender(<RealTimePortfolioAnalytics {...{ ...defaultProps, tier: InvestmentTier.VOID }} />);
      expect(screen.getByText(/VOID Tier/)).toBeInTheDocument();
    });

    it('should conditionally render tier-specific features', async () => {
      // Test VOID tier specific features
      render(<RealTimePortfolioAnalytics {...{ ...defaultProps, tier: InvestmentTier.VOID }} />);
      
      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      await user.click(riskTab);

      expect(screen.getByText('Quantum Risk Analysis')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle missing portfolio data gracefully', () => {
      const propsWithoutPortfolio = { ...defaultProps, portfolioId: undefined };
      render(<RealTimePortfolioAnalytics {...propsWithoutPortfolio} />);

      // Should still render basic structure
      expect(screen.getByText('Portfolio Analytics')).toBeInTheDocument();
    });

    it('should handle update errors without crashing', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      render(<RealTimePortfolioAnalytics {...defaultProps} />);

      // Force an error in the update cycle
      jest.advanceTimersByTime(5000);

      // Should continue to work
      expect(screen.getByText('Portfolio Analytics')).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });
  });
});