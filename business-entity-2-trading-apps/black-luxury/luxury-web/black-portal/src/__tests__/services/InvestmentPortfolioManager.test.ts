/**
 * Investment Portfolio Manager Test Suite
 * Comprehensive testing for portfolio management system including
 * real-time tracking, performance analytics, and anonymous holdings management
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { 
  InvestmentPortfolioManager, 
  AssetClass, 
  PortfolioStrategy,
  InvestmentTier 
} from '../../services/InvestmentPortfolioManager';

// Mock EventEmitter
jest.mock('events');

describe('InvestmentPortfolioManager', () => {
  let portfolioManager: InvestmentPortfolioManager;

  beforeEach(() => {
    portfolioManager = new InvestmentPortfolioManager();
  });

  describe('Portfolio Creation and Configuration', () => {
    test('should create client portfolio with correct configuration', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'test-client-id',
        'test-anonymous-id',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.AGGRESSIVE,
          riskTolerance: 'aggressive',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      expect(portfolio.id).toMatch(/^portfolio-/);
      expect(portfolio.clientId).toBe('test-client-id');
      expect(portfolio.anonymousId).toBe('test-anonymous-id');
      expect(portfolio.tier).toBe(InvestmentTier.OBSIDIAN);
      expect(portfolio.configuration.strategy).toBe(PortfolioStrategy.AGGRESSIVE);
      expect(portfolio.configuration.riskTolerance).toBe('aggressive');
      expect(portfolio.configuration.liquidityNeeds).toBe(0.1);
      expect(portfolio.holdings).toHaveLength(0);
    });

    test('should set appropriate default allocations based on strategy', async () => {
      const aggressivePortfolio = await portfolioManager.createClientPortfolio(
        'aggressive-client',
        'aggressive-anonymous',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.AGGRESSIVE,
          riskTolerance: 'extreme',
          timeHorizon: '15+ years',
          liquidityNeeds: 0.05,
        }
      );

      const conservativePortfolio = await portfolioManager.createClientPortfolio(
        'conservative-client',
        'conservative-anonymous',
        InvestmentTier.ONYX,
        {
          strategy: PortfolioStrategy.CONSERVATIVE,
          riskTolerance: 'conservative',
          timeHorizon: '3-5 years',
          liquidityNeeds: 0.3,
        }
      );

      expect(aggressivePortfolio.targetAllocation[AssetClass.EQUITY]).toBeGreaterThan(
        conservativePortfolio.targetAllocation[AssetClass.EQUITY]
      );
      expect(conservativePortfolio.targetAllocation[AssetClass.FIXED_INCOME]).toBeGreaterThan(
        aggressivePortfolio.targetAllocation[AssetClass.FIXED_INCOME]
      );
    });

    test('should validate tier-specific investment access', async () => {
      const voidPortfolio = await portfolioManager.createClientPortfolio(
        'void-client',
        'void-anonymous',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.ALTERNATIVE_HEAVY,
          riskTolerance: 'extreme',
          timeHorizon: '20+ years',
          liquidityNeeds: 0.02,
        }
      );

      const onyxPortfolio = await portfolioManager.createClientPortfolio(
        'onyx-client',
        'onyx-anonymous',
        InvestmentTier.ONYX,
        {
          strategy: PortfolioStrategy.BALANCED,
          riskTolerance: 'moderate',
          timeHorizon: '5-10 years',
          liquidityNeeds: 0.15,
        }
      );

      // Void tier should have access to more alternative investments
      expect(voidPortfolio.tierBenefits.privateEquityAccess).toBe(true);
      expect(voidPortfolio.tierBenefits.hedgeFundAccess).toBe(true);
      expect(voidPortfolio.tierBenefits.artInvestmentAccess).toBe(true);

      // Onyx tier should have limited alternative access
      expect(onyxPortfolio.tierBenefits.artInvestmentAccess).toBe(false);
    });
  });

  describe('Portfolio Holdings Management', () => {
    test('should add holding to portfolio with correct calculations', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'holding-test-client',
        'holding-test-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.GROWTH,
          riskTolerance: 'aggressive',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      const holding = await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'SpaceX Series X',
          symbol: 'SPACEX',
          assetClass: AssetClass.EQUITY,
          category: 'PRE_IPO',
          type: 'private',
        },
        position: {
          quantity: 1000,
          unitCost: 500000,
          currentPrice: 650000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      expect(holding.id).toMatch(/^holding-/);
      expect(holding.portfolioId).toBe(portfolio.id);
      expect(holding.position.totalValue).toBe(650000000); // 1000 * 650000
      expect(holding.performance.unrealizedGain).toBe(150000000); // (650000 - 500000) * 1000
      expect(holding.performance.totalReturn).toBe(0.30); // 30% gain
      expect(holding.riskMetrics.var95).toBeDefined();
    });

    test('should calculate portfolio allocation percentages correctly', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'allocation-test-client',
        'allocation-test-anonymous',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.BALANCED,
          riskTolerance: 'moderate',
          timeHorizon: '10 years',
          liquidityNeeds: 0.1,
        }
      );

      // Add multiple holdings
      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'SpaceX Equity',
          assetClass: AssetClass.EQUITY,
          category: 'PRE_IPO',
          type: 'private',
        },
        position: {
          quantity: 1000,
          unitCost: 500000,
          currentPrice: 650000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Dubai Real Estate',
          assetClass: AssetClass.REAL_ESTATE,
          category: 'LUXURY_REAL_ESTATE',
          type: 'alternative',
        },
        position: {
          quantity: 1,
          unitCost: 400000000,
          currentPrice: 480000000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      const updatedPortfolio = await portfolioManager.getPortfolio(portfolio.id);
      const totalValue = updatedPortfolio!.performance.totalValue;

      expect(updatedPortfolio!.allocation[AssetClass.EQUITY]).toBeCloseTo(
        (650000000 / totalValue) * 100, 1
      );
      expect(updatedPortfolio!.allocation[AssetClass.REAL_ESTATE]).toBeCloseTo(
        (480000000 / totalValue) * 100, 1
      );
    });

    test('should update holding prices and recalculate performance', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'update-test-client',
        'update-test-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.GROWTH,
          riskTolerance: 'aggressive',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      const holding = await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Test Asset',
          assetClass: AssetClass.EQUITY,
          category: 'PUBLIC_EQUITY',
          type: 'public',
        },
        position: {
          quantity: 100,
          unitCost: 1000000,
          currentPrice: 1000000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      // Update price
      const updatedHolding = await portfolioManager.updateHoldingPrice(
        holding.id, 
        1200000 // 20% increase
      );

      expect(updatedHolding.position.currentPrice).toBe(1200000);
      expect(updatedHolding.position.totalValue).toBe(120000000);
      expect(updatedHolding.performance.unrealizedGain).toBe(20000000);
      expect(updatedHolding.performance.totalReturn).toBe(0.20);
    });
  });

  describe('Performance Analytics', () => {
    test('should calculate portfolio performance metrics accurately', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'performance-test-client',
        'performance-test-anonymous',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.AGGRESSIVE,
          riskTolerance: 'extreme',
          timeHorizon: '15+ years',
          liquidityNeeds: 0.05,
        }
      );

      // Add profitable holding
      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'High Performer',
          assetClass: AssetClass.EQUITY,
          category: 'PRE_IPO',
          type: 'private',
        },
        position: {
          quantity: 1000,
          unitCost: 100000,
          currentPrice: 150000, // 50% gain
          currency: 'INR',
        },
        acquisitionDate: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 year ago
      });

      // Add losing holding
      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Underperformer',
          assetClass: AssetClass.ALTERNATIVES,
          category: 'HEDGE_FUND',
          type: 'alternative',
        },
        position: {
          quantity: 500,
          unitCost: 200000,
          currentPrice: 180000, // 10% loss
          currency: 'INR',
        },
        acquisitionDate: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(), // 6 months ago
      });

      const analytics = await portfolioManager.calculatePerformanceAnalytics(portfolio.id);

      expect(analytics.totalReturn).toBeGreaterThan(0); // Overall positive return
      expect(analytics.bestPerformer.name).toBe('High Performer');
      expect(analytics.worstPerformer.name).toBe('Underperformer');
      expect(analytics.sharpeRatio).toBeDefined();
      expect(analytics.volatility).toBeGreaterThan(0);
    });

    test('should calculate risk metrics including VaR and beta', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'risk-test-client',
        'risk-test-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.AGGRESSIVE,
          riskTolerance: 'aggressive',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'High Beta Stock',
          assetClass: AssetClass.EQUITY,
          category: 'PUBLIC_EQUITY',
          type: 'public',
        },
        position: {
          quantity: 100,
          unitCost: 1000000,
          currentPrice: 1100000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      const riskMetrics = await portfolioManager.calculateRiskMetrics(portfolio.id);

      expect(riskMetrics.portfolioBeta).toBeGreaterThan(0);
      expect(riskMetrics.var95).toBeLessThan(0); // VaR should be negative
      expect(riskMetrics.volatility).toBeGreaterThan(0);
      expect(riskMetrics.maxDrawdown).toBeLessThanOrEqual(0);
      expect(riskMetrics.correlationMatrix).toBeDefined();
    });

    test('should generate rebalancing recommendations', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'rebalance-test-client',
        'rebalance-test-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.BALANCED,
          riskTolerance: 'moderate',
          timeHorizon: '10 years',
          liquidityNeeds: 0.15,
        }
      );

      // Add holdings that create imbalance
      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Overweight Equity',
          assetClass: AssetClass.EQUITY,
          category: 'PUBLIC_EQUITY',
          type: 'public',
        },
        position: {
          quantity: 1000,
          unitCost: 800000,
          currentPrice: 1200000, // Large gain causing overweight
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      const recommendations = await portfolioManager.getRebalancingRecommendations(portfolio.id);

      expect(recommendations.required).toBe(true);
      expect(recommendations.suggestions.length).toBeGreaterThan(0);
      
      const equityRecommendation = recommendations.suggestions.find(s => s.assetClass === AssetClass.EQUITY);
      expect(equityRecommendation?.action).toBe('reduce'); // Should recommend reducing overweight equity
    });
  });

  describe('ESG and Impact Investing', () => {
    test('should track ESG scores and impact metrics', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'esg-test-client',
        'esg-test-anonymous',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.ESG_FOCUSED,
          riskTolerance: 'moderate',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'African Lithium ESG Fund',
          assetClass: AssetClass.ALTERNATIVES,
          category: 'ESG_INVESTMENT',
          type: 'alternative',
        },
        position: {
          quantity: 1000,
          unitCost: 200000,
          currentPrice: 240000,
          currency: 'INR',
        },
        esgData: {
          esgScore: 95,
          environmentalScore: 98,
          socialScore: 92,
          governanceScore: 95,
          impactMetrics: ['Carbon reduction: 50%', 'Local jobs: 10,000'],
        },
        acquisitionDate: new Date().toISOString(),
      });

      const esgMetrics = await portfolioManager.calculateESGMetrics(portfolio.id);

      expect(esgMetrics.portfolioESGScore).toBeGreaterThan(90);
      expect(esgMetrics.impactMetrics).toContain('Carbon reduction: 50%');
      expect(esgMetrics.esgAllocation).toBeGreaterThan(0);
      expect(esgMetrics.sustainabilityGoals.length).toBeGreaterThan(0);
    });

    test('should recommend ESG improvements', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'esg-improve-client',
        'esg-improve-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.ESG_FOCUSED,
          riskTolerance: 'moderate',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      // Add non-ESG holding
      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Traditional Energy Stock',
          assetClass: AssetClass.EQUITY,
          category: 'PUBLIC_EQUITY',
          type: 'public',
        },
        position: {
          quantity: 100,
          unitCost: 1000000,
          currentPrice: 1100000,
          currency: 'INR',
        },
        esgData: {
          esgScore: 25, // Low ESG score
          environmentalScore: 15,
          socialScore: 30,
          governanceScore: 30,
          impactMetrics: [],
        },
        acquisitionDate: new Date().toISOString(),
      });

      const recommendations = await portfolioManager.getESGRecommendations(portfolio.id);

      expect(recommendations.improvementOpportunities.length).toBeGreaterThan(0);
      expect(recommendations.suggestedReplacements.length).toBeGreaterThan(0);
      expect(recommendations.targetESGScore).toBeGreaterThan(80);
    });
  });

  describe('Liquidity Management', () => {
    test('should assess portfolio liquidity and provide recommendations', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'liquidity-test-client',
        'liquidity-test-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.BALANCED,
          riskTolerance: 'moderate',
          timeHorizon: '7 years',
          liquidityNeeds: 0.25, // High liquidity needs
        }
      );

      // Add illiquid holding
      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Private Real Estate Fund',
          assetClass: AssetClass.REAL_ESTATE,
          category: 'PRIVATE_REAL_ESTATE',
          type: 'alternative',
        },
        position: {
          quantity: 1,
          unitCost: 500000000,
          currentPrice: 550000000,
          currency: 'INR',
        },
        liquidity: {
          liquidityScore: 2, // Very illiquid
          estimatedLiquidationTime: '12-18 months',
          restrictions: ['Lock-up period', 'Notice required'],
        },
        acquisitionDate: new Date().toISOString(),
      });

      const liquidityAnalysis = await portfolioManager.analyzeLiquidity(portfolio.id);

      expect(liquidityAnalysis.liquidityScore).toBeLessThan(5); // Poor liquidity
      expect(liquidityAnalysis.illiquidAllocation).toBeGreaterThan(80); // High illiquid allocation
      expect(liquidityAnalysis.recommendations.length).toBeGreaterThan(0);
      expect(liquidityAnalysis.recommendations[0]).toContain('increase liquid'); // Should recommend more liquid assets
    });

    test('should handle liquidity stress testing', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'stress-test-client',
        'stress-test-anonymous',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.AGGRESSIVE,
          riskTolerance: 'extreme',
          timeHorizon: '15+ years',
          liquidityNeeds: 0.1,
        }
      );

      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Stress Test Asset',
          assetClass: AssetClass.EQUITY,
          category: 'PRE_IPO',
          type: 'private',
        },
        position: {
          quantity: 1000,
          unitCost: 300000,
          currentPrice: 400000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      const stressTest = await portfolioManager.runLiquidityStressTest(portfolio.id, {
        marketCrashScenario: true,
        immediateNeedScenario: true,
        timeHorizon: '30 days',
      });

      expect(stressTest.liquidityUnderStress).toBeDefined();
      expect(stressTest.emergencyLiquidationValue).toBeLessThan(
        stressTest.normalLiquidationValue
      );
      expect(stressTest.recommendations.length).toBeGreaterThan(0);
    });
  });

  describe('Anonymous Holdings and Privacy', () => {
    test('should maintain anonymity while tracking performance', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'anonymous-test-client',
        'anonymous-test-id',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.ALTERNATIVE_HEAVY,
          riskTolerance: 'extreme',
          timeHorizon: '20+ years',
          liquidityNeeds: 0.05,
        }
      );

      const holding = await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Anonymous SPV Investment',
          assetClass: AssetClass.ALTERNATIVES,
          category: 'PRIVATE_EQUITY',
          type: 'private',
        },
        position: {
          quantity: 1,
          unitCost: 1000000000,
          currentPrice: 1300000000,
          currency: 'INR',
        },
        anonymityFeatures: {
          spvStructure: true,
          nomineeOwnership: true,
          encryptedRecords: true,
          jurisdictionalMasking: ['Mauritius', 'Singapore'],
        },
        acquisitionDate: new Date().toISOString(),
      });

      expect(holding.anonymityFeatures?.spvStructure).toBe(true);
      expect(holding.anonymityFeatures?.jurisdictionalMasking).toContain('Mauritius');
      
      // Performance tracking should work despite anonymity
      expect(holding.performance.totalReturn).toBe(0.30);
      expect(holding.performance.unrealizedGain).toBe(300000000);
    });

    test('should generate anonymous performance reports', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'report-test-client',
        'report-anonymous-id',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.GROWTH,
          riskTolerance: 'aggressive',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Anonymous Holding',
          assetClass: AssetClass.EQUITY,
          category: 'PRE_IPO',
          type: 'private',
        },
        position: {
          quantity: 500,
          unitCost: 400000,
          currentPrice: 520000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      const report = await portfolioManager.generateAnonymousReport(portfolio.id, {
        includeHoldings: true,
        includePerformance: true,
        includeBenchmarks: true,
        maskSensitiveData: true,
      });

      expect(report.portfolioId).toBe(portfolio.id);
      expect(report.anonymousId).toBe('report-anonymous-id');
      expect(report.clientId).toBeUndefined(); // Should be masked
      expect(report.performance.totalReturn).toBeDefined();
      expect(report.holdings.length).toBeGreaterThan(0);
      expect(report.holdings[0].assetDetails.name).toMatch(/Anonymous/); // Names should be masked
    });
  });

  describe('Tax Optimization and Reporting', () => {
    test('should calculate tax-optimized rebalancing suggestions', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'tax-opt-client',
        'tax-opt-anonymous',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.BALANCED,
          riskTolerance: 'moderate',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.15,
        }
      );

      // Add holding with gains
      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Profitable Investment',
          assetClass: AssetClass.EQUITY,
          category: 'PUBLIC_EQUITY',
          type: 'public',
        },
        position: {
          quantity: 100,
          unitCost: 500000,
          currentPrice: 800000, // 60% gain
          currency: 'INR',
        },
        acquisitionDate: new Date(Date.now() - 400 * 24 * 60 * 60 * 1000).toISOString(), // Over 1 year (LTCG eligible)
      });

      const taxOptimization = await portfolioManager.getTaxOptimizedRecommendations(portfolio.id);

      expect(taxOptimization.capitalGainsOptimization).toBeDefined();
      expect(taxOptimization.ltcgOpportunities.length).toBeGreaterThan(0);
      expect(taxOptimization.taxLossHarvesting).toBeDefined();
      expect(taxOptimization.recommendedTiming.length).toBeGreaterThan(0);
    });

    test('should generate tax reports for regulatory compliance', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'tax-report-client',
        'tax-report-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.GROWTH,
          riskTolerance: 'aggressive',
          timeHorizon: '8 years',
          liquidityNeeds: 0.12,
        }
      );

      const taxReport = await portfolioManager.generateTaxReport(portfolio.id, {
        financialYear: '2024-25',
        includeUnrealizedGains: true,
        includeRealizedGains: true,
        includeForeignAssets: true,
      });

      expect(taxReport.financialYear).toBe('2024-25');
      expect(taxReport.totalRealizedGains).toBeDefined();
      expect(taxReport.totalUnrealizedGains).toBeDefined();
      expect(taxReport.ltcgLiability).toBeDefined();
      expect(taxReport.stcgLiability).toBeDefined();
      expect(taxReport.foreignAssetDisclosure).toBeDefined();
    });
  });

  describe('Real-time Updates and Monitoring', () => {
    test('should handle real-time price updates', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'realtime-client',
        'realtime-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.GROWTH,
          riskTolerance: 'aggressive',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      const holding = await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Real-time Asset',
          assetClass: AssetClass.EQUITY,
          category: 'PUBLIC_EQUITY',
          type: 'public',
        },
        position: {
          quantity: 100,
          unitCost: 1000000,
          currentPrice: 1000000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      // Simulate real-time price update
      await portfolioManager.updateRealTimePrice(holding.id, 1150000);

      const updatedHolding = await portfolioManager.getHolding(holding.id);
      const updatedPortfolio = await portfolioManager.getPortfolio(portfolio.id);

      expect(updatedHolding!.position.currentPrice).toBe(1150000);
      expect(updatedHolding!.performance.unrealizedGain).toBe(15000000);
      expect(updatedPortfolio!.performance.totalValue).toBeGreaterThan(100000000);
    });

    test('should emit events for portfolio changes', async () => {
      const emitSpy = jest.spyOn(portfolioManager, 'emit');

      const portfolio = await portfolioManager.createClientPortfolio(
        'event-client',
        'event-anonymous',
        InvestmentTier.VOID,
        {
          strategy: PortfolioStrategy.AGGRESSIVE,
          riskTolerance: 'extreme',
          timeHorizon: '15+ years',
          liquidityNeeds: 0.05,
        }
      );

      expect(emitSpy).toHaveBeenCalledWith('portfolio:created', expect.objectContaining({
        portfolioId: portfolio.id,
        tier: InvestmentTier.VOID,
      }));

      await portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: 'Event Test Asset',
          assetClass: AssetClass.EQUITY,
          category: 'PRE_IPO',
          type: 'private',
        },
        position: {
          quantity: 100,
          unitCost: 500000,
          currentPrice: 600000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      });

      expect(emitSpy).toHaveBeenCalledWith('holding:added', expect.objectContaining({
        portfolioId: portfolio.id,
        assetClass: AssetClass.EQUITY,
      }));
    });
  });

  describe('Error Handling and Edge Cases', () => {
    test('should handle invalid portfolio operations gracefully', async () => {
      await expect(portfolioManager.getPortfolio('invalid-portfolio-id'))
        .resolves.toBeNull();

      await expect(portfolioManager.addHolding('invalid-portfolio-id', {} as any))
        .rejects.toThrow('Portfolio not found');
    });

    test('should validate holding data before adding', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'validation-client',
        'validation-anonymous',
        InvestmentTier.ONYX,
        {
          strategy: PortfolioStrategy.BALANCED,
          riskTolerance: 'moderate',
          timeHorizon: '7 years',
          liquidityNeeds: 0.2,
        }
      );

      // Invalid holding without required fields
      await expect(portfolioManager.addHolding(portfolio.id, {
        assetDetails: {
          name: '',
          assetClass: AssetClass.EQUITY,
          category: 'TEST',
          type: 'public',
        },
        position: {
          quantity: -100, // Invalid negative quantity
          unitCost: 0, // Invalid zero cost
          currentPrice: 1000000,
          currency: 'INR',
        },
        acquisitionDate: new Date().toISOString(),
      })).rejects.toThrow();
    });

    test('should handle concurrent portfolio operations', async () => {
      const portfolio = await portfolioManager.createClientPortfolio(
        'concurrent-client',
        'concurrent-anonymous',
        InvestmentTier.OBSIDIAN,
        {
          strategy: PortfolioStrategy.GROWTH,
          riskTolerance: 'aggressive',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1,
        }
      );

      // Add multiple holdings concurrently
      const promises = Array.from({ length: 5 }, (_, i) =>
        portfolioManager.addHolding(portfolio.id, {
          assetDetails: {
            name: `Concurrent Asset ${i + 1}`,
            assetClass: AssetClass.EQUITY,
            category: 'PUBLIC_EQUITY',
            type: 'public',
          },
          position: {
            quantity: 100,
            unitCost: 1000000,
            currentPrice: 1100000,
            currency: 'INR',
          },
          acquisitionDate: new Date().toISOString(),
        })
      );

      const holdings = await Promise.all(promises);
      expect(holdings).toHaveLength(5);

      const updatedPortfolio = await portfolioManager.getPortfolio(portfolio.id);
      expect(updatedPortfolio!.holdings.length).toBe(5);
    });
  });
});