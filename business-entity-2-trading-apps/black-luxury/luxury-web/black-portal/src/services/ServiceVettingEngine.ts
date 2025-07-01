/**
 * Service Vetting Engine
 * Secure, unbiased, and automated service approval system for Black Portal
 */

import { EventEmitter } from 'events';
import { z } from 'zod';
import {
  ServiceProposal,
  ServiceCategory,
  ApprovalStatus,
  RiskLevel,
  UserRole,
  Permission,
  User,
  AuditLog,
  ROLE_PERMISSIONS,
  CATEGORY_RISK_REQUIREMENTS,
  ServiceProposalSchema,
  UserSchema,
} from '@/types/service-management';

interface VettingRule {
  id: string;
  name: string;
  category?: ServiceCategory;
  riskLevel?: RiskLevel;
  condition: (proposal: ServiceProposal) => boolean;
  weight: number; // 1-100
  errorMessage: string;
  automated: boolean;
}

interface VettingResult {
  passed: boolean;
  score: number; // 0-100
  failedRules: VettingRule[];
  recommendations: string[];
  requiredActions: string[];
  riskAssessment: {
    level: RiskLevel;
    factors: string[];
    mitigations: string[];
  };
}

export class ServiceVettingEngine extends EventEmitter {
  private vettingRules: VettingRule[] = [];
  private auditLogger: (log: Omit<AuditLog, 'id' | 'timestamp'>) => Promise<void>;

  constructor(auditLogger: (log: Omit<AuditLog, 'id' | 'timestamp'>) => Promise<void>) {
    super();
    this.auditLogger = auditLogger;
    this.initializeVettingRules();
  }

  /**
   * Comprehensive service vetting process
   */
  async vetService(
    proposal: ServiceProposal,
    submittedBy: User
  ): Promise<VettingResult> {
    try {
      // Log vetting initiation
      await this.auditLogger({
        userId: submittedBy.id,
        action: 'INITIATE_SERVICE_VETTING',
        resource: 'service_proposal',
        resourceId: proposal.id,
        changes: { proposalId: proposal.id, category: proposal.category },
        ipAddress: '0.0.0.0', // Would be real IP in production
        userAgent: 'ServiceVettingEngine',
        outcome: 'success',
        sensitiveData: false,
      });

      // Validate proposal schema
      const validatedProposal = ServiceProposalSchema.parse(proposal);

      // Run all applicable vetting rules
      const applicableRules = this.getApplicableRules(validatedProposal);
      const failedRules: VettingRule[] = [];
      let totalScore = 100;

      for (const rule of applicableRules) {
        try {
          const passed = rule.condition(validatedProposal);
          if (!passed) {
            failedRules.push(rule);
            totalScore -= rule.weight;
          }
        } catch (error) {
          console.error(`Rule ${rule.id} failed to execute:`, error);
          failedRules.push({
            ...rule,
            errorMessage: `Rule execution failed: ${error}`,
          });
          totalScore -= rule.weight;
        }
      }

      // Calculate final score and risk assessment
      const finalScore = Math.max(0, totalScore);
      const riskAssessment = this.assessRisk(validatedProposal, failedRules);
      const recommendations = this.generateRecommendations(validatedProposal, failedRules);
      const requiredActions = this.getRequiredActions(validatedProposal, failedRules);

      const result: VettingResult = {
        passed: finalScore >= 70 && failedRules.length === 0,
        score: finalScore,
        failedRules,
        recommendations,
        requiredActions,
        riskAssessment,
      };

      // Log vetting completion
      await this.auditLogger({
        userId: submittedBy.id,
        action: 'COMPLETE_SERVICE_VETTING',
        resource: 'service_proposal',
        resourceId: proposal.id,
        changes: { 
          score: finalScore,
          passed: result.passed,
          failedRulesCount: failedRules.length,
          riskLevel: riskAssessment.level,
        },
        ipAddress: '0.0.0.0',
        userAgent: 'ServiceVettingEngine',
        outcome: result.passed ? 'success' : 'warning',
        sensitiveData: false,
      });

      // Emit events for real-time notifications
      this.emit('vetting:completed', {
        proposalId: proposal.id,
        result,
        submittedBy: submittedBy.id,
      });

      if (!result.passed) {
        this.emit('vetting:failed', {
          proposalId: proposal.id,
          failedRules: failedRules.map(r => r.name),
          submittedBy: submittedBy.id,
        });
      }

      return result;

    } catch (error) {
      await this.auditLogger({
        userId: submittedBy.id,
        action: 'VETTING_ERROR',
        resource: 'service_proposal',
        resourceId: proposal.id,
        changes: { error: error instanceof Error ? error.message : 'Unknown error' },
        ipAddress: '0.0.0.0',
        userAgent: 'ServiceVettingEngine',
        outcome: 'failure',
        sensitiveData: false,
      });

      throw error;
    }
  }

  /**
   * Get required approval workflow for a service
   */
  getRequiredApprovalWorkflow(proposal: ServiceProposal): {
    stages: Array<{
      name: string;
      requiredRole: UserRole;
      permissions: Permission[];
      parallelApproval: boolean;
      timeoutHours: number;
    }>;
    minimumApprovers: number;
  } {
    const categoryRequirements = CATEGORY_RISK_REQUIREMENTS[proposal.category];
    const riskMultiplier = this.getRiskMultiplier(proposal.riskLevel);

    const baseStages = [
      {
        name: 'Initial Review',
        requiredRole: UserRole.SENIOR_INVESTMENT_ANALYST,
        permissions: [Permission.REVIEW_SERVICE_PROPOSAL],
        parallelApproval: false,
        timeoutHours: 24,
      },
      {
        name: 'Compliance Review',
        requiredRole: UserRole.CCO,
        permissions: [Permission.REVIEW_COMPLIANCE_DOCS, Permission.APPROVE_REGULATORY_COMPLIANCE],
        parallelApproval: false,
        timeoutHours: 48,
      },
      {
        name: 'Risk Assessment',
        requiredRole: UserRole.CRO,
        permissions: [Permission.MANAGE_RISK_ASSESSMENT, Permission.REVIEW_SERVICE_PROPOSAL],
        parallelApproval: false,
        timeoutHours: 48,
      },
    ];

    // Add category-specific stages
    if (proposal.category === ServiceCategory.PRE_IPO_FUNDS) {
      baseStages.push({
        name: 'Investment Committee Review',
        requiredRole: UserRole.INVESTMENT_HEAD,
        permissions: [Permission.APPROVE_INVESTMENT],
        parallelApproval: false,
        timeoutHours: 72,
      });
    }

    if (proposal.riskLevel === RiskLevel.HIGH || proposal.riskLevel === RiskLevel.CRITICAL) {
      baseStages.push({
        name: 'Executive Approval',
        requiredRole: UserRole.CEO,
        permissions: [Permission.APPROVE_SERVICE_PROPOSAL],
        parallelApproval: false,
        timeoutHours: 24,
      });
    }

    return {
      stages: baseStages,
      minimumApprovers: Math.max(categoryRequirements.minimumApprovers, riskMultiplier),
    };
  }

  /**
   * Validate user permissions for action
   */
  validateUserPermission(user: User, requiredPermission: Permission): boolean {
    const rolePermissions = ROLE_PERMISSIONS[user.role] || [];
    return user.permissions.includes(requiredPermission) || 
           rolePermissions.includes(requiredPermission);
  }

  /**
   * Check if user can approve based on limits
   */
  canUserApprove(user: User, proposal: ServiceProposal): {
    canApprove: boolean;
    reason?: string;
    requiresCoApproval?: boolean;
  } {
    // Check basic permission
    if (!this.validateUserPermission(user, Permission.APPROVE_SERVICE_PROPOSAL)) {
      return {
        canApprove: false,
        reason: 'Insufficient permissions',
      };
    }

    // Check approval limits
    const investmentAmount = proposal.serviceDetails.maximumInvestment || 0;
    if (investmentAmount > user.approvalLimits.investmentAmount) {
      return {
        canApprove: false,
        reason: 'Exceeds individual approval limit',
        requiresCoApproval: true,
      };
    }

    // Check risk level limits
    const riskLevels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL];
    const userMaxRisk = riskLevels.indexOf(user.approvalLimits.riskLevel);
    const proposalRisk = riskLevels.indexOf(proposal.riskLevel);

    if (proposalRisk > userMaxRisk) {
      return {
        canApprove: false,
        reason: 'Proposal risk exceeds user authority',
        requiresCoApproval: true,
      };
    }

    return { canApprove: true };
  }

  /**
   * Generate bias-free scoring report
   */
  generateBiasReport(proposal: ServiceProposal, vettingResult: VettingResult): {
    biasScore: number; // 0-100 (100 = completely unbiased)
    biasFactors: Array<{
      factor: string;
      impact: 'positive' | 'negative' | 'neutral';
      mitigation: string;
    }>;
    recommendations: string[];
  } {
    const biasFactors = [];
    let biasScore = 100;

    // Check for geographic bias
    if (proposal.provider.jurisdiction === 'India') {
      biasFactors.push({
        factor: 'Geographic preference (domestic)',
        impact: 'positive' as const,
        mitigation: 'Ensure international alternatives are equally considered',
      });
      biasScore -= 5;
    }

    // Check for size bias (too small providers might be overlooked)
    if (proposal.provider.financialHealth.netWorth < 100000000) {
      biasFactors.push({
        factor: 'Small provider bias',
        impact: 'negative' as const,
        mitigation: 'Focus on capability and track record over size',
      });
    }

    // Check for relationship bias (existing relationships)
    // This would require additional data about existing relationships

    // Check for cognitive biases in risk assessment
    if (vettingResult.riskAssessment.level !== proposal.riskLevel) {
      biasFactors.push({
        factor: 'Risk assessment inconsistency',
        impact: 'neutral' as const,
        mitigation: 'Review risk assessment methodology',
      });
      biasScore -= 10;
    }

    const recommendations = [
      'Use blind review processes where possible',
      'Rotate reviewers to prevent relationship bias',
      'Implement standardized scoring matrices',
      'Regular bias training for all reviewers',
      'Anonymous proposal submissions in initial stages',
    ];

    return {
      biasScore: Math.max(0, biasScore),
      biasFactors,
      recommendations,
    };
  }

  // Private helper methods

  private initializeVettingRules(): void {
    this.vettingRules = [
      // Financial health rules
      {
        id: 'FIN_001',
        name: 'Minimum Net Worth',
        condition: (proposal) => proposal.provider.financialHealth.netWorth >= 50000000, // ₹50 Cr
        weight: 20,
        errorMessage: 'Provider net worth below minimum threshold',
        automated: true,
      },
      
      {
        id: 'FIN_002',
        name: 'Recent Financial Audit',
        condition: (proposal) => {
          const auditDate = new Date(proposal.provider.financialHealth.lastAuditDate);
          const oneYearAgo = new Date();
          oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
          return auditDate > oneYearAgo;
        },
        weight: 15,
        errorMessage: 'Financial audit older than 12 months',
        automated: true,
      },

      // Compliance rules
      {
        id: 'COMP_001',
        name: 'Valid Business License',
        condition: (proposal) => proposal.provider.businessLicense.length > 0,
        weight: 25,
        errorMessage: 'Missing or invalid business license',
        automated: true,
      },

      {
        id: 'COMP_002',
        name: 'Insurance Coverage',
        condition: (proposal) => {
          const expiryDate = new Date(proposal.provider.insuranceCoverage.expiryDate);
          const today = new Date();
          const threeMonthsFromNow = new Date();
          threeMonthsFromNow.setMonth(threeMonthsFromNow.getMonth() + 3);
          return expiryDate > threeMonthsFromNow;
        },
        weight: 20,
        errorMessage: 'Insurance coverage expires within 3 months',
        automated: true,
      },

      // Security rules
      {
        id: 'SEC_001',
        name: 'ZK Proof Compatibility',
        category: ServiceCategory.PRE_IPO_FUNDS,
        condition: (proposal) => proposal.anonymityFeatures.zkProofCompatible,
        weight: 30,
        errorMessage: 'Service not compatible with ZK proof system',
        automated: true,
      },

      {
        id: 'SEC_002',
        name: 'Anonymous Transaction Support',
        condition: (proposal) => proposal.anonymityFeatures.anonymousTransactions,
        weight: 25,
        errorMessage: 'Service does not support anonymous transactions',
        automated: true,
      },

      // Due diligence rules
      {
        id: 'DD_001',
        name: 'Background Check Completed',
        condition: (proposal) => proposal.dueDiligence.backgroundCheckCompleted,
        weight: 20,
        errorMessage: 'Background check not completed',
        automated: false,
      },

      {
        id: 'DD_002',
        name: 'Legal Review Completed',
        condition: (proposal) => proposal.dueDiligence.legalReviewCompleted,
        weight: 20,
        errorMessage: 'Legal review not completed',
        automated: false,
      },

      // Risk-specific rules
      {
        id: 'RISK_001',
        name: 'High Risk Investment Limits',
        riskLevel: RiskLevel.HIGH,
        condition: (proposal) => {
          const maxInvestment = proposal.serviceDetails.maximumInvestment || 0;
          return maxInvestment <= 10000000000; // ₹1000 Cr max
        },
        weight: 25,
        errorMessage: 'Investment amount exceeds high-risk limits',
        automated: true,
      },

      // Category-specific rules
      {
        id: 'PRE_IPO_001',
        name: 'Pre-IPO Fund Registration',
        category: ServiceCategory.PRE_IPO_FUNDS,
        condition: (proposal) => {
          return proposal.dueDiligence.regulatoryApprovalObtained &&
                 proposal.complianceDocuments.some(doc => 
                   doc.type === 'fund_registration' && doc.verified
                 );
        },
        weight: 30,
        errorMessage: 'Pre-IPO fund lacks proper registration',
        automated: true,
      },

      {
        id: 'AVIATION_001',
        name: 'Aviation License Valid',
        category: ServiceCategory.PRIVATE_AVIATION,
        condition: (proposal) => {
          return proposal.complianceDocuments.some(doc => 
            doc.type === 'aviation_license' && doc.verified
          );
        },
        weight: 35,
        errorMessage: 'Valid aviation license required',
        automated: true,
      },

      {
        id: 'ART_001',
        name: 'Art Dealer Authentication',
        category: ServiceCategory.ART_ACQUISITION,
        condition: (proposal) => {
          return proposal.complianceDocuments.some(doc => 
            (doc.type === 'dealer_license' || doc.type === 'auction_house_registration') && 
            doc.verified
          );
        },
        weight: 30,
        errorMessage: 'Art dealer authentication required',
        automated: true,
      },
    ];
  }

  private getApplicableRules(proposal: ServiceProposal): VettingRule[] {
    return this.vettingRules.filter(rule => {
      // Check category match
      if (rule.category && rule.category !== proposal.category) {
        return false;
      }

      // Check risk level match
      if (rule.riskLevel && rule.riskLevel !== proposal.riskLevel) {
        return false;
      }

      return true;
    });
  }

  private assessRisk(proposal: ServiceProposal, failedRules: VettingRule[]): {
    level: RiskLevel;
    factors: string[];
    mitigations: string[];
  } {
    const factors: string[] = [];
    const mitigations: string[] = [];

    // Base risk from proposal
    let riskScore = this.getRiskScore(proposal.riskLevel);

    // Add risk from failed rules
    const criticalFailures = failedRules.filter(r => r.weight >= 25);
    riskScore += criticalFailures.length * 10;

    // Category-specific risk factors
    if (proposal.category === ServiceCategory.PRE_IPO_FUNDS) {
      factors.push('Pre-IPO investment volatility');
      mitigations.push('Diversified portfolio approach');
    }

    if (proposal.category === ServiceCategory.MEDICAL_EVACUATION) {
      factors.push('Life-critical service dependency');
      mitigations.push('Multiple provider redundancy');
    }

    // Provider financial health impact
    if (proposal.provider.financialHealth.netWorth < 100000000) {
      factors.push('Provider financial capacity');
      mitigations.push('Enhanced monitoring and guarantees');
    }

    // Determine final risk level
    let finalRiskLevel: RiskLevel;
    if (riskScore >= 80) {
      finalRiskLevel = RiskLevel.CRITICAL;
    } else if (riskScore >= 60) {
      finalRiskLevel = RiskLevel.HIGH;
    } else if (riskScore >= 40) {
      finalRiskLevel = RiskLevel.MEDIUM;
    } else {
      finalRiskLevel = RiskLevel.LOW;
    }

    return {
      level: finalRiskLevel,
      factors,
      mitigations,
    };
  }

  private generateRecommendations(proposal: ServiceProposal, failedRules: VettingRule[]): string[] {
    const recommendations: string[] = [];

    // Rule-based recommendations
    failedRules.forEach(rule => {
      switch (rule.id) {
        case 'FIN_001':
          recommendations.push('Require additional financial guarantees or collateral');
          break;
        case 'SEC_001':
          recommendations.push('Work with provider to implement ZK proof compatibility');
          break;
        case 'DD_001':
          recommendations.push('Complete comprehensive background investigation');
          break;
        default:
          recommendations.push(`Address: ${rule.errorMessage}`);
      }
    });

    // General recommendations
    if (proposal.riskLevel === RiskLevel.HIGH) {
      recommendations.push('Implement enhanced monitoring and reporting');
      recommendations.push('Consider pilot program with limited exposure');
    }

    if (proposal.tierAccess === 'void_exclusive') {
      recommendations.push('Ensure highest security and privacy standards');
      recommendations.push('Implement redundant service providers');
    }

    return recommendations;
  }

  private getRequiredActions(proposal: ServiceProposal, failedRules: VettingRule[]): string[] {
    const actions: string[] = [];

    failedRules.forEach(rule => {
      if (!rule.automated) {
        actions.push(`Manual review required: ${rule.name}`);
      } else {
        actions.push(`Resolve: ${rule.errorMessage}`);
      }
    });

    // Category-specific actions
    const categoryReqs = CATEGORY_RISK_REQUIREMENTS[proposal.category];
    categoryReqs.mandatoryChecks.forEach(check => {
      actions.push(`Complete mandatory check: ${check.replace('_', ' ')}`);
    });

    return actions;
  }

  private getRiskScore(riskLevel: RiskLevel): number {
    switch (riskLevel) {
      case RiskLevel.LOW: return 20;
      case RiskLevel.MEDIUM: return 40;
      case RiskLevel.HIGH: return 60;
      case RiskLevel.CRITICAL: return 80;
      default: return 40;
    }
  }

  private getRiskMultiplier(riskLevel: RiskLevel): number {
    switch (riskLevel) {
      case RiskLevel.LOW: return 1;
      case RiskLevel.MEDIUM: return 2;
      case RiskLevel.HIGH: return 3;
      case RiskLevel.CRITICAL: return 4;
      default: return 2;
    }
  }
}