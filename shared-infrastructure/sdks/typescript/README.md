# GridWorks B2B Infrastructure Services SDK

## Overview

The GridWorks B2B SDK provides comprehensive access to all GridWorks infrastructure services for financial institutions. This TypeScript/JavaScript SDK enables rapid integration with our enterprise-grade B2B services.

## Services Included

- **AI Suite**: Multi-language support, market intelligence, content moderation
- **Anonymous Services**: Zero-knowledge proofs, anonymous portfolio management (World's First)
- **Trading-as-a-Service**: Multi-exchange connectivity, risk management
- **Banking-as-a-Service**: Payment processing, account management, compliance

## Installation

```bash
npm install @gridworks/b2b-sdk
```

## Quick Start

```typescript
import { GridWorksSDK } from '@gridworks/b2b-sdk';

// Initialize SDK
const sdk = GridWorksSDK.createForEnvironment(
  'production', // or 'development', 'staging'
  'gw_prod_your_api_key_here',
  'your_client_id'
);

// Test connectivity
const isHealthy = await sdk.healthCheck();
console.log('SDK Status:', isHealthy);
```

## Configuration

```typescript
import { GridWorksSDK, GridWorksConfig } from '@gridworks/b2b-sdk';

const config: GridWorksConfig = {
  baseURL: 'https://api.gridworks.com',
  apiKey: 'gw_prod_your_api_key_here',
  clientId: 'your_client_id',
  environment: 'production',
  timeout: 30000,
  debug: false,
  retry: {
    attempts: 3,
    delay: 1000,
    backoff: 2
  }
};

const sdk = new GridWorksSDK(config);
```

## Service Usage Examples

### AI Suite Services

#### Multi-language Support
```typescript
// Get support in Hindi
const supportResponse = await sdk.aiSuite.getSupportInLanguage(
  'मुझे अपने पोर्टफोलियो के बारे में सहायता चाहिए',
  'hi'
);

// Get morning pulse
const morningPulse = await sdk.aiSuite.getMorningPulse(
  ['NSE', 'BSE', 'NASDAQ'],
  'whatsapp'
);
```

#### WhatsApp Business Integration
```typescript
// Send WhatsApp support message
const whatsappResponse = await sdk.aiSuite.getWhatsAppSupport(
  'Portfolio analysis required',
  '+919876543210'
);
```

### Anonymous Services (World's First)

#### Anonymous Portfolio Verification
```typescript
// Verify portfolio anonymously with ZK proofs
const portfolioVerification = await sdk.anonymous.verifyAnonymousPortfolio({
  portfolioData: {
    totalValue: 50000000, // ₹5Cr
    assetClasses: [
      { type: 'equity', allocation: 60, performance: 12.5 },
      { type: 'bonds', allocation: 30, performance: 8.2 },
      { type: 'alternatives', allocation: 10, performance: 15.0 }
    ],
    riskProfile: 'moderate',
    timeHorizon: '5-10 years'
  },
  privacyLevel: 'obsidian' // ₹2Cr-5Cr tier
});
```

#### Butler AI Assistance
```typescript
// Get investment advice from Butler AI
const butlerAdvice = await sdk.anonymous.getButlerInvestmentAdvice(
  'obsidian',
  'private_equity',
  'moderate',
  portfolioVerification.data.anonymousId
);
```

#### Anonymous Deal Flow
```typescript
// Share deal anonymously
const dealShare = await sdk.anonymous.shareDealFlow({
  dealId: 'deal_123',
  dealType: 'private_equity',
  minimumInvestment: 10000000, // ₹1Cr
  targetReturns: {
    expected: 18,
    minimum: 12,
    timeframe: '3-5 years'
  },
  riskAssessment: {
    level: 'medium',
    factors: ['market_risk', 'liquidity_risk'],
    mitigation: ['diversification', 'staged_deployment']
  },
  anonymityRequirements: {
    dealSourceAnonymous: true,
    investorAnonymous: true,
    intermediaryRequired: true
  }
});
```

### Trading-as-a-Service

#### Order Management
```typescript
// Place buy order
const orderResponse = await sdk.trading.placeOrder({
  symbol: 'RELIANCE',
  side: 'buy',
  quantity: 100,
  orderType: 'limit',
  price: 2450.50,
  timeInForce: 'DAY',
  exchange: 'NSE'
});

// Check order status
const orderStatus = await sdk.trading.getOrder(orderResponse.data.orderId);
```

#### Market Data
```typescript
// Get real-time quote
const quote = await sdk.trading.getQuote('NIFTY50', 'NSE');

// Get historical candles
const candles = await sdk.trading.getCandles(
  'RELIANCE',
  '1d',
  '2024-01-01',
  '2024-01-31'
);
```

#### Risk Assessment
```typescript
// Pre-trade risk check
const riskCheck = await sdk.trading.preTradeRiskCheck({
  symbol: 'RELIANCE',
  side: 'buy',
  quantity: 1000,
  orderType: 'market'
});

if (riskCheck.data.approved) {
  // Proceed with trade
} else {
  console.log('Risk warnings:', riskCheck.data.warnings);
}
```

### Banking-as-a-Service

#### Payment Processing
```typescript
// Process payment
const payment = await sdk.banking.processPayment({
  amount: 1000000, // ₹10L
  currency: 'INR',
  fromAccount: 'acc_sender_123',
  toAccount: 'acc_receiver_456',
  paymentMethod: 'bank_transfer',
  purpose: 'Investment transfer',
  urgency: 'express'
});
```

#### Account Management
```typescript
// Create virtual account
const account = await sdk.banking.createAccount({
  accountType: 'virtual',
  currency: 'INR',
  clientId: 'client_123',
  accountName: 'Trading Account',
  purpose: 'Securities trading'
});

// Get account balance
const balance = await sdk.banking.getAccountBalance(account.data.accountId);
```

#### Escrow Services
```typescript
// Create escrow for large transaction
const escrow = await sdk.banking.createEscrow({
  amount: 50000000, // ₹5Cr
  currency: 'INR',
  parties: {
    buyer: {
      accountId: 'acc_buyer_123',
      name: 'Buyer Corp',
      email: 'buyer@corp.com'
    },
    seller: {
      accountId: 'acc_seller_456',
      name: 'Seller Ltd',
      email: 'seller@ltd.com'
    }
  },
  terms: {
    description: 'Private equity investment',
    conditions: ['due_diligence_complete', 'legal_approval'],
    disputeResolution: 'arbitration',
    timeoutAction: 'refund'
  },
  timeline: {
    fundingDeadline: '2024-02-15T23:59:59Z',
    completionDeadline: '2024-03-31T23:59:59Z',
    inspectionPeriod: 30
  }
});
```

#### Compliance (KYC/AML)
```typescript
// Perform KYC
const kycResult = await sdk.banking.performKYC('client_123', [
  {
    type: 'passport',
    file: passportFile,
    metadata: { issueDate: '2020-01-15', expiryDate: '2030-01-15' }
  },
  {
    type: 'address_proof',
    file: addressProofFile
  }
]);
```

## Real-time Data (WebSocket)

```typescript
// Subscribe to market data
const subscription = await sdk.trading.subscribeToMarketData(
  ['NIFTY50', 'BANKNIFTY'],
  ['quote', 'trade'],
  (data) => {
    console.log('Market update:', data);
  }
);

// Unsubscribe when done
subscription.unsubscribe();
```

## Error Handling

```typescript
import { APIError, AuthenticationError, RateLimitError } from '@gridworks/b2b-sdk';

try {
  const result = await sdk.aiSuite.getSupport({
    message: 'Help with portfolio',
    language: 'en'
  });
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Authentication failed:', error.message);
  } else if (error instanceof RateLimitError) {
    console.error('Rate limit exceeded, retry after:', error.retryAfter);
  } else if (error instanceof APIError) {
    console.error('API Error:', error.statusCode, error.message);
  }
}
```

## Analytics and Monitoring

```typescript
// Get request metrics
const metrics = sdk.getMetrics();
console.log('API Performance:', metrics);

// Get service-specific analytics
const aiAnalytics = await sdk.aiSuite.getUsageAnalytics('30d');
const tradingAnalytics = await sdk.trading.getTradingAnalytics('30d');
const bankingAnalytics = await sdk.banking.getBankingAnalytics('30d');
```

## Advanced Configuration

### Custom Retry Logic
```typescript
const sdk = new GridWorksSDK(config, {
  maxConcurrentRequests: 20,
  enableLogging: true,
  websocket: {
    autoReconnect: true,
    reconnectInterval: 3000,
    maxReconnectAttempts: 10
  }
});
```

### Environment-specific Settings
```typescript
// Development environment with extended timeouts
const devSdk = GridWorksSDK.createForEnvironment(
  'development',
  'gw_dev_your_api_key',
  'dev_client_id'
);

// Production with custom headers
const prodSdk = new GridWorksSDK({
  ...config,
  environment: 'production',
  headers: {
    'X-Custom-Header': 'enterprise-client',
    'X-Request-Source': 'trading-dashboard'
  }
});
```

## TypeScript Support

Full TypeScript support with comprehensive type definitions:

```typescript
import type {
  SupportRequest,
  SupportResponse,
  AnonymousPortfolioRequest,
  OrderRequest,
  PaymentRequest
} from '@gridworks/b2b-sdk';

// Type-safe request building
const supportRequest: SupportRequest = {
  message: 'Portfolio analysis needed',
  language: 'en',
  priority: 'high',
  context: {
    userId: 'user_123',
    portfolioValue: 25000000
  }
};
```

## Rate Limiting

The SDK automatically handles rate limits:

```typescript
// SDK will automatically retry with exponential backoff
try {
  const result = await sdk.aiSuite.getSupport(request);
} catch (error) {
  if (error instanceof RateLimitError) {
    // Rate limit exceeded, SDK already retried
    console.log('Please try again after:', error.retryAfter, 'seconds');
  }
}
```

## Security Best Practices

1. **API Key Management**:
   ```typescript
   // Store API keys securely
   const config = {
     apiKey: process.env.GRIDWORKS_API_KEY,
     // Never hardcode API keys
   };
   ```

2. **Request Validation**:
   ```typescript
   // SDK validates API key format
   const isValid = GridWorksSDK.validateApiKey('gw_prod_...');
   ```

3. **Secure Communication**:
   - All requests use HTTPS
   - JWT tokens for enhanced security
   - Request signing for sensitive operations

## Support and Documentation

- **API Documentation**: [https://docs.gridworks.com/api](https://docs.gridworks.com/api)
- **SDK Documentation**: [https://docs.gridworks.com/sdk/typescript](https://docs.gridworks.com/sdk/typescript)
- **Support**: support@gridworks.com
- **GitHub**: [https://github.com/raosunjoy/gridworks-infra](https://github.com/raosunjoy/gridworks-infra)

## License

MIT License - see LICENSE file for details.

---

**GridWorks B2B Infrastructure Services SDK - Powering the future of financial technology! 🚀**