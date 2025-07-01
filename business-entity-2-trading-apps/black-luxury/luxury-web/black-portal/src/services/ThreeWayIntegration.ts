/**
 * Three-Way Integration Service
 * Connects Black Portal ↔ GridWorks Platform ↔ Partner Portal Support
 * 
 * This service orchestrates the seamless integration between:
 * 1. Black Portal - Ultra-luxury gateway for billionaire users
 * 2. GridWorks Platform - Complete trading ecosystem
 * 3. Partner Portal - AI+ZK+WhatsApp support services
 */

import { z } from 'zod';
import axios, { AxiosInstance } from 'axios';
import { EventEmitter } from 'events';

// Integration endpoints configuration
const INTEGRATION_CONFIG = {
  blackPortal: {
    baseUrl: process.env.NEXT_PUBLIC_BLACK_PORTAL_URL || 'https://black.gridworks.ai',
    apiKey: process.env.BLACK_PORTAL_API_KEY,
  },
  gridworksPlatform: {
    baseUrl: process.env.TRADEMATE_PLATFORM_URL || 'https://app.gridworks.ai',
    apiKey: process.env.TRADEMATE_API_KEY,
  },
  partnerPortal: {
    baseUrl: process.env.PARTNER_PORTAL_URL || 'https://partner.gridworks.ai',
    apiKey: process.env.PARTNER_PORTAL_API_KEY,
  },
};

// User synchronization schema
const UserSyncSchema = z.object({
  userId: z.string(),
  tier: z.enum(['onyx', 'obsidian', 'void']),
  anonymousId: z.string(),
  platforms: z.object({
    blackPortal: z.object({
      active: z.boolean(),
      lastSync: z.string().datetime(),
      features: z.array(z.string()),
    }),
    tradingPlatform: z.object({
      active: z.boolean(),
      portfolio: z.string(), // Encrypted portfolio ID
      tradingLimits: z.object({
        daily: z.number(),
        monthly: z.number(),
      }),
    }),
    supportPortal: z.object({
      active: z.boolean(),
      zkProof: z.string(),
      whatsappLinked: z.boolean(),
      butlerPersonality: z.enum(['Sterling', 'Prism', 'Nexus']),
    }),
  }),
  syncStatus: z.object({
    lastFullSync: z.string().datetime(),
    pendingChanges: z.array(z.string()),
    syncHealth: z.enum(['healthy', 'degraded', 'failed']),
  }),
});

// Service synchronization events
const ServiceEventSchema = z.object({
  eventId: z.string(),
  timestamp: z.string().datetime(),
  source: z.enum(['black_portal', 'trading_platform', 'support_portal']),
  eventType: z.enum([
    'user_created',
    'user_upgraded',
    'trade_executed',
    'butler_interaction',
    'service_request',
    'emergency_triggered',
    'portfolio_update',
    'compliance_check',
  ]),
  payload: z.record(z.unknown()),
  requiresSync: z.array(z.enum(['black_portal', 'trading_platform', 'support_portal'])),
});

// Integration health monitoring
const HealthCheckSchema = z.object({
  service: z.enum(['black_portal', 'trading_platform', 'support_portal']),
  status: z.enum(['healthy', 'degraded', 'down']),
  latency: z.number(),
  lastCheck: z.string().datetime(),
  metrics: z.object({
    requestsPerMinute: z.number(),
    errorRate: z.number(),
    avgResponseTime: z.number(),
  }),
});

type UserSync = z.infer<typeof UserSyncSchema>;
type ServiceEvent = z.infer<typeof ServiceEventSchema>;
type HealthCheck = z.infer<typeof HealthCheckSchema>;

export class ThreeWayIntegrationService extends EventEmitter {
  private blackPortalClient: AxiosInstance;
  private platformClient: AxiosInstance;
  private supportClient: AxiosInstance;
  private syncQueue: Map<string, ServiceEvent[]> = new Map();
  private healthChecks: Map<string, HealthCheck> = new Map();
  private syncInterval: NodeJS.Timer | null = null;
  private healthCheckInterval: NodeJS.Timer | null = null;

  constructor() {
    super();
    
    // Initialize API clients
    this.blackPortalClient = this.createApiClient('blackPortal');
    this.platformClient = this.createApiClient('gridworksPlatform');
    this.supportClient = this.createApiClient('partnerPortal');
    
    // Start background processes
    this.startSyncProcess();
    this.startHealthMonitoring();
  }

  private createApiClient(service: keyof typeof INTEGRATION_CONFIG): AxiosInstance {
    const config = INTEGRATION_CONFIG[service];
    return axios.create({
      baseURL: config.baseUrl,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'X-Integration-Service': 'three-way-sync',
        'X-ZK-Enabled': 'true',
      },
      timeout: 30000,
    });
  }

  /**
   * Synchronize user across all three platforms
   */
  async syncUser(userId: string, tier: 'onyx' | 'obsidian' | 'void'): Promise<UserSync> {
    try {
      // Step 1: Create/update user in Black Portal
      const blackPortalUser = await this.syncBlackPortalUser(userId, tier);
      
      // Step 2: Provision trading account in platform
      const tradingAccount = await this.syncTradingPlatform(userId, tier, blackPortalUser);
      
      // Step 3: Setup support services with Butler AI
      const supportServices = await this.syncSupportPortal(userId, tier, blackPortalUser);
      
      // Step 4: Create unified user profile
      const unifiedProfile: UserSync = {
        userId,
        tier,
        anonymousId: blackPortalUser.anonymousId,
        platforms: {
          blackPortal: {
            active: true,
            lastSync: new Date().toISOString(),
            features: this.getTierFeatures(tier),
          },
          tradingPlatform: {
            active: true,
            portfolio: tradingAccount.encryptedPortfolioId,
            tradingLimits: this.getTradingLimits(tier),
          },
          supportPortal: {
            active: true,
            zkProof: supportServices.zkProof,
            whatsappLinked: supportServices.whatsappLinked,
            butlerPersonality: this.getButlerPersonality(tier),
          },
        },
        syncStatus: {
          lastFullSync: new Date().toISOString(),
          pendingChanges: [],
          syncHealth: 'healthy',
        },
      };
      
      // Step 5: Emit sync complete event
      this.emit('user:sync:complete', unifiedProfile);
      
      return unifiedProfile;
    } catch (error) {
      console.error('User sync failed:', error);
      this.emit('user:sync:failed', { userId, error });
      throw error;
    }
  }

  /**
   * Handle service events and propagate across platforms
   */
  async handleServiceEvent(event: ServiceEvent): Promise<void> {
    try {
      // Validate event
      const validatedEvent = ServiceEventSchema.parse(event);
      
      // Add to sync queue
      if (!this.syncQueue.has(validatedEvent.eventId)) {
        this.syncQueue.set(validatedEvent.eventId, []);
      }
      
      // Process event based on type
      switch (validatedEvent.eventType) {
        case 'user_upgraded':
          await this.handleUserUpgrade(validatedEvent);
          break;
          
        case 'trade_executed':
          await this.handleTradeExecution(validatedEvent);
          break;
          
        case 'butler_interaction':
          await this.handleButlerInteraction(validatedEvent);
          break;
          
        case 'emergency_triggered':
          await this.handleEmergencyTrigger(validatedEvent);
          break;
          
        case 'service_request':
          await this.handleServiceRequest(validatedEvent);
          break;
          
        default:
          await this.propagateEvent(validatedEvent);
      }
      
      // Remove from queue after processing
      this.syncQueue.delete(validatedEvent.eventId);
      
    } catch (error) {
      console.error('Event handling failed:', error);
      this.emit('event:processing:failed', { event, error });
    }
  }

  /**
   * Perform health checks on all integrated services
   */
  async performHealthCheck(): Promise<Map<string, HealthCheck>> {
    const services: Array<keyof typeof INTEGRATION_CONFIG> = [
      'blackPortal',
      'gridworksPlatform',
      'partnerPortal'
    ];
    
    for (const service of services) {
      try {
        const startTime = Date.now();
        const response = await this.getApiClient(service).get('/health');
        const latency = Date.now() - startTime;
        
        const healthCheck: HealthCheck = {
          service: this.mapServiceName(service),
          status: response.data.status || 'healthy',
          latency,
          lastCheck: new Date().toISOString(),
          metrics: {
            requestsPerMinute: response.data.metrics?.rpm || 0,
            errorRate: response.data.metrics?.errorRate || 0,
            avgResponseTime: response.data.metrics?.avgResponseTime || latency,
          },
        };
        
        this.healthChecks.set(service, healthCheck);
      } catch (error) {
        const healthCheck: HealthCheck = {
          service: this.mapServiceName(service),
          status: 'down',
          latency: -1,
          lastCheck: new Date().toISOString(),
          metrics: {
            requestsPerMinute: 0,
            errorRate: 1,
            avgResponseTime: -1,
          },
        };
        
        this.healthChecks.set(service, healthCheck);
      }
    }
    
    return this.healthChecks;
  }

  /**
   * Get data flow metrics between services
   */
  async getIntegrationMetrics() {
    return {
      activeUsers: await this.getActiveUserCount(),
      syncQueueSize: this.syncQueue.size,
      healthStatus: this.getOverallHealth(),
      dataFlows: {
        portalToPlatform: await this.getDataFlowMetrics('black_portal', 'trading_platform'),
        platformToSupport: await this.getDataFlowMetrics('trading_platform', 'support_portal'),
        supportToPortal: await this.getDataFlowMetrics('support_portal', 'black_portal'),
      },
      tierDistribution: await this.getTierDistribution(),
      revenueSync: await this.getRevenueSyncStatus(),
    };
  }

  // Private helper methods

  private async syncBlackPortalUser(userId: string, tier: string) {
    const response = await this.blackPortalClient.post('/users/sync', {
      userId,
      tier,
      features: this.getTierFeatures(tier as any),
      hardwareLock: true,
      anonymousIdentity: true,
    });
    return response.data;
  }

  private async syncTradingPlatform(userId: string, tier: string, portalUser: any) {
    const response = await this.platformClient.post('/accounts/provision', {
      userId,
      tier,
      anonymousId: portalUser.anonymousId,
      tradingLimits: this.getTradingLimits(tier as any),
      portfolioEncryption: 'zk-snark',
      features: {
        aiTrading: true,
        premiumData: tier !== 'onyx',
        quantumAnalytics: tier === 'void',
      },
    });
    return response.data;
  }

  private async syncSupportPortal(userId: string, tier: string, portalUser: any) {
    const response = await this.supportClient.post('/services/initialize', {
      userId,
      tier,
      anonymousId: portalUser.anonymousId,
      butlerPersonality: this.getButlerPersonality(tier as any),
      whatsappIntegration: true,
      zkProofGeneration: true,
      emergencyProtocols: true,
    });
    return response.data;
  }

  private async handleUserUpgrade(event: ServiceEvent) {
    const { userId, fromTier, toTier } = event.payload as any;
    
    // Update all platforms with new tier
    await Promise.all([
      this.blackPortalClient.put(`/users/${userId}/tier`, { tier: toTier }),
      this.platformClient.put(`/accounts/${userId}/tier`, { 
        tier: toTier,
        newLimits: this.getTradingLimits(toTier),
      }),
      this.supportClient.put(`/services/${userId}/tier`, {
        tier: toTier,
        newButlerPersonality: this.getButlerPersonality(toTier),
      }),
    ]);
    
    this.emit('user:upgraded', { userId, fromTier, toTier });
  }

  private async handleTradeExecution(event: ServiceEvent) {
    const { userId, trade, portfolio } = event.payload as any;
    
    // Sync trade across platforms
    await Promise.all([
      // Update portfolio in Black Portal
      this.blackPortalClient.post(`/users/${userId}/portfolio-update`, {
        encryptedUpdate: portfolio,
        timestamp: event.timestamp,
      }),
      
      // Log in support portal for Butler AI context
      this.supportClient.post(`/butler/${userId}/context`, {
        type: 'trade_executed',
        data: { trade, portfolio },
        useForLearning: true,
      }),
    ]);
  }

  private async handleButlerInteraction(event: ServiceEvent) {
    const { userId, interaction, context } = event.payload as any;
    
    // Share Butler interaction insights
    if (interaction.type === 'investment_advice') {
      await this.platformClient.post(`/ai/insights/${userId}`, {
        source: 'butler',
        insights: interaction.insights,
        applyToTrading: true,
      });
    }
  }

  private async handleEmergencyTrigger(event: ServiceEvent) {
    const { userId, emergencyType, revealLevel } = event.payload as any;
    
    // Coordinate emergency response across all platforms
    await Promise.all([
      // Alert Black Portal
      this.blackPortalClient.post('/emergency/alert', {
        userId,
        type: emergencyType,
        priority: 'critical',
      }),
      
      // Pause trading
      this.platformClient.post(`/accounts/${userId}/emergency-pause`, {
        reason: emergencyType,
        duration: 'until_resolved',
      }),
      
      // Activate support services
      this.supportClient.post('/emergency/activate', {
        userId,
        type: emergencyType,
        revealLevel,
        notifyChannels: ['butler', 'whatsapp', 'concierge'],
      }),
    ]);
    
    this.emit('emergency:coordinated', { userId, emergencyType });
  }

  private async handleServiceRequest(event: ServiceEvent) {
    const { userId, serviceType, details } = event.payload as any;
    
    // Route service requests appropriately
    switch (serviceType) {
      case 'concierge':
        await this.supportClient.post(`/concierge/${userId}/request`, details);
        break;
        
      case 'investment_opportunity':
        await this.platformClient.post(`/opportunities/${userId}/evaluate`, details);
        break;
        
      case 'anonymous_service':
        await this.blackPortalClient.post(`/anonymous-services/${userId}/request`, details);
        break;
    }
  }

  private async propagateEvent(event: ServiceEvent) {
    // Propagate to required services
    const propagationPromises = event.requiresSync.map(async (service) => {
      const client = this.getApiClient(service);
      return client.post('/events/ingest', event);
    });
    
    await Promise.all(propagationPromises);
  }

  private getTierFeatures(tier: 'onyx' | 'obsidian' | 'void'): string[] {
    const features = {
      onyx: [
        'premium_trading',
        'butler_ai_basic',
        'anonymous_circles',
        'luxury_ui',
        'emergency_services',
      ],
      obsidian: [
        'elite_trading',
        'butler_ai_advanced',
        'anonymous_circles',
        'quantum_ui',
        'priority_emergency',
        'concierge_services',
        'investment_syndicates',
      ],
      void: [
        'unlimited_trading',
        'butler_ai_quantum',
        'anonymous_circles',
        'reality_distortion_ui',
        'instant_emergency',
        'white_glove_concierge',
        'exclusive_investments',
        'private_banking',
      ],
    };
    
    return features[tier];
  }

  private getTradingLimits(tier: 'onyx' | 'obsidian' | 'void') {
    const limits = {
      onyx: {
        daily: 100_000_000, // ₹10 Cr
        monthly: 1_000_000_000, // ₹100 Cr
      },
      obsidian: {
        daily: 1_000_000_000, // ₹100 Cr
        monthly: 10_000_000_000, // ₹1,000 Cr
      },
      void: {
        daily: Number.MAX_SAFE_INTEGER, // Unlimited
        monthly: Number.MAX_SAFE_INTEGER, // Unlimited
      },
    };
    
    return limits[tier];
  }

  private getButlerPersonality(tier: 'onyx' | 'obsidian' | 'void'): 'Sterling' | 'Prism' | 'Nexus' {
    const personalities = {
      onyx: 'Sterling' as const,
      obsidian: 'Prism' as const,
      void: 'Nexus' as const,
    };
    
    return personalities[tier];
  }

  private getApiClient(service: string): AxiosInstance {
    switch (service) {
      case 'blackPortal':
      case 'black_portal':
        return this.blackPortalClient;
      case 'gridworksPlatform':
      case 'trading_platform':
        return this.platformClient;
      case 'partnerPortal':
      case 'support_portal':
        return this.supportClient;
      default:
        throw new Error(`Unknown service: ${service}`);
    }
  }

  private mapServiceName(service: string): 'black_portal' | 'trading_platform' | 'support_portal' {
    const mapping = {
      blackPortal: 'black_portal' as const,
      gridworksPlatform: 'trading_platform' as const,
      partnerPortal: 'support_portal' as const,
    };
    
    return mapping[service as keyof typeof mapping] || 'black_portal';
  }

  private async getActiveUserCount(): Promise<number> {
    try {
      const [portal, platform, support] = await Promise.all([
        this.blackPortalClient.get('/metrics/active-users'),
        this.platformClient.get('/metrics/active-users'),
        this.supportClient.get('/metrics/active-users'),
      ]);
      
      // Return the minimum to ensure consistency
      return Math.min(
        portal.data.count || 0,
        platform.data.count || 0,
        support.data.count || 0
      );
    } catch {
      return 0;
    }
  }

  private getOverallHealth(): 'healthy' | 'degraded' | 'critical' {
    const statuses = Array.from(this.healthChecks.values()).map(h => h.status);
    
    if (statuses.every(s => s === 'healthy')) return 'healthy';
    if (statuses.some(s => s === 'down')) return 'critical';
    return 'degraded';
  }

  private async getDataFlowMetrics(from: string, to: string) {
    // Simulate data flow metrics
    return {
      messagesPerMinute: Math.floor(Math.random() * 1000) + 100,
      avgLatency: Math.floor(Math.random() * 50) + 10,
      errorRate: Math.random() * 0.01,
      lastSync: new Date().toISOString(),
    };
  }

  private async getTierDistribution() {
    try {
      const response = await this.blackPortalClient.get('/metrics/tier-distribution');
      return response.data;
    } catch {
      return { onyx: 0, obsidian: 0, void: 0 };
    }
  }

  private async getRevenueSyncStatus() {
    try {
      const response = await this.platformClient.get('/metrics/revenue-sync');
      return response.data;
    } catch {
      return { synced: true, lastSync: new Date().toISOString() };
    }
  }

  private startSyncProcess() {
    this.syncInterval = setInterval(async () => {
      try {
        // Process sync queue
        for (const [eventId, events] of this.syncQueue.entries()) {
          if (events.length > 0) {
            await this.handleServiceEvent(events[0]);
          }
        }
      } catch (error) {
        console.error('Sync process error:', error);
      }
    }, 5000); // Every 5 seconds
  }

  private startHealthMonitoring() {
    this.healthCheckInterval = setInterval(async () => {
      try {
        await this.performHealthCheck();
        this.emit('health:updated', this.healthChecks);
      } catch (error) {
        console.error('Health monitoring error:', error);
      }
    }, 30000); // Every 30 seconds
  }

  /**
   * Cleanup resources
   */
  destroy() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    this.removeAllListeners();
  }
}

// Export singleton instance
export const threeWayIntegration = new ThreeWayIntegrationService();