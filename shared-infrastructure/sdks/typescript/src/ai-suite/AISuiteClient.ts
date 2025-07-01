/**
 * AI Suite Client for GridWorks B2B SDK
 * Comprehensive AI services for financial institutions
 */

import { GridWorksSDK } from '../core/GridWorksSDK';
import { APIResponse } from '../core/types';
import {
  SupportRequest,
  SupportResponse,
  IntelligenceRequest,
  IntelligenceResponse,
  ModerationRequest,
  ModerationResponse,
  WhatsAppMessage,
  WhatsAppResponse,
  ExpertVerification,
  ConversationContext
} from './types';

export class AISuiteClient {
  constructor(private sdk: GridWorksSDK) {}

  /**
   * AI Support Engine - Multi-language financial support
   */
  async getSupport(request: SupportRequest): Promise<APIResponse<SupportResponse>> {
    return this.sdk.request('POST', '/api/v1/ai-suite/support', request);
  }

  /**
   * Get support in specific language
   */
  async getSupportInLanguage(
    message: string, 
    language: string, 
    context?: any
  ): Promise<APIResponse<SupportResponse>> {
    return this.getSupport({
      message,
      language,
      context
    });
  }

  /**
   * Get support via WhatsApp Business
   */
  async getWhatsAppSupport(
    message: string,
    phoneNumber: string,
    context?: any
  ): Promise<APIResponse<{ supportResponse: SupportResponse; whatsappResponse: WhatsAppResponse }>> {
    return this.sdk.request('POST', '/api/v1/ai-suite/support/whatsapp', {
      message,
      phoneNumber,
      context
    });
  }

  /**
   * AI Intelligence Engine - Market correlation and analysis
   */
  async getIntelligence(request: IntelligenceRequest): Promise<APIResponse<IntelligenceResponse>> {
    return this.sdk.request('POST', '/api/v1/ai-suite/intelligence', request);
  }

  /**
   * Get Morning Pulse - Pre-market intelligence
   */
  async getMorningPulse(
    markets: string[] = ['NSE', 'BSE', 'NASDAQ'],
    deliveryFormat: 'text' | 'voice' | 'whatsapp' = 'text'
  ): Promise<APIResponse<IntelligenceResponse>> {
    return this.getIntelligence({
      type: 'morning_pulse',
      parameters: {
        markets,
        timeframe: 'daily',
        analysisDepth: 'comprehensive'
      },
      deliveryFormat
    });
  }

  /**
   * Get market correlation analysis
   */
  async getMarketCorrelation(
    sourceMarket: string,
    targetMarkets: string[],
    timeframe: string = '1M'
  ): Promise<APIResponse<IntelligenceResponse>> {
    return this.getIntelligence({
      type: 'market_correlation',
      parameters: {
        markets: [sourceMarket, ...targetMarkets],
        timeframe,
        analysisDepth: 'detailed'
      }
    });
  }

  /**
   * Get sector analysis
   */
  async getSectorAnalysis(
    sectors: string[],
    analysisDepth: 'basic' | 'detailed' | 'comprehensive' = 'detailed'
  ): Promise<APIResponse<IntelligenceResponse>> {
    return this.getIntelligence({
      type: 'sector_analysis',
      parameters: {
        sectors,
        analysisDepth
      }
    });
  }

  /**
   * Schedule intelligence delivery
   */
  async scheduleIntelligence(
    request: IntelligenceRequest,
    scheduledTime: string
  ): Promise<APIResponse<{ scheduleId: string; deliveryTime: string }>> {
    return this.sdk.request('POST', '/api/v1/ai-suite/intelligence/schedule', {
      ...request,
      scheduledDelivery: scheduledTime
    });
  }

  /**
   * AI Moderator Engine - Content moderation and expert verification
   */
  async moderateContent(request: ModerationRequest): Promise<APIResponse<ModerationResponse>> {
    return this.sdk.request('POST', '/api/v1/ai-suite/moderation', request);
  }

  /**
   * Moderate text content
   */
  async moderateText(
    content: string,
    source?: string,
    authorInfo?: any
  ): Promise<APIResponse<ModerationResponse>> {
    return this.moderateContent({
      content,
      contentType: 'text',
      source,
      authorInfo
    });
  }

  /**
   * Bulk moderate messages
   */
  async bulkModerate(
    messages: { content: string; id: string; authorInfo?: any }[]
  ): Promise<APIResponse<{ results: { id: string; moderation: ModerationResponse }[] }>> {
    return this.sdk.request('POST', '/api/v1/ai-suite/moderation/bulk', {
      messages: messages.map(msg => ({
        content: msg.content,
        contentType: 'text',
        authorInfo: msg.authorInfo,
        messageId: msg.id
      }))
    });
  }

  /**
   * Verify expert credentials
   */
  async verifyExpert(expertId: string): Promise<APIResponse<ExpertVerification>> {
    return this.sdk.request('GET', `/api/v1/ai-suite/experts/${expertId}/verify`);
  }

  /**
   * Get expert track record
   */
  async getExpertTrackRecord(
    expertId: string,
    timeframe?: string
  ): Promise<APIResponse<{
    predictions: any[];
    accuracy: number;
    reputationScore: number;
    verificationLevel: string;
  }>> {
    return this.sdk.request('GET', `/api/v1/ai-suite/experts/${expertId}/track-record`, {
      params: { timeframe }
    });
  }

  /**
   * WhatsApp Business Integration
   */
  async sendWhatsAppMessage(message: WhatsAppMessage): Promise<APIResponse<WhatsAppResponse>> {
    return this.sdk.request('POST', '/api/v1/ai-suite/whatsapp/send', message);
  }

  /**
   * Send voice message via WhatsApp
   */
  async sendVoiceMessage(
    to: string,
    audioBuffer: Buffer,
    context?: any
  ): Promise<APIResponse<WhatsAppResponse>> {
    const formData = new FormData();
    formData.append('to', to);
    formData.append('audio', new Blob([audioBuffer]), 'voice.ogg');
    if (context) formData.append('context', JSON.stringify(context));

    return this.sdk.request('POST', '/api/v1/ai-suite/whatsapp/send-voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }

  /**
   * Get WhatsApp conversation history
   */
  async getWhatsAppHistory(
    phoneNumber: string,
    limit: number = 50
  ): Promise<APIResponse<{
    messages: any[];
    totalCount: number;
    conversationId: string;
  }>> {
    return this.sdk.request('GET', `/api/v1/ai-suite/whatsapp/history/${phoneNumber}`, {
      params: { limit }
    });
  }

  /**
   * AI Model Management
   */
  async getAvailableModels(): Promise<APIResponse<{
    models: {
      name: string;
      description: string;
      languages: string[];
      capabilities: string[];
      pricing: any;
    }[];
  }>> {
    return this.sdk.request('GET', '/api/v1/ai-suite/models');
  }

  /**
   * Update AI model configuration
   */
  async updateModelConfig(
    service: 'support' | 'intelligence' | 'moderation',
    config: {
      model?: string;
      temperature?: number;
      maxTokens?: number;
      language?: string;
    }
  ): Promise<APIResponse<{ updated: boolean; config: any }>> {
    return this.sdk.request('PUT', `/api/v1/ai-suite/config/${service}`, config);
  }

  /**
   * Get conversation analysis
   */
  async analyzeConversation(
    conversationId: string
  ): Promise<APIResponse<{
    context: ConversationContext;
    insights: {
      sentiment: string;
      topics: string[];
      keyMoments: any[];
      recommendations: string[];
    };
  }>> {
    return this.sdk.request('GET', `/api/v1/ai-suite/conversations/${conversationId}/analyze`);
  }

  /**
   * Get AI Suite usage analytics
   */
  async getUsageAnalytics(
    timeframe: string = '30d'
  ): Promise<APIResponse<{
    support: { requests: number; languages: any; responseTime: number };
    intelligence: { reports: number; deliveries: any; accuracy: number };
    moderation: { moderations: number; approvalRate: number; violations: any };
    whatsapp: { messages: number; deliveryRate: number; engagement: number };
  }>> {
    return this.sdk.request('GET', '/api/v1/ai-suite/analytics', {
      params: { timeframe }
    });
  }

  /**
   * Test AI Suite connectivity
   */
  async healthCheck(): Promise<APIResponse<{
    support: boolean;
    intelligence: boolean;
    moderation: boolean;
    whatsapp: boolean;
    overall: boolean;
  }>> {
    return this.sdk.request('GET', '/api/v1/ai-suite/health');
  }
}