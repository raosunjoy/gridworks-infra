/**
 * Types for Banking-as-a-Service
 */

export interface PaymentRequest {
  amount: number;
  currency: string;
  fromAccount: string;
  toAccount: string;
  paymentMethod: 'bank_transfer' | 'wire' | 'ach' | 'card' | 'crypto';
  purpose: string;
  reference?: string;
  metadata?: {
    invoiceId?: string;
    orderId?: string;
    clientReference?: string;
  };
  urgency?: 'standard' | 'express' | 'instant';
  compliance?: {
    kycRequired?: boolean;
    amlChecked?: boolean;
    sanctionScreened?: boolean;
  };
}

export interface PaymentResponse {
  paymentId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  amount: number;
  currency: string;
  fees: {
    processing: number;
    exchange?: number;
    total: number;
  };
  timeline: {
    initiated: string;
    processing?: string;
    completed?: string;
    estimatedCompletion?: string;
  };
  reference: string;
  trackingNumber?: string;
  complianceChecks: {
    kyc: 'passed' | 'pending' | 'failed';
    aml: 'passed' | 'pending' | 'failed';
    sanctions: 'passed' | 'pending' | 'failed';
  };
}

export interface AccountRequest {
  accountType: 'checking' | 'savings' | 'escrow' | 'virtual' | 'multi_currency';
  currency: string;
  clientId: string;
  accountName: string;
  purpose: string;
  initialDeposit?: number;
  configuration?: {
    overdraftProtection?: boolean;
    interestBearing?: boolean;
    multiCurrency?: boolean;
    autoSweep?: boolean;
  };
  compliance?: {
    kycLevel: 'basic' | 'enhanced' | 'premium';
    entityType: 'individual' | 'corporate' | 'trust' | 'partnership';
    jurisdiction: string;
  };
}

export interface AccountResponse {
  accountId: string;
  accountNumber: string;
  routingNumber?: string;
  iban?: string;
  swift?: string;
  status: 'active' | 'pending' | 'suspended' | 'closed';
  balance: {
    available: number;
    pending: number;
    reserved: number;
    total: number;
  };
  currency: string;
  accountType: string;
  openedDate: string;
  lastActivity: string;
  limits: {
    dailyTransfer: number;
    monthlyTransfer: number;
    singleTransaction: number;
  };
}

export interface EscrowRequest {
  amount: number;
  currency: string;
  parties: {
    buyer: {
      accountId: string;
      name: string;
      email: string;
    };
    seller: {
      accountId: string;
      name: string;
      email: string;
    };
    agent?: {
      accountId: string;
      name: string;
      email: string;
    };
  };
  terms: {
    description: string;
    conditions: string[];
    milestones?: {
      description: string;
      amount: number;
      dueDate: string;
    }[];
    disputeResolution: string;
    timeoutAction: 'refund' | 'release' | 'hold';
  };
  timeline: {
    fundingDeadline: string;
    completionDeadline: string;
    inspectionPeriod?: number; // days
  };
}

export interface EscrowResponse {
  escrowId: string;
  status: 'created' | 'funded' | 'in_progress' | 'disputed' | 'completed' | 'cancelled';
  amount: number;
  currency: string;
  balance: {
    deposited: number;
    reserved: number;
    released: number;
    pending: number;
  };
  parties: any;
  timeline: {
    created: string;
    funded?: string;
    completed?: string;
    nextMilestone?: string;
  };
  conditions: {
    total: number;
    completed: number;
    pending: string[];
  };
  fees: {
    setup: number;
    management: number;
    release: number;
    total: number;
  };
}

export interface ComplianceCheck {
  checkId: string;
  type: 'kyc' | 'aml' | 'sanctions' | 'pep' | 'adverse_media';
  status: 'pending' | 'passed' | 'failed' | 'requires_review';
  score?: number;
  details: {
    provider: string;
    timestamp: string;
    reference: string;
    findings?: any[];
  };
  documents?: {
    type: string;
    status: string;
    url?: string;
  }[];
}

export interface CurrencyExchange {
  fromCurrency: string;
  toCurrency: string;
  amount: number;
  exchangeRate: number;
  fees: {
    exchange: number;
    processing: number;
    total: number;
  };
  estimatedAmount: number;
  validUntil: string;
  reference: string;
}

export interface WireTransfer {
  wireId: string;
  amount: number;
  currency: string;
  sender: {
    name: string;
    account: string;
    bank: string;
    address: any;
  };
  receiver: {
    name: string;
    account: string;
    bank: string;
    address: any;
  };
  purpose: string;
  charges: 'our' | 'ben' | 'sha';
  status: string;
  swiftMessage?: string;
}