import React from 'react';
import { render, screen } from '@testing-library/react';
import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import DashboardPage from '../page';

// Mock NextAuth
jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}));

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  redirect: jest.fn(),
}));

const mockUseSession = useSession as jest.MockedFunction<typeof useSession>;
const mockRedirect = redirect as jest.MockedFunction<typeof redirect>;

describe('DashboardPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Loading State', () => {
    it('should show loading spinner when session is loading', () => {
      mockUseSession.mockReturnValue({
        data: null,
        status: 'loading',
        update: jest.fn(),
      });

      render(<DashboardPage />);

      expect(screen.getByRole('generic')).toHaveClass('animate-spin');
    });
  });

  describe('Unauthenticated State', () => {
    it('should redirect to sign in when unauthenticated', () => {
      mockUseSession.mockReturnValue({
        data: null,
        status: 'unauthenticated',
        update: jest.fn(),
      });

      render(<DashboardPage />);

      expect(mockRedirect).toHaveBeenCalledWith('/auth/signin');
    });
  });

  describe('Authenticated State', () => {
    const mockSession = {
      user: {
        id: '1',
        name: 'John Doe',
        email: 'john@example.com',
        image: null,
      },
      expires: '2024-12-31',
    };

    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: mockSession,
        status: 'authenticated',
        update: jest.fn(),
      });
    });

    it('should render dashboard correctly for authenticated user', () => {
      render(<DashboardPage />);

      expect(screen.getByText('TradeMate Portal')).toBeInTheDocument();
      expect(screen.getByText('Welcome back, John')).toBeInTheDocument();
      expect(screen.getByText('Manage your TradeMate integration and monitor your API usage.')).toBeInTheDocument();
    });

    it('should display user information in header', () => {
      render(<DashboardPage />);

      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
    });

    it('should render quick stats cards', () => {
      render(<DashboardPage />);

      expect(screen.getByText('API Calls')).toBeInTheDocument();
      expect(screen.getByText('12.4K')).toBeInTheDocument();
      expect(screen.getByText('Active Users')).toBeInTheDocument();
      expect(screen.getByText('1,284')).toBeInTheDocument();
      expect(screen.getByText('Revenue')).toBeInTheDocument();
      expect(screen.getByText('₹85.2K')).toBeInTheDocument();
      expect(screen.getByText('Uptime')).toBeInTheDocument();
      expect(screen.getByText('99.9%')).toBeInTheDocument();
    });

    it('should render API management section', () => {
      render(<DashboardPage />);

      expect(screen.getByText('API Management')).toBeInTheDocument();
      expect(screen.getByText('Monitor your API usage, manage keys, and view integration status.')).toBeInTheDocument();
      expect(screen.getByText('View API Documentation')).toBeInTheDocument();
      expect(screen.getByText('Manage API Keys')).toBeInTheDocument();
      expect(screen.getByText('Usage Analytics')).toBeInTheDocument();
    });

    it('should render system health section', () => {
      render(<DashboardPage />);

      expect(screen.getByText('System Health')).toBeInTheDocument();
      expect(screen.getByText('Monitor system health and view self-healing status.')).toBeInTheDocument();
      expect(screen.getByText('API Service')).toBeInTheDocument();
      expect(screen.getByText('Database')).toBeInTheDocument();
      expect(screen.getByText('Cache')).toBeInTheDocument();
      expect(screen.getAllByText('Healthy')).toHaveLength(2);
      expect(screen.getByText('Degraded')).toBeInTheDocument();
    });

    it('should render recent activity section', () => {
      render(<DashboardPage />);

      expect(screen.getByText('Recent Activity')).toBeInTheDocument();
      expect(screen.getByText('API key generated')).toBeInTheDocument();
      expect(screen.getByText('WhatsApp integration tested')).toBeInTheDocument();
      expect(screen.getByText('Rate limit warning')).toBeInTheDocument();
      expect(screen.getByText('User authentication successful')).toBeInTheDocument();
    });

    it('should have proper navigation links', () => {
      render(<DashboardPage />);

      const apiDocsLink = screen.getByText('View API Documentation').closest('a');
      expect(apiDocsLink).toHaveAttribute('href', '/developer');

      const healthDashboardLink = screen.getByText('View Self-Healing Dashboard').closest('a');
      expect(healthDashboardLink).toHaveAttribute('href', '/dashboard/health');
    });

    it('should display proper growth indicators', () => {
      render(<DashboardPage />);

      const growthIndicators = screen.getAllByText(/^\+\d+\.\d+%$/);
      expect(growthIndicators).toHaveLength(4); // One for each metric
      
      expect(screen.getByText('+8.2%')).toBeInTheDocument(); // API Calls growth
      expect(screen.getByText('+12.5%')).toBeInTheDocument(); // Active Users growth
      expect(screen.getByText('+15.3%')).toBeInTheDocument(); // Revenue growth
      expect(screen.getByText('+0.1%')).toBeInTheDocument(); // Uptime growth
    });

    it('should show proper status indicators for services', () => {
      render(<DashboardPage />);

      const healthyStatuses = screen.getAllByText('Healthy');
      expect(healthyStatuses).toHaveLength(2); // API Service and Database
      
      const degradedStatus = screen.getByText('Degraded');
      expect(degradedStatus).toBeInTheDocument(); // Cache service
    });

    it('should display activity timestamps', () => {
      render(<DashboardPage />);

      expect(screen.getByText('2 minutes ago')).toBeInTheDocument();
      expect(screen.getByText('15 minutes ago')).toBeInTheDocument();
      expect(screen.getByText('1 hour ago')).toBeInTheDocument();
      expect(screen.getByText('2 hours ago')).toBeInTheDocument();
    });
  });

  describe('User Name Handling', () => {
    it('should handle user with single name', () => {
      const mockSessionSingleName = {
        user: {
          id: '1',
          name: 'John',
          email: 'john@example.com',
          image: null,
        },
        expires: '2024-12-31',
      };

      mockUseSession.mockReturnValue({
        data: mockSessionSingleName,
        status: 'authenticated',
        update: jest.fn(),
      });

      render(<DashboardPage />);

      expect(screen.getByText('Welcome back, John')).toBeInTheDocument();
    });

    it('should handle user with no name', () => {
      const mockSessionNoName = {
        user: {
          id: '1',
          name: null,
          email: 'john@example.com',
          image: null,
        },
        expires: '2024-12-31',
      };

      mockUseSession.mockReturnValue({
        data: mockSessionNoName,
        status: 'authenticated',
        update: jest.fn(),
      });

      render(<DashboardPage />);

      expect(screen.getByText('Welcome back,')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            id: '1',
            name: 'John Doe',
            email: 'john@example.com',
            image: null,
          },
          expires: '2024-12-31',
        },
        status: 'authenticated',
        update: jest.fn(),
      });
    });

    it('should have proper heading structure', () => {
      render(<DashboardPage />);

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('TradeMate Portal');
      expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Welcome back, John');
      expect(screen.getByRole('heading', { level: 3, name: /API Management/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 3, name: /System Health/i })).toBeInTheDocument();
    });

    it('should have proper button accessibility', () => {
      render(<DashboardPage />);

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toBeInTheDocument();
      });
    });

    it('should have proper link accessibility', () => {
      render(<DashboardPage />);

      const links = screen.getAllByRole('link');
      links.forEach(link => {
        expect(link).toHaveAttribute('href');
      });
    });
  });

  describe('Visual Elements', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            id: '1',
            name: 'John Doe',
            email: 'john@example.com',
            image: null,
          },
          expires: '2024-12-31',
        },
        status: 'authenticated',
        update: jest.fn(),
      });
    });

    it('should display status indicators with proper colors', () => {
      render(<DashboardPage />);

      // Check for green status indicators (healthy services)
      const healthyIndicators = document.querySelectorAll('.bg-green-500');
      expect(healthyIndicators.length).toBeGreaterThan(0);

      // Check for yellow status indicator (degraded service)
      const degradedIndicators = document.querySelectorAll('.bg-yellow-500');
      expect(degradedIndicators.length).toBeGreaterThan(0);
    });

    it('should display trending up icons for growth metrics', () => {
      render(<DashboardPage />);

      // All metrics should show positive growth
      const trendingElements = screen.getAllByText(/vs last month/);
      expect(trendingElements).toHaveLength(4);
    });
  });
});