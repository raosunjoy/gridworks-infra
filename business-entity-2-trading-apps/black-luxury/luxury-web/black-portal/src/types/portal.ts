// Black Portal Core Types
// Comprehensive type definitions for the ultra-luxury trading portal

export enum BlackPortalStage {
  MYSTERY_LANDING = 'mystery_landing',
  INVITATION_PROMPT = 'invitation_prompt',
  BIOMETRIC_AUTH = 'biometric_auth',
  TIER_ASSIGNMENT = 'tier_assignment',
  WELCOME_CEREMONY = 'welcome_ceremony',
  PORTAL_DASHBOARD = 'portal_dashboard',
  APP_DOWNLOAD = 'app_download',
  BUTLER_CHAT = 'butler_chat',
  EMERGENCY_MODE = 'emergency_mode'
}

export enum BlackTier {
  MYSTERY = 'mystery',
  ONYX = 'onyx',
  OBSIDIAN = 'obsidian',
  VOID = 'void'
}

export enum AccessLevel {
  GUEST = 'guest',
  MEMBER = 'member',
  PREMIUM = 'premium',
  CONCIERGE = 'concierge',
  EXCLUSIVE = 'exclusive',
  INFINITE = 'infinite'
}

export enum InvestmentClass {
  STOCKS = 'stocks',
  OPTIONS = 'options',
  FUTURES = 'futures',
  CRYPTO = 'crypto',
  HEDGE_FUNDS = 'hedge_funds',
  PRIVATE_EQUITY = 'private_equity',
  PRE_IPO = 'pre_ipo',
  STRUCTURED_PRODUCTS = 'structured_products',
  ALTERNATIVE_INVESTMENTS = 'alternative_investments',
  GOVERNMENT_BONDS = 'government_bonds'
}

// Core User Types
export interface BlackUser {
  userId: string;
  tier: BlackTier;
  accessLevel: AccessLevel;
  
  // Identity & Verification
  name: string;
  email: string;
  phone: string;
  
  // Financial Profile
  portfolioValue: number;
  netWorth: number;
  riskAppetite: 'conservative' | 'moderate' | 'aggressive' | 'ultra_aggressive';
  investmentPreferences: InvestmentClass[];
  
  // Portal Access
  invitationCode: string;
  invitedBy: string;
  joiningDate: Date;
  tierProgressionDate: Date;
  
  // Butler & Concierge
  dedicatedButler: string;
  butlerContactPreference: 'text' | 'call' | 'video' | 'in_person';
  conciergeAccess: boolean;
  emergencyServicesActive: boolean;
  
  // Compliance & Security
  kycLevel: 'basic' | 'premium' | 'ultra_premium';
  amlScore: number;
  riskScore: number;
  complianceStatus: 'pending' | 'verified' | 'flagged' | 'suspended';
  
  // Preferences
  tradingHoursPreference: 'market_hours' | 'extended' | '24x7';
  notificationPreferences: NotificationPreferences;
  privacySettings: PrivacySettings;
  luxuryPreferences: LuxuryPreferences;
  
  // Activity Tracking
  isActive: boolean;
  lastActivity: Date;
  sessionCount: number;
  totalTrades: number;
  totalVolume: number;
  satisfactionScore?: number;
}

export interface NotificationPreferences {
  marketAlerts: boolean;
  butlerUpdates: boolean;
  conciergeNotifications: boolean;
  emergencyAlerts: boolean;
  portfolioUpdates: boolean;
  exclusiveOpportunities: boolean;
  tierProgressionAlerts: boolean;
  securityAlerts: boolean;
}

export interface PrivacySettings {
  publicProfile: boolean;
  tradeVisibility: 'public' | 'members' | 'tier' | 'none';
  networthVisible: boolean;
  portfolioVisible: boolean;
  allowDirectMessages: boolean;
  sharePerformanceMetrics: boolean;
}

export interface LuxuryPreferences {
  preferredCommunicationStyle: 'formal' | 'casual' | 'concierge';
  languagePreference: string;
  timeZone: string;
  culturalPreferences: string[];
  lifestyleInterests: string[];
  travelPreferences: string[];
  artCollectionInterests: string[];
  charitableInterests: string[];
}

// Invitation System
export interface BlackInvitation {
  code: string;
  targetTier: BlackTier;
  invitedBy: string;
  inviteeEmail: string;
  portfolioRequirement: number;
  createdAt: Date;
  expiresAt: Date;
  used: boolean;
  usedBy?: string;
  usedAt?: Date;
  personalMessage?: string;
  specialPrivileges?: string[];
}

// Device & Security
export interface DeviceFingerprint {
  deviceId: string;
  fingerprint: string;
  platform: string;
  browser: string;
  screenResolution: string;
  timezone: string;
  language: string;
  canvasFingerprint: string;
  webglFingerprint: any;
  audioFingerprint: string;
  touchSupport: boolean;
  cookiesEnabled: boolean;
  doNotTrack: boolean;
  createdAt: Date;
  lastSeen: Date;
  isSecure: boolean;
  isTrusted: boolean;
  riskScore: number;
}

export interface BiometricData {
  type: 'face' | 'fingerprint' | 'voice' | 'iris' | 'palm';
  data: string;
  confidence: number;
  timestamp: Date;
  deviceId: string;
  verified: boolean;
}

// Portal Session
export interface BlackSession {
  sessionId: string;
  userId: string;
  deviceId: string;
  startTime: Date;
  lastActivity: Date;
  sessionDuration: number;
  
  // Authentication Details
  authenticationMethod: string;
  deviceFingerprint: string;
  biometricVerified: boolean;
  location?: GeolocationCoordinates;
  riskScore: number;
  
  // Activity Tracking
  screensVisited: string[];
  actionsPerformed: SessionAction[];
  tradesExecuted: number;
  volumeTraded: number;
  butlerConversations: ButlerConversation[];
  supportInteractions: number;
  conciergeRequests: number;
  
  // Performance Metrics
  responseTimes: number[];
  errorCount: number;
  satisfactionScore?: number;
  
  // Security
  securityEvents: SecurityEvent[];
  anomaliesDetected: string[];
  isSecure: boolean;
}

export interface SessionAction {
  action: string;
  timestamp: Date;
  details: any;
  duration: number;
  successful: boolean;
  errorMessage?: string;
}

export interface SecurityEvent {
  type: 'login' | 'logout' | 'suspicious_activity' | 'device_change' | 'location_change';
  timestamp: Date;
  details: any;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  resolved: boolean;
}

// Butler & AI
export interface ButlerProfile {
  butlerId: string;
  name: string;
  specialization: string[];
  experience: string;
  credentials: string[];
  languages: string[];
  availability: 'business_hours' | 'extended' | '24x7';
  currentLoad: number;
  maxCapacity: number;
  satisfactionRating: number;
  responseTimeAvg: number;
}

export interface ButlerConversation {
  conversationId: string;
  butlerId: string;
  userId: string;
  startTime: Date;
  endTime?: Date;
  messages: ButlerMessage[];
  type: 'text' | 'voice' | 'video';
  topic: string;
  resolution: 'resolved' | 'escalated' | 'ongoing';
  satisfactionRating?: number;
}

export interface ButlerMessage {
  messageId: string;
  sender: 'butler' | 'user';
  content: string;
  timestamp: Date;
  type: 'text' | 'voice' | 'image' | 'document' | 'action';
  metadata?: any;
  isRead: boolean;
  isProcessed: boolean;
}

// Trading & Portfolio
export interface PortfolioSummary {
  totalValue: number;
  dayChange: {
    amount: number;
    percentage: number;
  };
  ytdPerformance: {
    amount: number;
    percentage: number;
  };
  riskMetrics: {
    beta: number;
    sharpeRatio: number;
    maxDrawdown: number;
    var95: number;
    volatility: number;
  };
  assetAllocation: {
    [key: string]: number;
  };
  exclusiveHoldings: ExclusiveHolding[];
  performance: PerformancePeriod[];
}

export interface ExclusiveHolding {
  name: string;
  type: InvestmentClass;
  value: number;
  allocation: number;
  entryDate: Date;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  isExclusive: boolean;
  exclusivityLevel: BlackTier;
}

export interface PerformancePeriod {
  period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  return: number;
  benchmark: number;
  alpha: number;
  beta: number;
  sharpeRatio: number;
  maxDrawdown: number;
}

// Exclusive Opportunities
export interface ExclusiveOpportunity {
  opportunityId: string;
  title: string;
  description: string;
  investmentClass: InvestmentClass;
  minimumInvestment: number;
  maximumInvestment: number;
  expectedReturn: number;
  riskLevel: 'low' | 'medium' | 'high' | 'ultra_high';
  investmentHorizon: string;
  totalSlots: number;
  availableSlots: number;
  tierRequirements: BlackTier[];
  accessLevelRequired: AccessLevel;
  
  // Timeline
  launchDate: Date;
  closingDate: Date;
  investmentStart: Date;
  expectedExit: Date;
  
  // Documentation
  pitchDeckUrl: string;
  dueDiligenceReport: string;
  legalDocuments: string[];
  trackRecord: any;
  similarInvestments: string[];
  successProbability: number;
  
  // Exclusivity
  isInviteOnly: boolean;
  requiresManualApproval: boolean;
  hasWaitingList: boolean;
  exclusivityReason: string;
}

// Market Intelligence
export interface MarketInsight {
  insightId: string;
  type: 'market_analysis' | 'sector_rotation' | 'macro_economics' | 'geopolitical' | 'technical_analysis';
  title: string;
  content: string;
  confidence: number;
  timeframe: 'immediate' | 'short_term' | 'medium_term' | 'long_term';
  timeSensitive: boolean;
  tier: BlackTier;
  source: 'ai_analysis' | 'human_analyst' | 'institutional_flow' | 'government_source';
  actionable: boolean;
  recommendedActions: string[];
  riskAssessment: string;
  expectedImpact: 'low' | 'medium' | 'high' | 'market_moving';
  createdAt: Date;
  expiresAt?: Date;
}

// Concierge Services
export interface ConciergeRequest {
  requestId: string;
  userId: string;
  type: 'travel' | 'dining' | 'events' | 'lifestyle' | 'emergency' | 'business' | 'personal';
  priority: 'low' | 'normal' | 'high' | 'urgent' | 'emergency';
  title: string;
  description: string;
  requirements: any;
  timeline: string;
  budget?: number;
  status: 'requested' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  assignedTo: string;
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  userSatisfaction?: number;
  notes: string[];
}

// Emergency Services
export interface EmergencyService {
  serviceId: string;
  type: 'medical' | 'security' | 'travel' | 'legal' | 'financial' | 'personal';
  name: string;
  description: string;
  responseTime: string;
  coverage: string[];
  contactMethod: string;
  isActive: boolean;
  tier: BlackTier;
  cost: number;
  provider: string;
  certifications: string[];
}

// App Distribution
export interface AppDownload {
  downloadId: string;
  userId: string;
  deviceId: string;
  appVersion: string;
  tier: BlackTier;
  downloadUrl: string;
  expiresAt: Date;
  isDownloaded: boolean;
  downloadedAt?: Date;
  installationCompleted: boolean;
  installedAt?: Date;
  configuration: AppConfiguration;
}

export interface AppConfiguration {
  theme: 'void' | 'obsidian' | 'onyx';
  features: string[];
  apiEndpoints: string[];
  encryptionLevel: 'standard' | 'premium' | 'military';
  offlineCapability: boolean;
  butlerIntegration: boolean;
  emergencyAccess: boolean;
  customizations: any;
}

// Luxury Effects & Interactions
export interface LuxuryEffect {
  type: 'portal-entry' | 'invitation-processing' | 'biometric-scan' | 'tier-reveal' | 'gold-shower' | 'reality-glitch';
  duration: number;
  intensity: number;
  soundEffect?: string;
  visualEffect?: string;
  hapticPattern?: number[];
}

export interface MousePosition {
  x: number;
  y: number;
}

// API Response Types
export interface BlackPortalResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: Date;
  requestId: string;
  tier?: BlackTier;
  securityLevel: 'public' | 'member' | 'secure' | 'ultra_secure';
}

// Event Types
export interface PortalEvent {
  eventType: string;
  timestamp: Date;
  userId?: string;
  sessionId?: string;
  deviceId?: string;
  details: any;
  riskLevel: 'low' | 'medium' | 'high';
}

// Analytics & Metrics
export interface PortalAnalytics {
  userId: string;
  sessionMetrics: {
    totalSessions: number;
    avgSessionDuration: number;
    screenTime: { [screen: string]: number };
    interactionCount: number;
    errorRate: number;
  };
  engagementMetrics: {
    featuresUsed: string[];
    butlerInteractions: number;
    tradesInitiated: number;
    supportRequests: number;
  };
  satisfactionMetrics: {
    overallSatisfaction: number;
    featureSatisfaction: { [feature: string]: number };
    npsScore: number;
  };
  businessMetrics: {
    revenueGenerated: number;
    conversionEvents: string[];
    referralsGenerated: number;
    ltv: number;
  };
}

// Export all types for easy importing
export type {
  BlackUser,
  BlackInvitation,
  DeviceFingerprint,
  BiometricData,
  BlackSession,
  ButlerProfile,
  PortfolioSummary,
  ExclusiveOpportunity,
  MarketInsight,
  ConciergeRequest,
  EmergencyService,
  AppDownload,
  LuxuryEffect,
  PortalAnalytics
};