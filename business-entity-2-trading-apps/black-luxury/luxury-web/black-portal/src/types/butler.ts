export interface ButlerPersonality {
  name: string;
  tier: 'onyx' | 'obsidian' | 'void';
  personality: 'professional' | 'friendly' | 'mystical' | 'quantum';
  expertise: string[];
  voiceProfile: {
    tone: 'warm' | 'authoritative' | 'ethereal' | 'cosmic';
    speed: 'slow' | 'normal' | 'fast';
    formality: 'casual' | 'formal' | 'ultra-formal';
  };
  capabilities: ButlerCapability[];
}

export interface ButlerCapability {
  id: string;
  name: string;
  description: string;
  tier: 'onyx' | 'obsidian' | 'void';
  category: 'trading' | 'analysis' | 'concierge' | 'security' | 'luxury';
  enabled: boolean;
}

export interface ButlerMessage {
  id: string;
  content: string;
  type: 'text' | 'voice' | 'action' | 'alert' | 'recommendation';
  priority: 'low' | 'medium' | 'high' | 'urgent' | 'critical';
  timestamp: Date;
  metadata?: {
    attachments?: string[];
    actions?: ButlerAction[];
    sentiment?: 'positive' | 'neutral' | 'negative' | 'urgent';
    confidenceLevel?: number;
  };
}

export interface ButlerAction {
  id: string;
  type: 'execute_trade' | 'schedule_meeting' | 'send_alert' | 'make_payment' | 'book_service';
  description: string;
  params: Record<string, any>;
  requiresConfirmation: boolean;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

export interface ButlerContext {
  userId: string;
  sessionId: string;
  currentTask?: string;
  conversationHistory: ButlerMessage[];
  userPreferences: {
    communicationStyle: 'brief' | 'detailed' | 'technical';
    alertFrequency: 'minimal' | 'normal' | 'verbose';
    autoExecuteLimit: number; // Max amount for auto-execution
    preferredLanguage: string;
    timeZone: string;
  };
  portfolioContext: {
    totalValue: number;
    riskProfile: 'conservative' | 'moderate' | 'aggressive' | 'quantum';
    activePositions: number;
    todaysPnL: number;
  };
}

export interface ButlerResponse {
  message: ButlerMessage;
  suggestedActions?: ButlerAction[];
  nextSteps?: string[];
  confidence: number;
  processingTime: number;
}

export interface ButlerAnalytics {
  totalInteractions: number;
  successfulExecutions: number;
  averageResponseTime: number;
  userSatisfactionScore: number;
  mostUsedCapabilities: string[];
  emergencyInterventions: number;
}

export interface LuxuryService {
  id: string;
  name: string;
  category: 'transport' | 'hospitality' | 'dining' | 'entertainment' | 'health' | 'security';
  tier: 'onyx' | 'obsidian' | 'void';
  provider: string;
  description: string;
  priceRange: string;
  availability: '24/7' | 'business_hours' | 'by_appointment';
  bookingMethod: 'instant' | 'confirmation_required' | 'concierge_arranged';
  location?: string;
}

export interface EmergencyContact {
  id: string;
  name: string;
  type: 'medical' | 'security' | 'legal' | 'concierge' | 'family';
  phoneNumber: string;
  email?: string;
  priority: number;
  available24x7: boolean;
  responseTime: string; // e.g., "< 5 minutes"
}

export interface MarketInsight {
  id: string;
  title: string;
  summary: string;
  content: string;
  type: 'opportunity' | 'risk' | 'news' | 'analysis' | 'prediction';
  relevanceScore: number;
  timeframe: 'immediate' | 'short_term' | 'medium_term' | 'long_term';
  confidenceLevel: number;
  sources: string[];
  actionableItems: string[];
  estimatedImpact: {
    portfolioPercentage: number;
    riskAdjustedReturn: number;
  };
}

export interface ButlerNotification {
  id: string;
  type: 'market_alert' | 'portfolio_update' | 'service_reminder' | 'emergency' | 'luxury_opportunity';
  title: string;
  message: string;
  actionRequired: boolean;
  expiresAt?: Date;
  metadata?: Record<string, any>;
}

// Advanced AI Butler Types
export interface QuantumButlerState {
  currentDimension: 'reality' | 'probability' | 'quantum_superposition';
  parallelAnalyses: number;
  quantumCoherence: number;
  realityDistortionLevel: number;
}

export interface PredictiveModel {
  id: string;
  name: string;
  type: 'neural_network' | 'quantum_algorithm' | 'hybrid_ai' | 'reality_synthesis';
  accuracy: number;
  lastTrainingDate: Date;
  predictions: MarketPrediction[];
}

export interface MarketPrediction {
  symbol: string;
  predictedPrice: number;
  timeframe: string;
  confidence: number;
  riskFactors: string[];
  quantumProbabilities?: number[];
}

export interface ButlerLearning {
  interactionPatterns: Record<string, number>;
  successfulStrategies: string[];
  userFeedbackHistory: Array<{
    action: string;
    feedback: 'positive' | 'negative' | 'neutral';
    timestamp: Date;
  }>;
  adaptationLevel: number;
  personalityEvolution: {
    basePersonality: string;
    learnedTraits: string[];
    emergentBehaviors: string[];
  };
}