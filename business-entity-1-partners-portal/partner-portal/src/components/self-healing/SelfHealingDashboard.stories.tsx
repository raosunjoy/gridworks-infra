import type { Meta, StoryObj } from '@storybook/react';
import SelfHealingDashboard from './SelfHealingDashboard';
import { HealthStatus } from '@/types';

// Mock the store for Storybook
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
      {
        type: 'info' as const,
        message: 'Scheduled maintenance window in 24 hours',
        probability: 1.0,
        timeframe: '24 hours',
        suggestedAction: 'No action required',
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
      timestamp: new Date(Date.now() - 3600000),
      duration: 30000,
      actions: ['Restarted service', 'Cleared cache'],
    },
    {
      id: 'incident_2',
      type: 'preventive_action' as const,
      service: 'database',
      description: 'Preventive connection pool reset',
      status: 'in_progress' as const,
      timestamp: new Date(Date.now() - 1800000),
      actions: ['Connection pool reset initiated'],
    },
  ],
  startHealthMonitoring: () => {},
  stopHealthMonitoring: () => {},
  triggerManualRecovery: () => {},
};

// Mock the store hook
jest.mock('@/store/self-healing', () => ({
  useSelfHealingStore: () => mockStore,
}));

const meta: Meta<typeof SelfHealingDashboard> = {
  title: 'Dashboard/SelfHealingDashboard',
  component: SelfHealingDashboard,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'A comprehensive self-healing dashboard that monitors system health and displays autonomous recovery activities.',
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

// Default healthy state
export const Healthy: Story = {};

// Critical system state
export const Critical: Story = {
  decorators: [
    (Story) => {
      // Override mock for critical state
      const criticalMockStore = {
        ...mockStore,
        healingStatus: {
          ...mockStore.healingStatus,
          overall: HealthStatus.CRITICAL,
          services: [
            {
              name: 'api',
              status: HealthStatus.CRITICAL,
              lastCheck: new Date(),
              responseTime: 5000,
              errorRate: 0.25,
              uptime: 0.75,
            },
            {
              name: 'database',
              status: HealthStatus.CRITICAL,
              lastCheck: new Date(),
              responseTime: 8000,
              errorRate: 0.30,
              uptime: 0.60,
            },
            {
              name: 'cache',
              status: HealthStatus.UNKNOWN,
              lastCheck: new Date(Date.now() - 300000),
              responseTime: 0,
              errorRate: 1.0,
              uptime: 0.0,
            },
          ],
        },
        metrics: {
          ...mockStore.metrics,
          autoRecoveryRate: 45,
          incidentsPrevented: 12,
          recoveryTrend: 'down' as const,
        },
      };
      
      require('@/store/self-healing').useSelfHealingStore.mockReturnValue(criticalMockStore);
      
      return <Story />;
    },
  ],
};

// No incidents state
export const NoIncidents: Story = {
  decorators: [
    (Story) => {
      const noIncidentsMockStore = {
        ...mockStore,
        incidents: [],
        metrics: {
          ...mockStore.metrics,
          predictions: [],
        },
      };
      
      require('@/store/self-healing').useSelfHealingStore.mockReturnValue(noIncidentsMockStore);
      
      return <Story />;
    },
  ],
};

// Many incidents state
export const ManyIncidents: Story = {
  decorators: [
    (Story) => {
      const manyIncidentsMockStore = {
        ...mockStore,
        incidents: [
          ...mockStore.incidents,
          {
            id: 'incident_3',
            type: 'security_event' as const,
            service: 'auth',
            description: 'Suspicious login attempts detected',
            status: 'investigating' as const,
            timestamp: new Date(Date.now() - 900000),
            actions: ['IP blocked', 'Alert sent'],
          },
          {
            id: 'incident_4',
            type: 'performance_issue' as const,
            service: 'api',
            description: 'High response time detected',
            status: 'resolved' as const,
            timestamp: new Date(Date.now() - 7200000),
            duration: 120000,
            actions: ['Auto-scaled instances', 'Optimized queries'],
          },
          {
            id: 'incident_5',
            type: 'auto_recovery' as const,
            service: 'cache',
            description: 'Cache cluster failover executed',
            status: 'resolved' as const,
            timestamp: new Date(Date.now() - 10800000),
            duration: 60000,
            actions: ['Failover to backup cluster', 'Primary cluster restored'],
          },
        ],
      };
      
      require('@/store/self-healing').useSelfHealingStore.mockReturnValue(manyIncidentsMockStore);
      
      return <Story />;
    },
  ],
};

// Mobile view
export const Mobile: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile',
    },
  },
};

// Tablet view
export const Tablet: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
  },
};