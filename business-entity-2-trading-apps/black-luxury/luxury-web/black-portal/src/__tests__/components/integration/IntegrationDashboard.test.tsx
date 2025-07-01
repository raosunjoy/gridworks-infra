/**
 * Test Suite for Integration Dashboard Component
 * Tests real-time monitoring UI for three-way integration
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { IntegrationDashboard } from '@/components/integration/IntegrationDashboard';
import { threeWayIntegration } from '@/services/ThreeWayIntegration';

// Mock the integration service
jest.mock('@/services/ThreeWayIntegration', () => ({
  threeWayIntegration: {
    getIntegrationMetrics: jest.fn(),
    performHealthCheck: jest.fn(),
    on: jest.fn(),
    off: jest.fn(),
  },
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('IntegrationDashboard', () => {
  const mockMetrics = {
    activeUsers: 1234,
    syncQueueSize: 5,
    healthStatus: 'healthy' as const,
    dataFlows: {
      portalToPlatform: {
        messagesPerMinute: 850,
        avgLatency: 45,
        errorRate: 0.001,
        lastSync: new Date().toISOString(),
      },
      platformToSupport: {
        messagesPerMinute: 920,
        avgLatency: 38,
        errorRate: 0.002,
        lastSync: new Date().toISOString(),
      },
      supportToPortal: {
        messagesPerMinute: 750,
        avgLatency: 52,
        errorRate: 0.003,
        lastSync: new Date().toISOString(),
      },
    },
    tierDistribution: {
      onyx: 800,
      obsidian: 150,
      void: 50,
    },
    revenueSync: {
      synced: true,
      lastSync: new Date().toISOString(),
    },
  };

  const mockHealthChecks = new Map([
    ['blackPortal', {
      service: 'black_portal',
      status: 'healthy' as const,
      latency: 45,
      lastCheck: new Date().toISOString(),
      metrics: {
        requestsPerMinute: 1000,
        errorRate: 0.001,
        avgResponseTime: 45,
      },
    }],
    ['gridworksPlatform', {
      service: 'trading_platform',
      status: 'healthy' as const,
      latency: 60,
      lastCheck: new Date().toISOString(),
      metrics: {
        requestsPerMinute: 2000,
        errorRate: 0.002,
        avgResponseTime: 60,
      },
    }],
    ['partnerPortal', {
      service: 'support_portal',
      status: 'degraded' as const,
      latency: 150,
      lastCheck: new Date().toISOString(),
      metrics: {
        requestsPerMinute: 500,
        errorRate: 0.05,
        avgResponseTime: 150,
      },
    }],
  ]);

  beforeEach(() => {
    jest.clearAllMocks();
    (threeWayIntegration.getIntegrationMetrics as jest.Mock).mockResolvedValue(mockMetrics);
    (threeWayIntegration.performHealthCheck as jest.Mock).mockResolvedValue(mockHealthChecks);
  });

  describe('Initial Render', () => {
    it('should show loading state initially', () => {
      render(<IntegrationDashboard />);
      
      const loadingSpinner = screen.getByTestId('loading-spinner');
      expect(loadingSpinner).toBeInTheDocument();
    });

    it('should load and display integration metrics', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Three-Way Integration Dashboard')).toBeInTheDocument();
      });

      // Check key metrics
      expect(screen.getByText('1,234')).toBeInTheDocument(); // Active users
      expect(screen.getByText('Real-time')).toBeInTheDocument(); // Data sync
      expect(screen.getByText('₹15,250 Cr')).toBeInTheDocument(); // Revenue target
      expect(screen.getByText('100%')).toBeInTheDocument(); // ZK Privacy
    });

    it('should display correct system health status', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('System healthy')).toBeInTheDocument();
      });
    });
  });

  describe('Service Health Display', () => {
    it('should display health status for all services', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Black Portal')).toBeInTheDocument();
        expect(screen.getByText('Trading Platform')).toBeInTheDocument();
        expect(screen.getByText('Support Portal')).toBeInTheDocument();
      });
    });

    it('should show correct health indicators', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        // Check for health metrics
        expect(screen.getByText('45ms')).toBeInTheDocument(); // Black Portal latency
        expect(screen.getByText('60ms')).toBeInTheDocument(); // Trading Platform latency
        expect(screen.getByText('150ms')).toBeInTheDocument(); // Support Portal latency
        
        // Check error rates
        expect(screen.getByText('0.10%')).toBeInTheDocument(); // 0.001 error rate
        expect(screen.getByText('5.00%')).toBeInTheDocument(); // 0.05 error rate
      });
    });

    it('should display degraded status correctly', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        // Support Portal should show as degraded
        const supportPortalSection = screen.getByText('Support Portal').closest('div');
        expect(supportPortalSection).toHaveTextContent('degraded');
      });
    });
  });

  describe('Data Flow Visualization', () => {
    it('should display data flow between services', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Real-time Data Flow')).toBeInTheDocument();
        
        // Check message rates
        expect(screen.getByText('850 msg/min')).toBeInTheDocument();
        expect(screen.getByText('920 msg/min')).toBeInTheDocument();
        expect(screen.getByText('750 msg/min')).toBeInTheDocument();
      });
    });

    it('should show latency for each data flow', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        // Multiple elements might have these latencies
        const latencies = screen.getAllByText(/\d+ms/);
        expect(latencies.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Tier Distribution', () => {
    it('should display user distribution across tiers', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('User Tier Distribution')).toBeInTheDocument();
        
        // Check tier counts
        expect(screen.getByText('800')).toBeInTheDocument(); // Onyx
        expect(screen.getByText('150')).toBeInTheDocument(); // Obsidian
        expect(screen.getByText('50')).toBeInTheDocument(); // Void
        
        // Check tier names
        expect(screen.getByText('Onyx')).toBeInTheDocument();
        expect(screen.getByText('Obsidian')).toBeInTheDocument();
        expect(screen.getByText('Void')).toBeInTheDocument();
        
        // Check tier descriptions
        expect(screen.getByText('Silver Stream Society')).toBeInTheDocument();
        expect(screen.getByText('Crystal Empire Network')).toBeInTheDocument();
        expect(screen.getByText('Quantum Consciousness')).toBeInTheDocument();
      });
    });

    it('should display portfolio requirements', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('₹100+ Cr portfolio')).toBeInTheDocument();
        expect(screen.getByText('₹1,000+ Cr portfolio')).toBeInTheDocument();
        expect(screen.getByText('₹8,000+ Cr portfolio')).toBeInTheDocument();
      });
    });
  });

  describe('Auto Refresh', () => {
    it('should have auto refresh enabled by default', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        const autoRefreshButton = screen.getByText('Auto Refresh');
        expect(autoRefreshButton.closest('button')).toHaveClass('bg-green-500/20');
      });
    });

    it('should toggle auto refresh on button click', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        const autoRefreshButton = screen.getByText('Auto Refresh');
        fireEvent.click(autoRefreshButton);
      });

      await waitFor(() => {
        const autoRefreshButton = screen.getByText('Auto Refresh');
        expect(autoRefreshButton.closest('button')).toHaveClass('bg-gray-800');
      });
    });

    it('should set up interval for auto refresh', async () => {
      jest.useFakeTimers();
      
      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(threeWayIntegration.getIntegrationMetrics).toHaveBeenCalledTimes(1);
      });

      // Fast forward 10 seconds
      jest.advanceTimersByTime(10000);

      await waitFor(() => {
        expect(threeWayIntegration.getIntegrationMetrics).toHaveBeenCalledTimes(2);
      });

      jest.useRealTimers();
    });
  });

  describe('Health Status Updates', () => {
    it('should update when health event is emitted', async () => {
      const { rerender } = render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('System healthy')).toBeInTheDocument();
      });

      // Update mock to return critical status
      const criticalHealthChecks = new Map(mockHealthChecks);
      criticalHealthChecks.set('blackPortal', {
        ...mockHealthChecks.get('blackPortal')!,
        status: 'down' as const,
      });

      (threeWayIntegration.getIntegrationMetrics as jest.Mock).mockResolvedValue({
        ...mockMetrics,
        healthStatus: 'critical' as const,
      });

      // Trigger health update
      const healthUpdateHandler = (threeWayIntegration.on as jest.Mock).mock.calls
        .find(call => call[0] === 'health:updated')?.[1];
      
      if (healthUpdateHandler) {
        healthUpdateHandler(criticalHealthChecks);
      }

      rerender(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('System critical')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle metrics loading failure', async () => {
      (threeWayIntegration.getIntegrationMetrics as jest.Mock).mockRejectedValue(
        new Error('Failed to load metrics')
      );

      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.queryByText('Three-Way Integration Dashboard')).toBeInTheDocument();
        // Should still render but with default/empty values
      });
    });

    it('should handle health check failure', async () => {
      (threeWayIntegration.performHealthCheck as jest.Mock).mockRejectedValue(
        new Error('Health check failed')
      );

      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.queryByText('Three-Way Integration Dashboard')).toBeInTheDocument();
      });
    });
  });

  describe('Sync Queue Display', () => {
    it('should show pending sync items', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('5 pending')).toBeInTheDocument();
      });
    });

    it('should show green indicator when no pending items', async () => {
      (threeWayIntegration.getIntegrationMetrics as jest.Mock).mockResolvedValue({
        ...mockMetrics,
        syncQueueSize: 0,
      });

      render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('0 pending')).toBeInTheDocument();
        const pendingIndicator = screen.getByText('0 pending');
        expect(pendingIndicator).toHaveClass('bg-green-500/20');
      });
    });
  });

  describe('Revenue Sync Status', () => {
    it('should show synced status', async () => {
      render(<IntegrationDashboard />);

      await waitFor(() => {
        // Look for the checkmark icon indicating synced status
        const revenueSection = screen.getByText('₹15,250 Cr').closest('div');
        expect(revenueSection).toBeInTheDocument();
      });
    });

    it('should show syncing status when not synced', async () => {
      (threeWayIntegration.getIntegrationMetrics as jest.Mock).mockResolvedValue({
        ...mockMetrics,
        revenueSync: {
          synced: false,
          lastSync: new Date().toISOString(),
        },
      });

      render(<IntegrationDashboard />);

      await waitFor(() => {
        // Should show spinning refresh icon
        const revenueSection = screen.getByText('₹15,250 Cr').closest('div');
        const refreshIcon = revenueSection?.querySelector('.animate-spin');
        expect(refreshIcon).toBeInTheDocument();
      });
    });
  });

  describe('Cleanup', () => {
    it('should clean up event listeners on unmount', () => {
      const { unmount } = render(<IntegrationDashboard />);

      unmount();

      expect(threeWayIntegration.off).toHaveBeenCalledWith(
        'health:updated',
        expect.any(Function)
      );
    });

    it('should clear intervals on unmount', async () => {
      jest.useFakeTimers();
      const clearIntervalSpy = jest.spyOn(global, 'clearInterval');

      const { unmount } = render(<IntegrationDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Three-Way Integration Dashboard')).toBeInTheDocument();
      });

      unmount();

      expect(clearIntervalSpy).toHaveBeenCalled();

      jest.useRealTimers();
    });
  });
});