/**
 * Test Suite for Three-Way Integration Service
 * Ensures complete coverage of cross-platform synchronization
 */

import { ThreeWayIntegrationService } from '@/services/ThreeWayIntegration';
import axios from 'axios';
import { EventEmitter } from 'events';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ThreeWayIntegrationService', () => {
  let service: ThreeWayIntegrationService;
  let mockBlackPortalClient: any;
  let mockPlatformClient: any;
  let mockSupportClient: any;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();

    // Setup mock axios clients
    mockBlackPortalClient = {
      post: jest.fn(),
      get: jest.fn(),
      put: jest.fn(),
    };

    mockPlatformClient = {
      post: jest.fn(),
      get: jest.fn(),
      put: jest.fn(),
    };

    mockSupportClient = {
      post: jest.fn(),
      get: jest.fn(),
      put: jest.fn(),
    };

    // Mock axios.create to return our mock clients
    mockedAxios.create.mockImplementation((config) => {
      if (config?.baseURL?.includes('black')) return mockBlackPortalClient;
      if (config?.baseURL?.includes('app')) return mockPlatformClient;
      if (config?.baseURL?.includes('partner')) return mockSupportClient;
      return mockBlackPortalClient;
    });

    // Create service instance
    service = new ThreeWayIntegrationService();
  });

  afterEach(() => {
    // Cleanup
    service.destroy();
  });

  describe('User Synchronization', () => {
    it('should successfully sync a new user across all platforms', async () => {
      // Arrange
      const userId = 'test-user-123';
      const tier = 'void';
      
      mockBlackPortalClient.post.mockResolvedValueOnce({
        data: { 
          anonymousId: 'Quantum_Sage_42',
          hardwareLocked: true,
        },
      });

      mockPlatformClient.post.mockResolvedValueOnce({
        data: {
          encryptedPortfolioId: 'encrypted-portfolio-123',
          tradingEnabled: true,
        },
      });

      mockSupportClient.post.mockResolvedValueOnce({
        data: {
          zkProof: 'zk-proof-123',
          whatsappLinked: true,
          butlerActive: true,
        },
      });

      // Act
      const result = await service.syncUser(userId, tier);

      // Assert
      expect(result).toMatchObject({
        userId,
        tier,
        anonymousId: 'Quantum_Sage_42',
        platforms: {
          blackPortal: {
            active: true,
            features: expect.arrayContaining([
              'unlimited_trading',
              'butler_ai_quantum',
              'reality_distortion_ui',
            ]),
          },
          tradingPlatform: {
            active: true,
            portfolio: 'encrypted-portfolio-123',
            tradingLimits: {
              daily: Number.MAX_SAFE_INTEGER,
              monthly: Number.MAX_SAFE_INTEGER,
            },
          },
          supportPortal: {
            active: true,
            zkProof: 'zk-proof-123',
            whatsappLinked: true,
            butlerPersonality: 'Nexus',
          },
        },
        syncStatus: {
          syncHealth: 'healthy',
          pendingChanges: [],
        },
      });

      // Verify API calls
      expect(mockBlackPortalClient.post).toHaveBeenCalledWith('/users/sync', {
        userId,
        tier,
        features: expect.arrayContaining(['unlimited_trading']),
        hardwareLock: true,
        anonymousIdentity: true,
      });

      expect(mockPlatformClient.post).toHaveBeenCalledWith('/accounts/provision', {
        userId,
        tier,
        anonymousId: 'Quantum_Sage_42',
        tradingLimits: { daily: Number.MAX_SAFE_INTEGER, monthly: Number.MAX_SAFE_INTEGER },
        portfolioEncryption: 'zk-snark',
        features: {
          aiTrading: true,
          premiumData: true,
          quantumAnalytics: true,
        },
      });

      expect(mockSupportClient.post).toHaveBeenCalledWith('/services/initialize', {
        userId,
        tier,
        anonymousId: 'Quantum_Sage_42',
        butlerPersonality: 'Nexus',
        whatsappIntegration: true,
        zkProofGeneration: true,
        emergencyProtocols: true,
      });
    });

    it('should handle sync failures gracefully', async () => {
      // Arrange
      const userId = 'test-user-456';
      const tier = 'obsidian';
      
      mockBlackPortalClient.post.mockRejectedValueOnce(new Error('Network error'));

      // Act & Assert
      await expect(service.syncUser(userId, tier)).rejects.toThrow('Network error');
    });

    it('should emit events on successful sync', async () => {
      // Arrange
      const userId = 'test-user-789';
      const tier = 'onyx';
      const syncCompleteHandler = jest.fn();
      
      service.on('user:sync:complete', syncCompleteHandler);

      mockBlackPortalClient.post.mockResolvedValueOnce({
        data: { anonymousId: 'Silver_Navigator_88' },
      });
      mockPlatformClient.post.mockResolvedValueOnce({
        data: { encryptedPortfolioId: 'portfolio-789' },
      });
      mockSupportClient.post.mockResolvedValueOnce({
        data: { zkProof: 'zk-789', whatsappLinked: false },
      });

      // Act
      await service.syncUser(userId, tier);

      // Assert
      expect(syncCompleteHandler).toHaveBeenCalledWith(
        expect.objectContaining({
          userId,
          tier,
          anonymousId: 'Silver_Navigator_88',
        })
      );
    });
  });

  describe('Event Handling', () => {
    it('should handle user upgrade events', async () => {
      // Arrange
      const event = {
        eventId: 'evt-123',
        timestamp: new Date().toISOString(),
        source: 'trading_platform' as const,
        eventType: 'user_upgraded' as const,
        payload: {
          userId: 'user-123',
          fromTier: 'onyx',
          toTier: 'obsidian',
        },
        requiresSync: ['black_portal', 'support_portal'] as const,
      };

      mockBlackPortalClient.put.mockResolvedValueOnce({ data: { success: true } });
      mockPlatformClient.put.mockResolvedValueOnce({ data: { success: true } });
      mockSupportClient.put.mockResolvedValueOnce({ data: { success: true } });

      // Act
      await service.handleServiceEvent(event);

      // Assert
      expect(mockBlackPortalClient.put).toHaveBeenCalledWith(
        '/users/user-123/tier',
        { tier: 'obsidian' }
      );
      expect(mockPlatformClient.put).toHaveBeenCalledWith(
        '/accounts/user-123/tier',
        expect.objectContaining({ tier: 'obsidian' })
      );
      expect(mockSupportClient.put).toHaveBeenCalledWith(
        '/services/user-123/tier',
        expect.objectContaining({ tier: 'obsidian' })
      );
    });

    it('should handle trade execution events', async () => {
      // Arrange
      const event = {
        eventId: 'evt-456',
        timestamp: new Date().toISOString(),
        source: 'trading_platform' as const,
        eventType: 'trade_executed' as const,
        payload: {
          userId: 'user-456',
          trade: { symbol: 'RELIANCE', quantity: 100, price: 2500 },
          portfolio: 'encrypted-update-123',
        },
        requiresSync: ['black_portal', 'support_portal'] as const,
      };

      mockBlackPortalClient.post.mockResolvedValueOnce({ data: { success: true } });
      mockSupportClient.post.mockResolvedValueOnce({ data: { success: true } });

      // Act
      await service.handleServiceEvent(event);

      // Assert
      expect(mockBlackPortalClient.post).toHaveBeenCalledWith(
        '/users/user-456/portfolio-update',
        expect.objectContaining({
          encryptedUpdate: 'encrypted-update-123',
          timestamp: event.timestamp,
        })
      );
      expect(mockSupportClient.post).toHaveBeenCalledWith(
        '/butler/user-456/context',
        expect.objectContaining({
          type: 'trade_executed',
          data: { trade: event.payload.trade, portfolio: event.payload.portfolio },
          useForLearning: true,
        })
      );
    });

    it('should handle emergency trigger events', async () => {
      // Arrange
      const event = {
        eventId: 'evt-789',
        timestamp: new Date().toISOString(),
        source: 'support_portal' as const,
        eventType: 'emergency_triggered' as const,
        payload: {
          userId: 'user-789',
          emergencyType: 'medical',
          revealLevel: 'location_only',
        },
        requiresSync: ['black_portal', 'trading_platform'] as const,
      };

      mockBlackPortalClient.post.mockResolvedValueOnce({ data: { success: true } });
      mockPlatformClient.post.mockResolvedValueOnce({ data: { success: true } });
      mockSupportClient.post.mockResolvedValueOnce({ data: { success: true } });

      const emergencyHandler = jest.fn();
      service.on('emergency:coordinated', emergencyHandler);

      // Act
      await service.handleServiceEvent(event);

      // Assert
      expect(mockBlackPortalClient.post).toHaveBeenCalledWith(
        '/emergency/alert',
        expect.objectContaining({
          userId: 'user-789',
          type: 'medical',
          priority: 'critical',
        })
      );
      expect(mockPlatformClient.post).toHaveBeenCalledWith(
        '/accounts/user-789/emergency-pause',
        expect.objectContaining({
          reason: 'medical',
          duration: 'until_resolved',
        })
      );
      expect(emergencyHandler).toHaveBeenCalledWith({
        userId: 'user-789',
        emergencyType: 'medical',
      });
    });

    it('should handle butler interaction events', async () => {
      // Arrange
      const event = {
        eventId: 'evt-butler-123',
        timestamp: new Date().toISOString(),
        source: 'support_portal' as const,
        eventType: 'butler_interaction' as const,
        payload: {
          userId: 'user-butler',
          interaction: {
            type: 'investment_advice',
            insights: { recommendation: 'diversify_portfolio' },
          },
          context: { riskProfile: 'moderate' },
        },
        requiresSync: ['trading_platform'] as const,
      };

      mockPlatformClient.post.mockResolvedValueOnce({ data: { success: true } });

      // Act
      await service.handleServiceEvent(event);

      // Assert
      expect(mockPlatformClient.post).toHaveBeenCalledWith(
        '/ai/insights/user-butler',
        expect.objectContaining({
          source: 'butler',
          insights: { recommendation: 'diversify_portfolio' },
          applyToTrading: true,
        })
      );
    });

    it('should propagate generic events to required services', async () => {
      // Arrange
      const event = {
        eventId: 'evt-generic-123',
        timestamp: new Date().toISOString(),
        source: 'black_portal' as const,
        eventType: 'portfolio_update' as const,
        payload: { userId: 'user-generic', data: 'test' },
        requiresSync: ['trading_platform', 'support_portal'] as const,
      };

      mockPlatformClient.post.mockResolvedValueOnce({ data: { success: true } });
      mockSupportClient.post.mockResolvedValueOnce({ data: { success: true } });

      // Act
      await service.handleServiceEvent(event);

      // Assert
      expect(mockPlatformClient.post).toHaveBeenCalledWith('/events/ingest', event);
      expect(mockSupportClient.post).toHaveBeenCalledWith('/events/ingest', event);
    });
  });

  describe('Health Monitoring', () => {
    it('should perform health checks on all services', async () => {
      // Arrange
      mockBlackPortalClient.get.mockResolvedValueOnce({
        data: {
          status: 'healthy',
          metrics: { rpm: 1000, errorRate: 0.001, avgResponseTime: 45 },
        },
      });
      mockPlatformClient.get.mockResolvedValueOnce({
        data: {
          status: 'healthy',
          metrics: { rpm: 2000, errorRate: 0.002, avgResponseTime: 60 },
        },
      });
      mockSupportClient.get.mockResolvedValueOnce({
        data: {
          status: 'degraded',
          metrics: { rpm: 500, errorRate: 0.05, avgResponseTime: 150 },
        },
      });

      // Act
      const healthChecks = await service.performHealthCheck();

      // Assert
      expect(healthChecks.size).toBe(3);
      
      const blackPortalHealth = healthChecks.get('blackPortal');
      expect(blackPortalHealth).toMatchObject({
        service: 'black_portal',
        status: 'healthy',
        metrics: {
          requestsPerMinute: 1000,
          errorRate: 0.001,
          avgResponseTime: 45,
        },
      });

      const supportPortalHealth = healthChecks.get('partnerPortal');
      expect(supportPortalHealth).toMatchObject({
        service: 'support_portal',
        status: 'degraded',
      });
    });

    it('should handle health check failures', async () => {
      // Arrange
      mockBlackPortalClient.get.mockRejectedValueOnce(new Error('Connection refused'));
      mockPlatformClient.get.mockResolvedValueOnce({
        data: { status: 'healthy' },
      });
      mockSupportClient.get.mockResolvedValueOnce({
        data: { status: 'healthy' },
      });

      // Act
      const healthChecks = await service.performHealthCheck();

      // Assert
      const blackPortalHealth = healthChecks.get('blackPortal');
      expect(blackPortalHealth).toMatchObject({
        service: 'black_portal',
        status: 'down',
        latency: -1,
        metrics: {
          requestsPerMinute: 0,
          errorRate: 1,
          avgResponseTime: -1,
        },
      });
    });
  });

  describe('Integration Metrics', () => {
    it('should retrieve comprehensive integration metrics', async () => {
      // Arrange
      mockBlackPortalClient.get
        .mockResolvedValueOnce({ data: { count: 1000 } }) // active users
        .mockResolvedValueOnce({ data: { onyx: 800, obsidian: 150, void: 50 } }); // tier distribution
      
      mockPlatformClient.get
        .mockResolvedValueOnce({ data: { count: 1000 } }) // active users
        .mockResolvedValueOnce({ data: { synced: true, lastSync: new Date().toISOString() } }); // revenue sync
      
      mockSupportClient.get
        .mockResolvedValueOnce({ data: { count: 1000 } }); // active users

      // Act
      const metrics = await service.getIntegrationMetrics();

      // Assert
      expect(metrics).toMatchObject({
        activeUsers: 1000,
        syncQueueSize: 0,
        healthStatus: expect.stringMatching(/healthy|degraded|critical/),
        dataFlows: {
          portalToPlatform: expect.objectContaining({
            messagesPerMinute: expect.any(Number),
            avgLatency: expect.any(Number),
            errorRate: expect.any(Number),
            lastSync: expect.any(String),
          }),
          platformToSupport: expect.any(Object),
          supportToPortal: expect.any(Object),
        },
        tierDistribution: {
          onyx: 800,
          obsidian: 150,
          void: 50,
        },
        revenueSync: {
          synced: true,
          lastSync: expect.any(String),
        },
      });
    });

    it('should handle metric retrieval failures gracefully', async () => {
      // Arrange
      mockBlackPortalClient.get.mockRejectedValue(new Error('API Error'));
      mockPlatformClient.get.mockRejectedValue(new Error('API Error'));
      mockSupportClient.get.mockRejectedValue(new Error('API Error'));

      // Act
      const metrics = await service.getIntegrationMetrics();

      // Assert
      expect(metrics.activeUsers).toBe(0);
      expect(metrics.tierDistribution).toEqual({ onyx: 0, obsidian: 0, void: 0 });
      expect(metrics.revenueSync).toMatchObject({ synced: true });
    });
  });

  describe('Event Queue Management', () => {
    it('should add events to sync queue', async () => {
      // Arrange
      const event = {
        eventId: 'queue-test-123',
        timestamp: new Date().toISOString(),
        source: 'black_portal' as const,
        eventType: 'user_created' as const,
        payload: { userId: 'new-user' },
        requiresSync: [] as const,
      };

      // Act
      await service.handleServiceEvent(event);

      // Assert
      // Event should be processed and removed from queue
      expect(service['syncQueue'].has(event.eventId)).toBe(false);
    });

    it('should handle invalid events', async () => {
      // Arrange
      const invalidEvent = {
        eventId: '', // Invalid
        timestamp: 'invalid-date',
        source: 'unknown' as any,
        eventType: 'invalid' as any,
        payload: null,
        requiresSync: [],
      };

      // Act & Assert
      await expect(service.handleServiceEvent(invalidEvent)).rejects.toThrow();
    });
  });

  describe('Tier-Specific Features', () => {
    it('should return correct features for each tier', () => {
      // Test through user sync
      const tiers: Array<'onyx' | 'obsidian' | 'void'> = ['onyx', 'obsidian', 'void'];
      
      tiers.forEach(tier => {
        const features = service['getTierFeatures'](tier);
        
        expect(features).toContain('anonymous_circles');
        expect(features).toContain('luxury_ui');
        
        if (tier === 'void') {
          expect(features).toContain('unlimited_trading');
          expect(features).toContain('reality_distortion_ui');
          expect(features).toContain('private_banking');
        } else if (tier === 'obsidian') {
          expect(features).toContain('elite_trading');
          expect(features).toContain('quantum_ui');
          expect(features).toContain('investment_syndicates');
        } else {
          expect(features).toContain('premium_trading');
          expect(features).toContain('butler_ai_basic');
        }
      });
    });

    it('should return correct trading limits for each tier', () => {
      // Test trading limits
      const onyxLimits = service['getTradingLimits']('onyx');
      expect(onyxLimits).toEqual({
        daily: 100_000_000,
        monthly: 1_000_000_000,
      });

      const obsidianLimits = service['getTradingLimits']('obsidian');
      expect(obsidianLimits).toEqual({
        daily: 1_000_000_000,
        monthly: 10_000_000_000,
      });

      const voidLimits = service['getTradingLimits']('void');
      expect(voidLimits).toEqual({
        daily: Number.MAX_SAFE_INTEGER,
        monthly: Number.MAX_SAFE_INTEGER,
      });
    });

    it('should return correct Butler personality for each tier', () => {
      expect(service['getButlerPersonality']('onyx')).toBe('Sterling');
      expect(service['getButlerPersonality']('obsidian')).toBe('Prism');
      expect(service['getButlerPersonality']('void')).toBe('Nexus');
    });
  });

  describe('Service Lifecycle', () => {
    it('should start background processes on initialization', () => {
      // Verify intervals are set
      expect(service['syncInterval']).toBeTruthy();
      expect(service['healthCheckInterval']).toBeTruthy();
    });

    it('should clean up resources on destroy', () => {
      // Arrange
      const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
      const removeAllListenersSpy = jest.spyOn(service, 'removeAllListeners');

      // Act
      service.destroy();

      // Assert
      expect(clearIntervalSpy).toHaveBeenCalledTimes(2);
      expect(removeAllListenersSpy).toHaveBeenCalled();
      expect(service['syncInterval']).toBeNull();
      expect(service['healthCheckInterval']).toBeNull();
    });
  });

  describe('Error Handling', () => {
    it('should emit error events on sync failure', async () => {
      // Arrange
      const errorHandler = jest.fn();
      service.on('user:sync:failed', errorHandler);
      
      mockBlackPortalClient.post.mockRejectedValueOnce(new Error('Sync failed'));

      // Act
      try {
        await service.syncUser('error-user', 'void');
      } catch {
        // Expected error
      }

      // Assert
      expect(errorHandler).toHaveBeenCalledWith({
        userId: 'error-user',
        error: expect.any(Error),
      });
    });

    it('should emit error events on event processing failure', async () => {
      // Arrange
      const errorHandler = jest.fn();
      service.on('event:processing:failed', errorHandler);
      
      const event = {
        eventId: 'error-evt',
        timestamp: new Date().toISOString(),
        source: 'black_portal' as const,
        eventType: 'user_upgraded' as const,
        payload: { userId: 'user-123' },
        requiresSync: ['trading_platform'] as const,
      };

      mockPlatformClient.post.mockRejectedValueOnce(new Error('Event processing failed'));

      // Act
      await service.handleServiceEvent(event);

      // Assert
      expect(errorHandler).toHaveBeenCalledWith({
        event,
        error: expect.any(Error),
      });
    });
  });
});