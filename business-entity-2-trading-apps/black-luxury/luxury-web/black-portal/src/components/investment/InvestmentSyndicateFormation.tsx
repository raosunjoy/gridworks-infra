/**
 * Investment Syndicate Formation Interface
 * Advanced UI for lead investors to create and manage investment syndicates
 * with anonymous structures, governance controls, and participant management
 */

import React, { useState, useEffect } from 'react';
import { InvestmentTier, InvestmentCategory, InvestmentOpportunity } from '../../services/InvestmentSyndicateEngine';
import { LuxuryCard } from '../ui/LuxuryCard';
import { TierGlow } from '../ui/TierGlow';

interface InvestmentSyndicateFormationProps {
  opportunity: InvestmentOpportunity;
  leadInvestorTier: InvestmentTier;
  anonymousId: string;
  onSyndicateCreated: (syndicate: any) => void;
  onCancel: () => void;
}

interface SyndicateConfiguration {
  leadCommitment: number;
  minimumSyndicateSize: number;
  maximumSyndicateSize: number;
  minimumParticipantCommitment: number;
  maximumParticipantCommitment: number;
  governanceStructure: 'lead_decides' | 'majority_vote' | 'unanimous' | 'weighted_vote';
  feeStructure: {
    managementFee: number; // Percentage
    carriedInterest: number; // Percentage
    adminFee: number; // Fixed amount
  };
  distributionPolicy: 'pro_rata' | 'waterfall' | 'preferred_return';
  lockupPeriod: string;
  exitStrategy: string[];
}

interface ParticipantCriteria {
  minimumNetWorth: number;
  geographicRestrictions: string[];
  institutionalOnly: boolean;
  accreditationRequired: boolean;
  tierRestrictions: InvestmentTier[];
  maxExposurePerParticipant: number;
}

interface AnonymousStructure {
  spvName: string;
  jurisdiction: 'mauritius' | 'singapore' | 'cayman' | 'luxembourg';
  taxOptimization: string[];
  beneficialOwnership: 'nominee' | 'trust' | 'foundation';
  reportingRequirements: string[];
  complianceLevel: 'standard' | 'enhanced' | 'quantum';
}

const governanceOptions = [
  {
    value: 'lead_decides',
    label: 'Lead Investor Decides',
    description: 'Lead investor makes all decisions unilaterally',
    minTier: InvestmentTier.ONYX,
  },
  {
    value: 'majority_vote',
    label: 'Majority Vote',
    description: 'Decisions require >50% vote by commitment amount',
    minTier: InvestmentTier.ONYX,
  },
  {
    value: 'unanimous',
    label: 'Unanimous Consent',
    description: 'All participants must agree to major decisions',
    minTier: InvestmentTier.OBSIDIAN,
  },
  {
    value: 'weighted_vote',
    label: 'Weighted Voting',
    description: 'Votes weighted by commitment amount and tier',
    minTier: InvestmentTier.VOID,
  },
];

const jurisdictionOptions = [
  {
    value: 'mauritius',
    label: 'Mauritius',
    benefits: ['DTAA with India', 'No capital gains tax', 'Strong regulatory framework'],
    setupTime: '2-3 weeks',
    cost: '₹15-25 L',
  },
  {
    value: 'singapore',
    label: 'Singapore',
    benefits: ['Global financial hub', 'Stable regulatory environment', 'Tax treaty network'],
    setupTime: '3-4 weeks', 
    cost: '₹20-35 L',
  },
  {
    value: 'cayman',
    label: 'Cayman Islands',
    benefits: ['No direct taxation', 'Flexible structure', 'Global acceptance'],
    setupTime: '4-6 weeks',
    cost: '₹25-45 L',
  },
  {
    value: 'luxembourg',
    label: 'Luxembourg',
    benefits: ['EU access', 'Strong investor protection', 'Sophisticated structures'],
    setupTime: '6-8 weeks',
    cost: '₹35-55 L',
  },
];

export const InvestmentSyndicateFormation: React.FC<InvestmentSyndicateFormationProps> = ({
  opportunity,
  leadInvestorTier,
  anonymousId,
  onSyndicateCreated,
  onCancel,
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [syndicateConfig, setSyndicateConfig] = useState<SyndicateConfiguration>({
    leadCommitment: opportunity.minimumInvestment,
    minimumSyndicateSize: 3,
    maximumSyndicateSize: 15,
    minimumParticipantCommitment: opportunity.minimumInvestment,
    maximumParticipantCommitment: opportunity.maximumInvestment / 2,
    governanceStructure: 'lead_decides',
    feeStructure: {
      managementFee: 2.0,
      carriedInterest: 20.0,
      adminFee: 5000000, // ₹50 L
    },
    distributionPolicy: 'pro_rata',
    lockupPeriod: opportunity.lockupPeriod,
    exitStrategy: ['IPO', 'Strategic Sale', 'Secondary Market'],
  });

  const [participantCriteria, setParticipantCriteria] = useState<ParticipantCriteria>({
    minimumNetWorth: 1000000000, // ₹100 Cr
    geographicRestrictions: [],
    institutionalOnly: false,
    accreditationRequired: true,
    tierRestrictions: [InvestmentTier.ONYX, InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
    maxExposurePerParticipant: 25, // 25% of total syndicate
  });

  const [anonymousStructure, setAnonymousStructure] = useState<AnonymousStructure>({
    spvName: `BlackPortal ${opportunity.companyDetails?.name} SPV`,
    jurisdiction: 'mauritius',
    taxOptimization: ['DTAA benefits', 'Capital gains exemption'],
    beneficialOwnership: 'nominee',
    reportingRequirements: ['Annual audited accounts', 'Quarterly investor reports'],
    complianceLevel: leadInvestorTier === InvestmentTier.VOID ? 'quantum' : 'enhanced',
  });

  const [participants, setParticipants] = useState<any[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const formatCurrency = (amount: number) => {
    const crores = amount / 10000000;
    return `₹${crores.toLocaleString('en-IN')} Cr`;
  };

  const validateConfiguration = () => {
    const errors: string[] = [];

    if (syndicateConfig.leadCommitment < opportunity.minimumInvestment) {
      errors.push('Lead commitment must meet minimum investment requirement');
    }

    if (syndicateConfig.minimumSyndicateSize > syndicateConfig.maximumSyndicateSize) {
      errors.push('Minimum syndicate size cannot exceed maximum size');
    }

    if (syndicateConfig.minimumParticipantCommitment > syndicateConfig.maximumParticipantCommitment) {
      errors.push('Minimum participant commitment cannot exceed maximum');
    }

    const totalPotentialCommitment = syndicateConfig.leadCommitment + 
      (syndicateConfig.maximumSyndicateSize * syndicateConfig.maximumParticipantCommitment);
    
    if (totalPotentialCommitment > opportunity.maximumInvestment) {
      errors.push('Total potential commitment exceeds opportunity maximum');
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  const handleCreateSyndicate = async () => {
    if (!validateConfiguration()) {
      return;
    }

    setIsCreating(true);
    try {
      // In real implementation, this would call InvestmentSyndicateEngine
      const newSyndicate = {
        id: `syn-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
        opportunityId: opportunity.id,
        leadInvestor: {
          anonymousId,
          tier: leadInvestorTier,
          commitmentAmount: syndicateConfig.leadCommitment,
          role: 'lead',
        },
        configuration: syndicateConfig,
        participantCriteria,
        anonymousStructure,
        participants: [],
        status: 'forming',
        createdAt: new Date().toISOString(),
        syndicateTerms: {
          minimumSyndicateSize: syndicateConfig.minimumSyndicateSize,
          maximumSyndicateSize: syndicateConfig.maximumSyndicateSize,
          decisionMaking: syndicateConfig.governanceStructure,
          feeStructure: syndicateConfig.feeStructure,
        },
      };

      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      onSyndicateCreated(newSyndicate);
    } catch (error) {
      console.error('Failed to create syndicate:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex justify-center mb-8">
      <div className="flex space-x-4">
        {[
          { step: 1, title: 'Configuration' },
          { step: 2, title: 'Structure' },
          { step: 3, title: 'Participants' },
          { step: 4, title: 'Review' },
        ].map(({ step, title }) => (
          <div
            key={step}
            className={`flex items-center space-x-2 ${
              currentStep >= step ? 'text-gold-400' : 'text-gray-500'
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                currentStep >= step
                  ? 'bg-gold-500 border-gold-500 text-black'
                  : 'border-gray-500 text-gray-500'
              }`}
            >
              {step}
            </div>
            <span className="text-sm font-medium">{title}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const renderConfigurationStep = () => (
    <div className="space-y-8">
      <LuxuryCard className="p-8">
        <h3 className="text-xl font-bold mb-6 text-gold-400">Syndicate Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Lead Investor Commitment
            </label>
            <input
              type="number"
              value={syndicateConfig.leadCommitment}
              onChange={(e) => setSyndicateConfig({
                ...syndicateConfig,
                leadCommitment: parseInt(e.target.value)
              })}
              className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                       focus:border-gold-500 focus:outline-none"
              min={opportunity.minimumInvestment}
              max={opportunity.maximumInvestment}
            />
            <p className="text-xs text-gray-400 mt-1">
              Minimum: {formatCurrency(opportunity.minimumInvestment)}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Governance Structure
            </label>
            <select
              value={syndicateConfig.governanceStructure}
              onChange={(e) => setSyndicateConfig({
                ...syndicateConfig,
                governanceStructure: e.target.value as any
              })}
              className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                       focus:border-gold-500 focus:outline-none"
            >
              {governanceOptions
                .filter(option => {
                  const tierOrder = { onyx: 1, obsidian: 2, void: 3 };
                  return tierOrder[leadInvestorTier] >= tierOrder[option.minTier];
                })
                .map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Syndicate Size Range
            </label>
            <div className="flex space-x-2">
              <input
                type="number"
                value={syndicateConfig.minimumSyndicateSize}
                onChange={(e) => setSyndicateConfig({
                  ...syndicateConfig,
                  minimumSyndicateSize: parseInt(e.target.value)
                })}
                className="flex-1 px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
                min="2"
                max="50"
                placeholder="Min"
              />
              <span className="flex items-center text-gray-400">to</span>
              <input
                type="number"
                value={syndicateConfig.maximumSyndicateSize}
                onChange={(e) => setSyndicateConfig({
                  ...syndicateConfig,
                  maximumSyndicateSize: parseInt(e.target.value)
                })}
                className="flex-1 px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
                min={syndicateConfig.minimumSyndicateSize}
                max="50"
                placeholder="Max"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Participant Commitment Range
            </label>
            <div className="space-y-2">
              <input
                type="number"
                value={syndicateConfig.minimumParticipantCommitment}
                onChange={(e) => setSyndicateConfig({
                  ...syndicateConfig,
                  minimumParticipantCommitment: parseInt(e.target.value)
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
                placeholder="Minimum participant commitment"
              />
              <input
                type="number"
                value={syndicateConfig.maximumParticipantCommitment}
                onChange={(e) => setSyndicateConfig({
                  ...syndicateConfig,
                  maximumParticipantCommitment: parseInt(e.target.value)
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
                placeholder="Maximum participant commitment"
              />
            </div>
          </div>
        </div>

        <div className="mt-8">
          <h4 className="text-lg font-semibold mb-4 text-gold-400">Fee Structure</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Management Fee (%)
              </label>
              <input
                type="number"
                value={syndicateConfig.feeStructure.managementFee}
                onChange={(e) => setSyndicateConfig({
                  ...syndicateConfig,
                  feeStructure: {
                    ...syndicateConfig.feeStructure,
                    managementFee: parseFloat(e.target.value)
                  }
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
                min="0"
                max="5"
                step="0.1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Carried Interest (%)
              </label>
              <input
                type="number"
                value={syndicateConfig.feeStructure.carriedInterest}
                onChange={(e) => setSyndicateConfig({
                  ...syndicateConfig,
                  feeStructure: {
                    ...syndicateConfig.feeStructure,
                    carriedInterest: parseFloat(e.target.value)
                  }
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
                min="0"
                max="30"
                step="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Admin Fee (₹)
              </label>
              <input
                type="number"
                value={syndicateConfig.feeStructure.adminFee}
                onChange={(e) => setSyndicateConfig({
                  ...syndicateConfig,
                  feeStructure: {
                    ...syndicateConfig.feeStructure,
                    adminFee: parseInt(e.target.value)
                  }
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
                min="0"
              />
            </div>
          </div>
        </div>
      </LuxuryCard>
    </div>
  );

  const renderStructureStep = () => (
    <div className="space-y-8">
      <LuxuryCard className="p-8">
        <h3 className="text-xl font-bold mb-6 text-gold-400">Anonymous Structure</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              SPV Name
            </label>
            <input
              type="text"
              value={anonymousStructure.spvName}
              onChange={(e) => setAnonymousStructure({
                ...anonymousStructure,
                spvName: e.target.value
              })}
              className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                       focus:border-gold-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Jurisdiction
            </label>
            <select
              value={anonymousStructure.jurisdiction}
              onChange={(e) => setAnonymousStructure({
                ...anonymousStructure,
                jurisdiction: e.target.value as any
              })}
              className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                       focus:border-gold-500 focus:outline-none"
            >
              {jurisdictionOptions.map(jurisdiction => (
                <option key={jurisdiction.value} value={jurisdiction.value}>
                  {jurisdiction.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-6">
          <h4 className="text-lg font-semibold mb-4">Jurisdiction Benefits</h4>
          {jurisdictionOptions
            .filter(j => j.value === anonymousStructure.jurisdiction)
            .map(jurisdiction => (
              <div key={jurisdiction.value} className="bg-black/30 p-4 rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h5 className="font-medium text-gold-400 mb-2">Benefits</h5>
                    <ul className="text-sm text-gray-300 space-y-1">
                      {jurisdiction.benefits.map((benefit, index) => (
                        <li key={index}>• {benefit}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-medium text-gold-400 mb-2">Setup Time</h5>
                    <p className="text-sm text-gray-300">{jurisdiction.setupTime}</p>
                  </div>
                  <div>
                    <h5 className="font-medium text-gold-400 mb-2">Estimated Cost</h5>
                    <p className="text-sm text-gray-300">{jurisdiction.cost}</p>
                  </div>
                </div>
              </div>
            ))}
        </div>

        <div className="mt-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Beneficial Ownership
              </label>
              <select
                value={anonymousStructure.beneficialOwnership}
                onChange={(e) => setAnonymousStructure({
                  ...anonymousStructure,
                  beneficialOwnership: e.target.value as any
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
              >
                <option value="nominee">Nominee Ownership</option>
                <option value="trust">Trust Structure</option>
                <option value="foundation">Foundation Structure</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Compliance Level
              </label>
              <select
                value={anonymousStructure.complianceLevel}
                onChange={(e) => setAnonymousStructure({
                  ...anonymousStructure,
                  complianceLevel: e.target.value as any
                })}
                className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                         focus:border-gold-500 focus:outline-none"
              >
                <option value="standard">Standard Compliance</option>
                <option value="enhanced">Enhanced Compliance</option>
                {leadInvestorTier === InvestmentTier.VOID && (
                  <option value="quantum">Quantum Compliance</option>
                )}
              </select>
            </div>
          </div>
        </div>
      </LuxuryCard>
    </div>
  );

  const renderParticipantsStep = () => (
    <div className="space-y-8">
      <LuxuryCard className="p-8">
        <h3 className="text-xl font-bold mb-6 text-gold-400">Participant Criteria</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Minimum Net Worth Requirement
            </label>
            <input
              type="number"
              value={participantCriteria.minimumNetWorth}
              onChange={(e) => setParticipantCriteria({
                ...participantCriteria,
                minimumNetWorth: parseInt(e.target.value)
              })}
              className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                       focus:border-gold-500 focus:outline-none"
            />
            <p className="text-xs text-gray-400 mt-1">
              Current: {formatCurrency(participantCriteria.minimumNetWorth)}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Maximum Exposure Per Participant (%)
            </label>
            <input
              type="number"
              value={participantCriteria.maxExposurePerParticipant}
              onChange={(e) => setParticipantCriteria({
                ...participantCriteria,
                maxExposurePerParticipant: parseInt(e.target.value)
              })}
              className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                       focus:border-gold-500 focus:outline-none"
              min="1"
              max="50"
            />
          </div>
        </div>

        <div className="mt-6">
          <h4 className="text-lg font-semibold mb-4">Tier Access</h4>
          <div className="flex space-x-4">
            {[
              { tier: InvestmentTier.ONYX, label: 'Onyx', color: 'border-gray-500' },
              { tier: InvestmentTier.OBSIDIAN, label: 'Obsidian', color: 'border-purple-500' },
              { tier: InvestmentTier.VOID, label: 'Void', color: 'border-black' },
            ].map(({ tier, label, color }) => (
              <label key={tier} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={participantCriteria.tierRestrictions.includes(tier)}
                  onChange={(e) => {
                    const tiers = e.target.checked
                      ? [...participantCriteria.tierRestrictions, tier]
                      : participantCriteria.tierRestrictions.filter(t => t !== tier);
                    setParticipantCriteria({
                      ...participantCriteria,
                      tierRestrictions: tiers
                    });
                  }}
                  className="rounded border-gold-500/30 bg-black/50 text-gold-500 focus:ring-gold-500"
                />
                <span className={`px-3 py-1 rounded border ${color} text-sm`}>{label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <h4 className="text-lg font-semibold mb-4">Additional Requirements</h4>
          <div className="space-y-3">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={participantCriteria.accreditationRequired}
                onChange={(e) => setParticipantCriteria({
                  ...participantCriteria,
                  accreditationRequired: e.target.checked
                })}
                className="rounded border-gold-500/30 bg-black/50 text-gold-500 focus:ring-gold-500"
              />
              <span className="text-sm text-gray-300">Accredited investor status required</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={participantCriteria.institutionalOnly}
                onChange={(e) => setParticipantCriteria({
                  ...participantCriteria,
                  institutionalOnly: e.target.checked
                })}
                className="rounded border-gold-500/30 bg-black/50 text-gold-500 focus:ring-gold-500"
              />
              <span className="text-sm text-gray-300">Institutional investors only</span>
            </label>
          </div>
        </div>
      </LuxuryCard>
    </div>
  );

  const renderReviewStep = () => (
    <div className="space-y-8">
      <LuxuryCard className="p-8">
        <h3 className="text-xl font-bold mb-6 text-gold-400">Syndicate Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h4 className="text-lg font-semibold mb-4">Investment Details</h4>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Opportunity:</span>
                <span className="text-white">{opportunity.title}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Lead Commitment:</span>
                <span className="text-white">{formatCurrency(syndicateConfig.leadCommitment)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Syndicate Size:</span>
                <span className="text-white">
                  {syndicateConfig.minimumSyndicateSize}-{syndicateConfig.maximumSyndicateSize} participants
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Governance:</span>
                <span className="text-white">
                  {governanceOptions.find(g => g.value === syndicateConfig.governanceStructure)?.label}
                </span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-4">Structure Details</h4>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">SPV Name:</span>
                <span className="text-white">{anonymousStructure.spvName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Jurisdiction:</span>
                <span className="text-white">
                  {jurisdictionOptions.find(j => j.value === anonymousStructure.jurisdiction)?.label}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Compliance Level:</span>
                <span className="text-white capitalize">{anonymousStructure.complianceLevel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Min Net Worth:</span>
                <span className="text-white">{formatCurrency(participantCriteria.minimumNetWorth)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <h4 className="text-lg font-semibold mb-4">Fee Structure</h4>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="text-center p-4 bg-black/30 rounded-lg">
              <div className="text-gold-400 font-semibold">{syndicateConfig.feeStructure.managementFee}%</div>
              <div className="text-gray-400">Management Fee</div>
            </div>
            <div className="text-center p-4 bg-black/30 rounded-lg">
              <div className="text-gold-400 font-semibold">{syndicateConfig.feeStructure.carriedInterest}%</div>
              <div className="text-gray-400">Carried Interest</div>
            </div>
            <div className="text-center p-4 bg-black/30 rounded-lg">
              <div className="text-gold-400 font-semibold">
                {formatCurrency(syndicateConfig.feeStructure.adminFee)}
              </div>
              <div className="text-gray-400">Admin Fee</div>
            </div>
          </div>
        </div>

        {validationErrors.length > 0 && (
          <div className="mt-6 p-4 bg-red-900/30 border border-red-500/50 rounded-lg">
            <h5 className="text-red-400 font-semibold mb-2">Validation Errors:</h5>
            <ul className="text-red-300 text-sm space-y-1">
              {validationErrors.map((error, index) => (
                <li key={index}>• {error}</li>
              ))}
            </ul>
          </div>
        )}
      </LuxuryCard>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderConfigurationStep();
      case 2:
        return renderStructureStep();
      case 3:
        return renderParticipantsStep();
      case 4:
        return renderReviewStep();
      default:
        return renderConfigurationStep();
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gold-400 to-gold-600 bg-clip-text text-transparent">
          Create Investment Syndicate
        </h1>
        <p className="text-lg text-gray-300">
          Form a syndicate for {opportunity.title} • {leadInvestorTier.toUpperCase()} Tier Lead
        </p>
      </div>

      {/* Step Indicator */}
      {renderStepIndicator()}

      {/* Main Content */}
      {renderCurrentStep()}

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center">
        <div className="flex space-x-4">
          <button
            onClick={onCancel}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors"
          >
            Cancel
          </button>
          {currentStep > 1 && (
            <button
              onClick={() => setCurrentStep(currentStep - 1)}
              className="px-6 py-3 bg-gold-500/20 text-gold-400 rounded-lg hover:bg-gold-500/30 transition-colors"
            >
              Previous
            </button>
          )}
        </div>

        <div>
          {currentStep < 4 ? (
            <button
              onClick={() => setCurrentStep(currentStep + 1)}
              className="px-8 py-3 bg-gradient-to-r from-gold-500 to-gold-600 text-black font-bold rounded-lg
                       hover:from-gold-400 hover:to-gold-500 transition-all duration-300"
            >
              Next: {['Structure', 'Participants', 'Review'][currentStep - 1]}
            </button>
          ) : (
            <button
              onClick={handleCreateSyndicate}
              disabled={isCreating || validationErrors.length > 0}
              className="px-8 py-3 bg-gradient-to-r from-gold-500 to-gold-600 text-black font-bold rounded-lg
                       hover:from-gold-400 hover:to-gold-500 transition-all duration-300
                       disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isCreating ? 'Creating Syndicate...' : 'Create Syndicate'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};