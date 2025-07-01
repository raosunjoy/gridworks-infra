/**
 * API Route for Three-Way Integration Synchronization
 * Handles cross-platform user and data synchronization
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { threeWayIntegration } from '@/services/ThreeWayIntegration';

// Request validation schemas
const UserSyncRequestSchema = z.object({
  userId: z.string().min(1),
  tier: z.enum(['onyx', 'obsidian', 'void']),
  source: z.enum(['black_portal', 'trading_platform', 'support_portal']).optional(),
  forceSync: z.boolean().optional(),
});

const EventSyncRequestSchema = z.object({
  eventId: z.string().min(1),
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

const BulkSyncRequestSchema = z.object({
  userIds: z.array(z.string()).min(1).max(100),
  syncType: z.enum(['full', 'incremental', 'portfolio_only']),
  source: z.enum(['black_portal', 'trading_platform', 'support_portal']),
});

// API route handlers
export async function POST(request: NextRequest) {
  try {
    const { pathname } = new URL(request.url);
    const body = await request.json();

    // User synchronization endpoint
    if (pathname.endsWith('/sync/user')) {
      const validatedData = UserSyncRequestSchema.parse(body);
      
      const result = await threeWayIntegration.syncUser(
        validatedData.userId,
        validatedData.tier
      );

      return NextResponse.json({
        success: true,
        data: result,
        message: 'User synchronized successfully across all platforms',
      });
    }

    // Event synchronization endpoint
    if (pathname.endsWith('/sync/event')) {
      const validatedData = EventSyncRequestSchema.parse(body);
      
      await threeWayIntegration.handleServiceEvent(validatedData);

      return NextResponse.json({
        success: true,
        message: 'Event processed and propagated successfully',
        eventId: validatedData.eventId,
      });
    }

    // Bulk synchronization endpoint
    if (pathname.endsWith('/sync/bulk')) {
      const validatedData = BulkSyncRequestSchema.parse(body);
      
      const results = await Promise.allSettled(
        validatedData.userIds.map(async (userId) => {
          // For bulk sync, we need to fetch user tier first
          // This would normally come from a database
          const tier = await getUserTier(userId);
          return threeWayIntegration.syncUser(userId, tier);
        })
      );

      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;

      return NextResponse.json({
        success: true,
        summary: {
          total: validatedData.userIds.length,
          successful,
          failed,
        },
        results: results.map((result, index) => ({
          userId: validatedData.userIds[index],
          status: result.status,
          error: result.status === 'rejected' ? result.reason?.message : undefined,
        })),
      });
    }

    return NextResponse.json(
      { error: 'Invalid endpoint' },
      { status: 404 }
    );

  } catch (error) {
    console.error('Sync API error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation error',
          details: error.errors,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// Health check endpoint
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const includeMetrics = searchParams.get('metrics') === 'true';

    const healthChecks = await threeWayIntegration.performHealthCheck();
    const healthArray = Array.from(healthChecks.entries()).map(([key, value]) => ({
      service: key,
      ...value,
    }));

    const response: any = {
      status: 'operational',
      timestamp: new Date().toISOString(),
      services: healthArray,
    };

    if (includeMetrics) {
      const metrics = await threeWayIntegration.getIntegrationMetrics();
      response.metrics = metrics;
    }

    // Determine overall status
    const hasDown = healthArray.some(h => h.status === 'down');
    const hasDegraded = healthArray.some(h => h.status === 'degraded');
    
    if (hasDown) {
      response.status = 'partial_outage';
    } else if (hasDegraded) {
      response.status = 'degraded_performance';
    }

    return NextResponse.json(response);

  } catch (error) {
    console.error('Health check error:', error);
    
    return NextResponse.json(
      {
        status: 'error',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 503 }
    );
  }
}

// Webhook endpoint for external service notifications
export async function PUT(request: NextRequest) {
  try {
    const signature = request.headers.get('x-webhook-signature');
    const source = request.headers.get('x-webhook-source');

    // Verify webhook signature
    if (!verifyWebhookSignature(signature, await request.text())) {
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 401 }
      );
    }

    const body = await request.json();

    // Process webhook based on source
    switch (source) {
      case 'trading_platform':
        await handleTradingPlatformWebhook(body);
        break;
        
      case 'support_portal':
        await handleSupportPortalWebhook(body);
        break;
        
      case 'payment_processor':
        await handlePaymentWebhook(body);
        break;
        
      default:
        return NextResponse.json(
          { error: 'Unknown webhook source' },
          { status: 400 }
        );
    }

    return NextResponse.json({
      success: true,
      message: 'Webhook processed successfully',
    });

  } catch (error) {
    console.error('Webhook processing error:', error);
    
    return NextResponse.json(
      {
        error: 'Webhook processing failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// Helper functions

async function getUserTier(userId: string): Promise<'onyx' | 'obsidian' | 'void'> {
  // In production, this would fetch from database
  // For now, return a mock tier based on user ID
  const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const tierIndex = hash % 3;
  
  return ['onyx', 'obsidian', 'void'][tierIndex] as 'onyx' | 'obsidian' | 'void';
}

function verifyWebhookSignature(signature: string | null, payload: string): boolean {
  // In production, implement proper HMAC signature verification
  // For now, basic validation
  return signature !== null && signature.length > 0;
}

async function handleTradingPlatformWebhook(data: any) {
  // Convert trading platform events to integration events
  const event = {
    eventId: data.id || `tp_${Date.now()}`,
    timestamp: new Date().toISOString(),
    source: 'trading_platform' as const,
    eventType: mapTradingEventType(data.type),
    payload: data,
    requiresSync: ['black_portal', 'support_portal'] as const,
  };

  await threeWayIntegration.handleServiceEvent(event);
}

async function handleSupportPortalWebhook(data: any) {
  // Convert support portal events to integration events
  const event = {
    eventId: data.id || `sp_${Date.now()}`,
    timestamp: new Date().toISOString(),
    source: 'support_portal' as const,
    eventType: mapSupportEventType(data.type),
    payload: data,
    requiresSync: ['black_portal', 'trading_platform'] as const,
  };

  await threeWayIntegration.handleServiceEvent(event);
}

async function handlePaymentWebhook(data: any) {
  // Handle payment-related webhooks
  const event = {
    eventId: data.id || `pay_${Date.now()}`,
    timestamp: new Date().toISOString(),
    source: 'trading_platform' as const,
    eventType: 'portfolio_update' as const,
    payload: {
      userId: data.userId,
      amount: data.amount,
      currency: data.currency,
      type: 'deposit',
    },
    requiresSync: ['black_portal', 'support_portal'] as const,
  };

  await threeWayIntegration.handleServiceEvent(event);
}

function mapTradingEventType(type: string): any {
  const mapping: Record<string, string> = {
    'order_placed': 'trade_executed',
    'order_filled': 'trade_executed',
    'portfolio_updated': 'portfolio_update',
    'account_upgraded': 'user_upgraded',
  };

  return mapping[type] || 'portfolio_update';
}

function mapSupportEventType(type: string): any {
  const mapping: Record<string, string> = {
    'butler_message': 'butler_interaction',
    'concierge_request': 'service_request',
    'emergency_alert': 'emergency_triggered',
    'compliance_flag': 'compliance_check',
  };

  return mapping[type] || 'butler_interaction';
}

// Export route configuration
export const runtime = 'edge';
export const dynamic = 'force-dynamic';