/**
 * Test Suite for Integration Sync API Routes
 * Tests synchronization endpoints and webhook handling
 */

import { NextRequest } from 'next/server';
import { POST, GET, PUT } from '@/api/integration/sync';
import { threeWayIntegration } from '@/services/ThreeWayIntegration';

// Mock the integration service
jest.mock('@/services/ThreeWayIntegration', () => ({
  threeWayIntegration: {
    syncUser: jest.fn(),
    handleServiceEvent: jest.fn(),
    performHealthCheck: jest.fn(),
    getIntegrationMetrics: jest.fn(),
  },
}));

describe('Integration Sync API', () => {
  let mockRequest: Partial<NextRequest>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockRequest = {
      url: 'http://localhost:3000/api/integration/sync',
      json: jest.fn(),
      headers: new Headers(),
    };
  });

  describe('POST /api/integration/sync/user', () => {
    it('should sync user successfully', async () => {
      // Arrange
      const requestBody = {
        userId: 'test-user-123',
        tier: 'void' as const,
        source: 'black_portal' as const,
      };

      const mockSyncResult = {
        userId: 'test-user-123',
        tier: 'void',
        anonymousId: 'Quantum_Sage_42',
        platforms: {
          blackPortal: { active: true, features: ['unlimited_trading'] },
          tradingPlatform: { active: true, portfolio: 'encrypted-123' },
          supportPortal: { active: true, zkProof: 'zk-123' },
        },
        syncStatus: { syncHealth: 'healthy' },
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync/user';
      (mockRequest.json as jest.Mock).mockResolvedValue(requestBody);
      (threeWayIntegration.syncUser as jest.Mock).mockResolvedValue(mockSyncResult);

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData).toEqual({
        success: true,
        data: mockSyncResult,
        message: 'User synchronized successfully across all platforms',
      });

      expect(threeWayIntegration.syncUser).toHaveBeenCalledWith('test-user-123', 'void');
    });

    it('should handle validation errors', async () => {
      // Arrange
      const invalidRequestBody = {
        userId: '', // Invalid - empty string
        tier: 'invalid-tier',
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync/user';
      (mockRequest.json as jest.Mock).mockResolvedValue(invalidRequestBody);

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(400);
      expect(responseData.error).toBe('Validation error');
      expect(responseData.details).toBeDefined();
    });

    it('should handle sync service errors', async () => {
      // Arrange
      const requestBody = {
        userId: 'error-user',
        tier: 'onyx' as const,
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync/user';
      (mockRequest.json as jest.Mock).mockResolvedValue(requestBody);
      (threeWayIntegration.syncUser as jest.Mock).mockRejectedValue(
        new Error('Sync service unavailable')
      );

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(500);
      expect(responseData.error).toBe('Internal server error');
      expect(responseData.message).toBe('Sync service unavailable');
    });
  });

  describe('POST /api/integration/sync/event', () => {
    it('should process service event successfully', async () => {
      // Arrange
      const eventBody = {
        eventId: 'evt-123',
        timestamp: new Date().toISOString(),
        source: 'trading_platform' as const,
        eventType: 'trade_executed' as const,
        payload: {
          userId: 'user-123',
          trade: { symbol: 'RELIANCE', quantity: 100 },
        },
        requiresSync: ['black_portal', 'support_portal'] as const,
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync/event';
      (mockRequest.json as jest.Mock).mockResolvedValue(eventBody);
      (threeWayIntegration.handleServiceEvent as jest.Mock).mockResolvedValue(undefined);

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData).toEqual({
        success: true,
        message: 'Event processed and propagated successfully',
        eventId: 'evt-123',
      });

      expect(threeWayIntegration.handleServiceEvent).toHaveBeenCalledWith(eventBody);
    });

    it('should handle invalid event structure', async () => {
      // Arrange
      const invalidEventBody = {
        eventId: 'evt-123',
        // Missing required fields
        payload: {},
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync/event';
      (mockRequest.json as jest.Mock).mockResolvedValue(invalidEventBody);

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(400);
      expect(responseData.error).toBe('Validation error');
    });
  });

  describe('POST /api/integration/sync/bulk', () => {
    it('should handle bulk synchronization successfully', async () => {
      // Arrange
      const bulkRequestBody = {
        userIds: ['user1', 'user2', 'user3'],
        syncType: 'full' as const,
        source: 'black_portal' as const,
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync/bulk';
      (mockRequest.json as jest.Mock).mockResolvedValue(bulkRequestBody);

      // Mock successful sync for all users
      (threeWayIntegration.syncUser as jest.Mock)
        .mockResolvedValueOnce({ userId: 'user1', tier: 'onyx' })
        .mockResolvedValueOnce({ userId: 'user2', tier: 'obsidian' })
        .mockResolvedValueOnce({ userId: 'user3', tier: 'void' });

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData.success).toBe(true);
      expect(responseData.summary).toEqual({
        total: 3,
        successful: 3,
        failed: 0,
      });
      expect(responseData.results).toHaveLength(3);
      expect(responseData.results[0]).toMatchObject({
        userId: 'user1',
        status: 'fulfilled',
      });
    });

    it('should handle partial failures in bulk sync', async () => {
      // Arrange
      const bulkRequestBody = {
        userIds: ['user1', 'user2'],
        syncType: 'incremental' as const,
        source: 'trading_platform' as const,
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync/bulk';
      (mockRequest.json as jest.Mock).mockResolvedValue(bulkRequestBody);

      // Mock one success, one failure
      (threeWayIntegration.syncUser as jest.Mock)
        .mockResolvedValueOnce({ userId: 'user1', tier: 'onyx' })
        .mockRejectedValueOnce(new Error('Sync failed for user2'));

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData.summary).toEqual({
        total: 2,
        successful: 1,
        failed: 1,
      });
      expect(responseData.results[1]).toMatchObject({
        userId: 'user2',
        status: 'rejected',
        error: 'Sync failed for user2',
      });
    });

    it('should validate bulk request limits', async () => {
      // Arrange
      const oversizedBulkRequest = {
        userIds: new Array(101).fill(0).map((_, i) => `user${i}`), // 101 users (over limit)
        syncType: 'full' as const,
        source: 'black_portal' as const,
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync/bulk';
      (mockRequest.json as jest.Mock).mockResolvedValue(oversizedBulkRequest);

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(400);
      expect(responseData.error).toBe('Validation error');
    });
  });

  describe('GET /api/integration/sync (Health Check)', () => {
    it('should return health status for all services', async () => {
      // Arrange
      const mockHealthChecks = new Map([
        ['blackPortal', {
          service: 'black_portal',
          status: 'healthy' as const,
          latency: 45,
          lastCheck: new Date().toISOString(),
          metrics: { requestsPerMinute: 1000, errorRate: 0.001, avgResponseTime: 45 },
        }],
        ['gridworksPlatform', {
          service: 'trading_platform',
          status: 'healthy' as const,
          latency: 60,
          lastCheck: new Date().toISOString(),
          metrics: { requestsPerMinute: 2000, errorRate: 0.002, avgResponseTime: 60 },
        }],
      ]);

      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      (threeWayIntegration.performHealthCheck as jest.Mock).mockResolvedValue(mockHealthChecks);

      // Act
      const response = await GET(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData.status).toBe('operational');
      expect(responseData.services).toHaveLength(2);
      expect(responseData.services[0]).toMatchObject({
        service: 'blackPortal',
        status: 'healthy',
        latency: 45,
      });
    });

    it('should include metrics when requested', async () => {
      // Arrange
      const mockMetrics = {
        activeUsers: 1000,
        syncQueueSize: 5,
        healthStatus: 'healthy' as const,
        dataFlows: {},
        tierDistribution: { onyx: 800, obsidian: 150, void: 50 },
        revenueSync: { synced: true, lastSync: new Date().toISOString() },
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync?metrics=true';
      (threeWayIntegration.performHealthCheck as jest.Mock).mockResolvedValue(new Map());
      (threeWayIntegration.getIntegrationMetrics as jest.Mock).mockResolvedValue(mockMetrics);

      // Act
      const response = await GET(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData.metrics).toEqual(mockMetrics);
    });

    it('should detect partial outage status', async () => {
      // Arrange
      const mockHealthChecks = new Map([
        ['blackPortal', {
          service: 'black_portal',
          status: 'down' as const,
          latency: -1,
          lastCheck: new Date().toISOString(),
          metrics: { requestsPerMinute: 0, errorRate: 1, avgResponseTime: -1 },
        }],
        ['gridworksPlatform', {
          service: 'trading_platform',
          status: 'healthy' as const,
          latency: 60,
          lastCheck: new Date().toISOString(),
          metrics: { requestsPerMinute: 2000, errorRate: 0.002, avgResponseTime: 60 },
        }],
      ]);

      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      (threeWayIntegration.performHealthCheck as jest.Mock).mockResolvedValue(mockHealthChecks);

      // Act
      const response = await GET(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData.status).toBe('partial_outage');
    });

    it('should detect degraded performance status', async () => {
      // Arrange
      const mockHealthChecks = new Map([
        ['blackPortal', {
          service: 'black_portal',
          status: 'degraded' as const,
          latency: 200,
          lastCheck: new Date().toISOString(),
          metrics: { requestsPerMinute: 500, errorRate: 0.1, avgResponseTime: 200 },
        }],
        ['gridworksPlatform', {
          service: 'trading_platform',
          status: 'healthy' as const,
          latency: 60,
          lastCheck: new Date().toISOString(),
          metrics: { requestsPerMinute: 2000, errorRate: 0.002, avgResponseTime: 60 },
        }],
      ]);

      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      (threeWayIntegration.performHealthCheck as jest.Mock).mockResolvedValue(mockHealthChecks);

      // Act
      const response = await GET(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData.status).toBe('degraded_performance');
    });

    it('should handle health check failures', async () => {
      // Arrange
      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      (threeWayIntegration.performHealthCheck as jest.Mock).mockRejectedValue(
        new Error('Health check service unavailable')
      );

      // Act
      const response = await GET(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(503);
      expect(responseData.status).toBe('error');
      expect(responseData.error).toBe('Health check service unavailable');
    });
  });

  describe('PUT /api/integration/sync (Webhooks)', () => {
    it('should process trading platform webhook', async () => {
      // Arrange
      const webhookPayload = {
        id: 'trade-123',
        type: 'order_filled',
        userId: 'user-123',
        data: { symbol: 'RELIANCE', quantity: 100 },
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      mockRequest.headers = new Headers({
        'x-webhook-signature': 'valid-signature',
        'x-webhook-source': 'trading_platform',
      });
      (mockRequest.json as jest.Mock).mockResolvedValue(webhookPayload);
      (threeWayIntegration.handleServiceEvent as jest.Mock).mockResolvedValue(undefined);

      // Act
      const response = await PUT(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(responseData.success).toBe(true);
      expect(responseData.message).toBe('Webhook processed successfully');

      expect(threeWayIntegration.handleServiceEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          source: 'trading_platform',
          eventType: 'trade_executed',
          payload: webhookPayload,
        })
      );
    });

    it('should process support portal webhook', async () => {
      // Arrange
      const webhookPayload = {
        id: 'butler-456',
        type: 'butler_message',
        userId: 'user-456',
        data: { message: 'Investment advice requested' },
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      mockRequest.headers = new Headers({
        'x-webhook-signature': 'valid-signature',
        'x-webhook-source': 'support_portal',
      });
      (mockRequest.json as jest.Mock).mockResolvedValue(webhookPayload);
      (threeWayIntegration.handleServiceEvent as jest.Mock).mockResolvedValue(undefined);

      // Act
      const response = await PUT(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(threeWayIntegration.handleServiceEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          source: 'support_portal',
          eventType: 'butler_interaction',
          payload: webhookPayload,
        })
      );
    });

    it('should process payment webhook', async () => {
      // Arrange
      const webhookPayload = {
        id: 'pay-789',
        userId: 'user-789',
        amount: 1000000,
        currency: 'INR',
        status: 'success',
      };

      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      mockRequest.headers = new Headers({
        'x-webhook-signature': 'valid-signature',
        'x-webhook-source': 'payment_processor',
      });
      (mockRequest.json as jest.Mock).mockResolvedValue(webhookPayload);
      (threeWayIntegration.handleServiceEvent as jest.Mock).mockResolvedValue(undefined);

      // Act
      const response = await PUT(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(200);
      expect(threeWayIntegration.handleServiceEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          source: 'trading_platform',
          eventType: 'portfolio_update',
          payload: expect.objectContaining({
            userId: 'user-789',
            amount: 1000000,
            type: 'deposit',
          }),
        })
      );
    });

    it('should reject webhooks with invalid signatures', async () => {
      // Arrange
      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      mockRequest.headers = new Headers({
        'x-webhook-signature': '', // Invalid signature
        'x-webhook-source': 'trading_platform',
      });
      (mockRequest.text as jest.Mock) = jest.fn().mockResolvedValue('{}');

      // Act
      const response = await PUT(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(401);
      expect(responseData.error).toBe('Invalid signature');
    });

    it('should handle unknown webhook sources', async () => {
      // Arrange
      const webhookPayload = { id: 'unknown-123' };

      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      mockRequest.headers = new Headers({
        'x-webhook-signature': 'valid-signature',
        'x-webhook-source': 'unknown_service',
      });
      (mockRequest.json as jest.Mock).mockResolvedValue(webhookPayload);

      // Act
      const response = await PUT(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(400);
      expect(responseData.error).toBe('Unknown webhook source');
    });

    it('should handle webhook processing errors', async () => {
      // Arrange
      const webhookPayload = { id: 'error-webhook' };

      mockRequest.url = 'http://localhost:3000/api/integration/sync';
      mockRequest.headers = new Headers({
        'x-webhook-signature': 'valid-signature',
        'x-webhook-source': 'trading_platform',
      });
      (mockRequest.json as jest.Mock).mockResolvedValue(webhookPayload);
      (threeWayIntegration.handleServiceEvent as jest.Mock).mockRejectedValue(
        new Error('Event processing failed')
      );

      // Act
      const response = await PUT(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(500);
      expect(responseData.error).toBe('Webhook processing failed');
      expect(responseData.message).toBe('Event processing failed');
    });
  });

  describe('Invalid Endpoints', () => {
    it('should return 404 for unknown endpoints', async () => {
      // Arrange
      mockRequest.url = 'http://localhost:3000/api/integration/sync/unknown';
      (mockRequest.json as jest.Mock).mockResolvedValue({});

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(404);
      expect(responseData.error).toBe('Invalid endpoint');
    });
  });

  describe('Edge Cases', () => {
    it('should handle malformed JSON requests', async () => {
      // Arrange
      mockRequest.url = 'http://localhost:3000/api/integration/sync/user';
      (mockRequest.json as jest.Mock).mockRejectedValue(new Error('Invalid JSON'));

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(500);
      expect(responseData.error).toBe('Internal server error');
      expect(responseData.message).toBe('Invalid JSON');
    });

    it('should handle missing request body', async () => {
      // Arrange
      mockRequest.url = 'http://localhost:3000/api/integration/sync/user';
      (mockRequest.json as jest.Mock).mockResolvedValue(null);

      // Act
      const response = await POST(mockRequest as NextRequest);
      const responseData = await response.json();

      // Assert
      expect(response.status).toBe(400);
      expect(responseData.error).toBe('Validation error');
    });
  });
});