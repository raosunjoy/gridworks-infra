/**
 * Investment Opportunities Dashboard Test Suite
 * Comprehensive testing for investment opportunity browsing,
 * tier-based filtering, and real-time opportunity updates
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { InvestmentOpportunitiesDashboard } from '../../components/investment/InvestmentOpportunitiesDashboard';
import { InvestmentTier, InvestmentCategory } from '../../services/InvestmentSyndicateEngine';

// Mock dependencies
jest.mock('../../hooks/useInvestmentOpportunities', () => ({
  useInvestmentOpportunities: jest.fn(),
}));

jest.mock('../../components/ui/LuxuryCard', () => ({
  LuxuryCard: ({ children, className, onClick }: any) => (
    <div className={className} onClick={onClick} data-testid="luxury-card">
      {children}
    </div>
  ),
}));

jest.mock('../../components/ui/TierGlow', () => ({
  TierGlow: ({ children }: any) => <div data-testid="tier-glow">{children}</div>,
}));

const mockOpportunities = [
  {
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
    createdAt: '2024-06-01T00:00:00Z',
    updatedAt: '2024-06-29T00:00:00Z',
  },
  {
    id: 'realestate-dubai-001',
    title: 'Dubai Marina Luxury Penthouse',
    category: InvestmentCategory.LUXURY_REAL_ESTATE,
    minimumInvestment: 250000000, // ₹25 Cr
    maximumInvestment: 1000000000, // ₹100 Cr
    currency: 'INR',
    tierAccess: [InvestmentTier.ONYX, InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
    expectedReturns: {
      conservative: '12',
      optimistic: '18% annually',
    },
    riskRating: 'low',
    availableSlots: 10,
    currentCommitments: 500000000,
    status: 'active',
    realEstateDetails: {
      location: 'Dubai Marina, UAE',
      propertyType: 'Penthouse',
      size: '5,000 sq ft',
      amenities: ['Private helicopter pad', 'Infinity pool', 'Butler service'],
    },
    offeringPeriod: {
      startDate: '2024-05-15',
      endDate: '2024-08-15',
      finalClosing: '2024-09-01',
    },
    lockupPeriod: '2-3 years',
    createdAt: '2024-05-15T00:00:00Z',
    updatedAt: '2024-06-25T00:00:00Z',
  },
  {
    id: 'esg-lithium-001',
    title: 'African Lithium ESG Fund',
    category: InvestmentCategory.ESG_INVESTMENTS,
    minimumInvestment: 100000000, // ₹10 Cr
    maximumInvestment: 2000000000, // ₹200 Cr
    currency: 'INR',
    tierAccess: [InvestmentTier.ONYX, InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
    expectedReturns: {
      conservative: '20',
      optimistic: '35% annually',
    },
    riskRating: 'medium',
    availableSlots: 50,
    currentCommitments: 1500000000,
    status: 'active',
    esgDetails: {
      esgScore: 95,
      impactMetrics: ['Carbon footprint reduction: 50%', 'Local job creation: 10,000'],
      sustainabilityGoals: ['UN SDG 7: Affordable and Clean Energy'],
    },
    offeringPeriod: {
      startDate: '2024-04-01',
      endDate: '2024-10-31',
      finalClosing: '2024-11-15',
    },
    lockupPeriod: '5-7 years',
    createdAt: '2024-04-01T00:00:00Z',
    updatedAt: '2024-06-20T00:00:00Z',
  },
];

const mockUseInvestmentOpportunities = {
  opportunities: mockOpportunities,
  loading: false,
  error: null,
  refreshOpportunities: jest.fn(),
  filterByTier: jest.fn(),
  filterByCategory: jest.fn(),
};

describe('InvestmentOpportunitiesDashboard', () => {
  const defaultProps = {
    tier: InvestmentTier.OBSIDIAN,
    onInvestmentSelect: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    const { useInvestmentOpportunities } = require('../../hooks/useInvestmentOpportunities');
    useInvestmentOpportunities.mockReturnValue(mockUseInvestmentOpportunities);
  });

  describe('Component Rendering', () => {
    test('should render dashboard header with tier information', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('Investment Opportunities')).toBeInTheDocument();
      expect(screen.getByText(/OBSIDIAN Tier/)).toBeInTheDocument();
      expect(screen.getByText(/Exclusive access to premium investment opportunities/)).toBeInTheDocument();
    });

    test('should render all investment opportunities when loaded', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('SpaceX Series X Investment')).toBeInTheDocument();
      expect(screen.getByText('Dubai Marina Luxury Penthouse')).toBeInTheDocument();
      expect(screen.getByText('African Lithium ESG Fund')).toBeInTheDocument();
    });

    test('should display loading state when opportunities are loading', () => {
      const { useInvestmentOpportunities } = require('../../hooks/useInvestmentOpportunities');
      useInvestmentOpportunities.mockReturnValue({
        ...mockUseInvestmentOpportunities,
        loading: true,
        opportunities: [],
      });

      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('Loading investment opportunities...')).toBeInTheDocument();
    });

    test('should display error state when there is an error', () => {
      const { useInvestmentOpportunities } = require('../../hooks/useInvestmentOpportunities');
      useInvestmentOpportunities.mockReturnValue({
        ...mockUseInvestmentOpportunities,
        error: 'Failed to load opportunities',
        opportunities: [],
      });

      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('Failed to load opportunities')).toBeInTheDocument();
    });

    test('should display empty state when no opportunities available', () => {
      const { useInvestmentOpportunities } = require('../../hooks/useInvestmentOpportunities');
      useInvestmentOpportunities.mockReturnValue({
        ...mockUseInvestmentOpportunities,
        opportunities: [],
      });

      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('No investment opportunities available')).toBeInTheDocument();
    });
  });

  describe('Opportunity Display', () => {
    test('should display opportunity details correctly', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      // SpaceX opportunity
      expect(screen.getByText('SpaceX Series X Investment')).toBeInTheDocument();
      expect(screen.getByText('₹50 Cr')).toBeInTheDocument(); // Minimum investment
      expect(screen.getByText('₹500 Cr')).toBeInTheDocument(); // Maximum investment
      expect(screen.getByText('25-40% annually')).toBeInTheDocument(); // Expected returns
      expect(screen.getByText('3-5 years')).toBeInTheDocument(); // Lockup period
      expect(screen.getByText('25 slots available')).toBeInTheDocument();
    });

    test('should format currency amounts correctly', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      // Check various currency formatting
      expect(screen.getByText('₹50 Cr')).toBeInTheDocument(); // 500 million
      expect(screen.getByText('₹25 Cr')).toBeInTheDocument(); // 250 million
      expect(screen.getByText('₹10 Cr')).toBeInTheDocument(); // 100 million
    });

    test('should display tier-specific access badges', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      // SpaceX should show Obsidian/Void access
      const spacexCard = screen.getByText('SpaceX Series X Investment').closest('[data-testid="luxury-card"]');
      expect(spacexCard).toHaveTextContent('OBSIDIAN');
      expect(spacexCard).toHaveTextContent('VOID');
    });

    test('should show category-specific icons and labels', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('PRE-IPO')).toBeInTheDocument();
      expect(screen.getByText('REAL ESTATE')).toBeInTheDocument();
      expect(screen.getByText('ESG')).toBeInTheDocument();
    });

    test('should display risk ratings with appropriate colors', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const riskElements = screen.getAllByText(/risk/i);
      expect(riskElements.length).toBeGreaterThan(0);
    });
  });

  describe('Filtering and Sorting', () => {
    test('should render category filter buttons', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('All Categories')).toBeInTheDocument();
      expect(screen.getByText('Pre-IPO')).toBeInTheDocument();
      expect(screen.getByText('Real Estate')).toBeInTheDocument();
      expect(screen.getByText('ESG Investments')).toBeInTheDocument();
    });

    test('should filter opportunities by category when category button clicked', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const preIpoButton = screen.getByText('Pre-IPO');
      fireEvent.click(preIpoButton);
      
      expect(mockUseInvestmentOpportunities.filterByCategory).toHaveBeenCalledWith(InvestmentCategory.PRE_IPO);
    });

    test('should show "All Categories" as active by default', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const allCategoriesButton = screen.getByText('All Categories');
      expect(allCategoriesButton).toHaveClass('bg-gold-500');
    });

    test('should render sort options', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByDisplayValue('newest')).toBeInTheDocument();
    });

    test('should handle sort option changes', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const sortSelect = screen.getByDisplayValue('newest');
      fireEvent.change(sortSelect, { target: { value: 'min_investment' } });
      
      expect(sortSelect.value).toBe('min_investment');
    });
  });

  describe('Opportunity Interaction', () => {
    test('should call onInvestmentSelect when opportunity card is clicked', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const spacexCard = screen.getByText('SpaceX Series X Investment').closest('[data-testid="luxury-card"]');
      fireEvent.click(spacexCard!);
      
      expect(defaultProps.onInvestmentSelect).toHaveBeenCalledWith(mockOpportunities[0]);
    });

    test('should handle investment button clicks', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const investButtons = screen.getAllByText('View Investment');
      fireEvent.click(investButtons[0]);
      
      expect(defaultProps.onInvestmentSelect).toHaveBeenCalledWith(mockOpportunities[0]);
    });

    test('should disable investment buttons for unavailable opportunities', () => {
      const unavailableOpportunities = mockOpportunities.map(opp => ({
        ...opp,
        status: 'closed',
      }));
      
      const { useInvestmentOpportunities } = require('../../hooks/useInvestmentOpportunities');
      useInvestmentOpportunities.mockReturnValue({
        ...mockUseInvestmentOpportunities,
        opportunities: unavailableOpportunities,
      });

      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const investButtons = screen.getAllByText('Closed');
      expect(investButtons.length).toBeGreaterThan(0);
      investButtons.forEach(button => {
        expect(button).toBeDisabled();
      });
    });
  });

  describe('Tier-Specific Behavior', () => {
    test('should show only tier-accessible opportunities for ONYX tier', () => {
      const onyxProps = { ...defaultProps, tier: InvestmentTier.ONYX };
      render(<InvestmentOpportunitiesDashboard {...onyxProps} />);
      
      expect(mockUseInvestmentOpportunities.filterByTier).toHaveBeenCalledWith(InvestmentTier.ONYX);
    });

    test('should show all opportunities for VOID tier', () => {
      const voidProps = { ...defaultProps, tier: InvestmentTier.VOID };
      render(<InvestmentOpportunitiesDashboard {...voidProps} />);
      
      expect(mockUseInvestmentOpportunities.filterByTier).toHaveBeenCalledWith(InvestmentTier.VOID);
    });

    test('should display tier-specific minimum investment warnings', () => {
      const onyxProps = { ...defaultProps, tier: InvestmentTier.ONYX };
      render(<InvestmentOpportunitiesDashboard {...onyxProps} />);
      
      // ONYX tier should see warnings for high-minimum investments
      const spacexCard = screen.getByText('SpaceX Series X Investment').closest('[data-testid="luxury-card"]');
      expect(spacexCard).toHaveTextContent('₹50 Cr minimum');
    });
  });

  describe('Real-time Updates', () => {
    test('should refresh opportunities when refresh button is clicked', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const refreshButton = screen.getByLabelText('Refresh opportunities');
      fireEvent.click(refreshButton);
      
      expect(mockUseInvestmentOpportunities.refreshOpportunities).toHaveBeenCalled();
    });

    test('should update opportunity display when data changes', async () => {
      const { rerender } = render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('SpaceX Series X Investment')).toBeInTheDocument();
      
      // Update opportunities
      const updatedOpportunities = [
        {
          ...mockOpportunities[0],
          title: 'SpaceX Series Y Investment',
          currentCommitments: 3000000000,
          availableSlots: 20,
        },
      ];
      
      const { useInvestmentOpportunities } = require('../../hooks/useInvestmentOpportunities');
      useInvestmentOpportunities.mockReturnValue({
        ...mockUseInvestmentOpportunities,
        opportunities: updatedOpportunities,
      });
      
      rerender(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('SpaceX Series Y Investment')).toBeInTheDocument();
        expect(screen.getByText('20 slots available')).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design', () => {
    test('should render grid layout for opportunities', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const opportunityGrid = screen.getByTestId('opportunities-grid');
      expect(opportunityGrid).toHaveClass('grid');
      expect(opportunityGrid).toHaveClass('md:grid-cols-2');
      expect(opportunityGrid).toHaveClass('lg:grid-cols-3');
    });

    test('should handle mobile layout appropriately', () => {
      // This would require specific mobile testing setup
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const opportunityGrid = screen.getByTestId('opportunities-grid');
      expect(opportunityGrid).toHaveClass('grid-cols-1');
    });
  });

  describe('Performance Metrics Display', () => {
    test('should display funding progress indicators', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      // SpaceX has ₹250 Cr committed out of potential max
      const progressBars = screen.getAllByRole('progressbar');
      expect(progressBars.length).toBeGreaterThan(0);
    });

    test('should show time remaining in offering period', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      // Should show days remaining for each opportunity
      expect(screen.getByText(/days remaining/i)).toBeInTheDocument();
    });

    test('should display historical performance indicators', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      // Should show performance metrics for each category
      expect(screen.getByText(/Expected Returns/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('should have proper ARIA labels for interactive elements', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByLabelText('Refresh opportunities')).toBeInTheDocument();
      expect(screen.getByLabelText('Sort opportunities')).toBeInTheDocument();
    });

    test('should support keyboard navigation', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      const firstOpportunity = screen.getByText('SpaceX Series X Investment').closest('[data-testid="luxury-card"]');
      expect(firstOpportunity).toHaveAttribute('tabIndex', '0');
    });

    test('should provide screen reader friendly content', () => {
      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('Investment opportunities dashboard')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('should gracefully handle missing opportunity data', () => {
      const incompleteOpportunities = [
        {
          id: 'incomplete-001',
          title: 'Incomplete Opportunity',
          // Missing required fields
        },
      ];
      
      const { useInvestmentOpportunities } = require('../../hooks/useInvestmentOpportunities');
      useInvestmentOpportunities.mockReturnValue({
        ...mockUseInvestmentOpportunities,
        opportunities: incompleteOpportunities,
      });

      expect(() => {
        render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      }).not.toThrow();
    });

    test('should handle network errors gracefully', () => {
      const { useInvestmentOpportunities } = require('../../hooks/useInvestmentOpportunities');
      useInvestmentOpportunities.mockReturnValue({
        ...mockUseInvestmentOpportunities,
        error: 'Network error',
        opportunities: [],
      });

      render(<InvestmentOpportunitiesDashboard {...defaultProps} />);
      
      expect(screen.getByText('Network error')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });
});