/**
 * Tier-Based AI Personalities Performance Tests
 * Testing response times, scalability, and resource efficiency
 * for Sterling, Prism, and Nexus AI personalities
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { TierBasedAIPersonalities, AIPersonalityTier } from '../../services/TierBasedAIPersonalities';
import { ServiceCategory } from '../../types/service-management';

// Mock EventEmitter
jest.mock('events');

describe('TierBasedAIPersonalities Performance Tests', () => {
  let personalities: TierBasedAIPersonalities;
  
  beforeEach(() => {
    personalities = new TierBasedAIPersonalities();
  });

  describe('Response Time Performance', () => {
    test('should create Sterling personality interactions within performance thresholds', async () => {
      const startTime = performance.now();
      
      const interaction = await personalities.createPersonalizedInteraction(
        'perf-client-sterling',
        'onyx',
        {
          serviceCategory: ServiceCategory.PRE_IPO_FUNDS,
          urgencyLevel: 'medium',
          clientMood: 'analytical',
        }
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(100); // Sub-100ms for Sterling
      expect(interaction.personalityTier).toBe(AIPersonalityTier.STERLING);
      expect(interaction.conversationFlow.greeting).toBeDefined();
    });

    test('should create Prism personality interactions with enhanced processing time', async () => {
      const startTime = performance.now();
      
      const interaction = await personalities.createPersonalizedInteraction(
        'perf-client-prism',
        'obsidian',
        {
          serviceCategory: ServiceCategory.ART_ACQUISITION,
          urgencyLevel: 'high',
          clientMood: 'contemplative',
        }
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(150); // Sub-150ms for Prism (more complex)
      expect(interaction.personalityTier).toBe(AIPersonalityTier.PRISM);
      expect(interaction.conversationFlow.greeting).toContain('mystical');
    });

    test('should create Nexus personality interactions with quantum processing speed', async () => {
      const startTime = performance.now();
      
      const interaction = await personalities.createPersonalizedInteraction(
        'perf-client-nexus',
        'void',
        {
          serviceCategory: ServiceCategory.MEDICAL_EVACUATION,
          urgencyLevel: 'critical',
          clientMood: 'urgent',
        }
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(50); // Sub-50ms for Nexus (quantum processing)
      expect(interaction.personalityTier).toBe(AIPersonalityTier.NEXUS);
      expect(interaction.conversationFlow.greeting).toContain('quantum');
    });

    test('should handle batch personality interaction creation efficiently', async () => {
      const batchSize = 50;
      const startTime = performance.now();
      
      const interactions = await Promise.all(
        Array.from({ length: batchSize }, (_, i) => 
          personalities.createPersonalizedInteraction(
            `batch-client-${i}`,
            i % 3 === 0 ? 'onyx' : i % 3 === 1 ? 'obsidian' : 'void',
            {
              serviceCategory: ServiceCategory.PRE_IPO_FUNDS,
              urgencyLevel: 'medium',
            }
          )
        )
      );
      
      const endTime = performance.now();
      const totalTime = endTime - startTime;
      const averageTime = totalTime / batchSize;
      
      expect(interactions).toHaveLength(batchSize);
      expect(averageTime).toBeLessThan(200); // Average under 200ms per interaction
      expect(totalTime).toBeLessThan(10000); // Total under 10 seconds
      
      // Verify all interactions are valid
      interactions.forEach(interaction => {
        expect(interaction.interactionId).toBeDefined();
        expect(interaction.personalityTier).toBeDefined();
      });
    });
  });

  describe('Real-time Adaptation Performance', () => {
    let testInteractions: any[] = [];

    beforeEach(async () => {
      // Create test interactions for different tiers
      testInteractions = await Promise.all([
        personalities.createPersonalizedInteraction('adapt-sterling', 'onyx', {
          serviceCategory: ServiceCategory.REAL_ESTATE_FUNDS,
          urgencyLevel: 'low',
        }),
        personalities.createPersonalizedInteraction('adapt-prism', 'obsidian', {
          serviceCategory: ServiceCategory.WELLNESS_RETREATS,
          urgencyLevel: 'medium',
        }),
        personalities.createPersonalizedInteraction('adapt-nexus', 'void', {
          serviceCategory: ServiceCategory.FAMILY_OFFICE_SERVICES,
          urgencyLevel: 'high',
        }),
      ]);
    });

    test('should adapt Sterling personality in real-time efficiently', async () => {
      const startTime = performance.now();
      
      await personalities.adaptPersonalityRealTime(
        testInteractions[0].interactionId,
        {
          satisfaction: 8.5,
          feedback: ['more detail needed', 'excellent analysis'],
          preferences: { detail: 'high', formality: 'increased' },
        }
      );
      
      const endTime = performance.now();
      const adaptationTime = endTime - startTime;
      
      expect(adaptationTime).toBeLessThan(80); // Sub-80ms adaptation for Sterling
    });

    test('should adapt Prism personality with mystical processing efficiency', async () => {
      const startTime = performance.now();
      
      await personalities.adaptPersonalityRealTime(
        testInteractions[1].interactionId,
        {
          satisfaction: 9.2,
          feedback: ['perfectly harmonious', 'ethereal experience'],
          preferences: { mystique: 'enhanced', transcendence: 'increased' },
        }
      );
      
      const endTime = performance.now();
      const adaptationTime = endTime - startTime;
      
      expect(adaptationTime).toBeLessThan(120); // Sub-120ms for Prism (more complex)
    });

    test('should adapt Nexus personality with quantum-speed processing', async () => {
      const startTime = performance.now();
      
      await personalities.adaptPersonalityRealTime(
        testInteractions[2].interactionId,
        {
          satisfaction: 9.8,
          feedback: ['reality transcended', 'impossibility achieved'],
          preferences: { omniscience: 'maximum', reality_shaping: 'unlimited' },
        }
      );
      
      const endTime = performance.now();
      const adaptationTime = endTime - startTime;
      
      expect(adaptationTime).toBeLessThan(30); // Sub-30ms for Nexus (quantum processing)
    });

    test('should handle concurrent real-time adaptations efficiently', async () => {
      const startTime = performance.now();
      
      const adaptations = await Promise.all(
        testInteractions.map(interaction => 
          personalities.adaptPersonalityRealTime(
            interaction.interactionId,
            {
              satisfaction: 8 + Math.random() * 2,
              feedback: ['concurrent test'],
              preferences: { concurrent: true },
            }
          )
        )
      );
      
      const endTime = performance.now();
      const totalTime = endTime - startTime;
      
      expect(totalTime).toBeLessThan(300); // All adaptations under 300ms
      expect(adaptations).toHaveLength(3);
    });
  });

  describe('Memory and Resource Efficiency', () => {
    test('should efficiently manage memory for large numbers of interactions', async () => {
      const largeScale = 200;
      const initialMemory = process.memoryUsage();
      
      // Create many interactions
      const interactions = [];
      for (let i = 0; i < largeScale; i++) {
        const interaction = await personalities.createPersonalizedInteraction(
          `memory-test-${i}`,
          i % 3 === 0 ? 'onyx' : i % 3 === 1 ? 'obsidian' : 'void',
          {
            serviceCategory: ServiceCategory.PRE_IPO_FUNDS,
            urgencyLevel: 'medium',
          }
        );
        interactions.push(interaction);
        
        // Periodic memory check
        if (i % 50 === 0) {
          const currentMemory = process.memoryUsage();
          const memoryIncrease = currentMemory.heapUsed - initialMemory.heapUsed;
          
          // Memory increase should be reasonable (less than 100MB for 200 interactions)
          expect(memoryIncrease).toBeLessThan(100 * 1024 * 1024);
        }
      }
      
      expect(interactions).toHaveLength(largeScale);
      
      const finalMemory = process.memoryUsage();
      const totalMemoryIncrease = finalMemory.heapUsed - initialMemory.heapUsed;
      
      // Total memory increase should be reasonable
      expect(totalMemoryIncrease).toBeLessThan(150 * 1024 * 1024); // Less than 150MB
    });

    test('should efficiently handle rapid-fire personality switches', async () => {
      const switchCount = 100;
      const startTime = performance.now();
      
      const results = [];
      for (let i = 0; i < switchCount; i++) {
        const tier = i % 3 === 0 ? 'onyx' : i % 3 === 1 ? 'obsidian' : 'void';
        
        const interaction = await personalities.createPersonalizedInteraction(
          `switch-test-${i}`,
          tier,
          {
            serviceCategory: ServiceCategory.ART_ACQUISITION,
            urgencyLevel: 'medium',
          }
        );
        
        results.push(interaction);
      }
      
      const endTime = performance.now();
      const totalTime = endTime - startTime;
      const averageTime = totalTime / switchCount;
      
      expect(averageTime).toBeLessThan(100); // Sub-100ms average
      expect(results).toHaveLength(switchCount);
      
      // Verify personality distribution
      const onyxCount = results.filter(r => r.personalityTier === AIPersonalityTier.STERLING).length;
      const obsidianCount = results.filter(r => r.personalityTier === AIPersonalityTier.PRISM).length;
      const voidCount = results.filter(r => r.personalityTier === AIPersonalityTier.NEXUS).length;
      
      expect(onyxCount + obsidianCount + voidCount).toBe(switchCount);
    });

    test('should maintain consistent performance under sustained load', async () => {
      const loadTestDuration = 5000; // 5 seconds
      const startTime = Date.now();
      const results = [];
      
      while (Date.now() - startTime < loadTestDuration) {
        const batchStart = performance.now();
        
        const batchResults = await Promise.all([
          personalities.createPersonalizedInteraction(
            `load-sterling-${Date.now()}`,
            'onyx',
            { serviceCategory: ServiceCategory.PRE_IPO_FUNDS, urgencyLevel: 'medium' }
          ),
          personalities.createPersonalizedInteraction(
            `load-prism-${Date.now()}`,
            'obsidian',
            { serviceCategory: ServiceCategory.ART_ACQUISITION, urgencyLevel: 'medium' }
          ),
          personalities.createPersonalizedInteraction(
            `load-nexus-${Date.now()}`,
            'void',
            { serviceCategory: ServiceCategory.MEDICAL_EVACUATION, urgencyLevel: 'critical' }
          ),
        ]);
        
        const batchEnd = performance.now();
        const batchTime = batchEnd - batchStart;
        
        results.push({
          batchResults,
          batchTime,
          timestamp: Date.now(),
        });
        
        // Batch should complete within reasonable time
        expect(batchTime).toBeLessThan(500); // Sub-500ms for 3 interactions
      }
      
      expect(results.length).toBeGreaterThan(5); // Should process multiple batches
      
      // Verify performance consistency (no significant degradation)
      const firstHalfAverage = results.slice(0, Math.floor(results.length / 2))
        .reduce((sum, r) => sum + r.batchTime, 0) / Math.floor(results.length / 2);
      
      const secondHalfAverage = results.slice(Math.floor(results.length / 2))
        .reduce((sum, r) => sum + r.batchTime, 0) / Math.ceil(results.length / 2);
      
      // Performance should not degrade by more than 50%
      expect(secondHalfAverage).toBeLessThan(firstHalfAverage * 1.5);
    });
  });

  describe('Recommendation Engine Performance', () => {
    test('should generate Sterling recommendations efficiently', async () => {
      const startTime = performance.now();
      
      const recommendations = await personalities.getPersonalityRecommendations(
        'rec-client-sterling',
        'onyx',
        {
          currentPortfolio: { equity: 0.6, bonds: 0.3, alternatives: 0.1 },
          riskTolerance: 'moderate',
          investmentHorizon: '5-10 years',
        }
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(200); // Sub-200ms for recommendations
      expect(recommendations.recommendations).toBeDefined();
      expect(recommendations.personalityInsights).toBeDefined();
    });

    test('should generate Prism recommendations with mystical complexity', async () => {
      const startTime = performance.now();
      
      const recommendations = await personalities.getPersonalityRecommendations(
        'rec-client-prism',
        'obsidian',
        {
          aestheticPreferences: ['contemporary', 'mystical'],
          culturalInterests: ['Eastern philosophy', 'Sacred geometry'],
          transcendenceLevel: 'advanced',
        }
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(300); // Sub-300ms for complex Prism analysis
      expect(recommendations.recommendations).toBeDefined();
      expect(recommendations.personalityInsights).toBeDefined();
    });

    test('should generate Nexus recommendations with quantum speed', async () => {
      const startTime = performance.now();
      
      const recommendations = await personalities.getPersonalityRecommendations(
        'rec-client-nexus',
        'void',
        {
          realityManipulation: 'unlimited',
          quantumStates: ['superposition', 'entanglement'],
          impossibilityThreshold: 'transcended',
        }
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(100); // Sub-100ms for Nexus quantum processing
      expect(recommendations.recommendations).toBeDefined();
      expect(recommendations.personalityInsights).toBeDefined();
    });

    test('should handle concurrent recommendation requests efficiently', async () => {
      const concurrentRequests = 20;
      const startTime = performance.now();
      
      const recommendations = await Promise.all(
        Array.from({ length: concurrentRequests }, (_, i) => {
          const tier = i % 3 === 0 ? 'onyx' : i % 3 === 1 ? 'obsidian' : 'void';
          return personalities.getPersonalityRecommendations(
            `concurrent-rec-${i}`,
            tier,
            { concurrentTest: true, index: i }
          );
        })
      );
      
      const endTime = performance.now();
      const totalTime = endTime - startTime;
      const averageTime = totalTime / concurrentRequests;
      
      expect(averageTime).toBeLessThan(250); // Average under 250ms
      expect(totalTime).toBeLessThan(5000); // Total under 5 seconds
      expect(recommendations).toHaveLength(concurrentRequests);
      
      // Verify all recommendations are valid
      recommendations.forEach(rec => {
        expect(rec.recommendations).toBeDefined();
        expect(rec.personalityInsights).toBeDefined();
      });
    });
  });

  describe('Anonymous Interface Performance', () => {
    test('should create anonymous Sterling interface efficiently', async () => {
      const startTime = performance.now();
      
      const interface_ = await personalities.createAnonymousPersonalityInterface(
        'onyx',
        ServiceCategory.PRE_IPO_FUNDS
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(150); // Sub-150ms for interface creation
      expect(interface_.personalityInterface).toBeDefined();
      expect(interface_.serviceOrchestration).toBeDefined();
      expect(interface_.personalityInterface.communicationStyle).toContain('professional');
    });

    test('should create anonymous Prism interface with mystical processing', async () => {
      const startTime = performance.now();
      
      const interface_ = await personalities.createAnonymousPersonalityInterface(
        'obsidian',
        ServiceCategory.ART_ACQUISITION
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(200); // Sub-200ms for Prism complexity
      expect(interface_.personalityInterface).toBeDefined();
      expect(interface_.serviceOrchestration).toBeDefined();
      expect(interface_.personalityInterface.communicationStyle).toContain('mystical');
    });

    test('should create anonymous Nexus interface with quantum speed', async () => {
      const startTime = performance.now();
      
      const interface_ = await personalities.createAnonymousPersonalityInterface(
        'void',
        ServiceCategory.MEDICAL_EVACUATION
      );
      
      const endTime = performance.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(80); // Sub-80ms for Nexus quantum processing
      expect(interface_.personalityInterface).toBeDefined();
      expect(interface_.serviceOrchestration).toBeDefined();
      expect(interface_.serviceOrchestration.orchestrationLevel).toBe('transcendent');
    });

    test('should handle rapid anonymous interface creation efficiently', async () => {
      const rapidCreation = 30;
      const startTime = performance.now();
      
      const interfaces = await Promise.all(
        Array.from({ length: rapidCreation }, (_, i) => {
          const tier = i % 3 === 0 ? 'onyx' : i % 3 === 1 ? 'obsidian' : 'void';
          const category = Object.values(ServiceCategory)[i % Object.values(ServiceCategory).length];
          
          return personalities.createAnonymousPersonalityInterface(tier, category);
        })
      );
      
      const endTime = performance.now();
      const totalTime = endTime - startTime;
      const averageTime = totalTime / rapidCreation;
      
      expect(averageTime).toBeLessThan(180); // Average under 180ms
      expect(totalTime).toBeLessThan(5000); // Total under 5 seconds
      expect(interfaces).toHaveLength(rapidCreation);
      
      // Verify interface quality
      interfaces.forEach(interface_ => {
        expect(interface_.personalityInterface).toBeDefined();
        expect(interface_.serviceOrchestration).toBeDefined();
        expect(interface_.personalityInterface.communicationStyle).toBeDefined();
      });
    });
  });

  describe('Scalability and Stress Testing', () => {
    test('should maintain performance under extreme concurrent load', async () => {
      const extremeLoad = 100;
      const startTime = performance.now();
      
      // Create massive concurrent load
      const promises = Array.from({ length: extremeLoad }, (_, i) => {
        const operations = [
          personalities.createPersonalizedInteraction(
            `stress-${i}`,
            i % 3 === 0 ? 'onyx' : i % 3 === 1 ? 'obsidian' : 'void',
            {
              serviceCategory: ServiceCategory.PRE_IPO_FUNDS,
              urgencyLevel: 'high',
            }
          ),
          personalities.getPersonalityRecommendations(
            `stress-rec-${i}`,
            i % 3 === 0 ? 'onyx' : i % 3 === 1 ? 'obsidian' : 'void',
            { stressTest: true }
          ),
          personalities.createAnonymousPersonalityInterface(
            i % 3 === 0 ? 'onyx' : i % 3 === 1 ? 'obsidian' : 'void',
            ServiceCategory.ART_ACQUISITION
          ),
        ];
        
        return Promise.all(operations);
      });
      
      const results = await Promise.all(promises);
      
      const endTime = performance.now();
      const totalTime = endTime - startTime;
      
      expect(totalTime).toBeLessThan(15000); // Under 15 seconds for extreme load
      expect(results).toHaveLength(extremeLoad);
      
      // Verify all operations completed successfully
      results.forEach(operationSet => {
        expect(operationSet).toHaveLength(3);
        operationSet.forEach(result => {
          expect(result).toBeDefined();
        });
      });
    });

    test('should handle memory pressure gracefully', async () => {
      const memoryPressure = 500;
      const initialMemory = process.memoryUsage();
      
      // Create memory pressure
      const largeDataSets = [];
      for (let i = 0; i < memoryPressure; i++) {
        const interaction = await personalities.createPersonalizedInteraction(
          `memory-pressure-${i}`,
          'void', // Use most complex tier
          {
            serviceCategory: ServiceCategory.FAMILY_OFFICE_SERVICES,
            urgencyLevel: 'critical',
            portfolioContext: {
              // Large context object to increase memory usage
              holdings: Array.from({ length: 100 }, (_, j) => ({
                asset: `asset-${j}`,
                value: Math.random() * 1000000,
                metadata: Array.from({ length: 10 }, (_, k) => `data-${k}`),
              })),
            },
          }
        );
        
        largeDataSets.push(interaction);
        
        // Check memory usage periodically
        if (i % 100 === 0) {
          const currentMemory = process.memoryUsage();
          const memoryIncrease = currentMemory.heapUsed - initialMemory.heapUsed;
          
          // Should not exceed reasonable memory limits
          expect(memoryIncrease).toBeLessThan(500 * 1024 * 1024); // 500MB limit
        }
      }
      
      expect(largeDataSets).toHaveLength(memoryPressure);
      
      const finalMemory = process.memoryUsage();
      const totalMemoryIncrease = finalMemory.heapUsed - initialMemory.heapUsed;
      
      // Final memory usage should be reasonable
      expect(totalMemoryIncrease).toBeLessThan(800 * 1024 * 1024); // 800MB final limit
    });

    test('should maintain response time consistency under varied load patterns', async () => {
      const loadPatterns = [
        { requests: 10, tier: 'onyx', delay: 0 },
        { requests: 20, tier: 'obsidian', delay: 100 },
        { requests: 5, tier: 'void', delay: 50 },
        { requests: 15, tier: 'onyx', delay: 200 },
        { requests: 25, tier: 'obsidian', delay: 0 },
      ];
      
      const allResults = [];
      
      for (const pattern of loadPatterns) {
        await new Promise(resolve => setTimeout(resolve, pattern.delay));
        
        const patternStart = performance.now();
        const patternResults = await Promise.all(
          Array.from({ length: pattern.requests }, (_, i) =>
            personalities.createPersonalizedInteraction(
              `pattern-${pattern.tier}-${i}`,
              pattern.tier,
              {
                serviceCategory: ServiceCategory.PRE_IPO_FUNDS,
                urgencyLevel: 'medium',
              }
            )
          )
        );
        const patternEnd = performance.now();
        
        const averageTime = (patternEnd - patternStart) / pattern.requests;
        
        allResults.push({
          tier: pattern.tier,
          averageTime,
          results: patternResults,
        });
        
        // Each pattern should maintain reasonable performance
        expect(averageTime).toBeLessThan(300); // Sub-300ms average
      }
      
      // Verify overall consistency
      const totalAverageTime = allResults.reduce((sum, r) => sum + r.averageTime, 0) / allResults.length;
      expect(totalAverageTime).toBeLessThan(250); // Overall average under 250ms
    });
  });
});