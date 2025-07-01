/**
 * Service Management & Vetting System Types
 * Comprehensive RBAC and approval workflow for Black tier services
 */

import { z } from 'zod';

// User roles and permissions
export enum UserRole {
  // Executive level
  CEO = 'ceo',
  CRO = 'cro', // Chief Risk Officer
  CCO = 'cco', // Chief Compliance Officer
  
  // Department heads
  INVESTMENT_HEAD = 'investment_head',
  CONCIERGE_HEAD = 'concierge_head',
  SECURITY_HEAD = 'security_head',
  
  // Senior analysts
  SENIOR_INVESTMENT_ANALYST = 'senior_investment_analyst',
  SENIOR_COMPLIANCE_ANALYST = 'senior_compliance_analyst',
  SENIOR_SECURITY_ANALYST = 'senior_security_analyst',
  
  // Analysts
  INVESTMENT_ANALYST = 'investment_analyst',
  COMPLIANCE_ANALYST = 'compliance_analyst',
  SECURITY_ANALYST = 'security_analyst',
  
  // Operational
  SERVICE_COORDINATOR = 'service_coordinator',
  ADMIN = 'admin',
  READONLY = 'readonly',
}

export enum Permission {
  // Service management
  CREATE_SERVICE_PROPOSAL = 'create_service_proposal',
  REVIEW_SERVICE_PROPOSAL = 'review_service_proposal',
  APPROVE_SERVICE_PROPOSAL = 'approve_service_proposal',
  REJECT_SERVICE_PROPOSAL = 'reject_service_proposal',
  
  // Investment services
  CREATE_INVESTMENT_PROPOSAL = 'create_investment_proposal',
  REVIEW_INVESTMENT_DOCS = 'review_investment_docs',
  APPROVE_INVESTMENT = 'approve_investment',
  MANAGE_INVESTMENT_LIMITS = 'manage_investment_limits',
  
  // Concierge services
  CREATE_CONCIERGE_PROPOSAL = 'create_concierge_proposal',
  REVIEW_CONCIERGE_VENDOR = 'review_concierge_vendor',
  APPROVE_CONCIERGE_SERVICE = 'approve_concierge_service',
  
  // Security & compliance
  CONDUCT_SECURITY_AUDIT = 'conduct_security_audit',
  REVIEW_COMPLIANCE_DOCS = 'review_compliance_docs',
  APPROVE_REGULATORY_COMPLIANCE = 'approve_regulatory_compliance',
  MANAGE_RISK_ASSESSMENT = 'manage_risk_assessment',
  
  // Emergency overrides
  EMERGENCY_APPROVE = 'emergency_approve',
  EMERGENCY_SUSPEND = 'emergency_suspend',
  
  // Admin
  MANAGE_USERS = 'manage_users',
  MANAGE_ROLES = 'manage_roles',
  VIEW_AUDIT_LOGS = 'view_audit_logs',
  EXPORT_REPORTS = 'export_reports',
}

// Service categories
export enum ServiceCategory {
  // Investment services
  PRE_IPO_FUNDS = 'pre_ipo_funds',
  REAL_ESTATE_FUNDS = 'real_estate_funds',
  ESG_INVESTMENTS = 'esg_investments',
  STABLECOIN_PORTFOLIOS = 'stablecoin_portfolios',
  PRIVATE_EQUITY = 'private_equity',
  HEDGE_FUNDS = 'hedge_funds',
  
  // Concierge services
  PRIVATE_AVIATION = 'private_aviation',
  LUXURY_ACCOMMODATION = 'luxury_accommodation',
  EXCLUSIVE_DINING = 'exclusive_dining',
  ART_ACQUISITION = 'art_acquisition',
  GOLDEN_VISA_SERVICES = 'golden_visa_services',
  YACHT_CHARTER = 'yacht_charter',
  
  // Emergency services
  MEDICAL_EVACUATION = 'medical_evacuation',
  SECURITY_SERVICES = 'security_services',
  LEGAL_SERVICES = 'legal_services',
  CRISIS_MANAGEMENT = 'crisis_management',
  
  // Lifestyle services
  WELLNESS_RETREATS = 'wellness_retreats',
  EDUCATION_SERVICES = 'education_services',
  FAMILY_OFFICE_SERVICES = 'family_office_services',
}

// Tier access levels
export enum TierAccess {
  ONYX_ONLY = 'onyx_only',
  OBSIDIAN_PLUS = 'obsidian_plus', // Obsidian and Void
  VOID_EXCLUSIVE = 'void_exclusive',
  ALL_TIERS = 'all_tiers',
}

// Risk levels
export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// Approval status
export enum ApprovalStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  SECURITY_REVIEW = 'security_review',
  COMPLIANCE_REVIEW = 'compliance_review',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  CONDITIONALLY_APPROVED = 'conditionally_approved',
  REJECTED = 'rejected',
  SUSPENDED = 'suspended',
  EXPIRED = 'expired',
}

// Service provider information
export const ServiceProviderSchema = z.object({
  id: z.string(),
  name: z.string(),
  legalName: z.string(),
  registrationNumber: z.string(),
  jurisdiction: z.string(),
  website: z.string().url(),
  primaryContact: z.object({
    name: z.string(),
    email: z.string().email(),
    phone: z.string(),
    title: z.string(),
  }),
  businessLicense: z.string(),
  insuranceCoverage: z.object({
    provider: z.string(),
    policyNumber: z.string(),
    coverage: z.number(),
    expiryDate: z.string().datetime(),
  }),
  financialHealth: z.object({
    creditRating: z.string(),
    auditedFinancials: z.boolean(),
    lastAuditDate: z.string().datetime(),
    netWorth: z.number(),
  }),
});

// Service proposal schema
export const ServiceProposalSchema = z.object({
  id: z.string(),
  proposalNumber: z.string(),
  title: z.string(),
  description: z.string(),
  category: z.nativeEnum(ServiceCategory),
  tierAccess: z.nativeEnum(TierAccess),
  riskLevel: z.nativeEnum(RiskLevel),
  
  provider: ServiceProviderSchema,
  
  serviceDetails: z.object({
    minimumInvestment: z.number().optional(),
    maximumInvestment: z.number().optional(),
    expectedReturns: z.string().optional(),
    investmentPeriod: z.string().optional(),
    liquidityTerms: z.string().optional(),
    fees: z.object({
      managementFee: z.number(),
      performanceFee: z.number(),
      entryFee: z.number(),
      exitFee: z.number(),
    }),
  }),
  
  complianceDocuments: z.array(z.object({
    type: z.string(),
    name: z.string(),
    url: z.string(),
    uploadDate: z.string().datetime(),
    verified: z.boolean(),
  })),
  
  riskAssessment: z.object({
    overallRisk: z.nativeEnum(RiskLevel),
    marketRisk: z.nativeEnum(RiskLevel),
    liquidityRisk: z.nativeEnum(RiskLevel),
    operationalRisk: z.nativeEnum(RiskLevel),
    regulatoryRisk: z.nativeEnum(RiskLevel),
    riskMitigationMeasures: z.array(z.string()),
  }),
  
  dueDiligence: z.object({
    backgroundCheckCompleted: z.boolean(),
    financialAuditCompleted: z.boolean(),
    legalReviewCompleted: z.boolean(),
    regulatoryApprovalObtained: z.boolean(),
    referencesVerified: z.boolean(),
  }),
  
  anonymityFeatures: z.object({
    zkProofCompatible: z.boolean(),
    anonymousTransactions: z.boolean(),
    identityShielding: z.boolean(),
    communicationProtocol: z.string(),
  }),
  
  // Approval workflow
  status: z.nativeEnum(ApprovalStatus),
  submittedBy: z.string(),
  submittedAt: z.string().datetime(),
  
  reviewStages: z.array(z.object({
    stage: z.string(),
    reviewer: z.string(),
    reviewedAt: z.string().datetime(),
    status: z.enum(['pending', 'approved', 'rejected', 'requires_changes']),
    comments: z.string(),
    attachments: z.array(z.string()),
  })),
  
  approvals: z.array(z.object({
    approver: z.string(),
    role: z.nativeEnum(UserRole),
    approvedAt: z.string().datetime(),
    signature: z.string(),
    conditions: z.array(z.string()).optional(),
  })),
  
  // Operational details
  onboardingTimeline: z.string(),
  integrationRequirements: z.array(z.string()),
  supportRequirements: z.string(),
  
  // Metrics and monitoring
  expectedVolume: z.object({
    monthly: z.number(),
    annual: z.number(),
  }),
  
  successMetrics: z.array(z.object({
    metric: z.string(),
    target: z.number(),
    measurement: z.string(),
  })),
});

// User with role-based permissions
export const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string(),
  role: z.nativeEnum(UserRole),
  permissions: z.array(z.nativeEnum(Permission)),
  department: z.string(),
  
  mfaEnabled: z.boolean(),
  lastLogin: z.string().datetime(),
  isActive: z.boolean(),
  
  approvalLimits: z.object({
    investmentAmount: z.number(),
    riskLevel: z.nativeEnum(RiskLevel),
    requiresCoApproval: z.boolean(),
  }),
});

// Audit log entry
export const AuditLogSchema = z.object({
  id: z.string(),
  timestamp: z.string().datetime(),
  userId: z.string(),
  action: z.string(),
  resource: z.string(),
  resourceId: z.string(),
  changes: z.record(z.unknown()),
  ipAddress: z.string(),
  userAgent: z.string(),
  outcome: z.enum(['success', 'failure', 'warning']),
  sensitiveData: z.boolean(),
});

// Approval workflow configuration
export const ApprovalWorkflowSchema = z.object({
  id: z.string(),
  name: z.string(),
  category: z.nativeEnum(ServiceCategory),
  riskLevel: z.nativeEnum(RiskLevel),
  
  stages: z.array(z.object({
    name: z.string(),
    order: z.number(),
    requiredRole: z.nativeEnum(UserRole),
    requiredPermission: z.nativeEnum(Permission),
    parallelApproval: z.boolean(),
    mandatoryComments: z.boolean(),
    timeoutHours: z.number(),
    escalationRole: z.nativeEnum(UserRole).optional(),
  })),
  
  conditions: z.array(z.object({
    field: z.string(),
    operator: z.enum(['equals', 'greater_than', 'less_than', 'contains']),
    value: z.unknown(),
    requiredApproval: z.nativeEnum(UserRole),
  })),
});

// Notification preferences
export const NotificationSchema = z.object({
  id: z.string(),
  userId: z.string(),
  channels: z.array(z.enum(['email', 'sms', 'push', 'slack'])),
  
  triggers: z.object({
    newProposal: z.boolean(),
    reviewRequired: z.boolean(),
    approvalRequired: z.boolean(),
    proposalApproved: z.boolean(),
    proposalRejected: z.boolean(),
    emergencyActions: z.boolean(),
    systemAlerts: z.boolean(),
  }),
  
  escalationRules: z.array(z.object({
    condition: z.string(),
    delayHours: z.number(),
    escalateTo: z.nativeEnum(UserRole),
  })),
});

// Dashboard metrics
export const DashboardMetricsSchema = z.object({
  proposalsInReview: z.number(),
  pendingApprovals: z.number(),
  approvedThisMonth: z.number(),
  rejectedThisMonth: z.number(),
  
  byCategory: z.record(z.object({
    pending: z.number(),
    approved: z.number(),
    rejected: z.number(),
  })),
  
  byRiskLevel: z.record(z.object({
    count: z.number(),
    avgApprovalTime: z.number(),
  })),
  
  performanceMetrics: z.object({
    avgApprovalTime: z.number(),
    bottleneckStage: z.string(),
    complianceRate: z.number(),
    escalationRate: z.number(),
  }),
});

// Type exports
export type ServiceProvider = z.infer<typeof ServiceProviderSchema>;
export type ServiceProposal = z.infer<typeof ServiceProposalSchema>;
export type User = z.infer<typeof UserSchema>;
export type AuditLog = z.infer<typeof AuditLogSchema>;
export type ApprovalWorkflow = z.infer<typeof ApprovalWorkflowSchema>;
export type Notification = z.infer<typeof NotificationSchema>;
export type DashboardMetrics = z.infer<typeof DashboardMetricsSchema>;

// Role-based permission mapping
export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  [UserRole.CEO]: [
    Permission.APPROVE_SERVICE_PROPOSAL,
    Permission.EMERGENCY_APPROVE,
    Permission.EMERGENCY_SUSPEND,
    Permission.MANAGE_USERS,
    Permission.VIEW_AUDIT_LOGS,
    Permission.EXPORT_REPORTS,
  ],
  
  [UserRole.CRO]: [
    Permission.REVIEW_SERVICE_PROPOSAL,
    Permission.APPROVE_SERVICE_PROPOSAL,
    Permission.MANAGE_RISK_ASSESSMENT,
    Permission.CONDUCT_SECURITY_AUDIT,
    Permission.EMERGENCY_SUSPEND,
    Permission.VIEW_AUDIT_LOGS,
  ],
  
  [UserRole.CCO]: [
    Permission.REVIEW_SERVICE_PROPOSAL,
    Permission.APPROVE_REGULATORY_COMPLIANCE,
    Permission.REVIEW_COMPLIANCE_DOCS,
    Permission.REJECT_SERVICE_PROPOSAL,
    Permission.VIEW_AUDIT_LOGS,
  ],
  
  [UserRole.INVESTMENT_HEAD]: [
    Permission.CREATE_INVESTMENT_PROPOSAL,
    Permission.REVIEW_INVESTMENT_DOCS,
    Permission.APPROVE_INVESTMENT,
    Permission.MANAGE_INVESTMENT_LIMITS,
    Permission.REVIEW_SERVICE_PROPOSAL,
  ],
  
  [UserRole.CONCIERGE_HEAD]: [
    Permission.CREATE_CONCIERGE_PROPOSAL,
    Permission.REVIEW_CONCIERGE_VENDOR,
    Permission.APPROVE_CONCIERGE_SERVICE,
    Permission.REVIEW_SERVICE_PROPOSAL,
  ],
  
  [UserRole.SECURITY_HEAD]: [
    Permission.CONDUCT_SECURITY_AUDIT,
    Permission.REVIEW_SERVICE_PROPOSAL,
    Permission.APPROVE_SERVICE_PROPOSAL,
    Permission.EMERGENCY_SUSPEND,
  ],
  
  [UserRole.SENIOR_INVESTMENT_ANALYST]: [
    Permission.CREATE_INVESTMENT_PROPOSAL,
    Permission.REVIEW_INVESTMENT_DOCS,
    Permission.REVIEW_SERVICE_PROPOSAL,
  ],
  
  [UserRole.SENIOR_COMPLIANCE_ANALYST]: [
    Permission.REVIEW_COMPLIANCE_DOCS,
    Permission.REVIEW_SERVICE_PROPOSAL,
    Permission.APPROVE_REGULATORY_COMPLIANCE,
  ],
  
  [UserRole.SENIOR_SECURITY_ANALYST]: [
    Permission.CONDUCT_SECURITY_AUDIT,
    Permission.REVIEW_SERVICE_PROPOSAL,
  ],
  
  [UserRole.INVESTMENT_ANALYST]: [
    Permission.CREATE_INVESTMENT_PROPOSAL,
    Permission.REVIEW_INVESTMENT_DOCS,
  ],
  
  [UserRole.COMPLIANCE_ANALYST]: [
    Permission.REVIEW_COMPLIANCE_DOCS,
  ],
  
  [UserRole.SECURITY_ANALYST]: [
    Permission.CONDUCT_SECURITY_AUDIT,
  ],
  
  [UserRole.SERVICE_COORDINATOR]: [
    Permission.CREATE_SERVICE_PROPOSAL,
    Permission.CREATE_CONCIERGE_PROPOSAL,
  ],
  
  [UserRole.ADMIN]: [
    Permission.MANAGE_USERS,
    Permission.MANAGE_ROLES,
    Permission.VIEW_AUDIT_LOGS,
  ],
  
  [UserRole.READONLY]: [],
};

// Service category risk requirements
export const CATEGORY_RISK_REQUIREMENTS: Record<ServiceCategory, {
  minimumApprovers: number;
  requiredRoles: UserRole[];
  mandatoryChecks: string[];
}> = {
  [ServiceCategory.PRE_IPO_FUNDS]: {
    minimumApprovers: 3,
    requiredRoles: [UserRole.CRO, UserRole.CCO, UserRole.INVESTMENT_HEAD],
    mandatoryChecks: ['financial_audit', 'regulatory_approval', 'background_check'],
  },
  
  [ServiceCategory.REAL_ESTATE_FUNDS]: {
    minimumApprovers: 2,
    requiredRoles: [UserRole.CRO, UserRole.INVESTMENT_HEAD],
    mandatoryChecks: ['financial_audit', 'legal_review'],
  },
  
  [ServiceCategory.MEDICAL_EVACUATION]: {
    minimumApprovers: 2,
    requiredRoles: [UserRole.CRO, UserRole.SECURITY_HEAD],
    mandatoryChecks: ['license_verification', 'insurance_coverage'],
  },
  
  // ... other categories
  [ServiceCategory.ESG_INVESTMENTS]: {
    minimumApprovers: 2,
    requiredRoles: [UserRole.CRO, UserRole.INVESTMENT_HEAD],
    mandatoryChecks: ['financial_audit', 'esg_certification'],
  },
  
  [ServiceCategory.STABLECOIN_PORTFOLIOS]: {
    minimumApprovers: 3,
    requiredRoles: [UserRole.CRO, UserRole.CCO, UserRole.SECURITY_HEAD],
    mandatoryChecks: ['regulatory_approval', 'security_audit', 'custody_verification'],
  },
  
  [ServiceCategory.PRIVATE_AVIATION]: {
    minimumApprovers: 2,
    requiredRoles: [UserRole.CRO, UserRole.CONCIERGE_HEAD],
    mandatoryChecks: ['aviation_license', 'insurance_coverage', 'safety_record'],
  },
  
  [ServiceCategory.ART_ACQUISITION]: {
    minimumApprovers: 2,
    requiredRoles: [UserRole.CRO, UserRole.CONCIERGE_HEAD],
    mandatoryChecks: ['dealer_license', 'authenticity_guarantee', 'insurance_coverage'],
  },
  
  [ServiceCategory.GOLDEN_VISA_SERVICES]: {
    minimumApprovers: 3,
    requiredRoles: [UserRole.CRO, UserRole.CCO, UserRole.CONCIERGE_HEAD],
    mandatoryChecks: ['legal_authorization', 'government_approval', 'track_record'],
  },
  
  [ServiceCategory.SECURITY_SERVICES]: {
    minimumApprovers: 2,
    requiredRoles: [UserRole.CRO, UserRole.SECURITY_HEAD],
    mandatoryChecks: ['security_license', 'background_clearance', 'insurance_coverage'],
  },
  
  [ServiceCategory.LEGAL_SERVICES]: {
    minimumApprovers: 2,
    requiredRoles: [UserRole.CCO, UserRole.CRO],
    mandatoryChecks: ['bar_admission', 'malpractice_insurance', 'specialization_verification'],
  },
  
  [ServiceCategory.FAMILY_OFFICE_SERVICES]: {
    minimumApprovers: 3,
    requiredRoles: [UserRole.CRO, UserRole.CCO, UserRole.INVESTMENT_HEAD],
    mandatoryChecks: ['regulatory_registration', 'financial_audit', 'client_references'],
  },
};