/**
 * GridWorks B2B Infrastructure Services SDK
 * Complete TypeScript/JavaScript SDK for all B2B services
 */

// Core SDK
export { GridWorksSDK } from './core/GridWorksSDK';
export { GridWorksConfig, SDKOptions } from './core/types';

// AI Suite Services
export { AISuiteClient } from './ai-suite/AISuiteClient';
export { 
  SupportRequest, 
  SupportResponse, 
  IntelligenceRequest, 
  IntelligenceResponse,
  ModerationRequest,
  ModerationResponse 
} from './ai-suite/types';

// Anonymous Services
export { AnonymousServicesClient } from './anonymous-services/AnonymousServicesClient';
export {
  ZKProofRequest,
  ZKProofResponse,
  AnonymousPortfolioRequest,
  AnonymousPortfolioResponse,
  ButlerRequest,
  ButlerResponse
} from './anonymous-services/types';

// Trading Services
export { TradingClient } from './trading/TradingClient';
export {
  OrderRequest,
  OrderResponse,
  MarketDataRequest,
  MarketDataResponse,
  RiskAssessmentRequest,
  RiskAssessmentResponse
} from './trading/types';

// Banking Services
export { BankingClient } from './banking/BankingClient';
export {
  PaymentRequest,
  PaymentResponse,
  AccountRequest,
  AccountResponse,
  EscrowRequest,
  EscrowResponse
} from './banking/types';

// Utilities
export { APIError, ValidationError, AuthenticationError } from './core/errors';
export { Logger } from './core/logger';