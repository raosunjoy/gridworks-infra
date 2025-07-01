/**
 * Core types and interfaces for GridWorks B2B SDK
 */

export interface GridWorksConfig {
  /** Base URL for GridWorks API */
  baseURL: string;
  
  /** API key for authentication */
  apiKey: string;
  
  /** Optional JWT token for enhanced authentication */
  token?: string;
  
  /** Client ID for tracking */
  clientId: string;
  
  /** Environment (development, staging, production) */
  environment: 'development' | 'staging' | 'production';
  
  /** Request timeout in milliseconds */
  timeout?: number;
  
  /** Enable debug logging */
  debug?: boolean;
  
  /** Custom headers to include with requests */
  headers?: Record<string, string>;
  
  /** Retry configuration */
  retry?: {
    attempts: number;
    delay: number;
    backoff: number;
  };
}

export interface SDKOptions {
  /** Maximum number of concurrent requests */
  maxConcurrentRequests?: number;
  
  /** Enable request/response logging */
  enableLogging?: boolean;
  
  /** Custom user agent */
  userAgent?: string;
  
  /** WebSocket configuration */
  websocket?: {
    autoReconnect: boolean;
    reconnectInterval: number;
    maxReconnectAttempts: number;
  };
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
  requestId: string;
}

export interface PaginatedResponse<T = any> extends APIResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ServiceTier {
  name: 'Starter' | 'Professional' | 'Enterprise' | 'Custom';
  limits: {
    requestsPerMinute: number;
    requestsPerMonth: number;
    features: string[];
  };
}

export interface ClientInfo {
  id: string;
  name: string;
  email: string;
  tier: ServiceTier;
  status: 'active' | 'suspended' | 'trial';
  subscription: {
    plan: string;
    expiresAt: string;
    features: string[];
  };
}

export interface RequestMetrics {
  requestId: string;
  endpoint: string;
  method: string;
  duration: number;
  status: number;
  timestamp: string;
  rateLimitRemaining?: number;
  rateLimitReset?: string;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  channel?: string;
}

export interface AuthenticationInfo {
  type: 'api_key' | 'jwt' | 'oauth';
  token: string;
  expiresAt?: string;
  scopes?: string[];
  clientId: string;
}