/**
 * Service Proposal Creation Form
 * Comprehensive form for creating new service proposals with validation
 */

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ServiceProposal,
  ServiceCategory,
  RiskLevel,
  TierAccess,
  User,
  ServiceProposalSchema,
} from '@/types/service-management';
import { z } from 'zod';

interface ServiceProposalFormProps {
  currentUser: User;
  onSubmit: (proposal: Partial<ServiceProposal>) => Promise<void>;
  onCancel: () => void;
  initialData?: Partial<ServiceProposal>;
  mode?: 'create' | 'edit';
}

export const ServiceProposalForm: React.FC<ServiceProposalFormProps> = ({
  currentUser,
  onSubmit,
  onCancel,
  initialData,
  mode = 'create',
}) => {
  const [formData, setFormData] = useState<Partial<ServiceProposal>>({
    title: '',
    description: '',
    category: ServiceCategory.PRE_IPO_FUNDS,
    tierAccess: TierAccess.ALL_TIERS,
    riskLevel: RiskLevel.MEDIUM,
    provider: {
      id: '',
      name: '',
      legalName: '',
      registrationNumber: '',
      jurisdiction: 'India',
      website: '',
      primaryContact: {
        name: '',
        email: '',
        phone: '',
        title: '',
      },
      businessLicense: '',
      insuranceCoverage: {
        provider: '',
        policyNumber: '',
        coverage: 0,
        expiryDate: '',
      },
      financialHealth: {
        creditRating: '',
        auditedFinancials: false,
        lastAuditDate: '',
        netWorth: 0,
      },
    },
    serviceDetails: {
      fees: {
        managementFee: 0,
        performanceFee: 0,
        entryFee: 0,
        exitFee: 0,
      },
    },
    complianceDocuments: [],
    riskAssessment: {
      overallRisk: RiskLevel.MEDIUM,
      marketRisk: RiskLevel.MEDIUM,
      liquidityRisk: RiskLevel.MEDIUM,
      operationalRisk: RiskLevel.MEDIUM,
      regulatoryRisk: RiskLevel.MEDIUM,
      riskMitigationMeasures: [],
    },
    dueDiligence: {
      backgroundCheckCompleted: false,
      financialAuditCompleted: false,
      legalReviewCompleted: false,
      regulatoryApprovalObtained: false,
      referencesVerified: false,
    },
    anonymityFeatures: {
      zkProofCompatible: false,
      anonymousTransactions: false,
      identityShielding: false,
      communicationProtocol: '',
    },
    reviewStages: [],
    approvals: [],
    onboardingTimeline: '',
    integrationRequirements: [],
    supportRequirements: '',
    expectedVolume: {
      monthly: 0,
      annual: 0,
    },
    successMetrics: [],
    ...initialData,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedDocs, setUploadedDocs] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const totalSteps = 6;

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1: // Basic Information
        if (!formData.title?.trim()) newErrors.title = 'Title is required';
        if (!formData.description?.trim()) newErrors.description = 'Description is required';
        if (!formData.provider?.name?.trim()) newErrors.providerName = 'Provider name is required';
        if (!formData.provider?.legalName?.trim()) newErrors.providerLegalName = 'Legal name is required';
        break;

      case 2: // Provider Details
        if (!formData.provider?.registrationNumber?.trim()) {
          newErrors.registrationNumber = 'Registration number is required';
        }
        if (!formData.provider?.website?.trim()) {
          newErrors.website = 'Website is required';
        } else if (!formData.provider.website.match(/^https?:\/\/.*$/)) {
          newErrors.website = 'Please enter a valid URL starting with http:// or https://';
        }
        if (!formData.provider?.primaryContact?.email?.trim()) {
          newErrors.contactEmail = 'Contact email is required';
        }
        break;

      case 3: // Financial & Insurance
        if ((formData.provider?.financialHealth?.netWorth || 0) < 50000000) {
          newErrors.netWorth = 'Net worth must be at least ₹5 Crores';
        }
        if (!formData.provider?.insuranceCoverage?.provider?.trim()) {
          newErrors.insuranceProvider = 'Insurance provider is required';
        }
        break;

      case 4: // Service Details
        if (formData.serviceDetails?.fees?.managementFee === undefined) {
          newErrors.managementFee = 'Management fee is required';
        }
        break;

      case 5: // Risk Assessment
        if (!formData.riskAssessment?.riskMitigationMeasures?.length) {
          newErrors.riskMitigation = 'At least one risk mitigation measure is required';
        }
        break;

      case 6: // Final Review
        // No additional validation needed
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setIsSubmitting(true);
    try {
      // Validate entire form using Zod schema
      const validatedData = ServiceProposalSchema.parse({
        ...formData,
        id: formData.id || `proposal-${Date.now()}`,
        proposalNumber: formData.proposalNumber || `SP-${Date.now()}`,
        status: 'draft',
        submittedBy: currentUser.id,
        submittedAt: new Date().toISOString(),
      });

      await onSubmit(validatedData);
    } catch (error) {
      if (error instanceof z.ZodError) {
        const zodErrors: Record<string, string> = {};
        error.errors.forEach(err => {
          const path = err.path.join('.');
          zodErrors[path] = err.message;
        });
        setErrors(zodErrors);
      } else {
        console.error('Submission error:', error);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setUploadedDocs(prev => [...prev, ...files]);

    // Add documents to form data
    const newDocs = files.map(file => ({
      type: 'compliance_document',
      name: file.name,
      url: URL.createObjectURL(file),
      uploadDate: new Date().toISOString(),
      verified: false,
    }));

    setFormData(prev => ({
      ...prev,
      complianceDocuments: [...(prev.complianceDocuments || []), ...newDocs],
    }));
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Basic Information</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Service Title *
              </label>
              <input
                type="text"
                value={formData.title || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="e.g., SpaceX Pre-IPO Investment Fund"
              />
              {errors.title && <p className="text-red-400 text-sm mt-1">{errors.title}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description *
              </label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={4}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="Detailed description of the service offering..."
              />
              {errors.description && <p className="text-red-400 text-sm mt-1">{errors.description}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Category *
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as ServiceCategory }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                >
                  {Object.values(ServiceCategory).map(category => (
                    <option key={category} value={category}>
                      {category.replace(/_/g, ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tier Access *
                </label>
                <select
                  value={formData.tierAccess}
                  onChange={(e) => setFormData(prev => ({ ...prev, tierAccess: e.target.value as TierAccess }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                >
                  {Object.values(TierAccess).map(tier => (
                    <option key={tier} value={tier}>
                      {tier.replace(/_/g, ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Risk Level *
                </label>
                <select
                  value={formData.riskLevel}
                  onChange={(e) => setFormData(prev => ({ ...prev, riskLevel: e.target.value as RiskLevel }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                >
                  {Object.values(RiskLevel).map(risk => (
                    <option key={risk} value={risk}>
                      {risk.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Provider Name *
              </label>
              <input
                type="text"
                value={formData.provider?.name || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  provider: { ...prev.provider!, name: e.target.value }
                }))}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="Company name"
              />
              {errors.providerName && <p className="text-red-400 text-sm mt-1">{errors.providerName}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Legal Name *
              </label>
              <input
                type="text"
                value={formData.provider?.legalName || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  provider: { ...prev.provider!, legalName: e.target.value }
                }))}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="Legal company name as registered"
              />
              {errors.providerLegalName && <p className="text-red-400 text-sm mt-1">{errors.providerLegalName}</p>}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Provider Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Registration Number *
                </label>
                <input
                  type="text"
                  value={formData.provider?.registrationNumber || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    provider: { ...prev.provider!, registrationNumber: e.target.value }
                  }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="Company registration number"
                />
                {errors.registrationNumber && <p className="text-red-400 text-sm mt-1">{errors.registrationNumber}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Jurisdiction
                </label>
                <input
                  type="text"
                  value={formData.provider?.jurisdiction || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    provider: { ...prev.provider!, jurisdiction: e.target.value }
                  }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="Country/State of incorporation"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Website *
              </label>
              <input
                type="url"
                value={formData.provider?.website || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  provider: { ...prev.provider!, website: e.target.value }
                }))}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="https://company.com"
              />
              {errors.website && <p className="text-red-400 text-sm mt-1">{errors.website}</p>}
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-4">Primary Contact</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Contact Name
                  </label>
                  <input
                    type="text"
                    value={formData.provider?.primaryContact?.name || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        primaryContact: { ...prev.provider!.primaryContact!, name: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="Full name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Title
                  </label>
                  <input
                    type="text"
                    value={formData.provider?.primaryContact?.title || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        primaryContact: { ...prev.provider!.primaryContact!, title: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="Job title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={formData.provider?.primaryContact?.email || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        primaryContact: { ...prev.provider!.primaryContact!, email: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="email@company.com"
                  />
                  {errors.contactEmail && <p className="text-red-400 text-sm mt-1">{errors.contactEmail}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={formData.provider?.primaryContact?.phone || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        primaryContact: { ...prev.provider!.primaryContact!, phone: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="+91 98765 43210"
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Financial & Insurance</h3>
            
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-4">Financial Health</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Net Worth (₹) *
                  </label>
                  <input
                    type="number"
                    value={formData.provider?.financialHealth?.netWorth || 0}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        financialHealth: { ...prev.provider!.financialHealth!, netWorth: Number(e.target.value) }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="50000000"
                    min="0"
                  />
                  {errors.netWorth && <p className="text-red-400 text-sm mt-1">{errors.netWorth}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Credit Rating
                  </label>
                  <input
                    type="text"
                    value={formData.provider?.financialHealth?.creditRating || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        financialHealth: { ...prev.provider!.financialHealth!, creditRating: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="AAA, AA+, etc."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Last Audit Date
                  </label>
                  <input
                    type="date"
                    value={formData.provider?.financialHealth?.lastAuditDate || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        financialHealth: { ...prev.provider!.financialHealth!, lastAuditDate: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="auditedFinancials"
                    checked={formData.provider?.financialHealth?.auditedFinancials || false}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        financialHealth: { ...prev.provider!.financialHealth!, auditedFinancials: e.target.checked }
                      }
                    }))}
                    className="w-4 h-4 text-yellow-600 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500"
                  />
                  <label htmlFor="auditedFinancials" className="ml-2 text-sm text-gray-300">
                    Audited Financials Available
                  </label>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-4">Insurance Coverage</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Insurance Provider *
                  </label>
                  <input
                    type="text"
                    value={formData.provider?.insuranceCoverage?.provider || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        insuranceCoverage: { ...prev.provider!.insuranceCoverage!, provider: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="Insurance company name"
                  />
                  {errors.insuranceProvider && <p className="text-red-400 text-sm mt-1">{errors.insuranceProvider}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Policy Number
                  </label>
                  <input
                    type="text"
                    value={formData.provider?.insuranceCoverage?.policyNumber || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        insuranceCoverage: { ...prev.provider!.insuranceCoverage!, policyNumber: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="Policy number"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Coverage Amount (₹)
                  </label>
                  <input
                    type="number"
                    value={formData.provider?.insuranceCoverage?.coverage || 0}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        insuranceCoverage: { ...prev.provider!.insuranceCoverage!, coverage: Number(e.target.value) }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="10000000"
                    min="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Expiry Date
                  </label>
                  <input
                    type="date"
                    value={formData.provider?.insuranceCoverage?.expiryDate || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      provider: {
                        ...prev.provider!,
                        insuranceCoverage: { ...prev.provider!.insuranceCoverage!, expiryDate: e.target.value }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Service Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Minimum Investment (₹)
                </label>
                <input
                  type="number"
                  value={formData.serviceDetails?.minimumInvestment || 0}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    serviceDetails: { ...prev.serviceDetails!, minimumInvestment: Number(e.target.value) }
                  }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="1000000"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Maximum Investment (₹)
                </label>
                <input
                  type="number"
                  value={formData.serviceDetails?.maximumInvestment || 0}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    serviceDetails: { ...prev.serviceDetails!, maximumInvestment: Number(e.target.value) }
                  }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="100000000"
                  min="0"
                />
              </div>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-4">Fee Structure</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Management Fee (%) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.serviceDetails?.fees?.managementFee || 0}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      serviceDetails: {
                        ...prev.serviceDetails!,
                        fees: { ...prev.serviceDetails!.fees!, managementFee: Number(e.target.value) }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="2.00"
                    min="0"
                    max="100"
                  />
                  {errors.managementFee && <p className="text-red-400 text-sm mt-1">{errors.managementFee}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Performance Fee (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.serviceDetails?.fees?.performanceFee || 0}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      serviceDetails: {
                        ...prev.serviceDetails!,
                        fees: { ...prev.serviceDetails!.fees!, performanceFee: Number(e.target.value) }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="20.00"
                    min="0"
                    max="100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Entry Fee (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.serviceDetails?.fees?.entryFee || 0}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      serviceDetails: {
                        ...prev.serviceDetails!,
                        fees: { ...prev.serviceDetails!.fees!, entryFee: Number(e.target.value) }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="1.00"
                    min="0"
                    max="100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Exit Fee (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.serviceDetails?.fees?.exitFee || 0}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      serviceDetails: {
                        ...prev.serviceDetails!,
                        fees: { ...prev.serviceDetails!.fees!, exitFee: Number(e.target.value) }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    placeholder="0.50"
                    min="0"
                    max="100"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Expected Returns
                </label>
                <input
                  type="text"
                  value={formData.serviceDetails?.expectedReturns || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    serviceDetails: { ...prev.serviceDetails!, expectedReturns: e.target.value }
                  }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="15-25% annually"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Investment Period
                </label>
                <input
                  type="text"
                  value={formData.serviceDetails?.investmentPeriod || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    serviceDetails: { ...prev.serviceDetails!, investmentPeriod: e.target.value }
                  }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="3-5 years"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Liquidity Terms
              </label>
              <textarea
                value={formData.serviceDetails?.liquidityTerms || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  serviceDetails: { ...prev.serviceDetails!, liquidityTerms: e.target.value }
                }))}
                rows={3}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="Describe liquidity options and restrictions..."
              />
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Risk Assessment & Compliance</h3>
            
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-4">Risk Levels</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Market Risk
                  </label>
                  <select
                    value={formData.riskAssessment?.marketRisk}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      riskAssessment: { ...prev.riskAssessment!, marketRisk: e.target.value as RiskLevel }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  >
                    {Object.values(RiskLevel).map(risk => (
                      <option key={risk} value={risk}>
                        {risk.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Liquidity Risk
                  </label>
                  <select
                    value={formData.riskAssessment?.liquidityRisk}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      riskAssessment: { ...prev.riskAssessment!, liquidityRisk: e.target.value as RiskLevel }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  >
                    {Object.values(RiskLevel).map(risk => (
                      <option key={risk} value={risk}>
                        {risk.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Operational Risk
                  </label>
                  <select
                    value={formData.riskAssessment?.operationalRisk}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      riskAssessment: { ...prev.riskAssessment!, operationalRisk: e.target.value as RiskLevel }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  >
                    {Object.values(RiskLevel).map(risk => (
                      <option key={risk} value={risk}>
                        {risk.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Risk Mitigation Measures *
              </label>
              <textarea
                value={formData.riskAssessment?.riskMitigationMeasures?.join('\n') || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  riskAssessment: {
                    ...prev.riskAssessment!,
                    riskMitigationMeasures: e.target.value.split('\n').filter(m => m.trim())
                  }
                }))}
                rows={4}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="Enter each risk mitigation measure on a new line..."
              />
              {errors.riskMitigation && <p className="text-red-400 text-sm mt-1">{errors.riskMitigation}</p>}
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-4">Due Diligence Checklist</h4>
              
              <div className="space-y-3">
                {[
                  { key: 'backgroundCheckCompleted', label: 'Background Check Completed' },
                  { key: 'financialAuditCompleted', label: 'Financial Audit Completed' },
                  { key: 'legalReviewCompleted', label: 'Legal Review Completed' },
                  { key: 'regulatoryApprovalObtained', label: 'Regulatory Approval Obtained' },
                  { key: 'referencesVerified', label: 'References Verified' },
                ].map(({ key, label }) => (
                  <div key={key} className="flex items-center">
                    <input
                      type="checkbox"
                      id={key}
                      checked={formData.dueDiligence?.[key as keyof typeof formData.dueDiligence] || false}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        dueDiligence: { ...prev.dueDiligence!, [key]: e.target.checked }
                      }))}
                      className="w-4 h-4 text-yellow-600 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500"
                    />
                    <label htmlFor={key} className="ml-2 text-sm text-gray-300">
                      {label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-4">Anonymity Features</h4>
              
              <div className="space-y-3">
                {[
                  { key: 'zkProofCompatible', label: 'ZK Proof Compatible' },
                  { key: 'anonymousTransactions', label: 'Anonymous Transactions' },
                  { key: 'identityShielding', label: 'Identity Shielding' },
                ].map(({ key, label }) => (
                  <div key={key} className="flex items-center">
                    <input
                      type="checkbox"
                      id={key}
                      checked={formData.anonymityFeatures?.[key as keyof typeof formData.anonymityFeatures] || false}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        anonymityFeatures: { ...prev.anonymityFeatures!, [key]: e.target.checked }
                      }))}
                      className="w-4 h-4 text-yellow-600 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500"
                    />
                    <label htmlFor={key} className="ml-2 text-sm text-gray-300">
                      {label}
                    </label>
                  </div>
                ))}
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Communication Protocol
                </label>
                <input
                  type="text"
                  value={formData.anonymityFeatures?.communicationProtocol || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    anonymityFeatures: { ...prev.anonymityFeatures!, communicationProtocol: e.target.value }
                  }))}
                  className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="e.g., Butler AI mediated, End-to-end encrypted"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Upload Compliance Documents
              </label>
              <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  multiple
                  accept=".pdf,.doc,.docx,.jpg,.png"
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-yellow-400 hover:text-yellow-300 transition-colors"
                >
                  Click to upload or drag and drop
                </button>
                <p className="text-gray-400 text-sm mt-2">
                  PDF, DOC, DOCX, JPG, PNG files up to 10MB each
                </p>
                
                {uploadedDocs.length > 0 && (
                  <div className="mt-4 text-left">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Uploaded Files:</h4>
                    <div className="space-y-1">
                      {uploadedDocs.map((file, index) => (
                        <div key={index} className="text-sm text-gray-400">
                          {file.name} ({(file.size / 1024).toFixed(1)} KB)
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Final Review</h3>
            
            <div className="bg-gray-800 p-6 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-4">Proposal Summary</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-400">Service Title</p>
                  <p className="text-white font-medium">{formData.title}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-400">Category</p>
                  <p className="text-white font-medium">
                    {formData.category?.replace(/_/g, ' ').toUpperCase()}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-400">Provider</p>
                  <p className="text-white font-medium">{formData.provider?.name}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-400">Risk Level</p>
                  <p className="text-white font-medium">{formData.riskLevel?.toUpperCase()}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-400">Tier Access</p>
                  <p className="text-white font-medium">
                    {formData.tierAccess?.replace(/_/g, ' ').toUpperCase()}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-400">Management Fee</p>
                  <p className="text-white font-medium">{formData.serviceDetails?.fees?.managementFee}%</p>
                </div>
              </div>
              
              <div className="mt-6">
                <p className="text-sm text-gray-400">Description</p>
                <p className="text-white">{formData.description}</p>
              </div>
            </div>

            <div className="bg-yellow-900/20 border border-yellow-600 p-4 rounded-lg">
              <h4 className="text-yellow-300 font-medium mb-2">Important Notice</h4>
              <p className="text-yellow-200 text-sm">
                By submitting this proposal, you confirm that all information provided is accurate
                and complete. The proposal will enter the vetting workflow and be reviewed by
                appropriate personnel based on the service category and risk level.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-white mb-2">
            {mode === 'create' ? 'Create Service Proposal' : 'Edit Service Proposal'}
          </h1>
          <p className="text-gray-400">
            Complete all steps to submit your service proposal for review
          </p>
        </motion.div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-400">Step {currentStep} of {totalSteps}</span>
            <span className="text-sm text-gray-400">
              {Math.round((currentStep / totalSteps) * 100)}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-yellow-500 to-yellow-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${(currentStep / totalSteps) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Form */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="bg-gradient-to-br from-gray-800 to-gray-900 p-8 rounded-lg border border-gray-700 mb-8"
        >
          {renderStep()}
        </motion.div>

        {/* Navigation */}
        <div className="flex justify-between">
          <div className="flex gap-4">
            <button
              onClick={onCancel}
              className="px-6 py-2 text-gray-300 border border-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            
            {currentStep > 1 && (
              <button
                onClick={handlePrevious}
                className="px-6 py-2 text-white bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
              >
                Previous
              </button>
            )}
          </div>

          <div>
            {currentStep < totalSteps ? (
              <button
                onClick={handleNext}
                className="px-6 py-2 text-black bg-yellow-400 rounded-lg hover:bg-yellow-300 transition-colors font-medium"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="px-6 py-2 text-black bg-yellow-400 rounded-lg hover:bg-yellow-300 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSubmitting && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-4 h-4 border-2 border-black border-t-transparent rounded-full"
                  />
                )}
                {isSubmitting ? 'Submitting...' : 'Submit Proposal'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};