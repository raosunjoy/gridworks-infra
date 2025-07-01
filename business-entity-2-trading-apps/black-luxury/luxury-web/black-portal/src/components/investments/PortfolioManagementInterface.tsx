/**
 * Portfolio Management Interface
 * Comprehensive portfolio management system with real-time tracking,
 * performance analytics, and anonymous investment oversight
 */

import React, { useState, useEffect } from 'react';
import { InvestmentTier, PortfolioStrategy, AssetClass } from '../../services/InvestmentPortfolioManager';
import { LuxuryCard } from '../ui/LuxuryCard';
import { TierGlow } from '../ui/TierGlow';

interface ClientPortfolio {
  id: string;
  clientId: string;
  anonymousId: string;
  tier: InvestmentTier;
  configuration: {
    strategy: PortfolioStrategy;
    riskTolerance: 'conservative' | 'moderate' | 'aggressive' | 'extreme';
    timeHorizon: string;
    liquidityNeeds: number;
  };
  holdings: PortfolioHolding[];
  performance: {
    totalValue: number;
    totalCost: number;
    unrealizedGains: number;
    realizedGains: number;
    totalReturn: number;
    annualizedReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
  };
  allocation: Record<AssetClass, number>;
  riskMetrics: {
    portfolioBeta: number;
    var95: number;
    volatility: number;
    correlationMatrix: Record<string, number>;
  };
  rebalancingRecommendations: {
    required: boolean;
    suggestions: Array<{
      action: 'buy' | 'sell' | 'rebalance';
      asset: string;
      amount: number;
      reason: string;
    }>;
  };
  createdAt: string;
  updatedAt: string;
}

interface PortfolioHolding {
  id: string;
  assetDetails: {
    name: string;
    symbol?: string;
    assetClass: AssetClass;
    type: 'public' | 'private' | 'alternative';
  };
  position: {
    quantity: number;
    unitCost: number;
    currentPrice: number;
    totalValue: number;
    currency: string;
  };
  performance: {
    unrealizedGain: number;
    totalReturn: number;
    annualizedReturn: number;
  };
  allocation: number; // Percentage of total portfolio
}

interface PortfolioManagementInterfaceProps {
  tier: InvestmentTier;
  anonymousId: string;
}

export const PortfolioManagementInterface: React.FC<PortfolioManagementInterfaceProps> = ({
  tier,
  anonymousId,
}) => {
  const [portfolio, setPortfolio] = useState<ClientPortfolio | null>(null);
  const [selectedView, setSelectedView] = useState<'overview' | 'holdings' | 'performance' | 'analytics'>('overview');
  const [timeRange, setTimeRange] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('1Y');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadPortfolioData();
  }, [anonymousId, tier]);

  const loadPortfolioData = async () => {
    try {
      setIsLoading(true);
      // In real implementation, this would call the InvestmentPortfolioManager
      const mockPortfolio: ClientPortfolio = {
        id: `portfolio-${anonymousId}`,
        clientId: 'anonymous-client',
        anonymousId,
        tier,
        configuration: {
          strategy: PortfolioStrategy.AGGRESSIVE,
          riskTolerance: 'aggressive',
          timeHorizon: '10+ years',
          liquidityNeeds: 0.1, // 10%
        },
        holdings: [
          {
            id: 'holding-spacex',
            assetDetails: {
              name: 'SpaceX Series X',
              symbol: 'SPACEX',
              assetClass: AssetClass.EQUITY,
              type: 'private',
            },
            position: {
              quantity: 1000,
              unitCost: 500000,
              currentPrice: 650000,
              totalValue: 650000000,
              currency: 'INR',
            },
            performance: {
              unrealizedGain: 150000000,
              totalReturn: 0.30,
              annualizedReturn: 0.25,
            },
            allocation: 32.5,
          },
          {
            id: 'holding-dubai-real-estate',
            assetDetails: {
              name: 'Dubai Marina Penthouse',
              assetClass: AssetClass.REAL_ESTATE,
              type: 'alternative',
            },
            position: {
              quantity: 1,
              unitCost: 400000000,
              currentPrice: 480000000,
              totalValue: 480000000,
              currency: 'INR',
            },
            performance: {
              unrealizedGain: 80000000,
              totalReturn: 0.20,
              annualizedReturn: 0.18,
            },
            allocation: 24.0,
          },
          {
            id: 'holding-esg-fund',
            assetDetails: {
              name: 'African Lithium ESG Fund',
              assetClass: AssetClass.ALTERNATIVES,
              type: 'alternative',
            },
            position: {
              quantity: 5000,
              unitCost: 40000,
              currentPrice: 52000,
              totalValue: 260000000,
              currency: 'INR',
            },
            performance: {
              unrealizedGain: 60000000,
              totalReturn: 0.30,
              annualizedReturn: 0.28,
            },
            allocation: 13.0,
          },
          {
            id: 'holding-art-collection',
            assetDetails: {
              name: 'Contemporary Art Collection',
              assetClass: AssetClass.ART_COLLECTIBLES,
              type: 'alternative',
            },
            position: {
              quantity: 12,
              unitCost: 15000000,
              currentPrice: 22000000,
              totalValue: 264000000,
              currency: 'INR',
            },
            performance: {
              unrealizedGain: 84000000,
              totalReturn: 0.47,
              annualizedReturn: 0.35,
            },
            allocation: 13.2,
          },
          {
            id: 'holding-crypto',
            assetDetails: {
              name: 'Digital Assets Portfolio',
              assetClass: AssetClass.CRYPTOCURRENCY,
              type: 'alternative',
            },
            position: {
              quantity: 1,
              unitCost: 200000000,
              currentPrice: 290000000,
              totalValue: 290000000,
              currency: 'INR',
            },
            performance: {
              unrealizedGain: 90000000,
              totalReturn: 0.45,
              annualizedReturn: 0.38,
            },
            allocation: 14.5,
          },
          {
            id: 'holding-cash',
            assetDetails: {
              name: 'High-Yield Cash Reserves',
              assetClass: AssetClass.CASH,
              type: 'public',
            },
            position: {
              quantity: 1,
              unitCost: 56000000,
              currentPrice: 56000000,
              totalValue: 56000000,
              currency: 'INR',
            },
            performance: {
              unrealizedGain: 0,
              totalReturn: 0.08,
              annualizedReturn: 0.08,
            },
            allocation: 2.8,
          },
        ],
        performance: {
          totalValue: 2000000000, // ₹200 Cr
          totalCost: 1536000000, // ₹153.6 Cr
          unrealizedGains: 464000000, // ₹46.4 Cr
          realizedGains: 0,
          totalReturn: 0.302, // 30.2%
          annualizedReturn: 0.254, // 25.4%
          sharpeRatio: 1.85,
          maxDrawdown: -0.08, // -8%
        },
        allocation: {
          [AssetClass.EQUITY]: 32.5,
          [AssetClass.REAL_ESTATE]: 24.0,
          [AssetClass.ALTERNATIVES]: 13.0,
          [AssetClass.ART_COLLECTIBLES]: 13.2,
          [AssetClass.CRYPTOCURRENCY]: 14.5,
          [AssetClass.CASH]: 2.8,
          [AssetClass.FIXED_INCOME]: 0,
          [AssetClass.COMMODITIES]: 0,
        },
        riskMetrics: {
          portfolioBeta: 1.25,
          var95: -0.12, // -12%
          volatility: 0.18, // 18%
          correlationMatrix: {
            'equity': 1.0,
            'real_estate': 0.3,
            'alternatives': 0.4,
          },
        },
        rebalancingRecommendations: {
          required: true,
          suggestions: [
            {
              action: 'buy',
              asset: 'Fixed Income Securities',
              amount: 100000000,
              reason: 'Increase stability and reduce portfolio volatility',
            },
            {
              action: 'rebalance',
              asset: 'Cryptocurrency',
              amount: -50000000,
              reason: 'Overweight allocation exceeds target range',
            },
          ],
        },
        createdAt: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setPortfolio(mockPortfolio);
    } catch (error) {
      console.error('Failed to load portfolio data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    const crores = amount / 10000000;
    return `₹${crores.toLocaleString('en-IN', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} Cr`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getAssetClassColor = (assetClass: AssetClass) => {
    const colors = {
      [AssetClass.EQUITY]: 'text-blue-400',
      [AssetClass.REAL_ESTATE]: 'text-green-400',
      [AssetClass.ALTERNATIVES]: 'text-purple-400',
      [AssetClass.ART_COLLECTIBLES]: 'text-pink-400',
      [AssetClass.CRYPTOCURRENCY]: 'text-yellow-400',
      [AssetClass.CASH]: 'text-gray-400',
      [AssetClass.FIXED_INCOME]: 'text-indigo-400',
      [AssetClass.COMMODITIES]: 'text-orange-400',
    };
    return colors[assetClass] || 'text-gray-400';
  };

  const getTierGradient = (tier: InvestmentTier) => {
    switch (tier) {
      case InvestmentTier.ONYX: return 'from-slate-600 to-slate-900';
      case InvestmentTier.OBSIDIAN: return 'from-purple-600 to-purple-900';
      case InvestmentTier.VOID: return 'from-black to-gray-900';
      default: return 'from-gray-600 to-gray-900';
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Performance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <LuxuryCard className="p-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gold-400 mb-2">
              {formatCurrency(portfolio!.performance.totalValue)}
            </div>
            <div className="text-gray-400 text-sm">Total Portfolio Value</div>
            <div className="text-green-400 text-sm mt-1">
              +{formatCurrency(portfolio!.performance.unrealizedGains)} Unrealized
            </div>
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400 mb-2">
              {formatPercentage(portfolio!.performance.totalReturn)}
            </div>
            <div className="text-gray-400 text-sm">Total Return</div>
            <div className="text-gray-400 text-sm mt-1">
              {formatPercentage(portfolio!.performance.annualizedReturn)} Annualized
            </div>
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400 mb-2">
              {portfolio!.performance.sharpeRatio.toFixed(2)}
            </div>
            <div className="text-gray-400 text-sm">Sharpe Ratio</div>
            <div className="text-gray-400 text-sm mt-1">
              Risk-Adjusted Return
            </div>
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400 mb-2">
              {formatPercentage(Math.abs(portfolio!.performance.maxDrawdown))}
            </div>
            <div className="text-gray-400 text-sm">Max Drawdown</div>
            <div className="text-gray-400 text-sm mt-1">
              Worst Decline Period
            </div>
          </div>
        </LuxuryCard>
      </div>

      {/* Asset Allocation Chart */}
      <LuxuryCard className="p-6">
        <h3 className="text-xl font-bold mb-4">Asset Allocation</h3>
        <div className="space-y-4">
          {Object.entries(portfolio!.allocation)
            .filter(([, allocation]) => allocation > 0)
            .sort(([, a], [, b]) => b - a)
            .map(([assetClass, allocation]) => (
              <div key={assetClass} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${getAssetClassColor(assetClass as AssetClass).replace('text-', 'bg-')}`} />
                  <span className="text-gray-300">
                    {assetClass.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-32 bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getAssetClassColor(assetClass as AssetClass).replace('text-', 'bg-')}`}
                      style={{ width: `${allocation}%` }}
                    />
                  </div>
                  <span className="text-white font-medium min-w-[60px] text-right">
                    {allocation.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
        </div>
      </LuxuryCard>

      {/* Rebalancing Recommendations */}
      {portfolio!.rebalancingRecommendations.required && (
        <LuxuryCard className="p-6">
          <h3 className="text-xl font-bold mb-4 text-yellow-400">Rebalancing Recommendations</h3>
          <div className="space-y-3">
            {portfolio!.rebalancingRecommendations.suggestions.map((suggestion, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <div>
                  <div className="font-medium text-white">
                    {suggestion.action.toUpperCase()} {suggestion.asset}
                  </div>
                  <div className="text-gray-400 text-sm">{suggestion.reason}</div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-yellow-400">
                    {formatCurrency(Math.abs(suggestion.amount))}
                  </div>
                  <div className="text-gray-400 text-sm">
                    {suggestion.amount > 0 ? 'Add' : 'Reduce'}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button className="mt-4 w-full py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 text-black font-bold rounded-lg hover:from-yellow-400 hover:to-yellow-500 transition-all duration-300">
            Execute Rebalancing
          </button>
        </LuxuryCard>
      )}
    </div>
  );

  const renderHoldings = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold">Portfolio Holdings</h3>
        <button className="px-4 py-2 bg-gold-500/20 text-gold-400 rounded-lg hover:bg-gold-500/30 transition-colors">
          Add New Investment
        </button>
      </div>

      <div className="grid gap-4">
        {portfolio!.holdings.map((holding) => (
          <LuxuryCard key={holding.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h4 className="text-lg font-semibold text-white">{holding.assetDetails.name}</h4>
                  <span className={`px-2 py-1 text-xs rounded-full ${getAssetClassColor(holding.assetDetails.assetClass)} bg-current bg-opacity-20`}>
                    {holding.assetDetails.assetClass.replace('_', ' ')}
                  </span>
                  <span className="px-2 py-1 text-xs rounded-full bg-gray-600 text-gray-300">
                    {holding.assetDetails.type.toUpperCase()}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Current Value:</span>
                    <div className="text-white font-medium">{formatCurrency(holding.position.totalValue)}</div>
                  </div>
                  <div>
                    <span className="text-gray-400">Unrealized Gain:</span>
                    <div className={`font-medium ${holding.performance.unrealizedGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {holding.performance.unrealizedGain >= 0 ? '+' : ''}{formatCurrency(holding.performance.unrealizedGain)}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-400">Total Return:</span>
                    <div className={`font-medium ${holding.performance.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatPercentage(holding.performance.totalReturn)}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-400">Allocation:</span>
                    <div className="text-white font-medium">{holding.allocation.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button className="px-3 py-1 text-sm bg-blue-500/20 text-blue-400 rounded hover:bg-blue-500/30 transition-colors">
                  Details
                </button>
                <button className="px-3 py-1 text-sm bg-gold-500/20 text-gold-400 rounded hover:bg-gold-500/30 transition-colors">
                  Trade
                </button>
              </div>
            </div>
          </LuxuryCard>
        ))}
      </div>
    </div>
  );

  const renderPerformance = () => (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold">Performance Analytics</h3>
        <div className="flex space-x-2">
          {['1M', '3M', '6M', '1Y', 'ALL'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range as typeof timeRange)}
              className={`px-3 py-1 text-sm rounded ${
                timeRange === range
                  ? 'bg-gold-500 text-black'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              } transition-colors`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Performance Chart Placeholder */}
      <LuxuryCard className="p-6">
        <div className="h-80 bg-black/30 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="text-gray-400 mb-2">Performance Chart</div>
            <div className="text-sm text-gray-500">Interactive chart showing portfolio performance over time</div>
          </div>
        </div>
      </LuxuryCard>

      {/* Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <LuxuryCard className="p-6">
          <h4 className="font-semibold mb-4">Risk Metrics</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Portfolio Beta:</span>
              <span className="text-white">{portfolio!.riskMetrics.portfolioBeta.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Volatility:</span>
              <span className="text-white">{formatPercentage(portfolio!.riskMetrics.volatility)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">VaR (95%):</span>
              <span className="text-red-400">{formatPercentage(Math.abs(portfolio!.riskMetrics.var95))}</span>
            </div>
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <h4 className="font-semibold mb-4">Return Metrics</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Annualized Return:</span>
              <span className="text-green-400">{formatPercentage(portfolio!.performance.annualizedReturn)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Sharpe Ratio:</span>
              <span className="text-blue-400">{portfolio!.performance.sharpeRatio.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Max Drawdown:</span>
              <span className="text-purple-400">{formatPercentage(Math.abs(portfolio!.performance.maxDrawdown))}</span>
            </div>
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <h4 className="font-semibold mb-4">Portfolio Info</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Strategy:</span>
              <span className="text-white">{portfolio!.configuration.strategy.replace('_', ' ').toUpperCase()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Risk Tolerance:</span>
              <span className="text-white">{portfolio!.configuration.riskTolerance.toUpperCase()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Time Horizon:</span>
              <span className="text-white">{portfolio!.configuration.timeHorizon}</span>
            </div>
          </div>
        </LuxuryCard>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <TierGlow tier={tier}>
          <div className="animate-pulse text-xl">Loading portfolio data...</div>
        </TierGlow>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 text-lg mb-4">No portfolio data available</div>
        <button className="px-6 py-3 bg-gold-500/20 text-gold-400 rounded-lg hover:bg-gold-500/30 transition-colors">
          Create Portfolio
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gold-400 to-gold-600 bg-clip-text text-transparent">
          Portfolio Management
        </h1>
        <p className="text-lg text-gray-300">
          {tier.toUpperCase()} Tier • Anonymous ID: {anonymousId.slice(-8)}
        </p>
      </div>

      {/* Navigation */}
      <div className="flex justify-center">
        <nav className="flex space-x-1 bg-black/50 rounded-lg p-1">
          {[
            { key: 'overview', label: 'Overview' },
            { key: 'holdings', label: 'Holdings' },
            { key: 'performance', label: 'Performance' },
            { key: 'analytics', label: 'Analytics' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setSelectedView(tab.key as typeof selectedView)}
              className={`px-6 py-3 rounded-lg transition-all duration-200 ${
                selectedView === tab.key
                  ? 'bg-gold-500 text-black font-medium'
                  : 'text-gray-300 hover:text-white hover:bg-white/10'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div>
        {selectedView === 'overview' && renderOverview()}
        {selectedView === 'holdings' && renderHoldings()}
        {selectedView === 'performance' && renderPerformance()}
        {selectedView === 'analytics' && renderPerformance()} {/* Placeholder for analytics */}
      </div>
    </div>
  );
};