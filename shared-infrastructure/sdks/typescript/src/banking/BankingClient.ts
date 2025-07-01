/**
 * Banking-as-a-Service Client
 * Complete digital banking infrastructure without banking license requirement
 */

import { GridWorksSDK } from '../core/GridWorksSDK';
import { APIResponse, PaginatedResponse } from '../core/types';
import {
  PaymentRequest,
  PaymentResponse,
  AccountRequest,
  AccountResponse,
  EscrowRequest,
  EscrowResponse,
  ComplianceCheck,
  CurrencyExchange,
  WireTransfer
} from './types';

export class BankingClient {
  constructor(private sdk: GridWorksSDK) {}

  /**
   * Payment Processing
   */
  async processPayment(payment: PaymentRequest): Promise<APIResponse<PaymentResponse>> {
    return this.sdk.request('POST', '/api/v1/banking/payments', payment);
  }

  /**
   * Get payment status
   */
  async getPayment(paymentId: string): Promise<APIResponse<PaymentResponse>> {
    return this.sdk.request('GET', `/api/v1/banking/payments/${paymentId}`);
  }

  /**
   * Cancel payment
   */
  async cancelPayment(paymentId: string, reason?: string): Promise<APIResponse<{
    cancelled: boolean;
    paymentId: string;
    reason?: string;
    refundAmount?: number;
  }>> {
    return this.sdk.request('POST', `/api/v1/banking/payments/${paymentId}/cancel`, { reason });
  }

  /**
   * Get payment history
   */
  async getPaymentHistory(
    filters?: {
      accountId?: string;
      status?: string;
      currency?: string;
      startDate?: string;
      endDate?: string;
      minAmount?: number;
      maxAmount?: number;
    },
    pagination?: { page?: number; limit?: number }
  ): Promise<PaginatedResponse<PaymentResponse>> {
    return this.sdk.request('GET', '/api/v1/banking/payments', {
      params: { ...filters, ...pagination }
    });
  }

  /**
   * Bulk payment processing
   */
  async processBulkPayments(payments: PaymentRequest[]): Promise<APIResponse<{
    batchId: string;
    successful: PaymentResponse[];
    failed: { payment: PaymentRequest; error: string }[];
    summary: { total: number; successful: number; failed: number; totalAmount: number };
  }>> {
    return this.sdk.request('POST', '/api/v1/banking/payments/bulk', { payments });
  }

  /**
   * Account Management
   */
  async createAccount(account: AccountRequest): Promise<APIResponse<AccountResponse>> {
    return this.sdk.request('POST', '/api/v1/banking/accounts', account);
  }

  /**
   * Get account details
   */
  async getAccount(accountId: string): Promise<APIResponse<AccountResponse>> {
    return this.sdk.request('GET', `/api/v1/banking/accounts/${accountId}`);
  }

  /**
   * Update account
   */
  async updateAccount(
    accountId: string, 
    updates: Partial<AccountRequest>
  ): Promise<APIResponse<AccountResponse>> {
    return this.sdk.request('PUT', `/api/v1/banking/accounts/${accountId}`, updates);
  }

  /**
   * Close account
   */
  async closeAccount(accountId: string, reason?: string): Promise<APIResponse<{
    closed: boolean;
    accountId: string;
    finalBalance: number;
    closureDate: string;
  }>> {
    return this.sdk.request('POST', `/api/v1/banking/accounts/${accountId}/close`, { reason });
  }

  /**
   * Get account balance
   */
  async getAccountBalance(accountId: string): Promise<APIResponse<{
    accountId: string;
    balance: {
      available: number;
      pending: number;
      reserved: number;
      total: number;
    };
    currency: string;
    lastUpdated: string;
  }>> {
    return this.sdk.request('GET', `/api/v1/banking/accounts/${accountId}/balance`);
  }

  /**
   * Get account transaction history
   */
  async getAccountTransactions(
    accountId: string,
    filters?: {
      type?: string;
      status?: string;
      startDate?: string;
      endDate?: string;
    },
    pagination?: { page?: number; limit?: number }
  ): Promise<PaginatedResponse<{
    transactionId: string;
    type: string;
    amount: number;
    currency: string;
    status: string;
    description: string;
    timestamp: string;
    balance: number;
  }>> {
    return this.sdk.request('GET', `/api/v1/banking/accounts/${accountId}/transactions`, {
      params: { ...filters, ...pagination }
    });
  }

  /**
   * Get all accounts for client
   */
  async getAccounts(
    clientId?: string,
    filters?: { accountType?: string; currency?: string; status?: string }
  ): Promise<APIResponse<AccountResponse[]>> {
    return this.sdk.request('GET', '/api/v1/banking/accounts', {
      params: { clientId, ...filters }
    });
  }

  /**
   * Escrow Services
   */
  async createEscrow(escrow: EscrowRequest): Promise<APIResponse<EscrowResponse>> {
    return this.sdk.request('POST', '/api/v1/banking/escrow', escrow);
  }

  /**
   * Get escrow details
   */
  async getEscrow(escrowId: string): Promise<APIResponse<EscrowResponse>> {
    return this.sdk.request('GET', `/api/v1/banking/escrow/${escrowId}`);
  }

  /**
   * Fund escrow
   */
  async fundEscrow(
    escrowId: string, 
    amount: number, 
    fromAccountId: string
  ): Promise<APIResponse<{
    funded: boolean;
    escrowId: string;
    amount: number;
    newBalance: number;
    timestamp: string;
  }>> {
    return this.sdk.request('POST', `/api/v1/banking/escrow/${escrowId}/fund`, {
      amount,
      fromAccountId
    });
  }

  /**
   * Release escrow funds
   */
  async releaseEscrow(
    escrowId: string,
    amount: number,
    milestone?: string,
    authorization?: any
  ): Promise<APIResponse<{
    released: boolean;
    escrowId: string;
    amount: number;
    remainingBalance: number;
    timestamp: string;
  }>> {
    return this.sdk.request('POST', `/api/v1/banking/escrow/${escrowId}/release`, {
      amount,
      milestone,
      authorization
    });
  }

  /**
   * Dispute escrow
   */
  async disputeEscrow(
    escrowId: string,
    reason: string,
    evidence?: any[]
  ): Promise<APIResponse<{
    disputeId: string;
    escrowId: string;
    status: string;
    timeline: any;
  }>> {
    return this.sdk.request('POST', `/api/v1/banking/escrow/${escrowId}/dispute`, {
      reason,
      evidence
    });
  }

  /**
   * Get escrow history
   */
  async getEscrowHistory(
    filters?: {
      clientId?: string;
      status?: string;
      startDate?: string;
      endDate?: string;
    },
    pagination?: { page?: number; limit?: number }
  ): Promise<PaginatedResponse<EscrowResponse>> {
    return this.sdk.request('GET', '/api/v1/banking/escrow', {
      params: { ...filters, ...pagination }
    });
  }

  /**
   * Compliance and KYC/AML
   */
  async performKYC(
    clientId: string,
    documents: {
      type: string;
      file: File | Buffer;
      metadata?: any;
    }[]
  ): Promise<APIResponse<ComplianceCheck>> {
    const formData = new FormData();
    formData.append('clientId', clientId);
    
    documents.forEach((doc, index) => {
      formData.append(`document_${index}`, doc.file);
      formData.append(`type_${index}`, doc.type);
      if (doc.metadata) {
        formData.append(`metadata_${index}`, JSON.stringify(doc.metadata));
      }
    });

    return this.sdk.request('POST', '/api/v1/banking/compliance/kyc', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }

  /**
   * Perform AML screening
   */
  async performAML(
    clientId: string,
    transactionData?: any
  ): Promise<APIResponse<ComplianceCheck>> {
    return this.sdk.request('POST', '/api/v1/banking/compliance/aml', {
      clientId,
      transactionData
    });
  }

  /**
   * Sanctions screening
   */
  async screenSanctions(
    clientId: string,
    additionalInfo?: any
  ): Promise<APIResponse<ComplianceCheck>> {
    return this.sdk.request('POST', '/api/v1/banking/compliance/sanctions', {
      clientId,
      additionalInfo
    });
  }

  /**
   * Get compliance status
   */
  async getComplianceStatus(clientId: string): Promise<APIResponse<{
    clientId: string;
    overallStatus: 'compliant' | 'pending' | 'non_compliant';
    checks: ComplianceCheck[];
    expirations: {
      kyc?: string;
      aml?: string;
      sanctions?: string;
    };
    nextReview: string;
  }>> {
    return this.sdk.request('GET', `/api/v1/banking/compliance/status/${clientId}`);
  }

  /**
   * Currency Exchange
   */
  async getExchangeRate(
    fromCurrency: string,
    toCurrency: string,
    amount?: number
  ): Promise<APIResponse<{
    rate: number;
    inverseRate: number;
    spread: number;
    validUntil: string;
    estimatedAmount?: number;
  }>> {
    return this.sdk.request('GET', '/api/v1/banking/exchange/rate', {
      params: { fromCurrency, toCurrency, amount }
    });
  }

  /**
   * Execute currency exchange
   */
  async exchangeCurrency(
    fromAccount: string,
    toAccount: string,
    fromCurrency: string,
    toCurrency: string,
    amount: number,
    acceptedRate?: number
  ): Promise<APIResponse<CurrencyExchange & {
    exchangeId: string;
    status: string;
    executedAt: string;
  }>> {
    return this.sdk.request('POST', '/api/v1/banking/exchange/execute', {
      fromAccount,
      toAccount,
      fromCurrency,
      toCurrency,
      amount,
      acceptedRate
    });
  }

  /**
   * Wire Transfers
   */
  async initiateWireTransfer(wireTransfer: Omit<WireTransfer, 'wireId' | 'status'>): Promise<APIResponse<WireTransfer>> {
    return this.sdk.request('POST', '/api/v1/banking/wire', wireTransfer);
  }

  /**
   * Get wire transfer status
   */
  async getWireTransfer(wireId: string): Promise<APIResponse<WireTransfer>> {
    return this.sdk.request('GET', `/api/v1/banking/wire/${wireId}`);
  }

  /**
   * Cancel wire transfer
   */
  async cancelWireTransfer(wireId: string): Promise<APIResponse<{
    cancelled: boolean;
    wireId: string;
    refundAmount?: number;
  }>> {
    return this.sdk.request('POST', `/api/v1/banking/wire/${wireId}/cancel`);
  }

  /**
   * Virtual Account Management
   */
  async createVirtualAccount(
    clientId: string,
    currency: string,
    purpose: string
  ): Promise<APIResponse<{
    virtualAccountId: string;
    accountNumber: string;
    routingNumber: string;
    currency: string;
    purpose: string;
    status: string;
    createdAt: string;
  }>> {
    return this.sdk.request('POST', '/api/v1/banking/virtual-accounts', {
      clientId,
      currency,
      purpose
    });
  }

  /**
   * Banking Analytics
   */
  async getBankingAnalytics(
    timeframe: string = '30d',
    clientId?: string
  ): Promise<APIResponse<{
    payments: {
      total: number;
      volume: number;
      successful: number;
      failed: number;
      averageAmount: number;
    };
    accounts: {
      total: number;
      active: number;
      totalBalance: number;
      currencies: any;
    };
    escrow: {
      total: number;
      active: number;
      totalValue: number;
      completionRate: number;
    };
    compliance: {
      kycCompletionRate: number;
      amlAlerts: number;
      sanctionsHits: number;
    };
    fees: {
      total: number;
      byService: any;
    };
  }>> {
    return this.sdk.request('GET', '/api/v1/banking/analytics', {
      params: { timeframe, clientId }
    });
  }

  /**
   * Health check for banking services
   */
  async healthCheck(): Promise<APIResponse<{
    payments: boolean;
    accounts: boolean;
    escrow: boolean;
    compliance: boolean;
    exchange: boolean;
    wire: boolean;
    overall: boolean;
  }>> {
    return this.sdk.request('GET', '/api/v1/banking/health');
  }
}