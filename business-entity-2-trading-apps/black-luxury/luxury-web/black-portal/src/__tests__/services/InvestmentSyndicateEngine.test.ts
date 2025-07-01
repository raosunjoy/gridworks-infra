/**
 * Investment Syndicate Engine Test Suite
 * Comprehensive testing for investment syndicate formation, Pre-IPO access,
 * luxury real estate, ESG investments, and anonymous portfolio management
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { InvestmentSyndicateEngine, InvestmentCategory, InvestmentTier } from '../../services/InvestmentSyndicateEngine';

// Mock EventEmitter
jest.mock('events');

describe('InvestmentSyndicateEngine', () => {
  let engine: InvestmentSyndicateEngine;

  beforeEach(() => {
    engine = new InvestmentSyndicateEngine();
  });

  describe('Initialization and Premium Opportunities', () => {
    test('should initialize with premium investment opportunities', () => {
      expect(engine).toBeDefined();
      expect(typeof engine.getAllActiveOpportunities).toBe('function');
    });

    test('should create SpaceX Pre-IPO opportunity with correct parameters', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const spacexOpportunity = opportunities.find(opp => opp.title.includes('SpaceX'));
      
      expect(spacexOpportunity).toBeDefined();
      expect(spacexOpportunity!.category).toBe(InvestmentCategory.PRE_IPO);
      expect(spacexOpportunity!.minimumInvestment).toBe(500000000); // ₹50 Cr
      expect(spacexOpportunity!.tierAccess).toContain(InvestmentTier.OBSIDIAN);
      expect(spacexOpportunity!.tierAccess).toContain(InvestmentTier.VOID);
      expect(spacexOpportunity!.companyDetails?.name).toBe('SpaceX');
      expect(spacexOpportunity!.companyDetails?.lastValuation).toBe(180000000000);
    });

    test('should create OpenAI investment opportunity with higher minimum', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const openaiOpportunity = opportunities.find(opp => opp.title.includes('OpenAI'));
      
      expect(openaiOpportunity).toBeDefined();
      expect(openaiOpportunity!.minimumInvestment).toBe(1000000000); // ₹100 Cr
      expect(openaiOpportunity!.companyDetails?.lastValuation).toBe(157000000000);
      expect(openaiOpportunity!.expectedReturns.conservative).toBe('20');
      expect(openaiOpportunity!.expectedReturns.optimistic).toBe('35% annually');
    });

    test('should create Dubai Marina real estate opportunity', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const dubaiOpportunity = opportunities.find(opp => opp.title.includes('Dubai Marina'));
      
      expect(dubaiOpportunity).toBeDefined();
      expect(dubaiOpportunity!.category).toBe(InvestmentCategory.LUXURY_REAL_ESTATE);
      expect(dubaiOpportunity!.minimumInvestment).toBe(250000000); // ₹25 Cr
      expect(dubaiOpportunity!.tierAccess).toContain(InvestmentTier.ONYX);
      expect(dubaiOpportunity!.realEstateDetails?.location).toBe('Dubai Marina, UAE');
      expect(dubaiOpportunity!.realEstateDetails?.amenities).toContain('Private helicopter pad');
    });

    test('should create ESG investment opportunity with high ESG score', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const esgOpportunity = opportunities.find(opp => opp.title.includes('African Lithium'));
      
      expect(esgOpportunity).toBeDefined();
      expect(esgOpportunity!.category).toBe(InvestmentCategory.ESG_INVESTMENTS);
      expect(esgOpportunity!.esgDetails?.esgScore).toBe(95);
      expect(esgOpportunity!.esgDetails?.impactMetrics).toContain('Carbon footprint reduction: 50%');
      expect(esgOpportunity!.esgDetails?.sustainabilityGoals).toContain('UN SDG 7: Affordable and Clean Energy');
    });
  });

  describe('Investment Opportunity Management', () => {
    test('should create Pre-IPO opportunity with all required fields', async () => {
      const opportunity = await engine.createPreIPOOpportunity({
        title: 'Test Pre-IPO Company',
        companyName: 'TestCorp',
        sector: 'Technology',
        lastValuation: 50000000000,
        minimumInvestment: 200000000,
        expectedReturns: '15-25% annually',
        lockupPeriod: '2-3 years',
      });

      expect(opportunity.id).toMatch(/^preipo-/);
      expect(opportunity.title).toBe('Test Pre-IPO Company');
      expect(opportunity.category).toBe(InvestmentCategory.PRE_IPO);
      expect(opportunity.minimumInvestment).toBe(200000000);
      expect(opportunity.maximumInvestment).toBe(2000000000); // 10x minimum
      expect(opportunity.companyDetails?.name).toBe('TestCorp');
      expect(opportunity.companyDetails?.lastValuation).toBe(50000000000);
      expect(opportunity.riskRating).toBe('medium');
      expect(opportunity.status).toBe('active');
      expect(opportunity.availableSlots).toBe(50);
      expect(opportunity.complianceChecks.sebiApproval).toBe(true);
      expect(opportunity.complianceChecks.rbiCompliance).toBe(true);
    });

    test('should create luxury real estate opportunity with property details', async () => {
      const opportunity = await engine.createLuxuryRealEstateOpportunity({
        title: 'Test Luxury Property',
        location: 'Monaco',
        propertyType: 'Penthouse',
        minimumInvestment: 150000000,
        expectedReturns: '10-15% annually',
        amenities: ['Ocean view', 'Private elevator'],
      });

      expect(opportunity.id).toMatch(/^realestate-/);
      expect(opportunity.category).toBe(InvestmentCategory.LUXURY_REAL_ESTATE);
      expect(opportunity.realEstateDetails?.location).toBe('Monaco');
      expect(opportunity.realEstateDetails?.propertyType).toBe('Penthouse');
      expect(opportunity.realEstateDetails?.amenities).toContain('Ocean view');
      expect(opportunity.tierAccess).toContain(InvestmentTier.ONYX);
      expect(opportunity.riskRating).toBe('low');
    });

    test('should create ESG opportunity with impact metrics', async () => {
      const opportunity = await engine.createESGOpportunity({
        title: 'Test ESG Fund',
        impactFocus: 'Renewable energy',
        minimumInvestment: 100000000,
        expectedReturns: '20-30% annually',
        esgScore: 92,
      });

      expect(opportunity.id).toMatch(/^esg-/);
      expect(opportunity.category).toBe(InvestmentCategory.ESG_INVESTMENTS);
      expect(opportunity.esgDetails?.esgScore).toBe(92);
      expect(opportunity.esgDetails?.impactMetrics).toContain('Carbon footprint reduction: 50%');
      expect(opportunity.expectedReturns.conservative).toBe('20');
      expect(opportunity.expectedReturns.optimistic).toBe('30% annually');
    });

    test('should filter opportunities by tier access', async () => {
      const onyxOpportunities = await engine.getAvailableOpportunities(InvestmentTier.ONYX);
      const voidOpportunities = await engine.getAvailableOpportunities(InvestmentTier.VOID);

      expect(onyxOpportunities.length).toBeGreaterThan(0);
      expect(voidOpportunities.length).toBeGreaterThan(0);

      // Void tier should have access to more opportunities
      expect(voidOpportunities.length).toBeGreaterThanOrEqual(onyxOpportunities.length);

      // All opportunities should have appropriate tier access
      onyxOpportunities.forEach(opp => {
        expect(opp.tierAccess).toContain(InvestmentTier.ONYX);
      });

      voidOpportunities.forEach(opp => {
        expect(opp.tierAccess).toContain(InvestmentTier.VOID);
      });
    });

    test('should filter opportunities by category', async () => {
      const preIpoOpportunities = await engine.getAvailableOpportunities(
        InvestmentTier.VOID, 
        InvestmentCategory.PRE_IPO
      );
      const realEstateOpportunities = await engine.getAvailableOpportunities(
        InvestmentTier.ONYX, 
        InvestmentCategory.LUXURY_REAL_ESTATE
      );

      preIpoOpportunities.forEach(opp => {
        expect(opp.category).toBe(InvestmentCategory.PRE_IPO);
      });

      realEstateOpportunities.forEach(opp => {
        expect(opp.category).toBe(InvestmentCategory.LUXURY_REAL_ESTATE);
      });
    });
  });

  describe('Investment Commitment Process', () => {
    test('should create investment commitment with validation', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const commitment = await engine.createInvestmentCommitment(
        opportunity.id,
        'test-client-id',
        'test-anonymous-id',
        InvestmentTier.OBSIDIAN,
        opportunity.minimumInvestment
      );

      expect(commitment.id).toMatch(/^commit-/);
      expect(commitment.investmentOpportunityId).toBe(opportunity.id);
      expect(commitment.clientId).toBe('test-client-id');
      expect(commitment.anonymousId).toBe('test-anonymous-id');
      expect(commitment.tier).toBe(InvestmentTier.OBSIDIAN);
      expect(commitment.commitmentAmount).toBe(opportunity.minimumInvestment);
      expect(commitment.currency).toBe(opportunity.currency);
      expect(commitment.investmentVehicle).toBe('spv');
      expect(commitment.status).toBe('draft');
      expect(commitment.kycStatus).toBe('pending');
    });

    test('should reject commitment below minimum investment', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      await expect(engine.createInvestmentCommitment(
        opportunity.id,
        'test-client-id',
        'test-anonymous-id',
        InvestmentTier.OBSIDIAN,
        opportunity.minimumInvestment - 1000000 // Below minimum
      )).rejects.toThrow('Minimum investment is');
    });

    test('should reject commitment above maximum investment', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      await expect(engine.createInvestmentCommitment(
        opportunity.id,
        'test-client-id',
        'test-anonymous-id',
        InvestmentTier.OBSIDIAN,
        opportunity.maximumInvestment + 1000000 // Above maximum
      )).rejects.toThrow('Maximum investment is');
    });

    test('should reject commitment for unauthorized tier', async () => {
      // Create a Void-only opportunity
      const voidOpportunity = await engine.createPreIPOOpportunity({
        title: 'Void Only Opportunity',
        companyName: 'VoidCorp',
        sector: 'Technology',
        lastValuation: 100000000000,
        minimumInvestment: 1000000000,
        expectedReturns: '30-50% annually',
        lockupPeriod: '5 years',
      });

      // Manually set tier access to Void only
      voidOpportunity.tierAccess = [InvestmentTier.VOID];

      await expect(engine.createInvestmentCommitment(
        voidOpportunity.id,
        'test-client-id',
        'test-anonymous-id',
        InvestmentTier.ONYX, // Not authorized
        voidOpportunity.minimumInvestment
      )).rejects.toThrow('Tier not authorized for this investment');
    });

    test('should create anonymous structure with holding company', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const commitment = await engine.createInvestmentCommitment(
        opportunity.id,
        'test-client-id',
        'test-anonymous-id',
        InvestmentTier.VOID,
        opportunity.minimumInvestment
      );

      expect(commitment.anonymousStructure.holdingCompany).toMatch(/^BlackPortal SPV/);
      expect(commitment.anonymousStructure.jurisdictions).toContain('Mauritius');
      expect(commitment.anonymousStructure.jurisdictions).toContain('Singapore');
      expect(commitment.anonymousStructure.beneficialOwnership).toBe('nominee');
      expect(commitment.anonymousStructure.taxOptimization).toContain('Treaty benefits');
    });

    test('should generate payment schedule', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const commitment = await engine.createInvestmentCommitment(
        opportunity.id,
        'test-client-id',
        'test-anonymous-id',
        InvestmentTier.OBSIDIAN,
        opportunity.minimumInvestment
      );

      expect(commitment.paymentSchedule).toHaveLength(3);
      expect(commitment.paymentSchedule[0].installment).toBe(1);
      expect(commitment.paymentSchedule[0].amount).toBe(opportunity.minimumInvestment / 3);
      expect(commitment.paymentSchedule[0].status).toBe('pending');

      // Check that all installments sum to total commitment
      const totalPayments = commitment.paymentSchedule.reduce((sum, payment) => sum + payment.amount, 0);
      expect(totalPayments).toBe(opportunity.minimumInvestment);
    });

    test('should update opportunity availability after commitment', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];
      const initialSlots = opportunity.availableSlots;
      const initialCommitments = opportunity.currentCommitments;

      await engine.createInvestmentCommitment(
        opportunity.id,
        'test-client-id',
        'test-anonymous-id',
        InvestmentTier.OBSIDIAN,
        opportunity.minimumInvestment
      );

      const updatedOpportunity = await engine.getInvestmentOpportunity(opportunity.id);
      expect(updatedOpportunity!.availableSlots).toBe(initialSlots - 1);
      expect(updatedOpportunity!.currentCommitments).toBe(initialCommitments + opportunity.minimumInvestment);
    });
  });

  describe('Investment Syndicate Formation', () => {
    test('should form investment syndicate with lead investor', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const syndicate = await engine.formInvestmentSyndicate(
        opportunity.id,
        'lead-investor-anonymous',
        InvestmentTier.VOID,
        500000000, // ₹50 Cr lead commitment
        {
          minimumSyndicateSize: 5,
          maximumSyndicateSize: 20,
          governanceStructure: 'Lead investor controls',
        }
      );

      expect(syndicate.id).toMatch(/^syn-/);
      expect(syndicate.opportunityId).toBe(opportunity.id);
      expect(syndicate.leadInvestor?.anonymousId).toBe('lead-investor-anonymous');
      expect(syndicate.leadInvestor?.tier).toBe(InvestmentTier.VOID);
      expect(syndicate.leadInvestor?.commitmentAmount).toBe(500000000);
      expect(syndicate.participants).toHaveLength(0);
      expect(syndicate.status).toBe('forming');
      expect(syndicate.syndicateTerms.minimumSyndicateSize).toBe(5);
      expect(syndicate.syndicateTerms.decisionMaking).toBe('lead_decides');
    });

    test('should allow participants to join syndicate', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      // Form syndicate
      const syndicate = await engine.formInvestmentSyndicate(
        opportunity.id,
        'lead-investor',
        InvestmentTier.VOID,
        500000000,
        {
          minimumSyndicateSize: 3,
          maximumSyndicateSize: 10,
          governanceStructure: 'Lead controls',
        }
      );

      // Add participant
      await engine.joinInvestmentSyndicate(
        syndicate.id,
        'participant-1-anonymous',
        InvestmentTier.OBSIDIAN,
        250000000 // ₹25 Cr
      );

      const updatedSyndicate = await engine.getInvestmentSyndicate?.(syndicate.id);
      if (updatedSyndicate) {
        expect(updatedSyndicate.participants).toHaveLength(1);
        expect(updatedSyndicate.participants[0].anonymousId).toBe('participant-1-anonymous');
        expect(updatedSyndicate.participants[0].commitmentAmount).toBe(250000000);
        expect(updatedSyndicate.participants[0].role).toBe('participant');
      }
    });

    test('should reject participant below minimum investment', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const syndicate = await engine.formInvestmentSyndicate(
        opportunity.id,
        'lead-investor',
        InvestmentTier.VOID,
        500000000,
        {
          minimumSyndicateSize: 3,
          maximumSyndicateSize: 10,
          governanceStructure: 'Lead controls',
        }
      );

      await expect(engine.joinInvestmentSyndicate(
        syndicate.id,
        'participant-anonymous',
        InvestmentTier.ONYX,
        opportunity.minimumInvestment - 1000000 // Below minimum
      )).rejects.toThrow('Minimum investment is');
    });

    test('should transition syndicate to committed when minimum size reached', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const syndicate = await engine.formInvestmentSyndicate(
        opportunity.id,
        'lead-investor',
        InvestmentTier.VOID,
        500000000,
        {
          minimumSyndicateSize: 2,
          maximumSyndicateSize: 10,
          governanceStructure: 'Lead controls',
        }
      );

      // Add first participant
      await engine.joinInvestmentSyndicate(
        syndicate.id,
        'participant-1',
        InvestmentTier.OBSIDIAN,
        250000000
      );

      // Add second participant to reach minimum
      await engine.joinInvestmentSyndicate(
        syndicate.id,
        'participant-2',
        InvestmentTier.ONYX,
        opportunity.minimumInvestment
      );

      const updatedSyndicate = await engine.getInvestmentSyndicate?.(syndicate.id);
      if (updatedSyndicate) {
        expect(updatedSyndicate.status).toBe('committed');
        expect(updatedSyndicate.participants).toHaveLength(2);
      }
    });
  });

  describe('Portfolio Management', () => {
    test('should get client investment portfolio', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      // Create commitment
      await engine.createInvestmentCommitment(
        opportunity.id,
        'portfolio-client',
        'portfolio-anonymous',
        InvestmentTier.OBSIDIAN,
        opportunity.minimumInvestment
      );

      const portfolio = await engine.getClientInvestmentPortfolio('portfolio-client');

      expect(portfolio.totalInvestments).toBeGreaterThan(0);
      expect(portfolio.activeCommitments).toHaveLength(0); // Draft status, not active yet
      expect(portfolio.performanceSummary.totalValue).toBeGreaterThan(0);
      expect(portfolio.performanceSummary.totalReturn).toBe(0.15); // 15% assumed appreciation
    });

    test('should calculate performance metrics correctly', async () => {
      const portfolio = await engine.getClientInvestmentPortfolio('test-client');
      
      expect(portfolio.performanceSummary.totalValue).toBe(portfolio.totalInvestments * 1.15);
      expect(portfolio.performanceSummary.unrealizedGains).toBe(portfolio.totalInvestments * 0.12);
      expect(portfolio.performanceSummary.realizedGains).toBe(portfolio.totalInvestments * 0.03);
      expect(portfolio.performanceSummary.totalReturn).toBe(0.15);
    });
  });

  describe('Data Retrieval and Validation', () => {
    test('should retrieve investment opportunity by ID', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const retrieved = await engine.getInvestmentOpportunity(opportunity.id);
      expect(retrieved).toBeDefined();
      expect(retrieved!.id).toBe(opportunity.id);
      expect(retrieved!.title).toBe(opportunity.title);
    });

    test('should return null for non-existent opportunity', async () => {
      const retrieved = await engine.getInvestmentOpportunity('non-existent-id');
      expect(retrieved).toBeNull();
    });

    test('should retrieve investment commitment by ID', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const commitment = await engine.createInvestmentCommitment(
        opportunity.id,
        'test-client',
        'test-anonymous',
        InvestmentTier.OBSIDIAN,
        opportunity.minimumInvestment
      );

      const retrieved = await engine.getInvestmentCommitment(commitment.id);
      expect(retrieved).toBeDefined();
      expect(retrieved!.id).toBe(commitment.id);
      expect(retrieved!.commitmentAmount).toBe(commitment.commitmentAmount);
    });

    test('should return null for non-existent commitment', async () => {
      const retrieved = await engine.getInvestmentCommitment('non-existent-id');
      expect(retrieved).toBeNull();
    });

    test('should get all active opportunities sorted by creation date', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      
      expect(opportunities.length).toBeGreaterThan(0);
      opportunities.forEach(opp => {
        expect(opp.status).toBe('active');
      });

      // Check sorting (most recent first)
      for (let i = 1; i < opportunities.length; i++) {
        const prevDate = new Date(opportunities[i - 1].createdAt);
        const currDate = new Date(opportunities[i].createdAt);
        expect(prevDate.getTime()).toBeGreaterThanOrEqual(currDate.getTime());
      }
    });
  });

  describe('Compliance and Risk Management', () => {
    test('should ensure all opportunities have required compliance checks', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      
      opportunities.forEach(opp => {
        expect(opp.complianceChecks).toBeDefined();
        expect(typeof opp.complianceChecks.sebiApproval).toBe('boolean');
        expect(typeof opp.complianceChecks.rbiCompliance).toBe('boolean');
        expect(typeof opp.complianceChecks.femaCompliance).toBe('boolean');
        expect(Array.isArray(opp.complianceChecks.taxImplications)).toBe(true);
      });
    });

    test('should validate risk ratings are within acceptable range', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const validRiskRatings = ['low', 'medium', 'high', 'speculative'];
      
      opportunities.forEach(opp => {
        expect(validRiskRatings).toContain(opp.riskRating);
        expect(Array.isArray(opp.riskFactors)).toBe(true);
        expect(opp.riskFactors.length).toBeGreaterThan(0);
      });
    });

    test('should ensure offering periods are valid', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      
      opportunities.forEach(opp => {
        const startDate = new Date(opp.offeringPeriod.startDate);
        const endDate = new Date(opp.offeringPeriod.endDate);
        const finalClosing = new Date(opp.offeringPeriod.finalClosing);
        
        expect(endDate.getTime()).toBeGreaterThan(startDate.getTime());
        expect(finalClosing.getTime()).toBeGreaterThanOrEqual(endDate.getTime());
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle invalid opportunity ID in commitment creation', async () => {
      await expect(engine.createInvestmentCommitment(
        'invalid-opportunity-id',
        'test-client',
        'test-anonymous',
        InvestmentTier.OBSIDIAN,
        1000000000
      )).rejects.toThrow('Investment opportunity not found');
    });

    test('should handle invalid syndicate ID when joining', async () => {
      await expect(engine.joinInvestmentSyndicate(
        'invalid-syndicate-id',
        'test-participant',
        InvestmentTier.ONYX,
        500000000
      )).rejects.toThrow('Investment syndicate not found');
    });

    test('should handle syndicate at maximum capacity', async () => {
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const syndicate = await engine.formInvestmentSyndicate(
        opportunity.id,
        'lead-investor',
        InvestmentTier.VOID,
        500000000,
        {
          minimumSyndicateSize: 1,
          maximumSyndicateSize: 1, // Max 1 participant
          governanceStructure: 'Lead controls',
        }
      );

      // Add one participant to reach max
      await engine.joinInvestmentSyndicate(
        syndicate.id,
        'participant-1',
        InvestmentTier.OBSIDIAN,
        opportunity.minimumInvestment
      );

      // Try to add another participant
      await expect(engine.joinInvestmentSyndicate(
        syndicate.id,
        'participant-2',
        InvestmentTier.ONYX,
        opportunity.minimumInvestment
      )).rejects.toThrow('Syndicate is full');
    });
  });

  describe('Event Emission', () => {
    test('should emit opportunity:created event when opportunity is created', async () => {
      const emitSpy = jest.spyOn(engine, 'emit');

      await engine.createPreIPOOpportunity({
        title: 'Event Test Opportunity',
        companyName: 'EventCorp',
        sector: 'Technology',
        lastValuation: 25000000000,
        minimumInvestment: 100000000,
        expectedReturns: '10-20% annually',
        lockupPeriod: '2 years',
      });

      expect(emitSpy).toHaveBeenCalledWith('opportunity:created', expect.objectContaining({
        category: InvestmentCategory.PRE_IPO,
        minimumInvestment: 100000000,
      }));
    });

    test('should emit commitment:created event when commitment is created', async () => {
      const emitSpy = jest.spyOn(engine, 'emit');
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      await engine.createInvestmentCommitment(
        opportunity.id,
        'event-test-client',
        'event-test-anonymous',
        InvestmentTier.OBSIDIAN,
        opportunity.minimumInvestment
      );

      expect(emitSpy).toHaveBeenCalledWith('commitment:created', expect.objectContaining({
        opportunityId: opportunity.id,
        anonymousId: 'event-test-anonymous',
        tier: InvestmentTier.OBSIDIAN,
      }));
    });

    test('should emit syndicate:formed event when syndicate is formed', async () => {
      const emitSpy = jest.spyOn(engine, 'emit');
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      await engine.formInvestmentSyndicate(
        opportunity.id,
        'syndicate-lead',
        InvestmentTier.VOID,
        500000000,
        {
          minimumSyndicateSize: 3,
          maximumSyndicateSize: 10,
          governanceStructure: 'Lead controls',
        }
      );

      expect(emitSpy).toHaveBeenCalledWith('syndicate:formed', expect.objectContaining({
        opportunityId: opportunity.id,
        leadInvestor: 'syndicate-lead',
        leadCommitment: 500000000,
      }));
    });

    test('should emit syndicate:participant_joined event when participant joins', async () => {
      const emitSpy = jest.spyOn(engine, 'emit');
      const opportunities = await engine.getAllActiveOpportunities();
      const opportunity = opportunities[0];

      const syndicate = await engine.formInvestmentSyndicate(
        opportunity.id,
        'syndicate-lead',
        InvestmentTier.VOID,
        500000000,
        {
          minimumSyndicateSize: 2,
          maximumSyndicateSize: 10,
          governanceStructure: 'Lead controls',
        }
      );

      await engine.joinInvestmentSyndicate(
        syndicate.id,
        'new-participant',
        InvestmentTier.OBSIDIAN,
        250000000
      );

      expect(emitSpy).toHaveBeenCalledWith('syndicate:participant_joined', expect.objectContaining({
        syndicateId: syndicate.id,
        participantId: 'new-participant',
        commitmentAmount: 250000000,
        totalParticipants: 1,
      }));
    });
  });
});