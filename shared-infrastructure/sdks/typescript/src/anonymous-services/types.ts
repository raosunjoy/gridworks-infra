/**
 * Types for Anonymous Services - World's First Implementation
 */

export interface ZKProofRequest {
  statement: string;
  witness: any;
  publicInputs: any[];
  proofType: 'portfolio_verification' | 'identity_verification' | 'transaction_verification';
  privacyTier: 'onyx' | 'obsidian' | 'void';
}

export interface ZKProofResponse {
  proof: string;
  verificationKey: string;
  publicSignals: any[];
  isValid: boolean;
  generatedAt: string;
  expiresAt: string;
  proofHash: string;
}

export interface AnonymousPortfolioRequest {
  portfolioData: {
    totalValue: number;
    assetClasses: {
      type: string;
      allocation: number;
      performance?: number;
    }[];
    riskProfile: 'conservative' | 'moderate' | 'aggressive';
    timeHorizon: string;
  };
  privacyLevel: 'onyx' | 'obsidian' | 'void';
  verificationRequirements?: {
    minimumValue?: number;
    assetClassConstraints?: string[];
    performanceThresholds?: any;
  };
}

export interface AnonymousPortfolioResponse {
  verificationResult: {
    verified: boolean;
    meetsRequirements: boolean;
    confidenceScore: number;
    tier: string;
  };
  zkProof: ZKProofResponse;
  anonymousId: string;
  validationTimestamp: string;
  accessCredentials: {
    temporaryToken: string;
    expiresAt: string;
    scope: string[];
  };
}

export interface ButlerRequest {
  personality: 'sterling' | 'prism' | 'nexus';
  request: string;
  context?: {
    portfolioTier?: string;
    previousInteractions?: any[];
    preferences?: any;
    anonymousId?: string;
  };
  communicationStyle?: 'formal' | 'casual' | 'technical';
  responseFormat?: 'text' | 'structured' | 'recommendations';
}

export interface ButlerResponse {
  response: string;
  personality: string;
  confidence: number;
  recommendations?: {
    action: string;
    reasoning: string;
    priority: string;
    anonymityImpact: string;
  }[];
  followUpQuestions?: string[];
  escalationSuggested?: boolean;
  anonymityMaintained: boolean;
}

export interface EmergencyIdentityReveal {
  anonymousId: string;
  emergencyType: 'legal_requirement' | 'regulatory_inquiry' | 'security_breach' | 'client_request';
  requestedBy: {
    authority: string;
    jurisdiction: string;
    legalBasis: string;
    contactInfo: any;
  };
  approvalRequired: {
    internalApproval: boolean;
    clientConsent: boolean;
    legalReview: boolean;
  };
  timeline: {
    requestedAt: string;
    responseDeadline: string;
    reviewPeriod: string;
  };
}

export interface ProgressiveIdentityReveal {
  revealLevel: 'basic' | 'standard' | 'comprehensive' | 'full';
  revealedFields: string[];
  remainingAnonymity: string[];
  revealJustification: string;
  auditTrail: {
    timestamp: string;
    action: string;
    authorizedBy: string;
    reason: string;
  }[];
}

export interface AnonymousCommunication {
  channelId: string;
  participantLimit: number;
  admissionCriteria: {
    minimumPortfolioValue?: number;
    requiredTier?: string;
    inviteOnly?: boolean;
    verificationLevel?: string;
  };
  communicationRules: {
    noDirectIdentification: boolean;
    portfolioHintsAllowed: boolean;
    dealSharingEnabled: boolean;
    moderationLevel: string;
  };
}

export interface DealFlowSharing {
  dealId: string;
  dealType: 'private_equity' | 'venture_capital' | 'real_estate' | 'hedge_fund' | 'structured_product';
  minimumInvestment: number;
  targetReturns: {
    expected: number;
    minimum: number;
    timeframe: string;
  };
  riskAssessment: {
    level: string;
    factors: string[];
    mitigation: string[];
  };
  anonymityRequirements: {
    dealSourceAnonymous: boolean;
    investorAnonymous: boolean;
    intermediaryRequired: boolean;
  };
}

export interface ReputationScore {
  anonymousId: string;
  score: number;
  tier: string;
  components: {
    dealAccuracy: number;
    contributionQuality: number;
    networkValue: number;
    complianceRecord: number;
  };
  achievements: string[];
  penalties: any[];
  lastUpdated: string;
}

export interface CryptographicConfig {
  encryptionAlgorithm: string;
  keyLength: number;
  hashFunction: string;
  zkProofSystem: string;
  quantumResistant: boolean;
  securityLevel: number;
}