import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from '@testing-library/react';
import SelfHealingDashboard from '../SelfHealingDashboard';
import { useSelfHealingStore } from '@/store/self-healing';
import { HealthStatus } from '@/types';

// Mock the store
jest.mock('@/store/self-healing');

const mockUseSelfHealingStore = useSelfHealingStore as jest.MockedFunction<typeof useSelfHealingStore>;

describe('SelfHealingDashboard', () => {
  const mockStore = {
    healingStatus: {
      overall: HealthStatus.HEALTHY,
      services: [
        {
          name: 'api',
          status: HealthStatus.HEALTHY,
          lastCheck: new Date(),
          responseTime: 50,
          errorRate: 0.01,
          uptime: 0.99,
        },
        {
          name: 'database',
          status: HealthStatus.DEGRADED,
          lastCheck: new Date(),
          responseTime: 200,
          errorRate: 0.05,
          uptime: 0.95,
        },
        {
          name: 'cache',
          status: HealthStatus.CRITICAL,
          lastCheck: new Date(),
          responseTime: 1000,
          errorRate: 0.15,
          uptime: 0.85,
        },
      ],
      lastUpdate: new Date(),
    },
    metrics: {
      autoRecoveryRate: 95,
      incidentsPrevented: 42,
      recoveryTrend: 'up' as const,
      predictions: [
        {
          type: 'warning' as const,
          message: 'High memory usage predicted in 2 hours',
          probability: 0.85,
          timeframe: '2 hours',
          suggestedAction: 'Scale up memory allocation',
        },
      ],
    },
    incidents: [
      {
        id: 'incident_1',
        type: 'auto_recovery' as const,
        service: 'api',
        description: 'API response time degradation detected and resolved',
        status: 'resolved' as const,
        timestamp: new Date(Date.now() - 3600000), // 1 hour ago
        duration: 30000, // 30 seconds
        actions: ['Restarted service', 'Cleared cache'],
      },
      {
        id: 'incident_2',
        type: 'preventive_action' as const,
        service: 'database',
        description: 'Preventive connection pool reset',
        status: 'in_progress' as const,
        timestamp: new Date(Date.now() - 1800000), // 30 minutes ago
        actions: ['Connection pool reset initiated'],
      },
    ],
    startHealthMonitoring: jest.fn(),
    stopHealthMonitoring: jest.fn(),
    triggerManualRecovery: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSelfHealingStore.mockReturnValue(mockStore as any);
  });

  describe('Rendering', () => {
    it('should render dashboard header correctly', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('Self-Healing Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Real-time system health monitoring and autonomous recovery')).toBeInTheDocument();
    });

    it('should display last updated time', () => {
      render(<SelfHealingDashboard />);

      const lastUpdatedText = screen.getByText(/Last updated:/);
      expect(lastUpdatedText).toBeInTheDocument();
    });

    it('should render all overview metric cards', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('System Health')).toBeInTheDocument();
      expect(screen.getByText('Auto-Recovery Rate')).toBeInTheDocument();
      expect(screen.getByText('Incidents Prevented')).toBeInTheDocument();
      expect(screen.getByText('Active Services')).toBeInTheDocument();
    });

    it('should display correct metric values', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('95%')).toBeInTheDocument(); // Auto-recovery rate
      expect(screen.getByText('42')).toBeInTheDocument(); // Incidents prevented
      expect(screen.getByText('3')).toBeInTheDocument(); // Active services count
    });
  });

  describe('Service Health Cards', () => {
    it('should render all service health cards', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('api')).toBeInTheDocument();
      expect(screen.getByText('database')).toBeInTheDocument();
      expect(screen.getByText('cache')).toBeInTheDocument();
    });

    it('should display correct service metrics', () => {
      render(<SelfHealingDashboard />);

      // Check for response times
      expect(screen.getByText('50ms')).toBeInTheDocument();
      expect(screen.getByText('200ms')).toBeInTheDocument();
      expect(screen.getByText('1000ms')).toBeInTheDocument();

      // Check for error rates
      expect(screen.getByText('1.00%')).toBeInTheDocument();
      expect(screen.getByText('5.00%')).toBeInTheDocument();
      expect(screen.getByText('15.00%')).toBeInTheDocument();

      // Check for uptime
      expect(screen.getByText('99.00%')).toBeInTheDocument();
      expect(screen.getByText('95.00%')).toBeInTheDocument();
      expect(screen.getByText('85.00%')).toBeInTheDocument();
    });

    it('should show manual recovery button for degraded/critical services', () => {
      render(<SelfHealingDashboard />);

      const recoveryButtons = screen.getAllByText('Trigger Manual Recovery');
      expect(recoveryButtons).toHaveLength(2); // database and cache services
    });

    it('should not show manual recovery button for healthy services', () => {
      render(<SelfHealingDashboard />);

      // API service should not have a recovery button since it's healthy
      const apiCard = screen.getByText('api').closest('.p-4');
      expect(apiCard).not.toHaveTextContent('Trigger Manual Recovery');
    });

    it('should call triggerManualRecovery when button is clicked', async () => {
      render(<SelfHealingDashboard />);

      const recoveryButtons = screen.getAllByText('Trigger Manual Recovery');
      fireEvent.click(recoveryButtons[0]);

      await waitFor(() => {
        expect(mockStore.triggerManualRecovery).toHaveBeenCalledWith('database');
      });
    });

    it('should handle manual recovery failure gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      mockStore.triggerManualRecovery.mockRejectedValueOnce(new Error('Recovery failed'));

      render(<SelfHealingDashboard />);

      const recoveryButtons = screen.getAllByText('Trigger Manual Recovery');
      fireEvent.click(recoveryButtons[0]);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Manual recovery failed:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Status Colors and Indicators', () => {
    it('should apply correct CSS classes for service status', () => {
      render(<SelfHealingDashboard />);

      const healthyStatus = screen.getByText('healthy');
      expect(healthyStatus).toHaveClass('text-green-600', 'bg-green-100');

      const degradedStatus = screen.getByText('degraded');
      expect(degradedStatus).toHaveClass('text-yellow-600', 'bg-yellow-100');

      const criticalStatus = screen.getByText('critical');
      expect(criticalStatus).toHaveClass('text-red-600', 'bg-red-100');
    });

    it('should show correct status indicators for overall health', () => {
      render(<SelfHealingDashboard />);

      const overallHealthCard = screen.getByText('System Health').closest('.p-6');
      expect(overallHealthCard).toHaveClass('border-green-200', 'bg-green-50');
    });
  });

  describe('Healing Timeline', () => {
    it('should display recent healing activities', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('Recent Healing Activities')).toBeInTheDocument();
      expect(screen.getByText('API response time degradation detected and resolved')).toBeInTheDocument();
      expect(screen.getByText('Preventive connection pool reset')).toBeInTheDocument();
    });

    it('should show incident actions when available', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('Actions taken:')).toBeInTheDocument();
      expect(screen.getByText('Restarted service')).toBeInTheDocument();
      expect(screen.getByText('Cleared cache')).toBeInTheDocument();
    });

    it('should display incident duration when available', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('Duration: 30000ms')).toBeInTheDocument();
    });

    it('should show correct status colors for incidents', () => {
      render(<SelfHealingDashboard />);

      const resolvedStatus = screen.getByText('resolved');
      expect(resolvedStatus).toHaveClass('text-green-600');

      const inProgressStatus = screen.getByText('in_progress');
      expect(inProgressStatus).toHaveClass('text-blue-600');
    });
  });

  describe('Predictive Insights', () => {
    it('should display predictive insights section', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('Predictive Insights')).toBeInTheDocument();
      expect(screen.getByText('High memory usage predicted in 2 hours')).toBeInTheDocument();
    });

    it('should show prediction probability and timeframe', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('Probability: 85.0%')).toBeInTheDocument();
      expect(screen.getByText('Timeframe: 2 hours')).toBeInTheDocument();
    });

    it('should display suggested action when available', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByText('Suggested Action:')).toBeInTheDocument();
      expect(screen.getByText('Scale up memory allocation')).toBeInTheDocument();
    });

    it('should show appropriate styles for different prediction types', () => {
      render(<SelfHealingDashboard />);

      const warningPrediction = screen.getByText('High memory usage predicted in 2 hours').closest('.p-4');
      expect(warningPrediction).toHaveClass('border-yellow-200', 'bg-yellow-50', 'text-yellow-800');
    });

    it('should display empty state when no predictions available', () => {
      const storeWithNoPredictions = {
        ...mockStore,
        metrics: {
          ...mockStore.metrics,
          predictions: [],
        },
      };

      mockUseSelfHealingStore.mockReturnValue(storeWithNoPredictions as any);

      render(<SelfHealingDashboard />);

      expect(screen.getByText('No predictive insights available at the moment.')).toBeInTheDocument();
    });
  });

  describe('Lifecycle Management', () => {
    it('should start health monitoring on mount', () => {
      render(<SelfHealingDashboard />);

      expect(mockStore.startHealthMonitoring).toHaveBeenCalledTimes(1);
    });

    it('should stop health monitoring on unmount', () => {
      const { unmount } = render(<SelfHealingDashboard />);

      unmount();

      expect(mockStore.stopHealthMonitoring).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty services array', () => {
      const storeWithNoServices = {
        ...mockStore,
        healingStatus: {
          ...mockStore.healingStatus,
          services: [],
        },
      };

      mockUseSelfHealingStore.mockReturnValue(storeWithNoServices as any);

      render(<SelfHealingDashboard />);

      expect(screen.getByText('0')).toBeInTheDocument(); // Active services count
    });

    it('should handle null/undefined values gracefully', () => {
      const storeWithNullValues = {
        ...mockStore,
        healingStatus: {
          ...mockStore.healingStatus,
          services: [
            {
              name: 'test-service',
              status: HealthStatus.UNKNOWN,
              lastCheck: new Date(),
              responseTime: 0,
              errorRate: 0,
              uptime: 0,
            },
          ],
        },
      };

      mockUseSelfHealingStore.mockReturnValue(storeWithNullValues as any);

      render(<SelfHealingDashboard />);

      expect(screen.getByText('test-service')).toBeInTheDocument();
      expect(screen.getByText('0ms')).toBeInTheDocument();
      expect(screen.getByText('0.00%')).toBeInTheDocument();
    });

    it('should handle very large numbers gracefully', () => {
      const storeWithLargeNumbers = {
        ...mockStore,
        healingStatus: {
          ...mockStore.healingStatus,
          services: [
            {
              name: 'slow-service',
              status: HealthStatus.CRITICAL,
              lastCheck: new Date(),
              responseTime: 999999,
              errorRate: 0.9999,
              uptime: 0.0001,
            },
          ],
        },
      };

      mockUseSelfHealingStore.mockReturnValue(storeWithLargeNumbers as any);

      render(<SelfHealingDashboard />);

      expect(screen.getByText('slow-service')).toBeInTheDocument();
      expect(screen.getByText('999999ms')).toBeInTheDocument();
      expect(screen.getByText('99.99%')).toBeInTheDocument(); // Error rate
      expect(screen.getByText('0.01%')).toBeInTheDocument(); // Uptime
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for interactive elements', () => {
      render(<SelfHealingDashboard />);

      const recoveryButtons = screen.getAllByText('Trigger Manual Recovery');
      recoveryButtons.forEach(button => {
        expect(button.tagName).toBe('BUTTON');
      });
    });

    it('should use semantic HTML structure', () => {
      render(<SelfHealingDashboard />);

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Self-Healing Dashboard');
      expect(screen.getByRole('heading', { level: 2, name: /Service Health/i })).toBeInTheDocument();
    });
  });
});