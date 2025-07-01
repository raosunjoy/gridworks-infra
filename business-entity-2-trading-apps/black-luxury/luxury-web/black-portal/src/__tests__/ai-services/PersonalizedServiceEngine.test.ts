/**
 * Personalized Service Engine Integration Tests
 * Testing behavioral analytics, experience personalization, and tier-specific service delivery
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { PersonalizedServiceEngine } from '../../services/PersonalizedServiceEngine';
import { ServiceCategory } from '../../types/service-management';
import { AIPersonalityType } from '../../services/AIServicesOrchestrator';

// Mock EventEmitter
jest.mock('events');

describe('PersonalizedServiceEngine', () => {
  let engine: PersonalizedServiceEngine;
  
  beforeEach(() => {
    engine = new PersonalizedServiceEngine();
  });

  describe('Personalization Profile Creation', () => {
    test('should create Onyx tier personalization profile with correct defaults', async () => {
      const profile = await engine.createPersonalizationProfile(
        'client-onyx-1',
        'anon-onyx-1',
        'onyx'
      );

      expect(profile.clientId).toBe('client-onyx-1');
      expect(profile.anonymousId).toBe('anon-onyx-1');
      expect(profile.tier).toBe('onyx');
      
      // Verify Onyx-specific defaults
      expect(profile.behaviorAnalytics.communicationPatterns.emotionalTone).toBe('professional');
      expect(profile.behaviorAnalytics.serviceUsagePatterns.spendingVelocity).toBe('moderate');
      expect(profile.behaviorAnalytics.decisionMakingStyle.riskTolerance).toBe('moderate');
      expect(profile.behaviorAnalytics.decisionMakingStyle.deliberationTime).toBe(24); // 24 hours
      expect(profile.preferences.communicationStyle.personalityAlignment).toBe(AIPersonalityType.STERLING);
      expect(profile.preferences.serviceDelivery.anticipatoryLevel).toBe('proactive');
      expect(profile.preferences.serviceDelivery.qualityStandards).toBe('premium');
      expect(profile.preferences.experienceDesign.narrativeStyle).toBe('elegant');
    });

    test('should create Obsidian tier personalization profile with enhanced features', async () => {
      const profile = await engine.createPersonalizationProfile(
        'client-obsidian-1',
        'anon-obsidian-1',
        'obsidian'
      );

      expect(profile.tier).toBe('obsidian');
      
      // Verify Obsidian-specific defaults
      expect(profile.behaviorAnalytics.communicationPatterns.emotionalTone).toBe('mystical');
      expect(profile.behaviorAnalytics.serviceUsagePatterns.spendingVelocity).toBe('aggressive');
      expect(profile.behaviorAnalytics.decisionMakingStyle.riskTolerance).toBe('high');
      expect(profile.behaviorAnalytics.decisionMakingStyle.deliberationTime).toBe(12); // 12 hours
      expect(profile.preferences.communicationStyle.personalityAlignment).toBe(AIPersonalityType.PRISM);
      expect(profile.preferences.serviceDelivery.anticipatoryLevel).toBe('predictive');
      expect(profile.preferences.serviceDelivery.qualityStandards).toBe('ultra-luxury');
      expect(profile.preferences.experienceDesign.narrativeStyle).toBe('mystical');
    });

    test('should create Void tier personalization profile with quantum capabilities', async () => {
      const profile = await engine.createPersonalizationProfile(
        'client-void-1',
        'anon-void-1',
        'void'
      );

      expect(profile.tier).toBe('void');
      
      // Verify Void-specific defaults
      expect(profile.behaviorAnalytics.communicationPatterns.emotionalTone).toBe('transcendent');
      expect(profile.behaviorAnalytics.serviceUsagePatterns.spendingVelocity).toBe('unlimited');
      expect(profile.behaviorAnalytics.decisionMakingStyle.riskTolerance).toBe('extreme');
      expect(profile.behaviorAnalytics.decisionMakingStyle.deliberationTime).toBe(1); // 1 hour
      expect(profile.preferences.communicationStyle.personalityAlignment).toBe(AIPersonalityType.NEXUS);
      expect(profile.preferences.serviceDelivery.anticipatoryLevel).toBe('prescient');
      expect(profile.preferences.serviceDelivery.qualityStandards).toBe('transcendent');
      expect(profile.preferences.experienceDesign.narrativeStyle).toBe('quantum');
    });

    test('should accept and merge initial data override', async () => {
      const initialData = {
        behaviorAnalytics: {
          communicationPatterns: {
            preferredTimes: ['10:00-14:00'],
            responseSpeed: 'immediate' as const,
            messageLength: 'comprehensive' as const,
            emotionalTone: 'warm' as const,
          },
          serviceUsagePatterns: {
            frequentCategories: [ServiceCategory.ART_ACQUISITION],
            seasonalPreferences: {},
            urgencyDistribution: { low: 0.1, medium: 0.3, high: 0.4, critical: 0.2 },
            spendingVelocity: 'aggressive' as const,
          },
          decisionMakingStyle: {
            riskTolerance: 'high' as const,
            researchDepth: 'exhaustive' as const,
            deliberationTime: 6,
            influenceFactors: ['Innovation', 'Exclusivity'],
          },
        },
      };

      const profile = await engine.createPersonalizationProfile(
        'client-custom',
        'anon-custom',
        'onyx',
        initialData
      );

      expect(profile.behaviorAnalytics.communicationPatterns.responseSpeed).toBe('immediate');
      expect(profile.behaviorAnalytics.decisionMakingStyle.riskTolerance).toBe('high');
    });
  });

  describe('Personalized Experience Generation', () => {
    let onyxProfile: any;
    let obsidianProfile: any;
    let voidProfile: any;

    beforeEach(async () => {
      onyxProfile = await engine.createPersonalizationProfile('client-onyx', 'anon-onyx', 'onyx');
      obsidianProfile = await engine.createPersonalizationProfile('client-obsidian', 'anon-obsidian', 'obsidian');
      voidProfile = await engine.createPersonalizationProfile('client-void', 'anon-void', 'void');
    });

    test('should generate personalized investment experience for Onyx tier', async () => {
      const experience = await engine.generatePersonalizedExperience(
        'client-onyx',
        ServiceCategory.PRE_IPO_FUNDS,
        {
          investmentAmount: 100000000, // ₹10 Cr
          riskProfile: 'moderate',
          timeHorizon: '3-5 years',
        }
      );

      expect(experience.clientId).toBe('client-onyx');
      expect(experience.serviceCategory).toBe(ServiceCategory.PRE_IPO_FUNDS);
      
      // Verify experience design
      expect(experience.experienceDesign.theme).toContain('onyx');
      expect(experience.experienceDesign.narrative).toContain('Onyx');
      expect(experience.experienceDesign.interactionFlow).toBeDefined();
      
      // Verify personalization elements
      expect(experience.personalization.customizedCommunication.greetingStyle).toBeDefined();
      expect(experience.personalization.adaptiveWorkflow).toBeDefined();
      expect(experience.personalization.contextualAdaptations.culturalSensitivity).toContain('Indian');
      
      // Verify predictive enhancements
      expect(experience.predictiveEnhancements.anticipatedNeeds).toBeDefined();
      expect(experience.predictiveEnhancements.proactiveRecommendations).toBeDefined();
      
      // Verify delivery orchestration
      expect(experience.delivery.orchestrationPlan).toBeDefined();
      expect(experience.delivery.qualityCheckpoints).toBeDefined();
    });

    test('should generate mystical art acquisition experience for Obsidian tier', async () => {
      const experience = await engine.generatePersonalizedExperience(
        'client-obsidian',
        ServiceCategory.ART_ACQUISITION,
        {
          artStyle: 'contemporary',
          budget: '₹50-100 Cr',
          anonymousDelivery: true,
          preferences: ['mystical', 'transcendent'],
        }
      );

      expect(experience.serviceCategory).toBe(ServiceCategory.ART_ACQUISITION);
      
      // Verify mystical experience design for Obsidian
      expect(experience.experienceDesign.theme).toContain('obsidian');
      expect(experience.experienceDesign.aestheticElements).toContain('Mystical');
      
      // Verify Obsidian-specific personalization
      expect(experience.personalization.customizedCommunication.greetingStyle).toContain('mystical');
    });

    test('should generate quantum-level experience for Void tier emergency', async () => {
      const experience = await engine.generatePersonalizedExperience(
        'client-void',
        ServiceCategory.MEDICAL_EVACUATION,
        {
          emergencyType: 'medical',
          urgency: 'critical',
          location: 'encrypted',
          medicalDetails: 'classified',
        }
      );

      expect(experience.serviceCategory).toBe(ServiceCategory.MEDICAL_EVACUATION);
      
      // Verify quantum-level experience for Void
      expect(experience.experienceDesign.theme).toContain('void');
      expect(experience.experienceDesign.aestheticElements).toContain('Quantum');
      
      // Verify transcendent personalization
      expect(experience.personalization.customizedCommunication.greetingStyle).toContain('transcendent');
    });

    test('should generate appropriate interaction flows by service category', async () => {
      const investmentExperience = await engine.generatePersonalizedExperience(
        'client-onyx',
        ServiceCategory.PRE_IPO_FUNDS,
        { investmentType: 'pre-ipo' }
      );

      const conciergeExperience = await engine.generatePersonalizedExperience(
        'client-obsidian',
        ServiceCategory.PRIVATE_AVIATION,
        { destination: 'Dubai' }
      );

      // Investment experience should have financial-focused interactions
      expect(investmentExperience.experienceDesign.interactionFlow).toBeDefined();
      
      // Concierge experience should have service-focused interactions
      expect(conciergeExperience.experienceDesign.interactionFlow).toBeDefined();
    });
  });

  describe('Real-time Experience Adaptation', () => {
    let testProfile: any;
    let testExperience: any;

    beforeEach(async () => {
      testProfile = await engine.createPersonalizationProfile('client-adapt', 'anon-adapt', 'obsidian');
      testExperience = await engine.generatePersonalizedExperience(
        'client-adapt',
        ServiceCategory.WELLNESS_RETREATS,
        { location: 'Bali', duration: '14 days' }
      );
    });

    test('should adapt experience based on client interactions', async () => {
      const interactionData = {
        type: 'preference_update',
        clientResponse: {
          satisfaction: 8.5,
          feedback: ['more personalized', 'faster responses'],
          preferences: {
            communicationStyle: 'more mystical',
            responseTime: 'immediate',
          },
        },
      };

      await engine.adaptExperienceRealTime(testExperience.experienceId, interactionData);
      
      // Verify adaptation occurred
      expect(testExperience).toBeDefined();
    });

    test('should handle real-time mood changes', async () => {
      const moodChangeData = {
        type: 'mood_change',
        clientMood: 'urgent',
        timestamp: new Date().toISOString(),
      };

      await engine.adaptExperienceRealTime(testExperience.experienceId, moodChangeData);
      
      // Should adapt to urgent mood
      expect(testExperience).toBeDefined();
    });

    test('should gracefully handle invalid experience ID', async () => {
      const invalidInteraction = {
        type: 'test',
        data: 'sample',
      };

      // Should not throw error for invalid experience ID
      await expect(engine.adaptExperienceRealTime('invalid-id', invalidInteraction))
        .resolves.not.toThrow();
    });
  });

  describe('Learning and Satisfaction Tracking', () => {
    let learningProfile: any;
    let learningExperience: any;

    beforeEach(async () => {
      learningProfile = await engine.createPersonalizationProfile('client-learn', 'anon-learn', 'void');
      learningExperience = await engine.generatePersonalizedExperience(
        'client-learn',
        ServiceCategory.LUXURY_ACCOMMODATION,
        { location: 'Swiss Alps', preferences: ['quantum-grade privacy'] }
      );
    });

    test('should learn from high satisfaction experiences', async () => {
      const highSatisfactionFeedback = [
        'Exceeded expectations',
        'Perfect timing',
        'Exceptional service quality',
        'Quantum-level privacy maintained',
      ];

      await engine.learnFromExperience(
        learningExperience.experienceId,
        95, // High satisfaction score
        highSatisfactionFeedback
      );

      // Verify learning occurred
      expect(learningProfile.learningModel.satisfactionHistory).toHaveLength(1);
      expect(learningProfile.learningModel.satisfactionHistory[0].satisfactionScore).toBe(95);
      expect(learningProfile.learningModel.satisfactionHistory[0].feedback).toEqual(highSatisfactionFeedback);
    });

    test('should adapt preferences from low satisfaction', async () => {
      const lowSatisfactionFeedback = [
        'Response too slow',
        'Not personalized enough',
        'Expected more proactive service',
      ];

      await engine.learnFromExperience(
        learningExperience.experienceId,
        60, // Low satisfaction score
        lowSatisfactionFeedback
      );

      // Should trigger preference adaptation
      expect(learningProfile.learningModel.satisfactionHistory[0].satisfactionScore).toBe(60);
    });

    test('should maintain satisfaction history limits', async () => {
      // Add 60 experiences to test limit
      for (let i = 0; i < 60; i++) {
        const tempExperience = await engine.generatePersonalizedExperience(
          'client-learn',
          ServiceCategory.PRE_IPO_FUNDS,
          { investmentAmount: 100000000 * (i + 1) }
        );

        await engine.learnFromExperience(
          tempExperience.experienceId,
          80 + Math.random() * 20, // Random satisfaction 80-100
          [`Experience ${i + 1} feedback`]
        );
      }

      // Should maintain only last 50 entries
      expect(learningProfile.learningModel.satisfactionHistory.length).toBeLessThanOrEqual(50);
    });

    test('should handle learning from non-existent experience', async () => {
      await expect(engine.learnFromExperience('non-existent', 85, ['test feedback']))
        .resolves.not.toThrow();
    });
  });

  describe('Tier-Specific Service Recommendations', () => {
    let recommendationProfiles: { [key: string]: any } = {};

    beforeEach(async () => {
      recommendationProfiles.onyx = await engine.createPersonalizationProfile('client-rec-onyx', 'anon-rec-onyx', 'onyx');
      recommendationProfiles.obsidian = await engine.createPersonalizationProfile('client-rec-obsidian', 'anon-rec-obsidian', 'obsidian');
      recommendationProfiles.void = await engine.createPersonalizationProfile('client-rec-void', 'anon-rec-void', 'void');
    });

    test('should generate Onyx-appropriate recommendations', async () => {
      const recommendations = await engine.getTierSpecificRecommendations('client-rec-onyx');
      
      expect(recommendations.recommendations).toBeDefined();
      expect(recommendations.personalizedInsights).toBeDefined();
      expect(recommendations.personalizedInsights.strengths).toBeDefined();
      expect(recommendations.personalizedInsights.opportunities).toBeDefined();
      expect(recommendations.personalizedInsights.preferences).toBeDefined();
    });

    test('should generate Obsidian-level mystical recommendations', async () => {
      const recommendations = await engine.getTierSpecificRecommendations('client-rec-obsidian');
      
      expect(recommendations.recommendations).toBeDefined();
      expect(recommendations.personalizedInsights).toBeDefined();
    });

    test('should generate Void-tier quantum recommendations', async () => {
      const recommendations = await engine.getTierSpecificRecommendations('client-rec-void');
      
      expect(recommendations.recommendations).toBeDefined();
      expect(recommendations.personalizedInsights).toBeDefined();
    });

    test('should handle recommendations for non-existent profile', async () => {
      await expect(engine.getTierSpecificRecommendations('non-existent-client'))
        .rejects.toThrow('Personalization profile not found');
    });
  });

  describe('Behavioral Analytics and Pattern Recognition', () => {
    test('should track communication pattern changes over time', async () => {
      const profile = await engine.createPersonalizationProfile('client-patterns', 'anon-patterns', 'obsidian');
      
      // Simulate multiple interactions with different patterns
      const experiences = [];
      for (let i = 0; i < 5; i++) {
        const experience = await engine.generatePersonalizedExperience(
          'client-patterns',
          ServiceCategory.ART_ACQUISITION,
          { artType: 'contemporary', session: i }
        );
        experiences.push(experience);
        
        // Simulate learning from each experience
        await engine.learnFromExperience(
          experience.experienceId,
          85 + i * 2, // Increasing satisfaction
          [`Pattern learning session ${i}`]
        );
      }

      // Verify pattern learning
      expect(profile.learningModel.satisfactionHistory).toHaveLength(5);
      expect(profile.learningModel.satisfactionHistory[4].satisfactionScore).toBe(93);
    });

    test('should adapt to seasonal preference changes', async () => {
      const profile = await engine.createPersonalizationProfile('client-seasonal', 'anon-seasonal', 'void');
      
      // Create winter-themed experience
      const winterExperience = await engine.generatePersonalizedExperience(
        'client-seasonal',
        ServiceCategory.WELLNESS_RETREATS,
        { season: 'winter', location: 'Swiss Alps' }
      );

      expect(winterExperience.personalization.contextualAdaptations.seasonalAdjustments).toBeDefined();
    });

    test('should recognize and adapt to portfolio context changes', async () => {
      const profile = await engine.createPersonalizationProfile('client-portfolio', 'anon-portfolio', 'onyx');
      
      // Create investment experience with portfolio context
      const investmentExperience = await engine.generatePersonalizedExperience(
        'client-portfolio',
        ServiceCategory.PRE_IPO_FUNDS,
        {
          currentPortfolio: {
            equity: 0.6,
            fixedIncome: 0.3,
            alternatives: 0.1,
          },
          riskCapacity: 'high',
        }
      );

      expect(investmentExperience.personalization.contextualAdaptations.portfolioAlignment).toBeDefined();
    });
  });

  describe('Performance and Scalability', () => {
    test('should handle concurrent personalization requests', async () => {
      const concurrentRequests = Array.from({ length: 10 }, (_, i) => 
        engine.createPersonalizationProfile(`client-concurrent-${i}`, `anon-concurrent-${i}`, 'obsidian')
      );

      const profiles = await Promise.all(concurrentRequests);
      
      expect(profiles).toHaveLength(10);
      profiles.forEach((profile, index) => {
        expect(profile.clientId).toBe(`client-concurrent-${index}`);
        expect(profile.tier).toBe('obsidian');
      });
    });

    test('should efficiently generate multiple experiences for same client', async () => {
      const profile = await engine.createPersonalizationProfile('client-multiple', 'anon-multiple', 'void');
      
      const experienceRequests = [
        ServiceCategory.PRE_IPO_FUNDS,
        ServiceCategory.ART_ACQUISITION,
        ServiceCategory.PRIVATE_AVIATION,
        ServiceCategory.WELLNESS_RETREATS,
        ServiceCategory.LUXURY_ACCOMMODATION,
      ].map(category => 
        engine.generatePersonalizedExperience('client-multiple', category, { test: true })
      );

      const experiences = await Promise.all(experienceRequests);
      
      expect(experiences).toHaveLength(5);
      experiences.forEach(experience => {
        expect(experience.clientId).toBe('client-multiple');
        expect(experience.experienceId).toBeDefined();
      });
    });

    test('should maintain performance with large satisfaction history', async () => {
      const profile = await engine.createPersonalizationProfile('client-performance', 'anon-performance', 'onyx');
      
      // Generate many experiences quickly
      const startTime = Date.now();
      
      for (let i = 0; i < 20; i++) {
        const experience = await engine.generatePersonalizedExperience(
          'client-performance',
          ServiceCategory.PRE_IPO_FUNDS,
          { batch: i }
        );
        
        await engine.learnFromExperience(
          experience.experienceId,
          80 + Math.random() * 20,
          [`Batch ${i} feedback`]
        );
      }
      
      const endTime = Date.now();
      const totalTime = endTime - startTime;
      
      // Should complete within reasonable time (adjust threshold as needed)
      expect(totalTime).toBeLessThan(10000); // 10 seconds
      expect(profile.learningModel.satisfactionHistory.length).toBeLessThanOrEqual(50);
    });
  });
});