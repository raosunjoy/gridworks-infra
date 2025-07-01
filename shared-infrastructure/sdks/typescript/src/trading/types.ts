/**
 * Types for Trading-as-a-Service
 */

export interface OrderRequest {
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  orderType: 'market' | 'limit' | 'stop' | 'stop_limit';
  price?: number;
  stopPrice?: number;
  timeInForce?: 'DAY' | 'GTC' | 'IOC' | 'FOK';
  exchange?: string;
  clientOrderId?: string;
  metadata?: {
    strategy?: string;
    riskLevel?: string;
    portfolioId?: string;
  };
}

export interface OrderResponse {
  orderId: string;
  clientOrderId?: string;
  status: 'pending' | 'filled' | 'partially_filled' | 'cancelled' | 'rejected';
  symbol: string;
  side: string;
  quantity: number;
  filledQuantity: number;
  averagePrice?: number;
  commission?: number;
  timestamp: string;
  exchange: string;
  executionDetails?: {
    fillPrice: number;
    fillQuantity: number;
    fillTime: string;
    fillId: string;
  }[];
}

export interface MarketDataRequest {
  symbols: string[];
  dataType: 'quote' | 'trade' | 'depth' | 'candles' | 'volume';
  exchange?: string;
  interval?: '1m' | '5m' | '15m' | '1h' | '4h' | '1d';
  startTime?: string;
  endTime?: string;
  limit?: number;
}

export interface MarketDataResponse {
  symbol: string;
  exchange: string;
  timestamp: string;
  data: {
    price?: number;
    bid?: number;
    ask?: number;
    volume?: number;
    high?: number;
    low?: number;
    open?: number;
    close?: number;
    change?: number;
    changePercent?: number;
  };
  metadata?: any;
}

export interface RiskAssessmentRequest {
  portfolioId: string;
  proposedTrade?: OrderRequest;
  timeframe?: string;
  riskMetrics?: string[];
}

export interface RiskAssessmentResponse {
  overallRisk: 'low' | 'medium' | 'high' | 'extreme';
  riskScore: number;
  metrics: {
    var: number; // Value at Risk
    expectedShortfall: number;
    beta: number;
    sharpeRatio: number;
    maxDrawdown: number;
    concentration: number;
  };
  warnings: {
    type: string;
    severity: string;
    message: string;
    recommendation: string;
  }[];
  limits: {
    positionLimit: number;
    exposureLimit: number;
    leverageLimit: number;
    dailyLossLimit: number;
  };
  approved: boolean;
  reason?: string;
}

export interface PortfolioPosition {
  symbol: string;
  quantity: number;
  averagePrice: number;
  marketPrice: number;
  unrealizedPnL: number;
  realizedPnL: number;
  percentOfPortfolio: number;
  lastUpdated: string;
}

export interface TradingAccount {
  accountId: string;
  accountType: 'cash' | 'margin' | 'options';
  balance: {
    cash: number;
    equity: number;
    buyingPower: number;
    marginUsed: number;
    dayTradingBuyingPower: number;
  };
  positions: PortfolioPosition[];
  orders: OrderResponse[];
  riskParameters: {
    maxDailyLoss: number;
    maxPositionSize: number;
    maxLeverage: number;
    allowedInstruments: string[];
  };
}

export interface TradeExecution {
  executionId: string;
  orderId: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  commission: number;
  fees: number;
  timestamp: string;
  exchange: string;
  venue: string;
  liquidityFlag: 'maker' | 'taker';
}