/**
 * Enhanced Concierge Services Test Suite
 * Comprehensive testing for ultra-luxury concierge services including
 * private aviation, art acquisition, golden visa programs, and anonymous service delivery
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { 
  EnhancedConciergeServices, 
  ConciergeCategory, 
  ServiceTier,
  ConciergeRequest,
  PrivateAviationService 
} from '../../services/EnhancedConciergeServices';

// Mock EventEmitter
jest.mock('events');

describe('EnhancedConciergeServices', () => {
  let conciergeService: EnhancedConciergeServices;

  beforeEach(() => {
    conciergeService = new EnhancedConciergeServices();
  });

  describe('Service Initialization', () => {
    test('should initialize with enhanced concierge capabilities', () => {
      expect(conciergeService).toBeDefined();
      expect(typeof conciergeService.createConciergeRequest).toBe('function');
      expect(typeof conciergeService.createPrivateAviationService).toBe('function');
      expect(typeof conciergeService.createArtAcquisitionService).toBe('function');
    });

    test('should validate service categories enum', () => {
      expect(ConciergeCategory.PRIVATE_AVIATION).toBe('private_aviation');
      expect(ConciergeCategory.ART_ACQUISITION).toBe('art_acquisition');
      expect(ConciergeCategory.LUXURY_ACCOMMODATION).toBe('luxury_accommodation');
      expect(ConciergeCategory.GOLDEN_VISA).toBe('golden_visa');
      expect(ConciergeCategory.YACHT_CHARTER).toBe('yacht_charter');
      expect(ConciergeCategory.PRIVATE_CHEF).toBe('private_chef');
      expect(ConciergeCategory.SECURITY_SERVICES).toBe('security_services');
      expect(ConciergeCategory.WELLNESS_RETREATS).toBe('wellness_retreats');
      expect(ConciergeCategory.EXCLUSIVE_EVENTS).toBe('exclusive_events');
      expect(ConciergeCategory.EDUCATIONAL_SERVICES).toBe('educational_services');
    });

    test('should validate service tiers enum', () => {
      expect(ServiceTier.ONYX).toBe('onyx');
      expect(ServiceTier.OBSIDIAN).toBe('obsidian');
      expect(ServiceTier.VOID).toBe('void');
    });
  });

  describe('Concierge Request Management', () => {
    test('should create basic concierge request with all required fields', async () => {
      const request = await conciergeService.createConciergeRequest(
        'test-client-id',
        'test-anonymous-id',
        ServiceTier.ONYX,
        ConciergeCategory.PRIVATE_AVIATION,
        {
          title: 'Private Jet to Dubai',
          description: 'Need immediate private jet charter from Mumbai to Dubai',
          urgencyLevel: 'priority',
          specifications: {
            dates: {
              preferred: ['2024-07-01'],
              flexible: false,
              duration: '3 hours',
            },
            location: {
              departure: 'Mumbai',
              destination: 'Dubai',
            },
            guests: {
              adults: 4,
              children: 2,
            },
            budget: {
              range: 'high',
              currency: 'INR',
            },
          },
          anonymityRequirements: {
            identityConcealment: 'enhanced',
            publicityRestrictions: ['No media coverage'],
            communicationProtocol: 'anonymous',
          },
        }
      );

      expect(request.id).toMatch(/^req-/);
      expect(request.clientId).toBe('test-client-id');
      expect(request.anonymousId).toBe('test-anonymous-id');
      expect(request.tier).toBe(ServiceTier.ONYX);
      expect(request.category).toBe(ConciergeCategory.PRIVATE_AVIATION);
      expect(request.title).toBe('Private Jet to Dubai');
      expect(request.urgencyLevel).toBe('priority');
      expect(request.status).toBe('received');
      expect(request.specifications.location.departure).toBe('Mumbai');
      expect(request.specifications.location.destination).toBe('Dubai');
      expect(request.anonymityRequirements.identityConcealment).toBe('enhanced');
    });

    test('should assign concierge based on service tier', async () => {
      const onyxRequest = await conciergeService.createConciergeRequest(
        'onyx-client',
        'onyx-anonymous',
        ServiceTier.ONYX,
        ConciergeCategory.PRIVATE_AVIATION,
        {
          title: 'Onyx Aviation Service',
          description: 'Test onyx service',
          urgencyLevel: 'standard',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'standard',
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      );

      const voidRequest = await conciergeService.createConciergeRequest(
        'void-client',
        'void-anonymous',
        ServiceTier.VOID,
        ConciergeCategory.PRIVATE_AVIATION,
        {
          title: 'Void Aviation Service',
          description: 'Test void service',
          urgencyLevel: 'impossible',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'absolute',
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      );

      expect(onyxRequest.assignedConcierge).toMatch(/Sterling/);
      expect(voidRequest.assignedConcierge).toMatch(/Nexus/);
    });

    test('should set appropriate anonymity requirements based on tier', async () => {
      const voidRequest = await conciergeService.createConciergeRequest(
        'void-client',
        'void-anonymous',
        ServiceTier.VOID,
        ConciergeCategory.ART_ACQUISITION,
        {
          title: 'Anonymous Art Purchase',
          description: 'Acquire contemporary art piece',
          urgencyLevel: 'standard',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'absolute',
            publicityRestrictions: ['No documentation', 'No records'],
            communicationProtocol: 'anonymous',
          },
        }
      );

      expect(voidRequest.anonymityRequirements.identityConcealment).toBe('absolute');
      expect(voidRequest.anonymityRequirements.publicityRestrictions).toContain('No documentation');
    });

    test('should handle all urgency levels including impossible for Void tier', async () => {
      const voidRequest = await conciergeService.createConciergeRequest(
        'void-client',
        'void-anonymous',
        ServiceTier.VOID,
        ConciergeCategory.MEDICAL_EVACUATION,
        {
          title: 'Impossible Medical Service',
          description: 'Critical medical situation requiring impossible response',
          urgencyLevel: 'impossible',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'absolute',
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      );

      expect(voidRequest.urgencyLevel).toBe('impossible');
      expect(voidRequest.estimatedCompletion).toBeDefined();
    });
  });

  describe('Private Aviation Services', () => {
    test('should create private aviation service with flight details', async () => {
      const aviationService = await conciergeService.createPrivateAviationService(
        'test-request-id',
        {
          departure: {
            city: 'Mumbai',
            airport: 'BOM',
            date: '2024-07-01',
            time: '14:00',
          },
          destination: {
            city: 'Dubai',
            airport: 'DXB',
          },
          passengers: 6,
        }
      );

      expect(aviationService.id).toMatch(/^aviation-/);
      expect(aviationService.requestId).toBe('test-request-id');
      expect(aviationService.flightDetails.departure.city).toBe('Mumbai');
      expect(aviationService.flightDetails.destination.city).toBe('Dubai');
      expect(aviationService.flightDetails.passengers).toBe(6);
      expect(aviationService.status).toBe('planning');
      expect(aviationService.estimatedCost.currency).toBe('INR');
    });

    test('should select appropriate aircraft based on passenger count and distance', async () => {
      const lightJetService = await conciergeService.createPrivateAviationService(
        'light-jet-request',
        {
          departure: { city: 'Mumbai', date: '2024-07-01', time: '10:00' },
          destination: { city: 'Goa' },
          passengers: 4,
        }
      );

      const heavyJetService = await conciergeService.createPrivateAviationService(
        'heavy-jet-request',
        {
          departure: { city: 'Mumbai', date: '2024-07-01', time: '10:00' },
          destination: { city: 'London' },
          passengers: 12,
        }
      );

      expect(lightJetService.aircraft.type).toBe('light_jet');
      expect(heavyJetService.aircraft.type).toBe('heavy_jet');
      expect(heavyJetService.aircraft.capacity).toBeGreaterThanOrEqual(12);
    });

    test('should calculate estimated costs based on distance and aircraft type', async () => {
      const domesticFlight = await conciergeService.createPrivateAviationService(
        'domestic-request',
        {
          departure: { city: 'Delhi', date: '2024-07-01', time: '09:00' },
          destination: { city: 'Mumbai' },
          passengers: 4,
        }
      );

      const internationalFlight = await conciergeService.createPrivateAviationService(
        'international-request',
        {
          departure: { city: 'Mumbai', date: '2024-07-01', time: '09:00' },
          destination: { city: 'Singapore' },
          passengers: 8,
        }
      );

      expect(domesticFlight.estimatedCost.amount).toBeGreaterThan(0);
      expect(internationalFlight.estimatedCost.amount).toBeGreaterThan(domesticFlight.estimatedCost.amount);
    });

    test('should include luxury amenities based on service tier', async () => {
      const aviationService = await conciergeService.createPrivateAviationService(
        'luxury-request',
        {
          departure: { city: 'Mumbai', date: '2024-07-01', time: '14:00' },
          destination: { city: 'Dubai' },
          passengers: 6,
        }
      );

      expect(aviationService.aircraft.amenities).toContain('Gourmet catering');
      expect(aviationService.aircraft.amenities).toContain('High-speed WiFi');
      expect(aviationService.aircraft.amenities).toContain('Private bedroom');
    });
  });

  describe('Art Acquisition Services', () => {
    test('should create art acquisition service with authentication', async () => {
      const artService = await conciergeService.createArtAcquisitionService(
        'art-request-id',
        {
          artType: 'Contemporary painting',
          artist: 'Banksy',
          budgetRange: '₹10-50 Cr',
          timeframe: '6 months',
          authentication: 'required',
          provenance: 'full documentation required',
        }
      );

      expect(artService.id).toMatch(/^art-/);
      expect(artService.requestId).toBe('art-request-id');
      expect(artService.acquisitionDetails.artType).toBe('Contemporary painting');
      expect(artService.acquisitionDetails.artist).toBe('Banksy');
      expect(artService.status).toBe('sourcing');
      expect(artService.authentication.required).toBe(true);
      expect(artService.provenance.documentationLevel).toBe('comprehensive');
    });

    test('should connect with major auction houses and galleries', async () => {
      const artService = await conciergeService.createArtAcquisitionService(
        'auction-request',
        {
          artType: 'Sculpture',
          artist: 'Jeff Koons',
          budgetRange: '₹25-100 Cr',
          timeframe: '12 months',
          authentication: 'museum-grade',
          provenance: 'complete chain required',
        }
      );

      expect(artService.sourceNetwork.auctionHouses).toContain("Sotheby's");
      expect(artService.sourceNetwork.auctionHouses).toContain("Christie's");
      expect(artService.sourceNetwork.galleries).toContain('Gagosian Gallery');
      expect(artService.sourceNetwork.privateDealers.length).toBeGreaterThan(0);
    });

    test('should provide anonymous acquisition with privacy protocols', async () => {
      const artService = await conciergeService.createArtAcquisitionService(
        'anonymous-art-request',
        {
          artType: 'Modern art',
          artist: 'Picasso',
          budgetRange: '₹50-200 Cr',
          timeframe: '18 months',
          authentication: 'required',
          anonymousAcquisition: true,
        }
      );

      expect(artService.anonymousAcquisition.enabled).toBe(true);
      expect(artService.anonymousAcquisition.buyerIdentityMasking).toBe('complete');
      expect(artService.anonymousAcquisition.publicRecordsPrevention).toBe(true);
      expect(artService.delivery.anonymousDelivery).toBe(true);
    });
  });

  describe('Golden Visa Programs', () => {
    test('should create golden visa service with investment requirements', async () => {
      const goldenVisaService = await conciergeService.createGoldenVisaService(
        'visa-request-id',
        {
          targetCountries: ['Portugal', 'Greece', 'Malta'],
          investmentType: 'real_estate',
          investmentAmount: 2500000000, // ₹250 Cr
          familyMembers: 4,
          timeline: '12-18 months',
          legalSupport: 'comprehensive',
        }
      );

      expect(goldenVisaService.id).toMatch(/^visa-/);
      expect(goldenVisaService.requestId).toBe('visa-request-id');
      expect(goldenVisaService.programs.length).toBeGreaterThan(0);
      expect(goldenVisaService.programs[0].country).toBe('Portugal');
      expect(goldenVisaService.programs[0].minimumInvestment).toBeDefined();
      expect(goldenVisaService.legalSupport.immigrationLawyers).toBe(true);
    });

    test('should recommend optimal programs based on investment amount', async () => {
      const highValueVisa = await conciergeService.createGoldenVisaService(
        'high-value-visa',
        {
          targetCountries: ['Portugal', 'Spain', 'Cyprus'],
          investmentType: 'mixed',
          investmentAmount: 5000000000, // ₹500 Cr
          familyMembers: 2,
          timeline: '12 months',
          legalSupport: 'full',
        }
      );

      const recommendedProgram = highValueVisa.programs.find(p => p.recommended);
      expect(recommendedProgram).toBeDefined();
      expect(recommendedProgram!.benefits).toContain('EU passport access');
      expect(recommendedProgram!.processingTime).toBeDefined();
    });

    test('should provide comprehensive legal and tax support', async () => {
      const goldenVisaService = await conciergeService.createGoldenVisaService(
        'comprehensive-visa',
        {
          targetCountries: ['Malta'],
          investmentType: 'government_bonds',
          investmentAmount: 3000000000, // ₹300 Cr
          familyMembers: 6,
          timeline: '6-12 months',
          legalSupport: 'full',
        }
      );

      expect(goldenVisaService.legalSupport.immigrationLawyers).toBe(true);
      expect(goldenVisaService.legalSupport.taxAdvisors).toBe(true);
      expect(goldenVisaService.taxOptimization.strategies.length).toBeGreaterThan(0);
      expect(goldenVisaService.compliance.dueDiligence).toBe(true);
    });
  });

  describe('Luxury Accommodation Services', () => {
    test('should create luxury accommodation booking', async () => {
      const accommodationService = await conciergeService.createLuxuryAccommodationService(
        'accommodation-request',
        {
          location: 'Maldives',
          checkIn: '2024-08-01',
          checkOut: '2024-08-07',
          guests: 8,
          propertyType: 'private_villa',
          amenities: ['Private beach', 'Butler service', 'Spa'],
          budget: 'ultra_high',
        }
      );

      expect(accommodationService.id).toMatch(/^accommodation-/);
      expect(accommodationService.bookingDetails.location).toBe('Maldives');
      expect(accommodationService.bookingDetails.guests).toBe(8);
      expect(accommodationService.propertyDetails.type).toBe('private_villa');
      expect(accommodationService.amenities).toContain('Private beach');
      expect(accommodationService.status).toBe('sourcing');
    });

    test('should provide ultra-exclusive properties for high-tier clients', async () => {
      const ultraLuxuryService = await conciergeService.createLuxuryAccommodationService(
        'ultra-luxury-request',
        {
          location: 'French Riviera',
          checkIn: '2024-09-01',
          checkOut: '2024-09-10',
          guests: 12,
          propertyType: 'private_estate',
          amenities: ['Helicopter pad', 'Private yacht', 'Michelin chef'],
          budget: 'no_limit',
        }
      );

      expect(ultraLuxuryService.propertyDetails.exclusivityRating).toBeGreaterThanOrEqual(9);
      expect(ultraLuxuryService.services.personalConcierge).toBe(true);
      expect(ultraLuxuryService.services.privateChef).toBe(true);
      expect(ultraLuxuryService.services.securityTeam).toBe(true);
    });
  });

  describe('Request Status Management', () => {
    test('should update request status appropriately', async () => {
      const request = await conciergeService.createConciergeRequest(
        'status-test-client',
        'status-test-anonymous',
        ServiceTier.OBSIDIAN,
        ConciergeCategory.YACHT_CHARTER,
        {
          title: 'Yacht Charter Service',
          description: 'Charter luxury yacht for Mediterranean cruise',
          urgencyLevel: 'standard',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'enhanced',
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      );

      expect(request.status).toBe('received');

      await conciergeService.updateRequestStatus(request.id, 'planning');
      const updatedRequest = await conciergeService.getRequest(request.id);
      expect(updatedRequest?.status).toBe('planning');
    });

    test('should track request history and updates', async () => {
      const request = await conciergeService.createConciergeRequest(
        'history-test-client',
        'history-test-anonymous',
        ServiceTier.ONYX,
        ConciergeCategory.PRIVATE_CHEF,
        {
          title: 'Private Chef Service',
          description: 'Personal chef for dinner party',
          urgencyLevel: 'priority',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'standard',
            publicityRestrictions: [],
            communicationProtocol: 'pseudonym',
          },
        }
      );

      const history = await conciergeService.getRequestHistory(request.id);
      expect(history.length).toBeGreaterThan(0);
      expect(history[0].action).toBe('request_created');
      expect(history[0].timestamp).toBeDefined();
    });
  });

  describe('Client Portfolio Management', () => {
    test('should get client service history', async () => {
      const clientId = 'portfolio-test-client';
      
      // Create multiple requests
      await conciergeService.createConciergeRequest(
        clientId,
        'anonymous-1',
        ServiceTier.OBSIDIAN,
        ConciergeCategory.PRIVATE_AVIATION,
        {
          title: 'First Aviation Request',
          description: 'Test request 1',
          urgencyLevel: 'standard',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'enhanced',
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      );

      await conciergeService.createConciergeRequest(
        clientId,
        'anonymous-2',
        ServiceTier.OBSIDIAN,
        ConciergeCategory.ART_ACQUISITION,
        {
          title: 'Art Purchase Request',
          description: 'Test request 2',
          urgencyLevel: 'priority',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'enhanced',
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      );

      const portfolio = await conciergeService.getClientServicePortfolio(clientId);
      expect(portfolio.totalRequests).toBe(2);
      expect(portfolio.activeRequests).toBeGreaterThanOrEqual(2);
      expect(portfolio.serviceCategories).toContain(ConciergeCategory.PRIVATE_AVIATION);
      expect(portfolio.serviceCategories).toContain(ConciergeCategory.ART_ACQUISITION);
    });

    test('should calculate service metrics and satisfaction scores', async () => {
      const clientId = 'metrics-test-client';
      
      await conciergeService.createConciergeRequest(
        clientId,
        'metrics-anonymous',
        ServiceTier.VOID,
        ConciergeCategory.EXCLUSIVE_EVENTS,
        {
          title: 'Exclusive Event Access',
          description: 'VIP access to exclusive event',
          urgencyLevel: 'standard',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'absolute',
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      );

      const portfolio = await conciergeService.getClientServicePortfolio(clientId);
      expect(portfolio.satisfactionMetrics.averageRating).toBeGreaterThanOrEqual(0);
      expect(portfolio.spendingAnalytics.totalSpent).toBeGreaterThanOrEqual(0);
      expect(portfolio.tierBenefits.currentTier).toBe(ServiceTier.VOID);
    });
  });

  describe('Anonymity and Privacy Features', () => {
    test('should maintain complete anonymity for Void tier services', async () => {
      const voidRequest = await conciergeService.createConciergeRequest(
        'void-privacy-client',
        'void-privacy-anonymous',
        ServiceTier.VOID,
        ConciergeCategory.SECURITY_SERVICES,
        {
          title: 'Personal Security Detail',
          description: 'Require personal protection team',
          urgencyLevel: 'emergency',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'absolute',
            publicityRestrictions: ['No records', 'No documentation', 'No traces'],
            communicationProtocol: 'anonymous',
          },
        }
      );

      expect(voidRequest.anonymityRequirements.identityConcealment).toBe('absolute');
      expect(voidRequest.anonymityRequirements.publicityRestrictions).toContain('No records');
      expect(voidRequest.communicationChannels.encrypted).toBe(true);
      expect(voidRequest.communicationChannels.temporaryChannels).toBe(true);
    });

    test('should implement progressive revelation protocols for emergencies', async () => {
      const emergencyRequest = await conciergeService.createConciergeRequest(
        'emergency-client',
        'emergency-anonymous',
        ServiceTier.OBSIDIAN,
        ConciergeCategory.MEDICAL_EVACUATION,
        {
          title: 'Medical Emergency Evacuation',
          description: 'Immediate medical evacuation required',
          urgencyLevel: 'emergency',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'enhanced',
            publicityRestrictions: ['Medical privacy'],
            communicationProtocol: 'representative',
          },
        }
      );

      expect(emergencyRequest.emergencyProtocols).toBeDefined();
      expect(emergencyRequest.emergencyProtocols?.identityReveal).toBe('progressive');
      expect(emergencyRequest.emergencyProtocols?.medicalDisclosure).toBe('authorized');
    });
  });

  describe('Error Handling and Edge Cases', () => {
    test('should handle invalid request IDs gracefully', async () => {
      const result = await conciergeService.getRequest('invalid-request-id');
      expect(result).toBeNull();
    });

    test('should validate tier access for service categories', async () => {
      // Attempt to create Void-exclusive service with Onyx tier
      await expect(conciergeService.createConciergeRequest(
        'invalid-tier-client',
        'invalid-tier-anonymous',
        ServiceTier.ONYX,
        ConciergeCategory.GOLDEN_VISA, // Typically requires higher tier
        {
          title: 'Golden Visa Service',
          description: 'Citizenship by investment',
          urgencyLevel: 'impossible', // Only available to Void tier
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'absolute', // Only available to Void/Obsidian
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      )).rejects.toThrow();
    });

    test('should handle concurrent request processing', async () => {
      const clientId = 'concurrent-test-client';
      
      const promises = Array.from({ length: 5 }, (_, i) =>
        conciergeService.createConciergeRequest(
          clientId,
          `concurrent-anonymous-${i}`,
          ServiceTier.OBSIDIAN,
          ConciergeCategory.WELLNESS_RETREATS,
          {
            title: `Wellness Retreat ${i + 1}`,
            description: `Concurrent request ${i + 1}`,
            urgencyLevel: 'standard',
            specifications: {},
            anonymityRequirements: {
              identityConcealment: 'enhanced',
              publicityRestrictions: [],
              communicationProtocol: 'anonymous',
            },
          }
        )
      );

      const results = await Promise.all(promises);
      expect(results).toHaveLength(5);
      results.forEach((request, index) => {
        expect(request.title).toBe(`Wellness Retreat ${index + 1}`);
        expect(request.clientId).toBe(clientId);
      });
    });
  });

  describe('Event Emission and Notifications', () => {
    test('should emit events for request lifecycle', async () => {
      const emitSpy = jest.spyOn(conciergeService, 'emit');

      await conciergeService.createConciergeRequest(
        'event-test-client',
        'event-test-anonymous',
        ServiceTier.OBSIDIAN,
        ConciergeCategory.EDUCATIONAL_SERVICES,
        {
          title: 'Elite Education Consultation',
          description: 'Educational planning for family',
          urgencyLevel: 'standard',
          specifications: {},
          anonymityRequirements: {
            identityConcealment: 'enhanced',
            publicityRestrictions: [],
            communicationProtocol: 'anonymous',
          },
        }
      );

      expect(emitSpy).toHaveBeenCalledWith('request:created', expect.objectContaining({
        category: ConciergeCategory.EDUCATIONAL_SERVICES,
        tier: ServiceTier.OBSIDIAN,
      }));
    });

    test('should emit specialized service events', async () => {
      const emitSpy = jest.spyOn(conciergeService, 'emit');

      await conciergeService.createPrivateAviationService(
        'aviation-event-test',
        {
          departure: { city: 'Mumbai', date: '2024-07-01', time: '15:00' },
          destination: { city: 'Dubai' },
          passengers: 4,
        }
      );

      expect(emitSpy).toHaveBeenCalledWith('aviation:service_created', expect.objectContaining({
        departure: expect.objectContaining({ city: 'Mumbai' }),
        destination: expect.objectContaining({ city: 'Dubai' }),
      }));
    });
  });
});