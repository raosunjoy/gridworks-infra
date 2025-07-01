/**
 * Types for AI Suite Services
 */

export interface SupportRequest {
  message: string;
  language?: string;
  context?: {
    userId?: string;
    sessionId?: string;
    previousMessages?: string[];
    userTier?: string;
    portfolioValue?: number;
  };
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  channel?: 'whatsapp' | 'api' | 'web' | 'mobile';
  attachments?: {
    type: string;
    url: string;
    name: string;
  }[];
}

export interface SupportResponse {
  response: string;
  language: string;
  confidence: number;
  responseTime: number;
  escalated: boolean;
  suggestions?: string[];
  followUpActions?: {
    type: string;
    description: string;
    priority: string;
  }[];
  supportTicketId?: string;
  expertRequired?: boolean;
}

export interface IntelligenceRequest {
  type: 'market_correlation' | 'morning_pulse' | 'sector_analysis' | 'custom';
  parameters?: {
    markets?: string[];
    sectors?: string[];
    timeframe?: string;
    analysisDepth?: 'basic' | 'detailed' | 'comprehensive';
  };
  clientTier?: string;
  deliveryFormat?: 'text' | 'voice' | 'pdf' | 'whatsapp';
  scheduledDelivery?: string; // ISO datetime
}

export interface IntelligenceResponse {
  analysis: {
    summary: string;
    keyPoints: string[];
    marketCorrelations: {
      source: string;
      target: string;
      correlation: number;
      significance: string;
    }[];
    recommendations: {
      action: string;
      reasoning: string;
      confidence: number;
      riskLevel: string;
    }[];
  };
  deliveryFormat: string;
  generatedAt: string;
  validUntil: string;
  sources: string[];
  disclaimer: string;
}

export interface ModerationRequest {
  content: string;
  contentType: 'text' | 'image' | 'voice' | 'document';
  source?: 'whatsapp' | 'telegram' | 'discord' | 'web';
  authorInfo?: {
    userId: string;
    reputation?: number;
    verificationLevel?: string;
  };
  context?: {
    chatId?: string;
    previousMessages?: string[];
    channelType?: string;
  };
}

export interface ModerationResponse {
  approved: boolean;
  confidence: number;
  reasons?: string[];
  violations?: {
    type: string;
    severity: string;
    description: string;
  }[];
  suggestedActions?: {
    action: string;
    reason: string;
  }[];
  requiresHumanReview: boolean;
  expertVerificationNeeded?: boolean;
}

export interface WhatsAppMessage {
  to: string;
  type: 'text' | 'voice' | 'document' | 'image';
  content: string | Buffer;
  context?: {
    replyToMessageId?: string;
    conversationId?: string;
  };
}

export interface WhatsAppResponse {
  messageId: string;
  status: 'sent' | 'delivered' | 'read' | 'failed';
  timestamp: string;
  deliveryReport?: {
    deliveredAt?: string;
    readAt?: string;
    errorCode?: string;
    errorMessage?: string;
  };
}

export interface ExpertVerification {
  expertId: string;
  credentials: {
    sebiRegistration?: string;
    certifications: string[];
    experience: number;
    specializations: string[];
  };
  trackRecord: {
    accuracy: number;
    totalPredictions: number;
    verifiedPredictions: number;
    reputationScore: number;
  };
  verificationLevel: 'basic' | 'verified' | 'premium';
}

export interface AIModelConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  language: string;
  domainSpecialization: string[];
}

export interface ConversationContext {
  conversationId: string;
  participantCount: number;
  messages: {
    timestamp: string;
    author: string;
    content: string;
    sentiment: number;
  }[];
  topics: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
}