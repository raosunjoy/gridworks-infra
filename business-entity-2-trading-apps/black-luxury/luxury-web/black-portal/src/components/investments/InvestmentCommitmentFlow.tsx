/**
 * Investment Commitment Flow
 * Multi-step investment commitment process with anonymous structure setup,
 * KYC verification, and payment orchestration for Black-tier clients
 */

import React, { useState, useEffect } from 'react';
import { InvestmentOpportunity, InvestmentTier, InvestmentCommitment } from '../../services/InvestmentSyndicateEngine';
import { LuxuryCard } from '../ui/LuxuryCard';
import { TierGlow } from '../ui/TierGlow';

interface InvestmentCommitmentFlowProps {
  opportunity: InvestmentOpportunity;
  clientTier: InvestmentTier;
  anonymousId: string;
  onCommitmentComplete: (commitment: InvestmentCommitment) => void;
  onCancel: () => void;
}

type FlowStep = 'commitment' | 'structure' | 'verification' | 'payment' | 'confirmation';

interface CommitmentData {
  amount: number;
  investmentVehicle: 'direct' | 'spv' | 'fund' | 'trust';
  anonymousStructure: {
    holdingCompany: string;
    jurisdictions: string[];
    beneficialOwnership: 'masked' | 'nominee' | 'trust';
    taxOptimization: string[];
  };
  fundingSource: {
    method: 'bank_transfer' | 'cryptocurrency' | 'existing_portfolio';
    details: Record<string, any>;
  };
  kycDocuments: File[];
  riskAcknowledgment: boolean;
  termsAccepted: boolean;
}

export const InvestmentCommitmentFlow: React.FC<InvestmentCommitmentFlowProps> = ({
  opportunity,
  clientTier,
  anonymousId,
  onCommitmentComplete,
  onCancel,
}) => {
  const [currentStep, setCurrentStep] = useState<FlowStep>('commitment');
  const [commitmentData, setCommitmentData] = useState<Partial<CommitmentData>>({
    amount: opportunity.minimumInvestment,
    investmentVehicle: 'spv',
    anonymousStructure: {
      holdingCompany: '',
      jurisdictions: ['Mauritius', 'Singapore', 'Netherlands'],
      beneficialOwnership: 'nominee',
      taxOptimization: ['Treaty benefits', 'Capital gains optimization'],
    },
    fundingSource: {
      method: 'bank_transfer',
      details: {},
    },
    kycDocuments: [],
    riskAcknowledgment: false,
    termsAccepted: false,
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const steps: { key: FlowStep; title: string; description: string }[] = [
    { key: 'commitment', title: 'Investment Details', description: 'Specify investment amount and preferences' },
    { key: 'structure', title: 'Anonymous Structure', description: 'Configure anonymous investment vehicle' },
    { key: 'verification', title: 'KYC & Compliance', description: 'Upload required documentation' },
    { key: 'payment', title: 'Payment Setup', description: 'Configure funding source and schedule' },
    { key: 'confirmation', title: 'Review & Confirm', description: 'Final review and commitment confirmation' },
  ];

  const formatCurrency = (amount: number) => {
    const crores = amount / 10000000;
    return `₹${crores.toLocaleString('en-IN')} Cr`;
  };

  const validateCurrentStep = () => {
    const newErrors: Record<string, string> = {};

    switch (currentStep) {
      case 'commitment':
        if (!commitmentData.amount || commitmentData.amount < opportunity.minimumInvestment) {
          newErrors.amount = `Minimum investment is ${formatCurrency(opportunity.minimumInvestment)}`;
        }
        if (commitmentData.amount && commitmentData.amount > opportunity.maximumInvestment) {
          newErrors.amount = `Maximum investment is ${formatCurrency(opportunity.maximumInvestment)}`;
        }
        break;

      case 'structure':
        if (!commitmentData.anonymousStructure?.holdingCompany) {
          newErrors.holdingCompany = 'Holding company name is required';
        }
        break;

      case 'verification':
        if (!commitmentData.kycDocuments || commitmentData.kycDocuments.length === 0) {
          newErrors.kycDocuments = 'At least one KYC document is required';
        }
        if (!commitmentData.riskAcknowledgment) {
          newErrors.riskAcknowledgment = 'Risk acknowledgment is required';
        }
        break;

      case 'payment':
        if (!commitmentData.fundingSource?.details.accountVerified && commitmentData.fundingSource?.method === 'bank_transfer') {
          newErrors.fundingSource = 'Bank account verification is required';
        }
        break;

      case 'confirmation':
        if (!commitmentData.termsAccepted) {
          newErrors.termsAccepted = 'Terms and conditions must be accepted';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateCurrentStep()) {
      const stepIndex = steps.findIndex(s => s.key === currentStep);
      if (stepIndex < steps.length - 1) {
        setCurrentStep(steps[stepIndex + 1].key);
      }
    }
  };

  const prevStep = () => {
    const stepIndex = steps.findIndex(s => s.key === currentStep);
    if (stepIndex > 0) {
      setCurrentStep(steps[stepIndex - 1].key);
    }
  };

  const submitCommitment = async () => {
    if (!validateCurrentStep()) return;

    setIsProcessing(true);
    try {
      // In real implementation, this would call the InvestmentSyndicateEngine
      const mockCommitment: InvestmentCommitment = {
        id: `commit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        investmentOpportunityId: opportunity.id,
        clientId: 'anonymous-client-id',
        anonymousId,
        tier: clientTier,
        commitmentAmount: commitmentData.amount!,
        currency: opportunity.currency,
        commitmentDate: new Date().toISOString(),
        investmentVehicle: commitmentData.investmentVehicle!,
        anonymousStructure: commitmentData.anonymousStructure!,
        kycStatus: 'pending',
        amlChecks: false,
        accreditationStatus: 'verified',
        legalDocumentation: {
          signed: false,
          documentsReceived: [],
          pendingDocuments: ['Subscription Agreement', 'KYC Documentation'],
        },
        paymentSchedule: [
          {
            installment: 1,
            amount: commitmentData.amount! / 3,
            dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'pending',
          },
          {
            installment: 2,
            amount: commitmentData.amount! / 3,
            dueDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'pending',
          },
          {
            installment: 3,
            amount: commitmentData.amount! / 3,
            dueDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'pending',
          },
        ],
        fundingSource: commitmentData.fundingSource!,
        status: 'draft',
        allocationConfirmed: false,
        investmentConfirmation: '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      onCommitmentComplete(mockCommitment);
    } catch (error) {
      console.error('Failed to create investment commitment:', error);
      setErrors({ submit: 'Failed to process commitment. Please try again.' });
    } finally {
      setIsProcessing(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 'commitment':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-4">Investment Amount</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Investment Amount (₹ Crores)
                  </label>
                  <input
                    type="number"
                    min={opportunity.minimumInvestment / 10000000}
                    max={opportunity.maximumInvestment / 10000000}
                    step="0.1"
                    value={(commitmentData.amount || 0) / 10000000}
                    onChange={(e) => setCommitmentData({
                      ...commitmentData,
                      amount: parseFloat(e.target.value) * 10000000
                    })}
                    className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                             focus:border-gold-500 focus:outline-none"
                  />
                  {errors.amount && (
                    <div className="text-red-400 text-sm mt-1">{errors.amount}</div>
                  )}
                  <div className="text-gray-400 text-sm mt-1">
                    Range: {formatCurrency(opportunity.minimumInvestment)} - {formatCurrency(opportunity.maximumInvestment)}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Investment Vehicle
                  </label>
                  <select
                    value={commitmentData.investmentVehicle}
                    onChange={(e) => setCommitmentData({
                      ...commitmentData,
                      investmentVehicle: e.target.value as 'direct' | 'spv' | 'fund' | 'trust'
                    })}
                    className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                             focus:border-gold-500 focus:outline-none"
                  >
                    <option value="spv">Special Purpose Vehicle (SPV)</option>
                    <option value="fund">Investment Fund</option>
                    <option value="trust">Trust Structure</option>
                    <option value="direct">Direct Investment</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="bg-gold-500/10 border border-gold-500/30 rounded-lg p-4">
              <h4 className="font-semibold text-gold-400 mb-2">Investment Summary</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Amount:</span>
                  <span className="text-white ml-2">{formatCurrency(commitmentData.amount || 0)}</span>
                </div>
                <div>
                  <span className="text-gray-400">Vehicle:</span>
                  <span className="text-white ml-2">{commitmentData.investmentVehicle?.toUpperCase()}</span>
                </div>
                <div>
                  <span className="text-gray-400">Expected Returns:</span>
                  <span className="text-green-400 ml-2">{opportunity.expectedReturns.conservative}-{opportunity.expectedReturns.optimistic}</span>
                </div>
                <div>
                  <span className="text-gray-400">Lock-up Period:</span>
                  <span className="text-white ml-2">{opportunity.lockupPeriod}</span>
                </div>
              </div>
            </div>
          </div>
        );

      case 'structure':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-4">Anonymous Investment Structure</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Holding Company Name
                  </label>
                  <input
                    type="text"
                    value={commitmentData.anonymousStructure?.holdingCompany || ''}
                    onChange={(e) => setCommitmentData({
                      ...commitmentData,
                      anonymousStructure: {
                        ...commitmentData.anonymousStructure!,
                        holdingCompany: e.target.value
                      }
                    })}
                    placeholder="e.g., BlackPortal Holdings Ltd"
                    className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                             focus:border-gold-500 focus:outline-none"
                  />
                  {errors.holdingCompany && (
                    <div className="text-red-400 text-sm mt-1">{errors.holdingCompany}</div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Beneficial Ownership Structure
                  </label>
                  <select
                    value={commitmentData.anonymousStructure?.beneficialOwnership}
                    onChange={(e) => setCommitmentData({
                      ...commitmentData,
                      anonymousStructure: {
                        ...commitmentData.anonymousStructure!,
                        beneficialOwnership: e.target.value as 'masked' | 'nominee' | 'trust'
                      }
                    })}
                    className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                             focus:border-gold-500 focus:outline-none"
                  >
                    <option value="nominee">Nominee Structure</option>
                    <option value="trust">Trust Structure</option>
                    <option value="masked">Masked Ownership</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Jurisdictions
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {['Mauritius', 'Singapore', 'Netherlands', 'Luxembourg', 'Ireland', 'Cayman Islands'].map((jurisdiction) => (
                      <label key={jurisdiction} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={commitmentData.anonymousStructure?.jurisdictions.includes(jurisdiction)}
                          onChange={(e) => {
                            const current = commitmentData.anonymousStructure?.jurisdictions || [];
                            const updated = e.target.checked
                              ? [...current, jurisdiction]
                              : current.filter(j => j !== jurisdiction);
                            setCommitmentData({
                              ...commitmentData,
                              anonymousStructure: {
                                ...commitmentData.anonymousStructure!,
                                jurisdictions: updated
                              }
                            });
                          }}
                          className="rounded border-gold-500/30 bg-black/50 text-gold-500 focus:ring-gold-500"
                        />
                        <span className="text-sm text-gray-300">{jurisdiction}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
              <h4 className="font-semibold text-purple-400 mb-2">Anonymity Features</h4>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• Zero-knowledge proof validation for identity verification</li>
                <li>• Multi-layered nominee structure for ownership masking</li>
                <li>• Encrypted communication channels for all interactions</li>
                <li>• Tax-optimized structure across multiple jurisdictions</li>
              </ul>
            </div>
          </div>
        );

      case 'verification':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-4">KYC & Compliance Verification</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Upload KYC Documents
                  </label>
                  <div className="border-2 border-dashed border-gold-500/30 rounded-lg p-6 text-center">
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => setCommitmentData({
                        ...commitmentData,
                        kycDocuments: Array.from(e.target.files || [])
                      })}
                      className="hidden"
                      id="kyc-upload"
                    />
                    <label htmlFor="kyc-upload" className="cursor-pointer">
                      <div className="text-gold-400 mb-2">
                        <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                      </div>
                      <div className="text-white">Click to upload documents</div>
                      <div className="text-gray-400 text-sm">PDF, JPG, PNG up to 10MB each</div>
                    </label>
                  </div>
                  {commitmentData.kycDocuments && commitmentData.kycDocuments.length > 0 && (
                    <div className="mt-2">
                      <h5 className="text-sm font-medium text-gray-300 mb-1">Uploaded Files:</h5>
                      {commitmentData.kycDocuments.map((file, index) => (
                        <div key={index} className="text-sm text-gray-400">• {file.name}</div>
                      ))}
                    </div>
                  )}
                  {errors.kycDocuments && (
                    <div className="text-red-400 text-sm mt-1">{errors.kycDocuments}</div>
                  )}
                </div>

                <div className="space-y-3">
                  <label className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      checked={commitmentData.riskAcknowledgment}
                      onChange={(e) => setCommitmentData({
                        ...commitmentData,
                        riskAcknowledgment: e.target.checked
                      })}
                      className="mt-1 rounded border-gold-500/30 bg-black/50 text-gold-500 focus:ring-gold-500"
                    />
                    <span className="text-sm text-gray-300">
                      I acknowledge that this is a high-risk investment and I understand all risk factors
                      including potential total loss of capital, illiquidity, and regulatory changes.
                    </span>
                  </label>
                  {errors.riskAcknowledgment && (
                    <div className="text-red-400 text-sm">{errors.riskAcknowledgment}</div>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <h4 className="font-semibold text-blue-400 mb-2">Required Documents</h4>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• Valid government-issued photo ID</li>
                <li>• Proof of address (recent utility bill or bank statement)</li>
                <li>• Bank account verification documents</li>
                <li>• Accredited investor certification (if applicable)</li>
                <li>• Source of funds declaration</li>
              </ul>
            </div>
          </div>
        );

      case 'payment':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-4">Payment Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Funding Source
                  </label>
                  <select
                    value={commitmentData.fundingSource?.method}
                    onChange={(e) => setCommitmentData({
                      ...commitmentData,
                      fundingSource: {
                        method: e.target.value as 'bank_transfer' | 'cryptocurrency' | 'existing_portfolio',
                        details: {}
                      }
                    })}
                    className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                             focus:border-gold-500 focus:outline-none"
                  >
                    <option value="bank_transfer">Bank Wire Transfer</option>
                    <option value="cryptocurrency">Cryptocurrency</option>
                    <option value="existing_portfolio">Existing Portfolio Transfer</option>
                  </select>
                </div>

                {commitmentData.fundingSource?.method === 'bank_transfer' && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Bank Account Details
                      </label>
                      <input
                        type="text"
                        placeholder="Account Number"
                        className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                                 focus:border-gold-500 focus:outline-none mb-2"
                      />
                      <input
                        type="text"
                        placeholder="SWIFT/IBAN Code"
                        className="w-full px-4 py-3 bg-black/50 border border-gold-500/30 rounded-lg text-white
                                 focus:border-gold-500 focus:outline-none"
                      />
                    </div>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        onChange={(e) => setCommitmentData({
                          ...commitmentData,
                          fundingSource: {
                            ...commitmentData.fundingSource!,
                            details: { accountVerified: e.target.checked }
                          }
                        })}
                        className="rounded border-gold-500/30 bg-black/50 text-gold-500 focus:ring-gold-500"
                      />
                      <span className="text-sm text-gray-300">Account verified and approved for transfers</span>
                    </label>
                  </div>
                )}

                <div>
                  <h4 className="font-medium text-gray-300 mb-3">Payment Schedule</h4>
                  <div className="space-y-2">
                    {[1, 2, 3].map((installment) => (
                      <div key={installment} className="flex justify-between items-center p-3 bg-black/30 rounded-lg">
                        <span className="text-gray-300">Installment {installment}</span>
                        <span className="text-white font-medium">
                          {formatCurrency((commitmentData.amount || 0) / 3)}
                        </span>
                        <span className="text-gray-400 text-sm">
                          Due: {new Date(Date.now() + installment * 30 * 24 * 60 * 60 * 1000).toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'confirmation':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-4">Review & Confirmation</h3>
              
              <div className="space-y-4">
                <LuxuryCard className="p-4">
                  <h4 className="font-semibold text-gold-400 mb-3">Investment Summary</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Opportunity:</span>
                      <div className="text-white font-medium">{opportunity.title}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Investment Amount:</span>
                      <div className="text-white font-medium">{formatCurrency(commitmentData.amount || 0)}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Vehicle:</span>
                      <div className="text-white font-medium">{commitmentData.investmentVehicle?.toUpperCase()}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Holding Company:</span>
                      <div className="text-white font-medium">{commitmentData.anonymousStructure?.holdingCompany}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Funding Method:</span>
                      <div className="text-white font-medium">{commitmentData.fundingSource?.method?.replace('_', ' ').toUpperCase()}</div>
                    </div>
                    <div>
                      <span className="text-gray-400">Expected Returns:</span>
                      <div className="text-green-400 font-medium">{opportunity.expectedReturns.conservative}-{opportunity.expectedReturns.optimistic}</div>
                    </div>
                  </div>
                </LuxuryCard>

                <div className="space-y-3">
                  <label className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      checked={commitmentData.termsAccepted}
                      onChange={(e) => setCommitmentData({
                        ...commitmentData,
                        termsAccepted: e.target.checked
                      })}
                      className="mt-1 rounded border-gold-500/30 bg-black/50 text-gold-500 focus:ring-gold-500"
                    />
                    <span className="text-sm text-gray-300">
                      I have read and accept the Investment Terms & Conditions, Subscription Agreement,
                      and all related legal documentation. I understand this commitment is binding
                      and subject to the terms outlined in the offering materials.
                    </span>
                  </label>
                  {errors.termsAccepted && (
                    <div className="text-red-400 text-sm">{errors.termsAccepted}</div>
                  )}
                </div>
              </div>
            </div>

            {errors.submit && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                <div className="text-red-400">{errors.submit}</div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Investment Commitment</h1>
        <p className="text-gray-400">{opportunity.title}</p>
      </div>

      {/* Progress Indicator */}
      <div className="flex items-center justify-between mb-8">
        {steps.map((step, index) => {
          const isActive = step.key === currentStep;
          const isCompleted = steps.findIndex(s => s.key === currentStep) > index;
          
          return (
            <div key={step.key} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 
                ${isActive ? 'bg-gold-500 border-gold-500 text-black' : 
                  isCompleted ? 'bg-green-500 border-green-500 text-white' : 
                  'border-gray-600 text-gray-400'}`}>
                {isCompleted ? '✓' : index + 1}
              </div>
              <div className="ml-3 min-w-0">
                <div className={`text-sm font-medium ${isActive ? 'text-gold-400' : isCompleted ? 'text-green-400' : 'text-gray-400'}`}>
                  {step.title}
                </div>
                <div className="text-xs text-gray-500">{step.description}</div>
              </div>
              {index < steps.length - 1 && (
                <div className={`w-12 h-0.5 mx-4 ${isCompleted ? 'bg-green-500' : 'bg-gray-600'}`} />
              )}
            </div>
          );
        })}
      </div>

      {/* Step Content */}
      <LuxuryCard className="p-8">
        {renderStepContent()}
      </LuxuryCard>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={currentStep === 'commitment' ? onCancel : prevStep}
          className="px-6 py-3 border border-gray-600 text-gray-300 rounded-lg hover:border-gray-500 transition-colors"
        >
          {currentStep === 'commitment' ? 'Cancel' : 'Previous'}
        </button>

        <button
          onClick={currentStep === 'confirmation' ? submitCommitment : nextStep}
          disabled={isProcessing}
          className="px-8 py-3 bg-gradient-to-r from-gold-500 to-gold-600 text-black font-bold rounded-lg
                   hover:from-gold-400 hover:to-gold-500 transition-all duration-300 disabled:opacity-50"
        >
          {isProcessing ? 'Processing...' : currentStep === 'confirmation' ? 'Submit Commitment' : 'Next'}
        </button>
      </div>
    </div>
  );
};