/**
 * Real-time Portfolio Analytics Dashboard
 * Advanced analytics dashboard with live data, risk metrics, performance tracking,
 * and sophisticated visualizations for Black-tier portfolio management
 */

import React, { useState, useEffect, useMemo } from 'react';
import { InvestmentTier } from '../../services/InvestmentSyndicateEngine';
import { AssetClass, PortfolioStrategy } from '../../services/InvestmentPortfolioManager';
import { LuxuryCard } from '../ui/LuxuryCard';
import { TierGlow } from '../ui/TierGlow';

// Mock chart components (in real implementation, use recharts or similar)
const LineChart = ({ children, ...props }: any) => (
  <div className="w-full h-64 bg-black/30 rounded-lg flex items-center justify-center" {...props}>
    <div className="text-gray-400">Live Performance Chart</div>
    {children}
  </div>
);

const PieChart = ({ children, ...props }: any) => (
  <div className="w-full h-48 bg-black/30 rounded-lg flex items-center justify-center" {...props}>
    <div className="text-gray-400">Asset Allocation</div>
    {children}
  </div>
);

const BarChart = ({ children, ...props }: any) => (
  <div className="w-full h-56 bg-black/30 rounded-lg flex items-center justify-center" {...props}>
    <div className="text-gray-400">Risk Analysis</div>
    {children}
  </div>
);

interface RealTimePortfolioAnalyticsProps {
  tier: InvestmentTier;
  anonymousId: string;
  portfolioId?: string;
}

interface LiveMetrics {
  totalValue: number;
  dayChange: number;
  dayChangePercent: number;
  totalReturn: number;
  totalReturnPercent: number;
  sharpeRatio: number;
  beta: number;
  volatility: number;
  var95: number;
  maxDrawdown: number;
  lastUpdated: string;
}

interface AssetAllocation {
  [AssetClass.EQUITY]: number;
  [AssetClass.REAL_ESTATE]: number;
  [AssetClass.FIXED_INCOME]: number;
  [AssetClass.ALTERNATIVES]: number;
  [AssetClass.CASH]: number;
}

interface PerformanceData {
  date: string;
  value: number;
  benchmark: number;
  drawdown: number;
}

interface RiskMetric {
  name: string;
  value: number;
  benchmark: number;
  status: 'good' | 'warning' | 'critical';
  description: string;
}

interface ESGScore {
  overall: number;
  environmental: number;
  social: number;
  governance: number;
  trend: 'up' | 'down' | 'stable';
}

const mockLiveMetrics: LiveMetrics = {
  totalValue: 1135000000, // ₹113.5 Cr
  dayChange: 15400000, // ₹1.54 Cr
  dayChangePercent: 1.38,
  totalReturn: 230000000, // ₹23 Cr
  totalReturnPercent: 25.4,
  sharpeRatio: 1.42,
  beta: 0.78,
  volatility: 18.5,
  var95: -42000000, // ₹4.2 Cr max daily loss at 95% confidence
  maxDrawdown: -8.2,
  lastUpdated: new Date().toISOString(),
};

const mockAssetAllocation: AssetAllocation = {
  [AssetClass.EQUITY]: 58.5,
  [AssetClass.REAL_ESTATE]: 24.2,
  [AssetClass.ALTERNATIVES]: 12.8,
  [AssetClass.FIXED_INCOME]: 3.5,
  [AssetClass.CASH]: 1.0,
};

const mockPerformanceData: PerformanceData[] = [
  { date: '2024-01-01', value: 900000000, benchmark: 900000000, drawdown: 0 },
  { date: '2024-02-01', value: 925000000, benchmark: 918000000, drawdown: -2.1 },
  { date: '2024-03-01', value: 1020000000, benchmark: 945000000, drawdown: 0 },
  { date: '2024-04-01', value: 1065000000, benchmark: 972000000, drawdown: 0 },
  { date: '2024-05-01', value: 1098000000, benchmark: 990000000, drawdown: -3.5 },
  { date: '2024-06-01', value: 1135000000, benchmark: 1008000000, drawdown: 0 },
];

const mockRiskMetrics: RiskMetric[] = [
  {
    name: 'Value at Risk (95%)',
    value: -3.7,
    benchmark: -4.2,
    status: 'good',
    description: 'Maximum expected loss over 1 day with 95% confidence',
  },
  {
    name: 'Sharpe Ratio',
    value: 1.42,
    benchmark: 1.20,
    status: 'good',
    description: 'Risk-adjusted return measurement',
  },
  {
    name: 'Beta',
    value: 0.78,
    benchmark: 1.00,
    status: 'good',
    description: 'Portfolio sensitivity to market movements',
  },
  {
    name: 'Volatility',
    value: 18.5,
    benchmark: 22.0,
    status: 'good',
    description: 'Annualized standard deviation of returns',
  },
  {
    name: 'Maximum Drawdown',
    value: -8.2,
    benchmark: -12.5,
    status: 'warning',
    description: 'Largest peak-to-trough decline',
  },
  {
    name: 'Correlation to Market',
    value: 0.65,
    benchmark: 0.85,
    status: 'good',
    description: 'Portfolio correlation with broad market index',
  },
];

const mockESGScore: ESGScore = {
  overall: 87,
  environmental: 92,
  social: 84,
  governance: 85,
  trend: 'up',
};

export const RealTimePortfolioAnalytics: React.FC<RealTimePortfolioAnalyticsProps> = ({
  tier,
  anonymousId,
  portfolioId,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'risk' | 'allocation' | 'esg'>('overview');
  const [timeRange, setTimeRange] = useState<'1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | 'ALL'>('1M');
  const [liveMetrics, setLiveMetrics] = useState<LiveMetrics>(mockLiveMetrics);
  const [isLive, setIsLive] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Simulate real-time updates
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      setLiveMetrics(prev => ({
        ...prev,
        totalValue: prev.totalValue + (Math.random() - 0.5) * 10000000, // ±₹1 Cr variation
        dayChange: prev.dayChange + (Math.random() - 0.5) * 2000000, // ±₹20 L variation
        dayChangePercent: ((prev.totalValue + prev.dayChange) / prev.totalValue - 1) * 100,
        lastUpdated: new Date().toISOString(),
      }));
      setLastUpdate(new Date());
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [isLive]);

  const formatCurrency = (amount: number) => {
    const crores = Math.abs(amount) / 10000000;
    const sign = amount < 0 ? '-' : '';
    return `${sign}₹${crores.toLocaleString('en-IN', { maximumFractionDigits: 2 })} Cr`;
  };

  const getChangeColor = (value: number) => {
    if (value > 0) return 'text-green-400';
    if (value < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  const getRiskColor = (status: 'good' | 'warning' | 'critical') => {
    switch (status) {
      case 'good': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'critical': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <LuxuryCard className="p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-400">Total Portfolio Value</h3>
            <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`} />
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {formatCurrency(liveMetrics.totalValue)}
          </div>
          <div className={`text-sm ${getChangeColor(liveMetrics.dayChange)}`}>
            {liveMetrics.dayChange > 0 ? '+' : ''}{formatCurrency(liveMetrics.dayChange)} ({liveMetrics.dayChangePercent.toFixed(2)}%)
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Total Returns</h3>
          <div className="text-2xl font-bold text-white mb-1">
            {formatCurrency(liveMetrics.totalReturn)}
          </div>
          <div className={`text-sm ${getChangeColor(liveMetrics.totalReturnPercent)}`}>
            +{liveMetrics.totalReturnPercent.toFixed(1)}% since inception
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Sharpe Ratio</h3>
          <div className="text-2xl font-bold text-white mb-1">
            {liveMetrics.sharpeRatio.toFixed(2)}
          </div>
          <div className="text-sm text-green-400">
            Excellent risk-adjusted returns
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Portfolio Beta</h3>
          <div className="text-2xl font-bold text-white mb-1">
            {liveMetrics.beta.toFixed(2)}
          </div>
          <div className="text-sm text-green-400">
            Lower market sensitivity
          </div>
        </LuxuryCard>
      </div>

      {/* Performance Chart */}
      <LuxuryCard className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white">Portfolio Performance</h3>
          <div className="flex space-x-2">
            {(['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL'] as const).map(range => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  timeRange === range
                    ? 'bg-gold-500 text-black'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>
        <LineChart data={mockPerformanceData} />
      </LuxuryCard>

      {/* Asset Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LuxuryCard className="p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Asset Allocation</h3>
          <PieChart data={mockAssetAllocation} />
          <div className="mt-4 space-y-2">
            {Object.entries(mockAssetAllocation).map(([assetClass, percentage]) => (
              <div key={assetClass} className="flex justify-between items-center">
                <span className="text-gray-300 capitalize">{assetClass.replace('_', ' ')}</span>
                <span className="text-white font-medium">{percentage.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <h3 className="text-lg font-semibold text-white mb-6">ESG Score</h3>
          <div className="text-center mb-6">
            <div className="text-4xl font-bold text-green-400 mb-2">{mockESGScore.overall}</div>
            <div className="text-sm text-gray-400">Overall ESG Rating</div>
            <div className={`text-xs mt-1 ${
              mockESGScore.trend === 'up' ? 'text-green-400' :
              mockESGScore.trend === 'down' ? 'text-red-400' : 'text-gray-400'
            }`}>
              {mockESGScore.trend === 'up' ? '↗' : mockESGScore.trend === 'down' ? '↘' : '→'} Trending {mockESGScore.trend}
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Environmental</span>
              <span className="text-green-400 font-medium">{mockESGScore.environmental}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Social</span>
              <span className="text-green-400 font-medium">{mockESGScore.social}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Governance</span>
              <span className="text-green-400 font-medium">{mockESGScore.governance}</span>
            </div>
          </div>
        </LuxuryCard>
      </div>
    </div>
  );

  const renderPerformanceTab = () => (
    <div className="space-y-6">
      <LuxuryCard className="p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Performance vs Benchmarks</h3>
        <LineChart data={mockPerformanceData} />
      </LuxuryCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LuxuryCard className="p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Rolling Returns</h3>
          <div className="space-y-4">
            {[
              { period: '1 Month', portfolio: 3.2, benchmark: 2.1 },
              { period: '3 Months', portfolio: 8.7, benchmark: 6.4 },
              { period: '6 Months', portfolio: 15.8, benchmark: 12.3 },
              { period: '1 Year', portfolio: 25.4, benchmark: 18.7 },
              { period: '3 Years (Ann.)', portfolio: 22.1, benchmark: 16.9 },
            ].map(item => (
              <div key={item.period} className="flex justify-between items-center">
                <span className="text-gray-400">{item.period}</span>
                <div className="flex space-x-4">
                  <span className={`font-medium ${getChangeColor(item.portfolio)}`}>
                    +{item.portfolio.toFixed(1)}%
                  </span>
                  <span className="text-gray-500 text-sm">
                    (Benchmark: +{item.benchmark.toFixed(1)}%)
                  </span>
                </div>
              </div>
            ))}
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Drawdown Analysis</h3>
          <BarChart data={mockPerformanceData} />
          <div className="mt-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">Current Drawdown</span>
              <span className="text-green-400">0.0%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Maximum Drawdown</span>
              <span className="text-yellow-400">-8.2%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Recovery Time</span>
              <span className="text-white">42 days</span>
            </div>
          </div>
        </LuxuryCard>
      </div>
    </div>
  );

  const renderRiskTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {mockRiskMetrics.map(metric => (
          <LuxuryCard key={metric.name} className="p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-white">{metric.name}</h3>
              <div className={`w-3 h-3 rounded-full ${
                metric.status === 'good' ? 'bg-green-400' :
                metric.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
              }`} />
            </div>
            <div className="text-2xl font-bold mb-2">
              <span className={getRiskColor(metric.status)}>
                {typeof metric.value === 'number' ? metric.value.toFixed(2) : metric.value}
                {metric.name.includes('Ratio') || metric.name.includes('Beta') || metric.name.includes('Correlation') ? '' : '%'}
              </span>
            </div>
            <div className="text-sm text-gray-400 mb-2">
              Benchmark: {metric.benchmark.toFixed(2)}%
            </div>
            <p className="text-xs text-gray-500">{metric.description}</p>
          </LuxuryCard>
        ))}
      </div>

      {tier === InvestmentTier.VOID && (
        <LuxuryCard className="p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Quantum Risk Analysis</h3>
          <div className="text-center p-8 bg-black/30 rounded-lg">
            <div className="text-gold-400 text-2xl font-bold mb-2">⚛️</div>
            <div className="text-white font-semibold mb-2">Advanced Risk Modeling</div>
            <div className="text-gray-400 text-sm">
              Monte Carlo simulations, scenario analysis, and quantum risk metrics available for VOID tier
            </div>
          </div>
        </LuxuryCard>
      )}
    </div>
  );

  const renderAllocationTab = () => (
    <div className="space-y-6">
      <LuxuryCard className="p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Current vs Target Allocation</h3>
        <div className="space-y-4">
          {Object.entries(mockAssetAllocation).map(([assetClass, current]) => {
            const target = {
              [AssetClass.EQUITY]: 60,
              [AssetClass.REAL_ESTATE]: 25,
              [AssetClass.ALTERNATIVES]: 10,
              [AssetClass.FIXED_INCOME]: 4,
              [AssetClass.CASH]: 1,
            }[assetClass as AssetClass] || 0;
            
            const difference = current - target;
            
            return (
              <div key={assetClass} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-white capitalize font-medium">
                    {assetClass.replace('_', ' ')}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400 text-sm">Target: {target}%</span>
                    <span className={`text-sm font-medium ${
                      Math.abs(difference) < 2 ? 'text-green-400' :
                      Math.abs(difference) < 5 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {current.toFixed(1)}% ({difference > 0 ? '+' : ''}{difference.toFixed(1)}%)
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gold-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(current / Math.max(...Object.values(mockAssetAllocation))) * 100}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </LuxuryCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LuxuryCard className="p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Rebalancing Recommendations</h3>
          <div className="space-y-4">
            <div className="p-4 bg-yellow-900/30 border border-yellow-500/50 rounded-lg">
              <div className="text-yellow-400 font-semibold mb-2">⚠️ Rebalancing Suggested</div>
              <div className="text-sm text-gray-300 space-y-1">
                <div>• Reduce Real Estate by 2.2% (₹2.5 Cr)</div>
                <div>• Increase Fixed Income by 1.5% (₹1.7 Cr)</div>
                <div>• Reduce Alternatives by 0.8% (₹0.9 Cr)</div>
              </div>
            </div>
            <button className="w-full py-3 bg-gold-500 text-black font-semibold rounded-lg hover:bg-gold-400 transition-colors">
              Execute Rebalancing
            </button>
          </div>
        </LuxuryCard>

        <LuxuryCard className="p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Sector Allocation</h3>
          <div className="space-y-3">
            {[
              { sector: 'Technology', percentage: 28.5, change: 2.1 },
              { sector: 'Real Estate', percentage: 24.2, change: -0.5 },
              { sector: 'Healthcare', percentage: 15.8, change: 1.3 },
              { sector: 'Financial Services', percentage: 12.3, change: -0.8 },
              { sector: 'Consumer Goods', percentage: 8.7, change: 0.4 },
              { sector: 'Energy & Utilities', percentage: 6.2, change: 1.8 },
              { sector: 'Others', percentage: 4.3, change: 0.2 },
            ].map(item => (
              <div key={item.sector} className="flex justify-between items-center">
                <span className="text-gray-300">{item.sector}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-white font-medium">{item.percentage}%</span>
                  <span className={`text-xs ${getChangeColor(item.change)}`}>
                    ({item.change > 0 ? '+' : ''}{item.change}%)
                  </span>
                </div>
              </div>
            ))}
          </div>
        </LuxuryCard>
      </div>
    </div>
  );

  const renderESGTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <LuxuryCard className="p-6 text-center">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Environmental Score</h3>
          <div className="text-3xl font-bold text-green-400 mb-2">{mockESGScore.environmental}</div>
          <div className="text-xs text-gray-500">Excellent rating</div>
        </LuxuryCard>

        <LuxuryCard className="p-6 text-center">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Social Score</h3>
          <div className="text-3xl font-bold text-green-400 mb-2">{mockESGScore.social}</div>
          <div className="text-xs text-gray-500">Very good rating</div>
        </LuxuryCard>

        <LuxuryCard className="p-6 text-center">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Governance Score</h3>
          <div className="text-3xl font-bold text-green-400 mb-2">{mockESGScore.governance}</div>
          <div className="text-xs text-gray-500">Very good rating</div>
        </LuxuryCard>
      </div>

      <LuxuryCard className="p-6">
        <h3 className="text-lg font-semibold text-white mb-6">ESG Impact Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h4 className="text-md font-semibold text-green-400">Environmental Impact</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Carbon Footprint Reduction</span>
                <span className="text-green-400">-45%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Renewable Energy Investment</span>
                <span className="text-green-400">₹28 Cr</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Water Conservation Projects</span>
                <span className="text-green-400">12 projects</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="text-md font-semibold text-blue-400">Social Impact</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Job Creation</span>
                <span className="text-blue-400">15,000+ jobs</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Education Investment</span>
                <span className="text-blue-400">₹8.5 Cr</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Healthcare Access</span>
                <span className="text-blue-400">45,000 beneficiaries</span>
              </div>
            </div>
          </div>
        </div>
      </LuxuryCard>
    </div>
  );

  const tabConfig = [
    { id: 'overview', label: 'Overview', content: renderOverviewTab },
    { id: 'performance', label: 'Performance', content: renderPerformanceTab },
    { id: 'risk', label: 'Risk Analysis', content: renderRiskTab },
    { id: 'allocation', label: 'Allocation', content: renderAllocationTab },
    { id: 'esg', label: 'ESG Analysis', content: renderESGTab },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-gold-400 to-gold-600 bg-clip-text text-transparent">
            Portfolio Analytics
          </h1>
          <p className="text-lg text-gray-300">
            Real-time analytics and insights • {tier.toUpperCase()} Tier
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsLive(!isLive)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              isLive 
                ? 'bg-green-500 text-black hover:bg-green-400'
                : 'bg-gray-600 text-white hover:bg-gray-500'
            }`}
          >
            {isLive ? '● LIVE' : '⏸ PAUSED'}
          </button>
          
          <div className="text-xs text-gray-400">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-black/50 rounded-lg p-1">
        {tabConfig.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-6 py-3 rounded-lg transition-all duration-200 ${
              activeTab === tab.id
                ? 'bg-gold-500 text-black font-medium'
                : 'text-gray-300 hover:text-white hover:bg-white/10'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tabConfig.find(tab => tab.id === activeTab)?.content()}
    </div>
  );
};