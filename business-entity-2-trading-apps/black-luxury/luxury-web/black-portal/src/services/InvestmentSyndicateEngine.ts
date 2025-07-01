/**
 * Investment Syndicate Engine
 * Advanced system for managing exclusive Pre-IPO investments, luxury real estate,
 * and ESG portfolios for Black-tier clients with complete anonymity
 */

import { EventEmitter } from 'events';
import { ServiceCategory } from '@/types/service-management';

export enum InvestmentCategory {
  PRE_IPO = 'pre_ipo',
  LUXURY_REAL_ESTATE = 'luxury_real_estate',
  ESG_INVESTMENTS = 'esg_investments',
  PRIVATE_EQUITY = 'private_equity',
  HEDGE_FUNDS = 'hedge_funds',
  CRYPTOCURRENCY = 'cryptocurrency',
  COMMODITIES = 'commodities',
  ART_COLLECTIBLES = 'art_collectibles',
}

export enum InvestmentTier {
  ONYX = 'onyx',      // ₹10-100 Cr minimum
  OBSIDIAN = 'obsidian', // ₹100-1000 Cr minimum  
  VOID = 'void',      // ₹1000+ Cr minimum
}

interface InvestmentOpportunity {
  id: string;
  title: string;
  category: InvestmentCategory;
  description: string;
  
  // Investment Details
  minimumInvestment: number;
  maximumInvestment: number;
  totalRaiseAmount: number;
  currentCommitments: number;
  currency: 'INR' | 'USD' | 'EUR' | 'GBP';
  
  // Terms
  expectedReturns: {
    conservative: string;
    optimistic: string;
    timeframe: string;
  };
  lockupPeriod: string;
  liquidityOptions: string[];
  
  // Access Control
  tierAccess: InvestmentTier[];
  geographicRestrictions: string[];
  regulatoryRequirements: string[];
  
  // Company/Asset Information
  companyDetails?: {
    name: string;
    sector: string;
    foundedYear: number;
    lastValuation: number;
    keyInvestors: string[];
    businessModel: string;
    competitiveAdvantage: string[];
  };
  
  realEstateDetails?: {
    location: string;
    propertyType: string;
    squareFootage?: number;
    amenities: string[];
    developmentStage: string;
    expectedCompletion?: string;
  };
  
  esgDetails?: {
    esgScore: number;
    impactMetrics: string[];
    sustainabilityGoals: string[];
    carbonFootprint: string;
    socialImpact: string[];
  };
  
  // Risk & Compliance
  riskRating: 'low' | 'medium' | 'high' | 'speculative';
  riskFactors: string[];
  dueDiligenceStatus: 'pending' | 'in_progress' | 'completed' | 'approved';
  complianceChecks: {
    sebiApproval: boolean;
    rbiCompliance: boolean;
    femaCompliance: boolean;
    taxImplications: string[];
  };
  
  // Timing
  offeringPeriod: {
    startDate: string;
    endDate: string;
    firstClosing?: string;
    finalClosing: string;
  };
  
  // Documentation
  documentPackage: {
    termSheet: string;
    offeringMemorandum: string;
    subscriptionAgreement: string;
    dueDiligenceReport: string;
    legalOpinion: string;
  };
  
  // Status
  status: 'draft' | 'active' | 'closing_soon' | 'closed' | 'cancelled';
  availableSlots: number;
  totalSlots: number;
  
  createdAt: string;
  updatedAt: string;
}

interface InvestmentCommitment {
  id: string;
  investmentOpportunityId: string;
  clientId: string;
  anonymousId: string;
  tier: InvestmentTier;
  
  // Commitment Details
  commitmentAmount: number;
  currency: string;
  commitmentDate: string;
  
  // Investment Structure
  investmentVehicle: 'direct' | 'spv' | 'fund' | 'trust';
  anonymousStructure: {
    holdingCompany: string;
    jurisdictions: string[];
    beneficialOwnership: 'masked' | 'nominee' | 'trust';
    taxOptimization: string[];
  };
  
  // Legal & Compliance
  kycStatus: 'pending' | 'in_progress' | 'completed' | 'approved';
  amlChecks: boolean;
  accreditationStatus: 'verified' | 'pending' | 'required';
  legalDocumentation: {
    signed: boolean;
    documentsReceived: string[];
    pendingDocuments: string[];
  };
  
  // Payment & Funding
  paymentSchedule: Array<{
    installment: number;
    amount: number;
    dueDate: string;
    status: 'pending' | 'completed' | 'overdue';
  }>;
  
  fundingSource: {
    bankTransfer?: {
      accountVerified: boolean;
      swiftDetails: string;
    };
    cryptocurrency?: {
      walletAddress: string;
      cryptoType: string;
      verified: boolean;
    };
    existingPortfolio?: {
      assetTransfer: boolean;
      valuationRequired: boolean;
    };
  };
  
  // Status & Tracking
  status: 'draft' | 'committed' | 'funded' | 'active' | 'exited' | 'defaulted';
  allocationConfirmed: boolean;
  investmentConfirmation: string;
  
  // Performance Tracking
  performanceMetrics?: {
    currentValuation: number;
    unrealizedGains: number;
    realizedGains: number;
    totalReturn: number;
    irr: number;
    lastUpdated: string;
  };
  
  createdAt: string;
  updatedAt: string;
}

interface SyndicateFormation {
  id: string;
  opportunityId: string;
  
  // Syndicate Structure
  leadInvestor?: {
    anonymousId: string;
    tier: InvestmentTier;
    commitmentAmount: number;
    leadershipRole: string;
  };
  
  participants: Array<{
    anonymousId: string;
    tier: InvestmentTier;
    commitmentAmount: number;
    joinedAt: string;
    role: 'participant' | 'co_lead' | 'follower';
  }>;
  
  // Terms & Governance
  syndicateTerms: {
    minimumSyndicateSize: number;
    maximumSyndicateSize: number;
    governanceStructure: string;
    decisionMaking: 'majority' | 'unanimous' | 'lead_decides';
    informationRights: string[];
  };
  
  // Coordination
  communicationChannel: {
    anonymousMessaging: boolean;
    updateFrequency: string;
    reportingSchedule: string[];
  };
  
  // Status
  status: 'forming' | 'committed' | 'active' | 'exiting' | 'closed';
  formationDeadline: string;
  
  createdAt: string;
  updatedAt: string;
}

export class InvestmentSyndicateEngine extends EventEmitter {
  private opportunities: Map<string, InvestmentOpportunity> = new Map();
  private commitments: Map<string, InvestmentCommitment> = new Map();
  private syndicates: Map<string, SyndicateFormation> = new Map();
  private clientPortfolios: Map<string, any> = new Map();

  constructor() {
    super();
    this.initializeInvestmentEngine();
  }

  /**
   * Initialize the investment engine with premium opportunities
   */
  private initializeInvestmentEngine(): void {
    this.createPremiumOpportunities();
    console.log('Investment Syndicate Engine initialized with premium opportunities');
  }

  /**
   * Create premium investment opportunities for Black-tier clients
   */
  private createPremiumOpportunities(): void {
    // SpaceX Pre-IPO Opportunity
    this.createPreIPOOpportunity({
      title: 'SpaceX Series X Pre-IPO',
      companyName: 'SpaceX',
      sector: 'Aerospace & Defense',
      lastValuation: 180000000000, // $180B
      minimumInvestment: 500000000, // ₹50 Cr
      expectedReturns: '15-25% annually',
      lockupPeriod: '3-5 years',
    });

    // OpenAI Strategic Investment
    this.createPreIPOOpportunity({
      title: 'OpenAI Strategic Round',
      companyName: 'OpenAI',
      sector: 'Artificial Intelligence',
      lastValuation: 157000000000, // $157B
      minimumInvestment: 1000000000, // ₹100 Cr
      expectedReturns: '20-35% annually',
      lockupPeriod: '2-4 years',
    });

    // Dubai Luxury Real Estate
    this.createLuxuryRealEstateOpportunity({
      title: 'Dubai Marina Penthouse Collection',
      location: 'Dubai Marina, UAE',
      propertyType: 'Ultra-luxury penthouses',
      minimumInvestment: 250000000, // ₹25 Cr
      expectedReturns: '12-18% annually',
      amenities: ['Private helicopter pad', 'Infinity pool', 'Private beach access'],
    });

    // ESG Carbon Credit Portfolio
    this.createESGOpportunity({
      title: 'African Lithium Mining ESG Fund',
      impactFocus: 'Sustainable lithium extraction',
      minimumInvestment: 200000000, // ₹20 Cr
      expectedReturns: '18-25% annually',
      esgScore: 95,
    });
  }

  /**
   * Create a Pre-IPO investment opportunity
   */
  async createPreIPOOpportunity(params: {
    title: string;
    companyName: string;
    sector: string;
    lastValuation: number;
    minimumInvestment: number;
    expectedReturns: string;
    lockupPeriod: string;
  }): Promise<InvestmentOpportunity> {
    
    const opportunity: InvestmentOpportunity = {
      id: `preipo-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      title: params.title,
      category: InvestmentCategory.PRE_IPO,
      description: `Exclusive pre-IPO investment opportunity in ${params.companyName}`,
      
      minimumInvestment: params.minimumInvestment,
      maximumInvestment: params.minimumInvestment * 10,
      totalRaiseAmount: params.minimumInvestment * 20,
      currentCommitments: 0,
      currency: 'INR',
      
      expectedReturns: {
        conservative: params.expectedReturns.split('-')[0],
        optimistic: params.expectedReturns.split('-')[1]?.replace('%', '') || params.expectedReturns,
        timeframe: params.lockupPeriod,
      },
      lockupPeriod: params.lockupPeriod,
      liquidityOptions: ['Secondary market', 'IPO exit', 'Strategic acquisition'],
      
      tierAccess: [InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
      geographicRestrictions: ['Available to Indian investors via LRS/ODI route'],
      regulatoryRequirements: ['RBI LRS compliance', 'FEMA approval', 'Tax planning required'],
      
      companyDetails: {
        name: params.companyName,
        sector: params.sector,
        foundedYear: 2002,
        lastValuation: params.lastValuation,
        keyInvestors: ['Founders Fund', 'Andreessen Horowitz', 'Google Ventures'],
        businessModel: 'Technology platform with multiple revenue streams',
        competitiveAdvantage: ['Market leadership', 'Technological moat', 'Network effects'],
      },
      
      riskRating: 'medium',
      riskFactors: [
        'Pre-IPO illiquidity',
        'Valuation volatility',
        'Regulatory changes',
        'Market timing risk',
        'Currency exchange risk',
      ],
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
        firstClosing: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        finalClosing: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      },
      
      documentPackage: {
        termSheet: `${params.companyName}_TermSheet_2024.pdf`,
        offeringMemorandum: `${params.companyName}_OfferingMemo_2024.pdf`,
        subscriptionAgreement: `${params.companyName}_Subscription_2024.pdf`,
        dueDiligenceReport: `${params.companyName}_DDReport_2024.pdf`,
        legalOpinion: `${params.companyName}_LegalOpinion_2024.pdf`,
      },
      
      status: 'active',
      availableSlots: 50,
      totalSlots: 50,
      
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.opportunities.set(opportunity.id, opportunity);

    this.emit('opportunity:created', {
      opportunityId: opportunity.id,
      category: opportunity.category,
      minimumInvestment: opportunity.minimumInvestment,
      tierAccess: opportunity.tierAccess,
    });

    return opportunity;
  }

  /**
   * Create a luxury real estate investment opportunity
   */
  async createLuxuryRealEstateOpportunity(params: {
    title: string;
    location: string;
    propertyType: string;
    minimumInvestment: number;
    expectedReturns: string;
    amenities: string[];
  }): Promise<InvestmentOpportunity> {
    
    const opportunity: InvestmentOpportunity = {
      id: `realestate-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      title: params.title,
      category: InvestmentCategory.LUXURY_REAL_ESTATE,
      description: `Premium real estate investment in ${params.location}`,
      
      minimumInvestment: params.minimumInvestment,
      maximumInvestment: params.minimumInvestment * 5,
      totalRaiseAmount: params.minimumInvestment * 10,
      currentCommitments: 0,
      currency: 'INR',
      
      expectedReturns: {
        conservative: params.expectedReturns.split('-')[0],
        optimistic: params.expectedReturns.split('-')[1]?.replace('%', '') || params.expectedReturns,
        timeframe: '5-7 years',
      },
      lockupPeriod: '3-5 years',
      liquidityOptions: ['Property sale', 'Rental income', 'Refinancing options'],
      
      tierAccess: [InvestmentTier.ONYX, InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
      geographicRestrictions: ['International property investment via LRS'],
      regulatoryRequirements: ['RBI LRS compliance', 'Property ownership regulations', 'Tax planning'],
      
      realEstateDetails: {
        location: params.location,
        propertyType: params.propertyType,
        squareFootage: 10000,
        amenities: params.amenities,
        developmentStage: 'Completed',
        expectedCompletion: 'Immediate possession',
      },
      
      riskRating: 'low',
      riskFactors: [
        'Property market fluctuations',
        'Currency exchange risk',
        'Liquidity constraints',
        'Regulatory changes',
      ],
      dueDiligenceStatus: 'completed',
      complianceChecks: {
        sebiApproval: false,
        rbiCompliance: true,
        femaCompliance: true,
        taxImplications: ['Property tax', 'Capital gains planning', 'Rental income tax'],
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
      availableSlots: 20,
      totalSlots: 20,
      
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.opportunities.set(opportunity.id, opportunity);

    this.emit('opportunity:created', {
      opportunityId: opportunity.id,
      category: opportunity.category,
      minimumInvestment: opportunity.minimumInvestment,
      tierAccess: opportunity.tierAccess,
    });

    return opportunity;
  }

  /**
   * Create an ESG investment opportunity
   */
  async createESGOpportunity(params: {
    title: string;
    impactFocus: string;
    minimumInvestment: number;
    expectedReturns: string;
    esgScore: number;
  }): Promise<InvestmentOpportunity> {
    
    const opportunity: InvestmentOpportunity = {
      id: `esg-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      title: params.title,
      category: InvestmentCategory.ESG_INVESTMENTS,
      description: `High-impact ESG investment focused on ${params.impactFocus}`,
      
      minimumInvestment: params.minimumInvestment,
      maximumInvestment: params.minimumInvestment * 8,
      totalRaiseAmount: params.minimumInvestment * 15,
      currentCommitments: 0,
      currency: 'INR',
      
      expectedReturns: {
        conservative: params.expectedReturns.split('-')[0],
        optimistic: params.expectedReturns.split('-')[1]?.replace('%', '') || params.expectedReturns,
        timeframe: '7-10 years',
      },
      lockupPeriod: '5-7 years',
      liquidityOptions: ['Carbon credit sales', 'Asset monetization', 'Green bond issuance'],
      
      tierAccess: [InvestmentTier.ONYX, InvestmentTier.OBSIDIAN, InvestmentTier.VOID],
      geographicRestrictions: ['Global ESG fund with Indian regulatory compliance'],
      regulatoryRequirements: ['Green bond guidelines', 'ESG compliance', 'Impact reporting'],
      
      esgDetails: {
        esgScore: params.esgScore,
        impactMetrics: [
          'Carbon footprint reduction: 50%',
          'Local employment creation: 10,000 jobs',
          'Biodiversity preservation: 50,000 hectares',
          'Clean energy generation: 500 MW',
        ],
        sustainabilityGoals: [
          'UN SDG 7: Affordable and Clean Energy',
          'UN SDG 13: Climate Action',
          'UN SDG 15: Life on Land',
        ],
        carbonFootprint: 'Net negative carbon impact',
        socialImpact: [
          'Community development programs',
          'Education and healthcare initiatives',
          'Indigenous rights protection',
        ],
      },
      
      riskRating: 'medium',
      riskFactors: [
        'Regulatory policy changes',
        'Carbon price volatility',
        'Technology adoption risk',
        'ESG standard evolution',
      ],
      dueDiligenceStatus: 'completed',
      complianceChecks: {
        sebiApproval: true,
        rbiCompliance: true,
        femaCompliance: true,
        taxImplications: ['Green bond tax benefits', 'Impact investment incentives'],
      },
      
      offeringPeriod: {
        startDate: new Date().toISOString(),
        endDate: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000).toISOString(),
        finalClosing: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000).toISOString(),
      },
      
      documentPackage: {
        termSheet: 'AfricanLithium_TermSheet_2024.pdf',
        offeringMemorandum: 'AfricanLithium_ESGMemo_2024.pdf',
        subscriptionAgreement: 'AfricanLithium_Subscription_2024.pdf',
        dueDiligenceReport: 'AfricanLithium_ImpactReport_2024.pdf',
        legalOpinion: 'AfricanLithium_LegalOpinion_2024.pdf',
      },
      
      status: 'active',
      availableSlots: 100,
      totalSlots: 100,
      
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.opportunities.set(opportunity.id, opportunity);

    this.emit('opportunity:created', {
      opportunityId: opportunity.id,
      category: opportunity.category,
      minimumInvestment: opportunity.minimumInvestment,
      tierAccess: opportunity.tierAccess,
    });

    return opportunity;
  }

  /**
   * Get available investment opportunities for a specific tier
   */
  async getAvailableOpportunities(
    tier: InvestmentTier,
    category?: InvestmentCategory
  ): Promise<InvestmentOpportunity[]> {
    
    const availableOpportunities = Array.from(this.opportunities.values()).filter(opportunity => {
      // Check tier access
      if (!opportunity.tierAccess.includes(tier)) return false;
      
      // Check category filter
      if (category && opportunity.category !== category) return false;
      
      // Check if opportunity is active
      if (opportunity.status !== 'active') return false;
      
      // Check if offering period is current
      const now = new Date();
      const startDate = new Date(opportunity.offeringPeriod.startDate);
      const endDate = new Date(opportunity.offeringPeriod.endDate);
      
      return now >= startDate && now <= endDate && opportunity.availableSlots > 0;
    });

    return availableOpportunities.sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  /**
   * Create an investment commitment
   */
  async createInvestmentCommitment(
    opportunityId: string,
    clientId: string,
    anonymousId: string,
    tier: InvestmentTier,
    commitmentAmount: number,
    investmentVehicle: 'direct' | 'spv' | 'fund' | 'trust' = 'spv'
  ): Promise<InvestmentCommitment> {
    
    const opportunity = this.opportunities.get(opportunityId);
    if (!opportunity) {
      throw new Error('Investment opportunity not found');
    }

    if (!opportunity.tierAccess.includes(tier)) {
      throw new Error('Tier not authorized for this investment');
    }

    if (commitmentAmount < opportunity.minimumInvestment) {
      throw new Error(`Minimum investment is ${opportunity.minimumInvestment}`);
    }

    if (commitmentAmount > opportunity.maximumInvestment) {
      throw new Error(`Maximum investment is ${opportunity.maximumInvestment}`);
    }

    if (opportunity.availableSlots <= 0) {
      throw new Error('No available slots for this investment');
    }

    const commitment: InvestmentCommitment = {
      id: `commit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      investmentOpportunityId: opportunityId,
      clientId,
      anonymousId,
      tier,
      
      commitmentAmount,
      currency: opportunity.currency,
      commitmentDate: new Date().toISOString(),
      
      investmentVehicle,
      anonymousStructure: {
        holdingCompany: `BlackPortal SPV ${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
        jurisdictions: ['Mauritius', 'Singapore', 'Netherlands'],
        beneficialOwnership: 'nominee',
        taxOptimization: ['Treaty benefits', 'Capital gains optimization', 'Withholding tax minimization'],
      },
      
      kycStatus: 'pending',
      amlChecks: false,
      accreditationStatus: 'verified',
      legalDocumentation: {
        signed: false,
        documentsReceived: [],
        pendingDocuments: [
          'Subscription Agreement',
          'KYC Documentation',
          'Bank Verification',
          'Accreditation Certificate',
        ],
      },
      
      paymentSchedule: this.generatePaymentSchedule(commitmentAmount, opportunity),
      
      fundingSource: {
        bankTransfer: {
          accountVerified: false,
          swiftDetails: 'To be provided',
        },
      },
      
      status: 'draft',
      allocationConfirmed: false,
      investmentConfirmation: '',
      
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.commitments.set(commitment.id, commitment);

    // Update opportunity availability
    opportunity.availableSlots -= 1;
    opportunity.currentCommitments += commitmentAmount;
    opportunity.updatedAt = new Date().toISOString();

    this.emit('commitment:created', {
      commitmentId: commitment.id,
      opportunityId,
      anonymousId,
      tier,
      commitmentAmount,
    });

    return commitment;
  }

  /**
   * Form an investment syndicate
   */
  async formInvestmentSyndicate(
    opportunityId: string,
    leadInvestorAnonymousId: string,
    leadInvestorTier: InvestmentTier,
    leadCommitmentAmount: number,
    syndicateTerms: {
      minimumSyndicateSize: number;
      maximumSyndicateSize: number;
      governanceStructure: string;
    }
  ): Promise<SyndicateFormation> {
    
    const opportunity = this.opportunities.get(opportunityId);
    if (!opportunity) {
      throw new Error('Investment opportunity not found');
    }

    const syndicate: SyndicateFormation = {
      id: `syn-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      opportunityId,
      
      leadInvestor: {
        anonymousId: leadInvestorAnonymousId,
        tier: leadInvestorTier,
        commitmentAmount: leadCommitmentAmount,
        leadershipRole: 'Lead Investor',
      },
      
      participants: [],
      
      syndicateTerms: {
        ...syndicateTerms,
        decisionMaking: 'lead_decides',
        informationRights: [
          'Quarterly performance reports',
          'Annual audited statements',
          'Material event notifications',
          'Exit opportunity communications',
        ],
      },
      
      communicationChannel: {
        anonymousMessaging: true,
        updateFrequency: 'Monthly',
        reportingSchedule: ['Quarterly performance', 'Annual comprehensive'],
      },
      
      status: 'forming',
      formationDeadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.syndicates.set(syndicate.id, syndicate);

    this.emit('syndicate:formed', {
      syndicateId: syndicate.id,
      opportunityId,
      leadInvestor: leadInvestorAnonymousId,
      leadCommitment: leadCommitmentAmount,
    });

    return syndicate;
  }

  /**
   * Join an investment syndicate
   */
  async joinInvestmentSyndicate(
    syndicateId: string,
    participantAnonymousId: string,
    participantTier: InvestmentTier,
    commitmentAmount: number
  ): Promise<void> {
    
    const syndicate = this.syndicates.get(syndicateId);
    if (!syndicate) {
      throw new Error('Investment syndicate not found');
    }

    if (syndicate.status !== 'forming') {
      throw new Error('Syndicate is not accepting new participants');
    }

    if (syndicate.participants.length >= syndicate.syndicateTerms.maximumSyndicateSize) {
      throw new Error('Syndicate is full');
    }

    const opportunity = this.opportunities.get(syndicate.opportunityId);
    if (!opportunity) {
      throw new Error('Investment opportunity not found');
    }

    if (commitmentAmount < opportunity.minimumInvestment) {
      throw new Error(`Minimum investment is ${opportunity.minimumInvestment}`);
    }

    syndicate.participants.push({
      anonymousId: participantAnonymousId,
      tier: participantTier,
      commitmentAmount,
      joinedAt: new Date().toISOString(),
      role: 'participant',
    });

    syndicate.updatedAt = new Date().toISOString();

    // Check if syndicate is ready to commit
    if (syndicate.participants.length >= syndicate.syndicateTerms.minimumSyndicateSize) {
      syndicate.status = 'committed';
    }

    this.emit('syndicate:participant_joined', {
      syndicateId,
      participantId: participantAnonymousId,
      commitmentAmount,
      totalParticipants: syndicate.participants.length,
    });
  }

  /**
   * Get client investment portfolio
   */
  async getClientInvestmentPortfolio(clientId: string): Promise<{
    totalInvestments: number;
    activeCommitments: InvestmentCommitment[];
    syndicateParticipations: SyndicateFormation[];
    performanceSummary: {
      totalValue: number;
      unrealizedGains: number;
      realizedGains: number;
      totalReturn: number;
    };
  }> {
    
    const activeCommitments = Array.from(this.commitments.values())
      .filter(commitment => commitment.clientId === clientId && commitment.status === 'active');

    const syndicateParticipations = Array.from(this.syndicates.values())
      .filter(syndicate => 
        syndicate.leadInvestor?.anonymousId === clientId ||
        syndicate.participants.some(p => p.anonymousId === clientId)
      );

    const totalInvestments = activeCommitments.reduce((sum, commitment) => 
      sum + commitment.commitmentAmount, 0);

    const performanceSummary = {
      totalValue: totalInvestments * 1.15, // Assume 15% average appreciation
      unrealizedGains: totalInvestments * 0.12,
      realizedGains: totalInvestments * 0.03,
      totalReturn: 0.15,
    };

    return {
      totalInvestments,
      activeCommitments,
      syndicateParticipations,
      performanceSummary,
    };
  }

  /**
   * Generate payment schedule for investment commitment
   */
  private generatePaymentSchedule(
    commitmentAmount: number,
    opportunity: InvestmentOpportunity
  ): Array<{
    installment: number;
    amount: number;
    dueDate: string;
    status: 'pending' | 'completed' | 'overdue';
  }> {
    
    // For most investments, create a 3-installment schedule
    const installments = 3;
    const installmentAmount = commitmentAmount / installments;
    
    return Array.from({ length: installments }, (_, index) => ({
      installment: index + 1,
      amount: installmentAmount,
      dueDate: new Date(Date.now() + (index + 1) * 30 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'pending' as const,
    }));
  }

  /**
   * Get investment opportunity by ID
   */
  async getInvestmentOpportunity(opportunityId: string): Promise<InvestmentOpportunity | null> {
    return this.opportunities.get(opportunityId) || null;
  }

  /**
   * Get investment commitment by ID
   */
  async getInvestmentCommitment(commitmentId: string): Promise<InvestmentCommitment | null> {
    return this.commitments.get(commitmentId) || null;
  }

  /**
   * Get all active investment opportunities
   */
  async getAllActiveOpportunities(): Promise<InvestmentOpportunity[]> {
    return Array.from(this.opportunities.values())
      .filter(opportunity => opportunity.status === 'active')
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }
}