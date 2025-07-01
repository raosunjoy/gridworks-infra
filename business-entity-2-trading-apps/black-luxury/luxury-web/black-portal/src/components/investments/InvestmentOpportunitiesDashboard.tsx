/**
 * Investment Opportunities Dashboard
 * Premium investment opportunity browsing and filtering interface
 * for Black-tier clients with real-time updates and anonymous access
 */

import React, { useState, useEffect } from 'react';
import { InvestmentOpportunity, InvestmentCategory, InvestmentTier } from '../../services/InvestmentSyndicateEngine';
import { LuxuryCard } from '../ui/LuxuryCard';
import { TierGlow } from '../ui/TierGlow';

interface InvestmentOpportunitiesDashboardProps {
  tier: InvestmentTier;
  onInvestmentSelect: (opportunity: InvestmentOpportunity) => void;
}

export const InvestmentOpportunitiesDashboard: React.FC<InvestmentOpportunitiesDashboardProps> = ({
  tier,
  onInvestmentSelect,
}) => {
  const [opportunities, setOpportunities] = useState<InvestmentOpportunity[]>([]);
  const [filteredOpportunities, setFilteredOpportunities] = useState<InvestmentOpportunity[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<InvestmentCategory | 'all'>('all');
  const [sortBy, setSortBy] = useState<'returns' | 'minimum' | 'deadline'>('returns');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadInvestmentOpportunities();
  }, [tier]);

  useEffect(() => {
    filterAndSortOpportunities();
  }, [opportunities, selectedCategory, sortBy]);

  const loadInvestmentOpportunities = async () => {
    try {
      setIsLoading(true);
      // In real implementation, this would call the InvestmentSyndicateEngine
      const mockOpportunities: InvestmentOpportunity[] = [
        {
          id: 'spacex-preipo-2024',
          title: 'SpaceX Series X Pre-IPO',
          category: InvestmentCategory.PRE_IPO,
          description: 'Exclusive access to SpaceX pre-IPO shares with projected 20-30% annual returns',
          minimumInvestment: 500000000, // ₹50 Cr
          maximumInvestment: 5000000000, // ₹500 Cr
          totalRaiseAmount: 50000000000, // ₹5000 Cr
          currentCommitments: 15000000000, // ₹1500 Cr
          currency: 'INR',
          expectedReturns: {
            conservative: '15%',
            optimistic: '30%',
            timeframe: '3-5 years',
          },
          lockupPeriod: '3-5 years',
          liquidityOptions: ['Secondary market', 'IPO exit', 'Strategic acquisition'],
          tierAccess: [InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
          geographicRestrictions: ['Available to Indian investors via LRS/ODI route'],
          regulatoryRequirements: ['RBI LRS compliance', 'FEMA approval', 'Tax planning required'],
          companyDetails: {
            name: 'SpaceX',
            sector: 'Aerospace & Defense',
            foundedYear: 2002,
            lastValuation: 180000000000,
            keyInvestors: ['Founders Fund', 'Andreessen Horowitz', 'Google Ventures'],
            businessModel: 'Space transportation and satellite internet',
            competitiveAdvantage: ['Market leadership', 'Technological moat', 'Network effects'],
          },
          riskRating: 'medium',
          riskFactors: ['Pre-IPO illiquidity', 'Valuation volatility', 'Regulatory changes'],
          dueDiligenceStatus: 'completed',
          complianceChecks: {
            sebiApproval: true,
            rbiCompliance: true,
            femaCompliance: true,
            taxImplications: ['Capital gains tax planning', 'LRS impact', 'DTR benefits'],
          },
          offeringPeriod: {
            startDate: new Date().toISOString(),
            endDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
            finalClosing: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
          },
          documentPackage: {
            termSheet: 'SpaceX_TermSheet_2024.pdf',
            offeringMemorandum: 'SpaceX_OfferingMemo_2024.pdf',
            subscriptionAgreement: 'SpaceX_Subscription_2024.pdf',
            dueDiligenceReport: 'SpaceX_DDReport_2024.pdf',
            legalOpinion: 'SpaceX_LegalOpinion_2024.pdf',
          },
          status: 'active',
          availableSlots: 35,
          totalSlots: 50,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: 'dubai-marina-penthouse-2024',
          title: 'Dubai Marina Penthouse Collection',
          category: InvestmentCategory.LUXURY_REAL_ESTATE,
          description: 'Ultra-luxury penthouses with private helicopter pads and infinity pools',
          minimumInvestment: 250000000, // ₹25 Cr
          maximumInvestment: 1250000000, // ₹125 Cr
          totalRaiseAmount: 2500000000, // ₹250 Cr
          currentCommitments: 750000000, // ₹75 Cr
          currency: 'INR',
          expectedReturns: {
            conservative: '12%',
            optimistic: '18%',
            timeframe: '5-7 years',
          },
          lockupPeriod: '3-5 years',
          liquidityOptions: ['Property sale', 'Rental income', 'Refinancing options'],
          tierAccess: [InvestmentTier.ONYX, InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
          geographicRestrictions: ['International property investment via LRS'],
          regulatoryRequirements: ['RBI LRS compliance', 'Property ownership regulations'],
          realEstateDetails: {
            location: 'Dubai Marina, UAE',
            propertyType: 'Ultra-luxury penthouses',
            squareFootage: 10000,
            amenities: ['Private helicopter pad', 'Infinity pool', 'Private beach access'],
            developmentStage: 'Completed',
            expectedCompletion: 'Immediate possession',
          },
          riskRating: 'low',
          riskFactors: ['Property market fluctuations', 'Currency exchange risk'],
          dueDiligenceStatus: 'completed',
          complianceChecks: {
            sebiApproval: false,
            rbiCompliance: true,
            femaCompliance: true,
            taxImplications: ['Property tax', 'Capital gains planning'],
          },
          offeringPeriod: {
            startDate: new Date().toISOString(),
            endDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
            finalClosing: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
          },
          documentPackage: {
            termSheet: 'DubaiMarina_TermSheet_2024.pdf',
            offeringMemorandum: 'DubaiMarina_PropertyMemo_2024.pdf',
            subscriptionAgreement: 'DubaiMarina_Purchase_2024.pdf',
            dueDiligenceReport: 'DubaiMarina_PropertyReport_2024.pdf',
            legalOpinion: 'DubaiMarina_LegalOpinion_2024.pdf',
          },
          status: 'active',
          availableSlots: 15,
          totalSlots: 20,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ];

      // Filter by tier access
      const tierFilteredOpportunities = mockOpportunities.filter(
        opp => opp.tierAccess.includes(tier)
      );

      setOpportunities(tierFilteredOpportunities);
    } catch (error) {
      console.error('Failed to load investment opportunities:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterAndSortOpportunities = () => {
    let filtered = opportunities;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(opp => opp.category === selectedCategory);
    }

    // Sort opportunities
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'returns':
          return parseFloat(b.expectedReturns.optimistic.replace('%', '')) - 
                 parseFloat(a.expectedReturns.optimistic.replace('%', ''));
        case 'minimum':
          return a.minimumInvestment - b.minimumInvestment;
        case 'deadline':
          return new Date(a.offeringPeriod.endDate).getTime() - 
                 new Date(b.offeringPeriod.endDate).getTime();
        default:
          return 0;
      }
    });

    setFilteredOpportunities(filtered);
  };

  const formatCurrency = (amount: number) => {
    const crores = amount / 10000000;
    return `₹${crores.toLocaleString('en-IN')} Cr`;
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getTierColor = (tier: InvestmentTier) => {
    switch (tier) {
      case InvestmentTier.ONYX: return 'from-slate-600 to-slate-900';
      case InvestmentTier.OBSIDIAN: return 'from-purple-600 to-purple-900';
      case InvestmentTier.VOID: return 'from-black to-gray-900';
      default: return 'from-gray-600 to-gray-900';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <TierGlow tier={tier}>
          <div className="animate-pulse text-xl">Loading investment opportunities...</div>
        </TierGlow>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gold-400 to-gold-600 bg-clip-text text-transparent">
          Exclusive Investment Opportunities
        </h1>
        <p className="text-lg text-gray-300">
          Curated premium investments for {tier.toUpperCase()} tier clients
        </p>
      </div>

      {/* Filters */}
      <LuxuryCard className="p-6">
        <div className="flex flex-wrap gap-6 items-center">
          {/* Category Filter */}
          <div className="flex flex-col">
            <label className="text-sm text-gray-400 mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value as InvestmentCategory | 'all')}
              className="bg-black/50 border border-gold-500/30 rounded-lg px-4 py-2 text-white focus:border-gold-500 focus:outline-none"
            >
              <option value="all">All Categories</option>
              <option value={InvestmentCategory.PRE_IPO}>Pre-IPO</option>
              <option value={InvestmentCategory.LUXURY_REAL_ESTATE}>Luxury Real Estate</option>
              <option value={InvestmentCategory.ESG_INVESTMENTS}>ESG Investments</option>
              <option value={InvestmentCategory.PRIVATE_EQUITY}>Private Equity</option>
              <option value={InvestmentCategory.HEDGE_FUNDS}>Hedge Funds</option>
              <option value={InvestmentCategory.ART_COLLECTIBLES}>Art & Collectibles</option>
            </select>
          </div>

          {/* Sort Filter */}
          <div className="flex flex-col">
            <label className="text-sm text-gray-400 mb-2">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'returns' | 'minimum' | 'deadline')}
              className="bg-black/50 border border-gold-500/30 rounded-lg px-4 py-2 text-white focus:border-gold-500 focus:outline-none"
            >
              <option value="returns">Expected Returns</option>
              <option value="minimum">Minimum Investment</option>
              <option value="deadline">Deadline</option>
            </select>
          </div>

          {/* Stats */}
          <div className="ml-auto flex gap-6 text-sm">
            <div className="text-center">
              <div className="text-gold-400 font-bold text-lg">{filteredOpportunities.length}</div>
              <div className="text-gray-400">Available</div>
            </div>
            <div className="text-center">
              <div className="text-gold-400 font-bold text-lg">
                {formatCurrency(filteredOpportunities.reduce((sum, opp) => sum + opp.minimumInvestment, 0))}
              </div>
              <div className="text-gray-400">Total Min. Investment</div>
            </div>
          </div>
        </div>
      </LuxuryCard>

      {/* Opportunities Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredOpportunities.map((opportunity) => (
          <LuxuryCard
            key={opportunity.id}
            className="group cursor-pointer transform transition-all duration-300 hover:scale-105"
            onClick={() => onInvestmentSelect(opportunity)}
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-2 group-hover:text-gold-400 transition-colors">
                    {opportunity.title}
                  </h3>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-gold-500/20 text-gold-400 text-xs rounded-full">
                      {opportunity.category.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full ${getRiskColor(opportunity.riskRating)}`}>
                      {opportunity.riskRating.toUpperCase()} RISK
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-green-400 font-bold text-lg">
                    {opportunity.expectedReturns.conservative}-{opportunity.expectedReturns.optimistic}
                  </div>
                  <div className="text-gray-400 text-sm">Expected Returns</div>
                </div>
              </div>

              {/* Company/Asset Details */}
              {opportunity.companyDetails && (
                <div className="mb-4">
                  <div className="text-gray-300 font-semibold">{opportunity.companyDetails.name}</div>
                  <div className="text-gray-400 text-sm">{opportunity.companyDetails.sector}</div>
                  <div className="text-gold-400 text-sm">
                    Last Valuation: ${(opportunity.companyDetails.lastValuation / 1000000000).toFixed(1)}B
                  </div>
                </div>
              )}

              {opportunity.realEstateDetails && (
                <div className="mb-4">
                  <div className="text-gray-300 font-semibold">{opportunity.realEstateDetails.propertyType}</div>
                  <div className="text-gray-400 text-sm">{opportunity.realEstateDetails.location}</div>
                  <div className="text-gold-400 text-sm">
                    {opportunity.realEstateDetails.squareFootage?.toLocaleString()} sq ft
                  </div>
                </div>
              )}

              {/* Investment Details */}
              <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div>
                  <div className="text-gray-400">Minimum</div>
                  <div className="text-white font-semibold">{formatCurrency(opportunity.minimumInvestment)}</div>
                </div>
                <div>
                  <div className="text-gray-400">Lock-up</div>
                  <div className="text-white font-semibold">{opportunity.lockupPeriod}</div>
                </div>
                <div>
                  <div className="text-gray-400">Available Slots</div>
                  <div className="text-white font-semibold">{opportunity.availableSlots}/{opportunity.totalSlots}</div>
                </div>
                <div>
                  <div className="text-gray-400">Deadline</div>
                  <div className="text-white font-semibold">
                    {new Date(opportunity.offeringPeriod.endDate).toLocaleDateString()}
                  </div>
                </div>
              </div>

              {/* Description */}
              <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                {opportunity.description}
              </p>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Commitment Progress</span>
                  <span>{((opportunity.currentCommitments / opportunity.totalRaiseAmount) * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-gold-400 to-gold-600 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${(opportunity.currentCommitments / opportunity.totalRaiseAmount) * 100}%`
                    }}
                  />
                </div>
              </div>

              {/* Action Button */}
              <button
                className="w-full py-3 bg-gradient-to-r from-gold-500 to-gold-600 text-black font-bold rounded-lg
                          hover:from-gold-400 hover:to-gold-500 transition-all duration-300
                          transform group-hover:scale-105"
                onClick={(e) => {
                  e.stopPropagation();
                  onInvestmentSelect(opportunity);
                }}
              >
                View Details & Invest
              </button>
            </div>
          </LuxuryCard>
        ))}
      </div>

      {/* Empty State */}
      {filteredOpportunities.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg mb-4">
            No investment opportunities available for selected criteria
          </div>
          <button
            onClick={() => {
              setSelectedCategory('all');
              setSortBy('returns');
            }}
            className="px-6 py-3 bg-gold-500/20 text-gold-400 rounded-lg hover:bg-gold-500/30 transition-colors"
          >
            Reset Filters
          </button>
        </div>
      )}
    </div>
  );
};