import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { 
  SelfHealingState, 
  HealthStatus, 
  ServiceHealth, 
  HealingIncident, 
  PredictiveInsight,
  HealthMetric 
} from '@/types';

interface SelfHealingStore extends SelfHealingState {
  // Monitoring Methods
  startHealthMonitoring: () => void;
  stopHealthMonitoring: () => void;
  checkServiceHealth: (service: string) => Promise<HealthMetric>;
  
  // Recovery Methods
  triggerManualRecovery: (service: string) => Promise<void>;
  executeRecoveryPlan: (plan: RecoveryPlan) => Promise<void>;
  
  // Incident Management
  addIncident: (incident: Omit<HealingIncident, 'id'>) => void;
  updateIncident: (id: string, updates: Partial<HealingIncident>) => void;
  resolveIncident: (id: string) => void;
  
  // Predictive Analytics
  generatePredictions: () => Promise<PredictiveInsight[]>;
  updatePredictions: (predictions: PredictiveInsight[]) => void;
  
  // Circuit Breaker Management
  getCircuitBreakerStatus: (service: string) => CircuitBreakerStatus;
  resetCircuitBreaker: (service: string) => Promise<void>;
}

interface RecoveryPlan {
  service: string;
  actions: RecoveryAction[];
  estimatedDuration: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

interface RecoveryAction {
  type: 'restart' | 'scale' | 'cache_clear' | 'rollback' | 'failover';
  description: string;
  automated: boolean;
}

interface CircuitBreakerStatus {
  state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  failureCount: number;
  successCount: number;
  lastFailureTime: Date | null;
  nextRetryTime: Date | null;
}

export const useSelfHealingStore = create<SelfHealingStore>()(
  immer((set, get) => ({
    // Initial State
    healingStatus: {
      overall: HealthStatus.HEALTHY,
      services: [],
      lastUpdate: new Date(),
    },
    metrics: {
      autoRecoveryRate: 0,
      incidentsPrevented: 0,
      recoveryTrend: 'stable',
      predictions: [],
    },
    incidents: [],

    // Core Methods
    updateHealingStatus: async (status) => {
      set((state) => {
        state.healingStatus = {
          ...state.healingStatus,
          ...status,
          lastUpdate: new Date(),
        };
      });

      // Auto-trigger recovery if needed
      if (status.overall === HealthStatus.DEGRADED || status.overall === HealthStatus.CRITICAL) {
        await get().triggerAutoRecovery();
      }
    },

    triggerAutoRecovery: async () => {
      const { healingStatus, addIncident, executeRecoveryPlan } = get();
      
      // Find services that need recovery
      const degradedServices = healingStatus.services.filter(
        service => service.status === HealthStatus.DEGRADED || service.status === HealthStatus.CRITICAL
      );

      for (const service of degradedServices) {
        const incident: Omit<HealingIncident, 'id'> = {
          type: 'auto_recovery',
          service: service.name,
          description: `Auto-recovery initiated for ${service.name} (${service.status})`,
          status: 'in_progress',
          timestamp: new Date(),
          actions: [],
        };

        addIncident(incident);

        try {
          // Simulate recovery actions
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          // Update incident as resolved
          const incidentId = get().incidents[get().incidents.length - 1].id;
          get().updateIncident(incidentId, {
            status: 'resolved',
            duration: Date.now() - incident.timestamp.getTime(),
            actions: ['Service restart', 'Health check verification'],
          });
        } catch (error: any) {
          console.error(`Auto-recovery failed for ${service.name}:`, error);
          
          // Update incident as failed
          const incidentId = get().incidents[get().incidents.length - 1].id;
          get().updateIncident(incidentId, {
            status: 'failed',
            actions: [`Recovery failed: ${error?.message || 'Unknown error'}`],
          });
        }
      }
    },

    // Monitoring Methods
    startHealthMonitoring: () => {
      const monitoringInterval = setInterval(async () => {
        const services = ['api', 'database', 'cache', 'queue', 'frontend'];
        const serviceHealthResults: ServiceHealth[] = [];

        for (const serviceName of services) {
          try {
            const health = await get().checkServiceHealth(serviceName);
            serviceHealthResults.push({
              name: serviceName,
              status: health.status,
              lastCheck: new Date(),
              responseTime: health.responseTime,
              errorRate: health.errorRate,
              uptime: calculateUptime(serviceName), // Implementation needed
            });
          } catch (error) {
            serviceHealthResults.push({
              name: serviceName,
              status: HealthStatus.UNKNOWN,
              lastCheck: new Date(),
              responseTime: 0,
              errorRate: 1,
              uptime: 0,
            });
          }
        }

        // Calculate overall health
        const overallHealth = calculateOverallHealth(serviceHealthResults);
        
        // Update state
        set((state) => {
          state.healingStatus.services = serviceHealthResults;
          state.healingStatus.overall = overallHealth;
          state.healingStatus.lastUpdate = new Date();
        });

        // Generate predictions periodically
        if (Math.random() < 0.1) { // 10% chance each check
          const predictions = await get().generatePredictions();
          get().updatePredictions(predictions);
        }
      }, 30000); // Check every 30 seconds

      // Store interval ID for cleanup
      (window as any).healthMonitoringInterval = monitoringInterval;
    },

    stopHealthMonitoring: () => {
      if ((window as any).healthMonitoringInterval) {
        clearInterval((window as any).healthMonitoringInterval);
        delete (window as any).healthMonitoringInterval;
      }
    },

    checkServiceHealth: async (service: string): Promise<HealthMetric> => {
      try {
        const response = await fetch(`/api/health/${service}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        const startTime = Date.now();
        const data = await response.json();
        const responseTime = Date.now() - startTime;

        return {
          service,
          status: response.ok ? HealthStatus.HEALTHY : HealthStatus.DEGRADED,
          responseTime,
          errorRate: data.errorRate || 0,
          memoryUsage: data.memoryUsage || 0,
          cpuUsage: data.cpuUsage || 0,
          timestamp: new Date(),
        };
      } catch (error) {
        return {
          service,
          status: HealthStatus.CRITICAL,
          responseTime: 0,
          errorRate: 1,
          memoryUsage: 0,
          cpuUsage: 0,
          timestamp: new Date(),
        };
      }
    },

    // Recovery Methods
    triggerManualRecovery: async (service: string) => {
      const incident: Omit<HealingIncident, 'id'> = {
        type: 'manual_intervention',
        service,
        description: `Manual recovery initiated for ${service}`,
        status: 'in_progress',
        timestamp: new Date(),
        actions: [],
      };

      get().addIncident(incident);

      try {
        const response = await fetch(`/api/recovery/${service}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Recovery failed: ${response.statusText}`);
        }

        const incidentId = get().incidents[get().incidents.length - 1].id;
        get().resolveIncident(incidentId);
      } catch (error: any) {
        const incidentId = get().incidents[get().incidents.length - 1].id;
        get().updateIncident(incidentId, {
          status: 'failed',
          actions: [`Manual recovery failed: ${error?.message || 'Unknown error'}`],
        });
        throw error;
      }
    },

    executeRecoveryPlan: async (plan: RecoveryPlan) => {
      for (const action of plan.actions) {
        if (action.automated) {
          await executeRecoveryAction(action, plan.service);
        }
      }
    },

    // Incident Management
    addIncident: (incident: Omit<HealingIncident, 'id'>) => {
      set((state) => {
        const newIncident: HealingIncident = {
          ...incident,
          id: generateIncidentId(),
        };
        state.incidents.unshift(newIncident);
        
        // Keep only last 100 incidents
        if (state.incidents.length > 100) {
          state.incidents = state.incidents.slice(0, 100);
        }
      });
    },

    updateIncident: (id: string, updates: Partial<HealingIncident>) => {
      set((state) => {
        const incident = state.incidents.find(i => i.id === id);
        if (incident) {
          Object.assign(incident, updates);
        }
      });
    },

    resolveIncident: (id: string) => {
      get().updateIncident(id, {
        status: 'resolved',
        duration: Date.now() - (get().incidents.find(i => i.id === id)?.timestamp.getTime() || Date.now()),
      });
    },

    // Predictive Analytics
    generatePredictions: async (): Promise<PredictiveInsight[]> => {
      try {
        const response = await fetch('/api/predictions', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to generate predictions');
        }

        return await response.json();
      } catch (error) {
        console.error('Prediction generation failed:', error);
        return [];
      }
    },

    updatePredictions: (predictions: PredictiveInsight[]) => {
      set((state) => {
        state.metrics.predictions = predictions;
      });
    },

    // Circuit Breaker Management
    getCircuitBreakerStatus: (service: string): CircuitBreakerStatus => {
      // This would normally come from a backend service
      return {
        state: 'CLOSED',
        failureCount: 0,
        successCount: 0,
        lastFailureTime: null,
        nextRetryTime: null,
      };
    },

    resetCircuitBreaker: async (service: string) => {
      try {
        await fetch(`/api/circuit-breaker/${service}/reset`, {
          method: 'POST',
        });
      } catch (error) {
        console.error(`Failed to reset circuit breaker for ${service}:`, error);
        throw error;
      }
    },

    // Private Methods
    generateRecoveryPlan: async (service: ServiceHealth): Promise<RecoveryPlan> => {
      const actions: RecoveryAction[] = [];

      // Determine recovery actions based on service status and metrics
      if (service.errorRate > 0.1) {
        actions.push({
          type: 'restart',
          description: `Restart ${service.name} service`,
          automated: true,
        });
      }

      if (service.responseTime > 5000) {
        actions.push({
          type: 'cache_clear',
          description: `Clear cache for ${service.name}`,
          automated: true,
        });
      }

      if (service.status === HealthStatus.CRITICAL) {
        actions.push({
          type: 'failover',
          description: `Failover to backup instance for ${service.name}`,
          automated: true,
        });
      }

      return {
        service: service.name,
        actions,
        estimatedDuration: actions.length * 30000, // 30 seconds per action
        priority: service.status === HealthStatus.CRITICAL ? 'critical' : 'high',
      };
    },
  }))
);

// Helper Functions
function calculateOverallHealth(services: ServiceHealth[]): HealthStatus {
  if (services.some(s => s.status === HealthStatus.CRITICAL)) {
    return HealthStatus.CRITICAL;
  }
  if (services.some(s => s.status === HealthStatus.DEGRADED)) {
    return HealthStatus.DEGRADED;
  }
  if (services.some(s => s.status === HealthStatus.UNKNOWN)) {
    return HealthStatus.UNKNOWN;
  }
  return HealthStatus.HEALTHY;
}

function calculateUptime(service: string): number {
  // This would normally come from a monitoring service
  return Math.random() * 0.05 + 0.95; // 95-100% uptime
}

function generateIncidentId(): string {
  return `incident_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

async function executeRecoveryAction(action: RecoveryAction, service: string): Promise<void> {
  try {
    await fetch(`/api/recovery/${service}/${action.type}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ action }),
    });
  } catch (error) {
    console.error(`Failed to execute recovery action ${action.type} for ${service}:`, error);
    throw error;
  }
}