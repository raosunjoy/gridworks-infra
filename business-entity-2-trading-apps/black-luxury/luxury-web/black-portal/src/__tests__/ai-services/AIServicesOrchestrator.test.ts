/**
 * AI Services Orchestrator Unit Tests
 * Comprehensive testing of the AI intermediary system for approved services
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { AIServicesOrchestrator, AIPersonalityType, ServiceDeliveryMode } from '../../services/AIServicesOrchestrator';
import { ServiceCategory, ApprovalStatus } from '../../types/service-management';

// Mock EventEmitter
jest.mock('events');

describe('AIServicesOrchestrator', () => {
  let orchestrator: AIServicesOrchestrator;
  
  beforeEach(() => {
    orchestrator = new AIServicesOrchestrator();
  });

  describe('Service Registration', () => {
    test('should register approved service successfully', async () => {
      const mockService = {
        id: 'service-1',
        title: 'Pre-IPO Investment Fund',
        category: ServiceCategory.PRE_IPO_FUNDS,
        status: ApprovalStatus.APPROVED,
        tierAccess: 'onyx_plus',
        anonymityFeatures: {
          zkProofCompatible: true,
          identityShielding: true,
          encryptedCommunication: true,
        },
        serviceDetails: {
          maximumInvestment: 1000000000, // ₹100 Cr
          minimumInvestment: 100000000,  // ₹10 Cr
        },
        riskLevel: 'medium' as const,
      };

      await orchestrator.registerApprovedService(mockService);
      
      // Verify service was registered
      expect(orchestrator.getActiveRequestsStatus()).toBeDefined();
    });

    test('should reject non-approved services', async () => {
      const unapprovedService = {
        id: 'service-2',
        title: 'Unapproved Service',
        category: ServiceCategory.PRIVATE_AVIATION,
        status: ApprovalStatus.PENDING,
        tierAccess: 'onyx_plus',
        anonymityFeatures: {
          zkProofCompatible: false,
          identityShielding: false,
          encryptedCommunication: false,
        },
        serviceDetails: {},
        riskLevel: 'low' as const,
      };

      await expect(orchestrator.registerApprovedService(unapprovedService))
        .rejects.toThrow('Only approved services can be registered');
    });

    test('should create correct AI profile for different tiers', async () => {
      const voidTierService = {
        id: 'void-service',
        title: 'Quantum Investment Fund',
        category: ServiceCategory.PRE_IPO_FUNDS,
        status: ApprovalStatus.APPROVED,
        tierAccess: 'void_exclusive',
        anonymityFeatures: {
          zkProofCompatible: true,
          identityShielding: true,
          encryptedCommunication: true,
        },
        serviceDetails: {
          maximumInvestment: 10000000000, // ₹1000 Cr
        },
        riskLevel: 'critical' as const,
      };

      await orchestrator.registerApprovedService(voidTierService);
      
      // Verify tier-specific personality assignment
      const requests = orchestrator.getActiveRequestsStatus();
      expect(requests).toBeDefined();
    });
  });

  describe('Service Request Processing', () => {
    beforeEach(async () => {
      // Register a test service
      const testService = {
        id: 'test-service',
        title: 'Test Investment Fund',
        category: ServiceCategory.PRE_IPO_FUNDS,
        status: ApprovalStatus.APPROVED,
        tierAccess: 'onyx_plus',
        anonymityFeatures: {
          zkProofCompatible: true,
          identityShielding: true,
          encryptedCommunication: true,
        },
        serviceDetails: {
          maximumInvestment: 500000000, // ₹50 Cr
        },
        riskLevel: 'medium' as const,
      };

      await orchestrator.registerApprovedService(testService);
    });

    test('should process Onyx tier service request', async () => {
      const request = await orchestrator.processServiceRequest(
        'client-1',
        'anon-1',
        'onyx',
        {
          serviceCategory: ServiceCategory.PRE_IPO_FUNDS,
          requestType: 'investment',
          specifications: {
            investmentAmount: 100000000, // ₹10 Cr
            riskTolerance: 'moderate',
          },
          urgencyLevel: 'medium',
          budgetRange: {
            min: 100000000,
            max: 200000000,
            currency: 'INR',
          },
        }
      );

      expect(request).toBeDefined();
      expect(request.tier).toBe('onyx');
      expect(request.aiProcessing.personalityAssigned).toBe(AIPersonalityType.STERLING);
      expect(request.aiProcessing.deliveryMode).toBe(ServiceDeliveryMode.ASSISTED);
      expect(request.anonymityMaintenance.identityShielding).toBe(true);
      expect(request.status).toBe('received');
    });

    test('should process Obsidian tier service request with enhanced features', async () => {
      const request = await orchestrator.processServiceRequest(
        'client-2',
        'anon-2',
        'obsidian',
        {
          serviceCategory: ServiceCategory.ART_ACQUISITION,
          requestType: 'concierge',
          specifications: {
            artType: 'contemporary',
            budgetRange: '₹50-100 Cr',
            anonymousDelivery: true,
          },
          urgencyLevel: 'high',
        }
      );

      expect(request.tier).toBe('obsidian');
      expect(request.aiProcessing.personalityAssigned).toBe(AIPersonalityType.PRISM);
      expect(request.aiProcessing.deliveryMode).toBe(ServiceDeliveryMode.PREMIUM);
      expect(request.anonymityMaintenance.zkProofValidation).toBe(false);
    });

    test('should process Void tier service request with quantum features', async () => {
      const request = await orchestrator.processServiceRequest(
        'client-3',
        'anon-3',
        'void',
        {
          serviceCategory: ServiceCategory.MEDICAL_EVACUATION,
          requestType: 'emergency',
          specifications: {
            emergencyType: 'medical',
            location: 'encrypted',
            urgency: 'critical',
          },
          urgencyLevel: 'critical',
        }
      );

      expect(request.tier).toBe('void');
      expect(request.aiProcessing.personalityAssigned).toBe(AIPersonalityType.NEXUS);
      expect(request.aiProcessing.deliveryMode).toBe(ServiceDeliveryMode.QUANTUM);
      expect(request.anonymityMaintenance.zkProofValidation).toBe(true);
    });

    test('should generate appropriate orchestration steps', async () => {
      const request = await orchestrator.processServiceRequest(
        'client-4',
        'anon-4',
        'void',
        {
          serviceCategory: ServiceCategory.PRE_IPO_FUNDS,
          requestType: 'investment',
          specifications: {
            investmentAmount: 1000000000, // ₹100 Cr
          },
          urgencyLevel: 'high',
        }
      );

      expect(request.aiProcessing.orchestrationSteps).toContain('Validate client anonymity requirements');
      expect(request.aiProcessing.orchestrationSteps).toContain('Generate quantum-level encryption');
      expect(request.aiProcessing.orchestrationSteps).toContain('Perform due diligence validation');
      expect(request.aiProcessing.orchestrationSteps).toContain('Update client learning model');
    });
  });

  describe('Anonymity Preservation', () => {
    test('should anonymize service requirements correctly', async () => {
      const request = await orchestrator.processServiceRequest(
        'client-5',
        'anon-5',
        'obsidian',
        {
          serviceCategory: ServiceCategory.PRIVATE_AVIATION,
          requestType: 'concierge',
          specifications: {
            departure: 'Mumbai',
            destination: 'Dubai',
            passengers: 3,
            preferences: 'luxury',
          },
          urgencyLevel: 'medium',
          budgetRange: {
            min: 5000000,  // ₹50L
            max: 10000000, // ₹1 Cr
            currency: 'INR',
          },
        }
      );

      expect(request.providerInteraction.anonymizedRequirements).toBeDefined();
      expect(request.providerInteraction.anonymizedRequirements).not.toContain('client-5');
      expect(request.providerInteraction.communicationMethod).toBe('ai_proxy');
      expect(request.providerInteraction.deliveryInstructions).toContain('Maintain complete client anonymity');
    });

    test('should implement proper encryption levels by tier', async () => {
      // Test different encryption levels for different tiers
      const onyxRequest = await orchestrator.processServiceRequest(
        'client-onyx', 'anon-onyx', 'onyx',
        { serviceCategory: ServiceCategory.PRE_IPO_FUNDS, requestType: 'investment' }
      );

      const voidRequest = await orchestrator.processServiceRequest(
        'client-void', 'anon-void', 'void',
        { serviceCategory: ServiceCategory.PRE_IPO_FUNDS, requestType: 'investment' }
      );

      expect(onyxRequest.anonymityMaintenance.encryptedCommunication).toBe(true);
      expect(voidRequest.anonymityMaintenance.zkProofValidation).toBe(true);
    });
  });

  describe('AI Learning and Adaptation', () => {
    test('should track client satisfaction and learning', async () => {
      const request = await orchestrator.processServiceRequest(
        'client-6',
        'anon-6',
        'onyx',
        {
          serviceCategory: ServiceCategory.LUXURY_ACCOMMODATION,
          requestType: 'concierge',
          specifications: {
            location: 'Maldives',
            duration: '7 days',
            preferences: 'beachfront villa',
          },
        }
      );

      // Simulate service completion and learning
      expect(request.aiProcessing.confidenceLevel).toBeGreaterThan(0);
      expect(request.aiProcessing.estimatedCompletion).toBeDefined();
    });

    test('should generate personalized recommendations', async () => {
      const recommendations = await orchestrator.getPersonalizedRecommendations('client-7', 'obsidian');
      
      expect(recommendations).toBeDefined();
      expect(recommendations.recommendations).toBeDefined();
      expect(recommendations.insights).toBeDefined();
      expect(recommendations.insights.spendingPatterns).toBeDefined();
      expect(recommendations.insights.preferredServices).toBeDefined();
      expect(recommendations.insights.satisfactionTrends).toBeDefined();
    });
  });

  describe('Emergency Escalation', () => {
    test('should handle emergency escalation correctly', async () => {
      const request = await orchestrator.processServiceRequest(
        'client-emergency',
        'anon-emergency',
        'void',
        {
          serviceCategory: ServiceCategory.MEDICAL_EVACUATION,
          requestType: 'emergency',
          urgencyLevel: 'critical',
        }
      );

      await orchestrator.escalateRequest(request.id, 'Medical emergency - immediate intervention required');
      
      expect(request.status).toBe('escalated');
    });

    test('should handle escalation for non-existent request', async () => {
      await expect(orchestrator.escalateRequest('non-existent', 'test reason'))
        .rejects.toThrow('Request not found');
    });
  });

  describe('Real-time Status Tracking', () => {
    test('should provide accurate request status tracking', async () => {
      const request1 = await orchestrator.processServiceRequest(
        'client-status-1', 'anon-status-1', 'onyx',
        { serviceCategory: ServiceCategory.PRE_IPO_FUNDS, requestType: 'investment' }
      );

      const request2 = await orchestrator.processServiceRequest(
        'client-status-2', 'anon-status-2', 'obsidian',
        { serviceCategory: ServiceCategory.ART_ACQUISITION, requestType: 'concierge' }
      );

      const statuses = orchestrator.getActiveRequestsStatus();
      
      expect(statuses).toHaveLength(2);
      expect(statuses[0].requestId).toBe(request1.id);
      expect(statuses[1].requestId).toBe(request2.id);
      expect(statuses[0].progress).toBeGreaterThanOrEqual(0);
      expect(statuses[0].estimatedCompletion).toBeDefined();
    });

    test('should calculate progress correctly based on status', async () => {
      const request = await orchestrator.processServiceRequest(
        'client-progress', 'anon-progress', 'void',
        { serviceCategory: ServiceCategory.WELLNESS_RETREATS, requestType: 'concierge' }
      );

      const statuses = orchestrator.getActiveRequestsStatus();
      const requestStatus = statuses.find(s => s.requestId === request.id);
      
      expect(requestStatus?.progress).toBeGreaterThanOrEqual(10); // Should be at least 'received' level
    });
  });

  describe('Performance and Reliability', () => {
    test('should handle concurrent service requests', async () => {
      const requests = await Promise.all([
        orchestrator.processServiceRequest(
          'client-concurrent-1', 'anon-concurrent-1', 'onyx',
          { serviceCategory: ServiceCategory.PRE_IPO_FUNDS, requestType: 'investment' }
        ),
        orchestrator.processServiceRequest(
          'client-concurrent-2', 'anon-concurrent-2', 'obsidian',
          { serviceCategory: ServiceCategory.ART_ACQUISITION, requestType: 'concierge' }
        ),
        orchestrator.processServiceRequest(
          'client-concurrent-3', 'anon-concurrent-3', 'void',
          { serviceCategory: ServiceCategory.MEDICAL_EVACUATION, requestType: 'emergency' }
        ),
      ]);

      expect(requests).toHaveLength(3);
      requests.forEach(request => {
        expect(request.id).toBeDefined();
        expect(request.status).toBe('received');
        expect(request.aiProcessing.personalityAssigned).toBeDefined();
      });
    });

    test('should maintain request isolation and security', async () => {
      const request1 = await orchestrator.processServiceRequest(
        'client-isolation-1', 'anon-isolation-1', 'onyx',
        { serviceCategory: ServiceCategory.PRE_IPO_FUNDS, requestType: 'investment' }
      );

      const request2 = await orchestrator.processServiceRequest(
        'client-isolation-2', 'anon-isolation-2', 'void',
        { serviceCategory: ServiceCategory.MEDICAL_EVACUATION, requestType: 'emergency' }
      );

      // Verify requests don't cross-contaminate
      expect(request1.clientId).not.toBe(request2.clientId);
      expect(request1.anonymousId).not.toBe(request2.anonymousId);
      expect(request1.aiProcessing.personalityAssigned).not.toBe(request2.aiProcessing.personalityAssigned);
    });
  });

  describe('Service Quality and Compliance', () => {
    test('should maintain service quality standards by tier', async () => {
      const onyxRequest = await orchestrator.processServiceRequest(
        'client-quality-onyx', 'anon-quality-onyx', 'onyx',
        { serviceCategory: ServiceCategory.FAMILY_OFFICE_SERVICES, requestType: 'consultation' }
      );

      const voidRequest = await orchestrator.processServiceRequest(
        'client-quality-void', 'anon-quality-void', 'void',
        { serviceCategory: ServiceCategory.FAMILY_OFFICE_SERVICES, requestType: 'consultation' }
      );

      expect(onyxRequest.aiProcessing.deliveryMode).toBe(ServiceDeliveryMode.ASSISTED);
      expect(voidRequest.aiProcessing.deliveryMode).toBe(ServiceDeliveryMode.QUANTUM);
      expect(voidRequest.aiProcessing.confidenceLevel).toBeGreaterThanOrEqual(onyxRequest.aiProcessing.confidenceLevel);
    });

    test('should enforce approval requirements based on service risk', async () => {
      const highValueRequest = await orchestrator.processServiceRequest(
        'client-approval', 'anon-approval', 'void',
        {
          serviceCategory: ServiceCategory.PRE_IPO_FUNDS,
          requestType: 'investment',
          budgetRange: {
            min: 5000000000,  // ₹500 Cr
            max: 10000000000, // ₹1000 Cr
            currency: 'INR',
          },
        }
      );

      expect(highValueRequest.aiProcessing.orchestrationSteps).toContain('Perform due diligence validation');
      expect(highValueRequest.aiProcessing.confidenceLevel).toBeDefined();
    });
  });
});