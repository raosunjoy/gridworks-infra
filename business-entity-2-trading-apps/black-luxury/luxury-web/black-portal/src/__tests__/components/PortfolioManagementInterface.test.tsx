/**
 * Portfolio Management Interface Test Suite
 * Comprehensive testing for portfolio tracking, analytics dashboard,
 * real-time performance metrics, and rebalancing recommendations
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { PortfolioManagementInterface } from '../../components/investment/PortfolioManagementInterface';
import { InvestmentTier } from '../../services/InvestmentSyndicateEngine';
import { AssetClass, PortfolioStrategy } from '../../services/InvestmentPortfolioManager';

// Mock dependencies
jest.mock('../../hooks/usePortfolioData', () => ({
  usePortfolioData: jest.fn(),
}));

jest.mock('../../components/ui/LuxuryCard', () => ({
  LuxuryCard: ({ children, className }: any) => (
    <div className={className} data-testid="luxury-card">
      {children}
    </div>
  ),
}));

jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
}));

const mockPortfolioData = {
  portfolio: {
    id: 'portfolio-obsidian-001',
    clientId: 'obsidian-client-001',
    anonymousId: 'test-anonymous-id',
    tier: InvestmentTier.OBSIDIAN,
    configuration: {
      strategy: PortfolioStrategy.AGGRESSIVE,
      riskTolerance: 'aggressive',
      timeHorizon: '10+ years',
      liquidityNeeds: 0.1,
    },
    holdings: [
      {
        id: 'holding-spacex-001',
        portfolioId: 'portfolio-obsidian-001',
        assetDetails: {
          name: 'SpaceX Series X',
          symbol: 'SPACEX',
          assetClass: AssetClass.EQUITY,
          category: 'PRE_IPO',
          type: 'private',
        },
        position: {
          quantity: 1000,
          unitCost: 500000,
          currentPrice: 650000,
          totalValue: 650000000,
          currency: 'INR',
        },
        performance: {
          unrealizedGain: 150000000,
          realizedGain: 0,
          totalReturn: 0.30,
          dayChange: 0.02,
          dayChangeAmount: 13000000,
        },
        acquisitionDate: '2024-01-15T00:00:00Z',
        riskMetrics: {
          var95: -25000000,
          beta: 1.2,
          volatility: 0.35,
        },
      },
      {
        id: 'holding-realestate-001',
        portfolioId: 'portfolio-obsidian-001',
        assetDetails: {
          name: 'Dubai Marina Penthouse',
          symbol: 'DXB-RE-001',
          assetClass: AssetClass.REAL_ESTATE,
          category: 'LUXURY_REAL_ESTATE',
          type: 'alternative',
        },
        position: {
          quantity: 1,
          unitCost: 400000000,
          currentPrice: 480000000,
          totalValue: 480000000,
          currency: 'INR',
        },
        performance: {
          unrealizedGain: 80000000,
          realizedGain: 0,
          totalReturn: 0.20,
          dayChange: 0.005,
          dayChangeAmount: 2400000,
        },
        acquisitionDate: '2024-02-01T00:00:00Z',
        riskMetrics: {
          var95: -15000000,
          beta: 0.4,
          volatility: 0.15,
        },
      },
    ],
    targetAllocation: {
      [AssetClass.EQUITY]: 60,
      [AssetClass.REAL_ESTATE]: 25,
      [AssetClass.FIXED_INCOME]: 10,
      [AssetClass.ALTERNATIVES]: 5,
    },
    allocation: {
      [AssetClass.EQUITY]: 57.5,
      [AssetClass.REAL_ESTATE]: 42.5,
      [AssetClass.FIXED_INCOME]: 0,
      [AssetClass.ALTERNATIVES]: 0,
    },
    performance: {
      totalValue: 1130000000, // ₹113 Cr
      totalInvestment: 900000000, // ₹90 Cr
      totalReturn: 0.256,
      unrealizedGains: 230000000,
      realizedGains: 0,
      dayChange: 0.014,
      dayChangeAmount: 15400000,
    },
    tierBenefits: {
      rebalancingFrequency: 'quarterly',
      taxOptimization: true,
      riskManagement: 'enhanced',
      reporting: 'detailed',
      conciergeSupport: true,
    },
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-06-29T00:00:00Z',
  },
  performanceHistory: [
    { date: '2024-01-01', value: 900000000 },
    { date: '2024-02-01', value: 950000000 },
    { date: '2024-03-01', value: 1020000000 },
    { date: '2024-04-01', value: 1080000000 },
    { date: '2024-05-01', value: 1100000000 },
    { date: '2024-06-01', value: 1130000000 },
  ],
  riskMetrics: {
    portfolioBeta: 0.8,
    var95: -40000000,
    volatility: 0.25,
    maxDrawdown: -0.08,
    sharpeRatio: 1.4,
    correlationMatrix: {
      'SPACEX': { 'DXB-RE-001': 0.15 },
      'DXB-RE-001': { 'SPACEX': 0.15 },
    },
  },
  rebalancingRecommendations: {
    required: true,
    suggestions: [
      {
        assetClass: AssetClass.REAL_ESTATE,
        action: 'reduce',
        currentAllocation: 42.5,
        targetAllocation: 25,
        suggestedAmount: 197500000, // Reduce by this amount
        reasoning: 'Real estate allocation exceeds target by 17.5%',
      },
      {
        assetClass: AssetClass.FIXED_INCOME,
        action: 'add',
        currentAllocation: 0,
        targetAllocation: 10,
        suggestedAmount: 113000000, // Add 10% of portfolio
        reasoning: 'No fixed income allocation for risk management',
      },
    ],
    estimatedCost: 50000, // Transaction costs
    taxImpact: 15000000, // Estimated tax on realized gains
  },
  loading: false,
  error: null,
};

const mockUsePortfolioData = {
  ...mockPortfolioData,
  refreshPortfolio: jest.fn(),
  updateHolding: jest.fn(),
  rebalancePortfolio: jest.fn(),
  executeRebalancing: jest.fn(),
};

describe('PortfolioManagementInterface', () => {
  const defaultProps = {
    tier: InvestmentTier.OBSIDIAN,
    anonymousId: 'test-anonymous-id',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    const { usePortfolioData } = require('../../hooks/usePortfolioData');
    usePortfolioData.mockReturnValue(mockUsePortfolioData);
  });

  describe('Component Rendering', () => {
    test('should render portfolio management interface with header', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Portfolio Management')).toBeInTheDocument();
      expect(screen.getByText(/OBSIDIAN Tier Portfolio/)).toBeInTheDocument();
      expect(screen.getByText(/Real-time tracking and analytics/)).toBeInTheDocument();
    });

    test('should display portfolio overview metrics', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Total Portfolio Value')).toBeInTheDocument();
      expect(screen.getByText('₹113 Cr')).toBeInTheDocument();
      expect(screen.getByText('Total Returns')).toBeInTheDocument();
      expect(screen.getByText('25.6%')).toBeInTheDocument();
      expect(screen.getByText('Today\'s Change')).toBeInTheDocument();
      expect(screen.getByText('+₹1.54 Cr')).toBeInTheDocument();
    });

    test('should show loading state when portfolio data is loading', () => {
      const { usePortfolioData } = require('../../hooks/usePortfolioData');
      usePortfolioData.mockReturnValue({
        ...mockUsePortfolioData,
        loading: true,
        portfolio: null,
      });

      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Loading portfolio data...')).toBeInTheDocument();
    });

    test('should display error state when there is an error', () => {
      const { usePortfolioData } = require('../../hooks/usePortfolioData');
      usePortfolioData.mockReturnValue({
        ...mockUsePortfolioData,
        error: 'Failed to load portfolio',
        portfolio: null,
      });

      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Failed to load portfolio')).toBeInTheDocument();
    });
  });

  describe('Navigation Tabs', () => {
    test('should render all navigation tabs', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Holdings')).toBeInTheDocument();
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('Rebalancing')).toBeInTheDocument();
    });

    test('should switch between tabs correctly', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      // Default to Overview tab
      expect(screen.getByText('Asset Allocation')).toBeInTheDocument();
      
      // Switch to Holdings tab
      fireEvent.click(screen.getByText('Holdings'));
      expect(screen.getByText('Portfolio Holdings')).toBeInTheDocument();
      
      // Switch to Performance tab
      fireEvent.click(screen.getByText('Performance'));
      expect(screen.getByText('Performance Chart')).toBeInTheDocument();
    });

    test('should show active tab styling', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      const overviewTab = screen.getByText('Overview');
      expect(overviewTab).toHaveClass('bg-gold-500');
      
      fireEvent.click(screen.getByText('Holdings'));
      const holdingsTab = screen.getByText('Holdings');
      expect(holdingsTab).toHaveClass('bg-gold-500');
    });
  });

  describe('Overview Tab', () => {
    test('should display asset allocation pie chart', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Asset Allocation')).toBeInTheDocument();
      expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
      expect(screen.getByText('Equity: 57.5%')).toBeInTheDocument();
      expect(screen.getByText('Real Estate: 42.5%')).toBeInTheDocument();
    });

    test('should show portfolio summary statistics', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Portfolio Strategy')).toBeInTheDocument();
      expect(screen.getByText('Aggressive Growth')).toBeInTheDocument();
      expect(screen.getByText('Risk Tolerance')).toBeInTheDocument();
      expect(screen.getByText('Aggressive')).toBeInTheDocument();
      expect(screen.getByText('Time Horizon')).toBeInTheDocument();
      expect(screen.getByText('10+ years')).toBeInTheDocument();
    });

    test('should display tier benefits', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Tier Benefits')).toBeInTheDocument();
      expect(screen.getByText('Quarterly Rebalancing')).toBeInTheDocument();
      expect(screen.getByText('Tax Optimization')).toBeInTheDocument();
      expect(screen.getByText('Enhanced Risk Management')).toBeInTheDocument();
      expect(screen.getByText('Concierge Support')).toBeInTheDocument();
    });

    test('should show quick actions', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Quick Actions')).toBeInTheDocument();
      expect(screen.getByText('Add Investment')).toBeInTheDocument();
      expect(screen.getByText('Rebalance Portfolio')).toBeInTheDocument();
      expect(screen.getByText('Download Report')).toBeInTheDocument();
    });
  });

  describe('Holdings Tab', () => {
    beforeEach(() => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      fireEvent.click(screen.getByText('Holdings'));
    });

    test('should display all portfolio holdings', () => {
      expect(screen.getByText('Portfolio Holdings')).toBeInTheDocument();
      expect(screen.getByText('SpaceX Series X')).toBeInTheDocument();
      expect(screen.getByText('Dubai Marina Penthouse')).toBeInTheDocument();
    });

    test('should show holding details with performance metrics', () => {
      expect(screen.getByText('₹65 Cr')).toBeInTheDocument(); // SpaceX total value
      expect(screen.getByText('₹48 Cr')).toBeInTheDocument(); // Real estate total value
      expect(screen.getByText('+30.0%')).toBeInTheDocument(); // SpaceX return
      expect(screen.getByText('+20.0%')).toBeInTheDocument(); // Real estate return
    });

    test('should display daily change indicators', () => {
      expect(screen.getByText('+2.0%')).toBeInTheDocument(); // SpaceX day change
      expect(screen.getByText('+0.5%')).toBeInTheDocument(); // Real estate day change
    });

    test('should show asset class and category labels', () => {
      expect(screen.getByText('EQUITY')).toBeInTheDocument();
      expect(screen.getByText('PRE-IPO')).toBeInTheDocument();
      expect(screen.getByText('REAL ESTATE')).toBeInTheDocument();
      expect(screen.getByText('LUXURY')).toBeInTheDocument();
    });

    test('should allow filtering holdings by asset class', () => {
      const equityFilter = screen.getByText('Equity Only');
      fireEvent.click(equityFilter);
      
      expect(screen.getByText('SpaceX Series X')).toBeInTheDocument();
      expect(screen.queryByText('Dubai Marina Penthouse')).not.toBeInTheDocument();
    });

    test('should allow sorting holdings by different criteria', () => {
      const sortSelect = screen.getByDisplayValue('value_desc');
      fireEvent.change(sortSelect, { target: { value: 'performance_desc' } });
      
      expect(sortSelect.value).toBe('performance_desc');
    });
  });

  describe('Performance Tab', () => {
    beforeEach(() => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      fireEvent.click(screen.getByText('Performance'));
    });

    test('should display performance chart', () => {
      expect(screen.getByText('Performance Chart')).toBeInTheDocument();
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    });

    test('should show performance time period selector', () => {
      expect(screen.getByText('1M')).toBeInTheDocument();
      expect(screen.getByText('3M')).toBeInTheDocument();
      expect(screen.getByText('6M')).toBeInTheDocument();
      expect(screen.getByText('1Y')).toBeInTheDocument();
      expect(screen.getByText('ALL')).toBeInTheDocument();
    });

    test('should update chart when time period is changed', () => {
      const sixMonthButton = screen.getByText('6M');
      fireEvent.click(sixMonthButton);
      
      expect(sixMonthButton).toHaveClass('bg-gold-500');
    });

    test('should display benchmark comparison', () => {
      expect(screen.getByText('Benchmark Comparison')).toBeInTheDocument();
      expect(screen.getByText('vs. NIFTY 50')).toBeInTheDocument();
      expect(screen.getByText('vs. Real Estate Index')).toBeInTheDocument();
    });

    test('should show performance statistics', () => {
      expect(screen.getByText('Sharpe Ratio')).toBeInTheDocument();
      expect(screen.getByText('1.4')).toBeInTheDocument();
      expect(screen.getByText('Max Drawdown')).toBeInTheDocument();
      expect(screen.getByText('-8.0%')).toBeInTheDocument();
      expect(screen.getByText('Volatility')).toBeInTheDocument();
      expect(screen.getByText('25.0%')).toBeInTheDocument();
    });
  });

  describe('Analytics Tab', () => {
    beforeEach(() => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      fireEvent.click(screen.getByText('Analytics'));
    });

    test('should display risk metrics', () => {
      expect(screen.getByText('Risk Analytics')).toBeInTheDocument();
      expect(screen.getByText('Portfolio Beta')).toBeInTheDocument();
      expect(screen.getByText('0.8')).toBeInTheDocument();
      expect(screen.getByText('Value at Risk (95%)')).toBeInTheDocument();
      expect(screen.getByText('₹4 Cr')).toBeInTheDocument();
    });

    test('should show correlation matrix', () => {
      expect(screen.getByText('Asset Correlation')).toBeInTheDocument();
      expect(screen.getByText('Correlation Matrix')).toBeInTheDocument();
    });

    test('should display sector and geographic allocation', () => {
      expect(screen.getByText('Sector Allocation')).toBeInTheDocument();
      expect(screen.getByText('Geographic Allocation')).toBeInTheDocument();
    });

    test('should show ESG metrics if applicable', () => {
      expect(screen.getByText('ESG Analysis')).toBeInTheDocument();
      expect(screen.getByText('Environmental Score')).toBeInTheDocument();
      expect(screen.getByText('Social Score')).toBeInTheDocument();
      expect(screen.getByText('Governance Score')).toBeInTheDocument();
    });
  });

  describe('Rebalancing Tab', () => {
    beforeEach(() => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      fireEvent.click(screen.getByText('Rebalancing'));
    });

    test('should display rebalancing recommendations', () => {
      expect(screen.getByText('Rebalancing Recommendations')).toBeInTheDocument();
      expect(screen.getByText('Portfolio rebalancing is recommended')).toBeInTheDocument();
    });

    test('should show current vs target allocation comparison', () => {
      expect(screen.getByText('Current vs Target Allocation')).toBeInTheDocument();
      expect(screen.getByText('Real Estate: 42.5% → 25%')).toBeInTheDocument();
      expect(screen.getByText('Fixed Income: 0% → 10%')).toBeInTheDocument();
    });

    test('should display suggested actions with amounts', () => {
      expect(screen.getByText('Reduce Real Estate')).toBeInTheDocument();
      expect(screen.getByText('₹19.75 Cr')).toBeInTheDocument(); // Reduction amount
      expect(screen.getByText('Add Fixed Income')).toBeInTheDocument();
      expect(screen.getByText('₹11.3 Cr')).toBeInTheDocument(); // Addition amount
    });

    test('should show rebalancing costs and tax impact', () => {
      expect(screen.getByText('Estimated Costs')).toBeInTheDocument();
      expect(screen.getByText('₹50,000')).toBeInTheDocument(); // Transaction costs
      expect(screen.getByText('Tax Impact')).toBeInTheDocument();
      expect(screen.getByText('₹1.5 Cr')).toBeInTheDocument(); // Tax impact
    });

    test('should allow executing rebalancing', () => {
      const executeButton = screen.getByText('Execute Rebalancing');
      fireEvent.click(executeButton);
      
      expect(screen.getByText('Confirm Rebalancing')).toBeInTheDocument();
    });

    test('should handle rebalancing confirmation', async () => {
      const executeButton = screen.getByText('Execute Rebalancing');
      fireEvent.click(executeButton);
      
      const confirmButton = screen.getByText('Confirm & Execute');
      fireEvent.click(confirmButton);
      
      await waitFor(() => {
        expect(mockUsePortfolioData.executeRebalancing).toHaveBeenCalled();
      });
    });
  });

  describe('Real-time Updates', () => {
    test('should refresh portfolio data when refresh button is clicked', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      const refreshButton = screen.getByLabelText('Refresh portfolio data');
      fireEvent.click(refreshButton);
      
      expect(mockUsePortfolioData.refreshPortfolio).toHaveBeenCalled();
    });

    test('should update display when portfolio data changes', async () => {
      const { rerender } = render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('₹113 Cr')).toBeInTheDocument();
      
      // Update portfolio data
      const updatedPortfolioData = {
        ...mockUsePortfolioData,
        portfolio: {
          ...mockUsePortfolioData.portfolio,
          performance: {
            ...mockUsePortfolioData.portfolio.performance,
            totalValue: 1200000000, // Updated to ₹120 Cr
          },
        },
      };
      
      const { usePortfolioData } = require('../../hooks/usePortfolioData');
      usePortfolioData.mockReturnValue(updatedPortfolioData);
      
      rerender(<PortfolioManagementInterface {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('₹120 Cr')).toBeInTheDocument();
      });
    });

    test('should handle live price updates', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      // Simulate live price update indicator
      expect(screen.getByText('Live')).toBeInTheDocument();
      expect(screen.getByTestId('live-indicator')).toHaveClass('animate-pulse');
    });
  });

  describe('Tier-Specific Features', () => {
    test('should show enhanced analytics for VOID tier', () => {
      const voidProps = { ...defaultProps, tier: InvestmentTier.VOID };
      render(<PortfolioManagementInterface {...voidProps} />);
      
      fireEvent.click(screen.getByText('Analytics'));
      
      expect(screen.getByText('Quantum Risk Analysis')).toBeInTheDocument();
      expect(screen.getByText('Advanced Modeling')).toBeInTheDocument();
    });

    test('should limit features for ONYX tier', () => {
      const onyxProps = { ...defaultProps, tier: InvestmentTier.ONYX };
      render(<PortfolioManagementInterface {...onyxProps} />);
      
      fireEvent.click(screen.getByText('Analytics'));
      
      expect(screen.queryByText('Quantum Risk Analysis')).not.toBeInTheDocument();
    });

    test('should show tier-appropriate rebalancing frequency', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Quarterly Rebalancing')).toBeInTheDocument();
    });
  });

  describe('Export and Reporting', () => {
    test('should allow downloading portfolio reports', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Report');
      fireEvent.click(downloadButton);
      
      expect(screen.getByText('Select Report Type')).toBeInTheDocument();
      expect(screen.getByText('Performance Report')).toBeInTheDocument();
      expect(screen.getByText('Holdings Summary')).toBeInTheDocument();
      expect(screen.getByText('Tax Report')).toBeInTheDocument();
    });

    test('should generate anonymous reports', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Report');
      fireEvent.click(downloadButton);
      
      const anonymousOption = screen.getByLabelText('Anonymous Report');
      expect(anonymousOption).toBeInTheDocument();
      expect(anonymousOption).toBeChecked(); // Should default to anonymous
    });
  });

  describe('Error Handling', () => {
    test('should handle API errors gracefully', () => {
      const { usePortfolioData } = require('../../hooks/usePortfolioData');
      usePortfolioData.mockReturnValue({
        ...mockUsePortfolioData,
        error: 'Network error occurred',
      });

      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Network error occurred')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });

    test('should handle missing portfolio data', () => {
      const { usePortfolioData } = require('../../hooks/usePortfolioData');
      usePortfolioData.mockReturnValue({
        ...mockUsePortfolioData,
        portfolio: null,
        loading: false,
        error: null,
      });

      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('No portfolio found')).toBeInTheDocument();
      expect(screen.getByText('Create Portfolio')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('should have proper ARIA labels for charts and data', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByLabelText('Portfolio asset allocation chart')).toBeInTheDocument();
      expect(screen.getByLabelText('Refresh portfolio data')).toBeInTheDocument();
    });

    test('should support keyboard navigation for tabs', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      const holdingsTab = screen.getByText('Holdings');
      expect(holdingsTab).toHaveAttribute('tabIndex', '0');
    });

    test('should provide screen reader friendly content', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      expect(screen.getByText('Portfolio management dashboard')).toBeInTheDocument();
    });
  });

  describe('Performance Optimization', () => {
    test('should memoize chart data to prevent unnecessary re-renders', () => {
      const { rerender } = render(<PortfolioManagementInterface {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Performance'));
      const chartElement = screen.getByTestId('line-chart');
      
      rerender(<PortfolioManagementInterface {...defaultProps} />);
      
      // Chart should not re-render if data hasn't changed
      expect(screen.getByTestId('line-chart')).toBe(chartElement);
    });

    test('should lazy load analytics data when tab is first accessed', () => {
      render(<PortfolioManagementInterface {...defaultProps} />);
      
      // Analytics should not be loaded initially
      expect(screen.queryByText('Risk Analytics')).not.toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Analytics'));
      
      // Analytics should load when tab is clicked
      expect(screen.getByText('Risk Analytics')).toBeInTheDocument();
    });
  });
});