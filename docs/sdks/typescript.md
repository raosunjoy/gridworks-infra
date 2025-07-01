# TypeScript/JavaScript SDK

## Enterprise-Grade SDK for GridWorks B2B Infrastructure

The GridWorks TypeScript SDK provides a comprehensive, type-safe interface to all GridWorks B2B infrastructure services. Designed for enterprise applications, it offers complete integration capabilities with modern JavaScript/TypeScript applications.

---

## 🚀 Quick Start

### Installation

```bash
npm install @gridworks/b2b-sdk
# or
yarn add @gridworks/b2b-sdk
```

### Basic Setup

```typescript
import { GridWorksSDK } from '@gridworks/b2b-sdk';

const client = new GridWorksSDK({
  apiKey: 'your-api-key',
  environment: 'production', // 'sandbox' | 'production'
  baseUrl: 'https://api.gridworks.com'
});
```

### First API Call

```typescript
// AI Suite - Get Support Response
const response = await client.aiSuite.getSupportResponse({
  message: 'Hello, I need help with trading',
  language: 'en',
  context: {
    userId: 'user123',
    sessionId: 'session456'
  }
});

console.log(response.reply); // AI-generated response
```

---

## 🏗️ SDK Architecture

### Core Components

```typescript
interface GridWorksSDK {
  // Core service clients
  aiSuite: AISuiteClient;
  anonymous: AnonymousServicesClient;
  trading: TradingClient;
  banking: BankingClient;
  
  // Utility methods
  config: SDKConfig;
  metrics: MetricsCollector;
  logger: Logger;
}
```

### Configuration Options

```typescript
interface GridWorksConfig {
  apiKey: string;
  environment: 'sandbox' | 'production';
  baseUrl?: string;
  timeout?: number;
  retries?: RetryConfig;
  logging?: LoggingConfig;
  metrics?: MetricsConfig;
}

interface RetryConfig {
  attempts: number;
  backoff: 'exponential' | 'linear';
  maxDelay: number;
  retryOn: number[];
}
```

---

## 🤖 AI Suite Client

### Support Engine

```typescript
// Get AI Support Response
const supportResponse = await client.aiSuite.getSupportResponse({
  message: 'How do I buy Reliance shares?',
  language: 'hi', // Hindi support
  context: {
    userId: 'user123',
    conversationId: 'conv456'
  }
});

// Response structure
interface SupportResponse {
  reply: string;
  confidence: number;
  language: string;
  suggestions?: string[];
  actions?: ActionItem[];
}
```

### Intelligence Engine

```typescript
// Get Morning Pulse
const morningPulse = await client.aiSuite.getMorningPulse({
  date: '2025-01-01',
  markets: ['NSE', 'BSE'],
  sectors: ['TECHNOLOGY', 'BANKING']
});

// Market Intelligence
const intelligence = await client.aiSuite.getMarketIntelligence({
  symbol: 'RELIANCE',
  timeframe: '1D',
  analysisType: 'technical'
});

interface MarketIntelligence {
  symbol: string;
  recommendation: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  analysis: {
    technical: TechnicalAnalysis;
    fundamental: FundamentalAnalysis;
    sentiment: SentimentAnalysis;
  };
  priceTargets: PriceTarget[];
}
```

### Moderation Engine

```typescript
// Content Moderation
const moderation = await client.aiSuite.moderateContent({
  content: 'Check out this amazing stock tip!',
  type: 'message',
  context: {
    platform: 'whatsapp',
    userId: 'user123'
  }
});

interface ModerationResult {
  approved: boolean;
  confidence: number;
  flags: ModerationFlag[];
  recommendations: string[];
}
```

### WhatsApp Integration

```typescript
// Send WhatsApp Message
const whatsappResponse = await client.aiSuite.sendWhatsAppMessage({
  to: '+919876543210',
  message: {
    type: 'text',
    content: 'Your trading order has been executed successfully.'
  },
  template?: 'order_confirmation'
});

// Handle WhatsApp Webhook
client.aiSuite.onWhatsAppMessage((message) => {
  console.log('Received:', message.content);
  // Process message and respond
});
```

---

## 🛡️ Anonymous Services Client

### Zero-Knowledge Portfolio Management

```typescript
// Generate ZK Proof for Portfolio
const zkProof = await client.anonymous.generatePortfolioProof({
  portfolioValue: 50000000, // ₹5Cr
  assetClasses: ['equity', 'debt', 'alternative'],
  proofType: 'net_worth',
  tier: 'obsidian'
});

interface ZKProof {
  proof: string;
  publicInputs: string[];
  verificationKey: string;
  metadata: {
    tier: 'onyx' | 'obsidian' | 'void';
    expiryDate: string;
    issuer: string;
  };
}
```

### Anonymous Communications

```typescript
// Send Anonymous Message
const anonMessage = await client.anonymous.sendAnonymousMessage({
  recipient: 'anon_id_xyz',
  message: {
    type: 'deal_flow',
    content: 'Interested in Series B opportunity, ₹100Cr+ deal size'
  },
  encryption: 'end_to_end'
});

// Create Anonymous Identity
const anonIdentity = await client.anonymous.createAnonymousIdentity({
  tier: 'void',
  preferences: {
    dealSize: { min: 100000000, max: 1000000000 },
    sectors: ['fintech', 'healthcare', 'ai'],
    geography: ['india', 'singapore', 'dubai']
  }
});
```

### Butler AI

```typescript
// Interact with Butler AI
const butlerResponse = await client.anonymous.chatWithButler({
  personality: 'nexus', // sterling | prism | nexus
  message: 'Find me private equity opportunities in Indian fintech',
  context: {
    anonymousId: 'anon_123',
    tier: 'void'
  }
});

interface ButlerResponse {
  reply: string;
  recommendations: Investment[];
  networkSuggestions: AnonymousContact[];
  confidentialityLevel: 'public' | 'restricted' | 'confidential';
}
```

---

## 📈 Trading Client

### Order Management

```typescript
// Place Order
const order = await client.trading.placeOrder({
  symbol: 'RELIANCE',
  side: 'BUY',
  quantity: 100,
  orderType: 'LIMIT',
  price: 2500.50,
  exchange: 'NSE',
  productType: 'MIS'
});

// Get Order Status
const orderStatus = await client.trading.getOrderStatus(order.orderId);

// Cancel Order
await client.trading.cancelOrder(order.orderId);
```

### Portfolio Management

```typescript
// Get Portfolio
const portfolio = await client.trading.getPortfolio();

// Get Positions
const positions = await client.trading.getPositions();

// Calculate Portfolio Metrics
const metrics = await client.trading.getPortfolioMetrics({
  period: '1Y',
  benchmark: 'NIFTY50'
});

interface PortfolioMetrics {
  totalValue: number;
  dayPnL: number;
  totalPnL: number;
  returns: {
    daily: number;
    weekly: number;
    monthly: number;
    yearly: number;
  };
  risk: {
    volatility: number;
    sharpeRatio: number;
    maxDrawdown: number;
  };
}
```

### Market Data

```typescript
// Get Live Quotes
const quotes = await client.trading.getQuotes(['RELIANCE', 'TCS', 'INFY']);

// Get Historical Data
const historicalData = await client.trading.getHistoricalData({
  symbol: 'RELIANCE',
  interval: '1D',
  fromDate: '2024-01-01',
  toDate: '2024-12-31'
});

// Subscribe to Real-time Data
client.trading.subscribeToQuotes(['RELIANCE'], (quote) => {
  console.log(`${quote.symbol}: ₹${quote.price}`);
});
```

### Risk Management

```typescript
// Set Risk Limits
await client.trading.setRiskLimits({
  maxLossPerDay: 50000,
  maxPositionSize: 1000000,
  maxLeverage: 5,
  allowedSymbols: ['RELIANCE', 'TCS', 'INFY']
});

// Get Risk Assessment
const riskAssessment = await client.trading.assessRisk({
  orderDetails: {
    symbol: 'RELIANCE',
    quantity: 500,
    side: 'BUY'
  }
});
```

---

## 💳 Banking Client

### Payment Processing

```typescript
// Process Payment
const payment = await client.banking.processPayment({
  amount: 100000,
  currency: 'INR',
  fromAccount: 'acc123',
  toAccount: 'acc456',
  purpose: 'TRADING_DEPOSIT',
  reference: 'TXN789'
});

// Get Payment Status
const paymentStatus = await client.banking.getPaymentStatus(payment.transactionId);
```

### Account Management

```typescript
// Create Virtual Account
const virtualAccount = await client.banking.createVirtualAccount({
  accountType: 'TRADING',
  currency: 'INR',
  clientId: 'client123'
});

// Get Account Balance
const balance = await client.banking.getAccountBalance('acc123');

// Get Transaction History
const transactions = await client.banking.getTransactionHistory({
  accountId: 'acc123',
  fromDate: '2024-01-01',
  toDate: '2024-12-31',
  limit: 100
});
```

### KYC/AML Compliance

```typescript
// Initiate KYC Process
const kycProcess = await client.banking.initiateKYC({
  customerId: 'cust123',
  documents: [
    { type: 'PAN', fileUrl: 'https://...' },
    { type: 'AADHAAR', fileUrl: 'https://...' }
  ]
});

// Check AML Status
const amlStatus = await client.banking.checkAMLStatus({
  customerId: 'cust123',
  transactionId: 'txn456'
});
```

---

## 🔄 Real-time Features

### WebSocket Integration

```typescript
// Connect to WebSocket
const ws = client.connectWebSocket();

// Subscribe to trading updates
ws.subscribe('trading.orders', (update) => {
  console.log('Order update:', update);
});

// Subscribe to market data
ws.subscribe('market.quotes.RELIANCE', (quote) => {
  console.log('RELIANCE quote:', quote);
});

// Subscribe to payment notifications
ws.subscribe('banking.payments', (notification) => {
  console.log('Payment notification:', notification);
});
```

### Event Handling

```typescript
// Order Events
client.trading.onOrderUpdate((order) => {
  console.log(`Order ${order.id} status: ${order.status}`);
});

// Payment Events
client.banking.onPaymentUpdate((payment) => {
  console.log(`Payment ${payment.id} status: ${payment.status}`);
});

// AI Events
client.aiSuite.onIntelligenceUpdate((intelligence) => {
  console.log('New market intelligence:', intelligence);
});
```

---

## 🛠️ Advanced Features

### Custom Configuration

```typescript
const client = new GridWorksSDK({
  apiKey: 'your-api-key',
  environment: 'production',
  baseUrl: 'https://api.gridworks.com',
  timeout: 30000,
  retries: {
    attempts: 3,
    backoff: 'exponential',
    maxDelay: 10000,
    retryOn: [500, 502, 503, 504]
  },
  logging: {
    level: 'info',
    format: 'json',
    destination: 'console'
  },
  metrics: {
    enabled: true,
    endpoint: 'https://metrics.gridworks.com'
  }
});
```

### Request Interceptors

```typescript
// Add request interceptor
client.addRequestInterceptor((config) => {
  config.headers['X-Custom-Header'] = 'custom-value';
  return config;
});

// Add response interceptor
client.addResponseInterceptor((response) => {
  console.log('Response received:', response.status);
  return response;
});
```

### Error Handling

```typescript
try {
  const response = await client.trading.placeOrder(orderData);
} catch (error) {
  if (error instanceof GridWorksAPIError) {
    console.error('API Error:', error.message);
    console.error('Error Code:', error.code);
    console.error('Details:', error.details);
  } else if (error instanceof GridWorksNetworkError) {
    console.error('Network Error:', error.message);
  } else {
    console.error('Unexpected Error:', error);
  }
}
```

### Metrics and Monitoring

```typescript
// Get SDK Metrics
const metrics = client.getMetrics();
console.log('Total API calls:', metrics.totalCalls);
console.log('Average response time:', metrics.averageResponseTime);
console.log('Error rate:', metrics.errorRate);

// Custom Metrics
client.metrics.increment('custom.trading.orders');
client.metrics.gauge('custom.portfolio.value', 1000000);
client.metrics.histogram('custom.response.time', 150);
```

---

## 🔧 Testing and Development

### Mock Client for Testing

```typescript
import { MockGridWorksSDK } from '@gridworks/b2b-sdk/testing';

const mockClient = new MockGridWorksSDK();

// Configure mock responses
mockClient.trading.placeOrder.mockResolvedValue({
  orderId: 'mock123',
  status: 'SUBMITTED',
  timestamp: new Date()
});

// Use in tests
const result = await mockClient.trading.placeOrder(orderData);
expect(result.orderId).toBe('mock123');
```

### Debug Mode

```typescript
const client = new GridWorksSDK({
  apiKey: 'your-api-key',
  debug: true, // Enable debug logging
  logLevel: 'debug'
});

// Debug information will be logged to console
await client.trading.getPortfolio();
```

---

## 📱 Framework Integration

### React Integration

```typescript
import { useGridWorks } from '@gridworks/react-sdk';

function TradingComponent() {
  const { client } = useGridWorks();
  const [portfolio, setPortfolio] = useState(null);
  
  useEffect(() => {
    client.trading.getPortfolio().then(setPortfolio);
  }, [client]);
  
  return (
    <div>
      <h1>Portfolio Value: ₹{portfolio?.totalValue}</h1>
    </div>
  );
}
```

### Next.js Integration

```typescript
// pages/api/trading/portfolio.ts
import { GridWorksSDK } from '@gridworks/b2b-sdk';

export default async function handler(req, res) {
  const client = new GridWorksSDK({
    apiKey: process.env.GRIDWORKS_API_KEY,
    environment: process.env.NODE_ENV === 'production' ? 'production' : 'sandbox'
  });
  
  const portfolio = await client.trading.getPortfolio();
  res.json(portfolio);
}
```

### Node.js Server Integration

```typescript
import express from 'express';
import { GridWorksSDK } from '@gridworks/b2b-sdk';

const app = express();
const client = new GridWorksSDK({
  apiKey: process.env.GRIDWORKS_API_KEY,
  environment: 'production'
});

app.post('/api/orders', async (req, res) => {
  try {
    const order = await client.trading.placeOrder(req.body);
    res.json(order);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

---

## 📚 Complete API Reference

### Type Definitions

```typescript
// Core Types
export interface Order {
  orderId: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price?: number;
  orderType: 'MARKET' | 'LIMIT' | 'STOP_LOSS';
  status: 'PENDING' | 'SUBMITTED' | 'FILLED' | 'CANCELLED';
  timestamp: Date;
}

export interface Portfolio {
  totalValue: number;
  dayPnL: number;
  positions: Position[];
  holdings: Holding[];
}

export interface AIResponse {
  reply: string;
  confidence: number;
  language: string;
  timestamp: Date;
}

export interface ZKProof {
  proof: string;
  publicInputs: string[];
  verificationKey: string;
  metadata: ProofMetadata;
}

export interface Payment {
  transactionId: string;
  amount: number;
  currency: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  timestamp: Date;
}
```

---

## 🚀 Performance Optimization

### Connection Pooling

```typescript
const client = new GridWorksSDK({
  apiKey: 'your-api-key',
  connectionPool: {
    maxConnections: 20,
    keepAlive: true,
    timeout: 30000
  }
});
```

### Request Batching

```typescript
// Batch multiple requests
const batchRequest = client.createBatch();
batchRequest.add('portfolio', client.trading.getPortfolio());
batchRequest.add('quotes', client.trading.getQuotes(['RELIANCE', 'TCS']));
batchRequest.add('balance', client.banking.getAccountBalance('acc123'));

const results = await batchRequest.execute();
console.log(results.portfolio);
console.log(results.quotes);
console.log(results.balance);
```

### Caching

```typescript
const client = new GridWorksSDK({
  apiKey: 'your-api-key',
  cache: {
    enabled: true,
    ttl: 60000, // 1 minute
    maxSize: 1000
  }
});

// Subsequent calls within TTL will return cached results
const portfolio1 = await client.trading.getPortfolio(); // API call
const portfolio2 = await client.trading.getPortfolio(); // Cached result
```

---

The GridWorks TypeScript SDK provides a comprehensive, type-safe, and performance-optimized interface to all GridWorks B2B infrastructure services, enabling rapid development of enterprise-grade financial applications.