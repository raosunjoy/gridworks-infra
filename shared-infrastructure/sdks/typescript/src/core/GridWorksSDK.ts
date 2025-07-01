/**
 * Main GridWorks B2B SDK Client
 * Provides unified access to all B2B infrastructure services
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { GridWorksConfig, SDKOptions, APIResponse, RequestMetrics } from './types';
import { APIError, AuthenticationError } from './errors';
import { Logger } from './logger';
import { AISuiteClient } from '../ai-suite/AISuiteClient';
import { AnonymousServicesClient } from '../anonymous-services/AnonymousServicesClient';
import { TradingClient } from '../trading/TradingClient';
import { BankingClient } from '../banking/BankingClient';

export class GridWorksSDK {
  private config: GridWorksConfig;
  private options: SDKOptions;
  private httpClient: AxiosInstance;
  private logger: Logger;
  private requestMetrics: RequestMetrics[] = [];

  // Service clients
  public readonly aiSuite: AISuiteClient;
  public readonly anonymous: AnonymousServicesClient;
  public readonly trading: TradingClient;
  public readonly banking: BankingClient;

  constructor(config: GridWorksConfig, options: SDKOptions = {}) {
    this.config = config;
    this.options = {
      maxConcurrentRequests: 10,
      enableLogging: config.debug || false,
      userAgent: 'GridWorks-SDK/1.0.0',
      websocket: {
        autoReconnect: true,
        reconnectInterval: 5000,
        maxReconnectAttempts: 5
      },
      ...options
    };

    this.logger = new Logger(this.options.enableLogging || false);
    this.httpClient = this.createHttpClient();

    // Initialize service clients
    this.aiSuite = new AISuiteClient(this);
    this.anonymous = new AnonymousServicesClient(this);
    this.trading = new TradingClient(this);
    this.banking = new BankingClient(this);

    this.logger.info('GridWorks SDK initialized', {
      environment: config.environment,
      clientId: config.clientId
    });
  }

  /**
   * Create and configure HTTP client
   */
  private createHttpClient(): AxiosInstance {
    const client = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': this.options.userAgent,
        'X-Client-ID': this.config.clientId,
        'X-SDK-Version': '1.0.0',
        ...this.config.headers
      }
    });

    // Request interceptor
    client.interceptors.request.use(
      (config) => {
        // Add authentication
        if (this.config.token) {
          config.headers.Authorization = `Bearer ${this.config.token}`;
        } else if (this.config.apiKey) {
          config.headers['X-API-Key'] = this.config.apiKey;
        }

        // Add request ID for tracking
        const requestId = this.generateRequestId();
        config.headers['X-Request-ID'] = requestId;

        this.logger.debug('Request initiated', {
          method: config.method?.toUpperCase(),
          url: config.url,
          requestId
        });

        return config;
      },
      (error) => {
        this.logger.error('Request configuration error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    client.interceptors.response.use(
      (response) => {
        const metrics: RequestMetrics = {
          requestId: response.config.headers['X-Request-ID'] as string,
          endpoint: response.config.url || '',
          method: response.config.method?.toUpperCase() || '',
          duration: Date.now() - (response.config as any).startTime,
          status: response.status,
          timestamp: new Date().toISOString(),
          rateLimitRemaining: response.headers['x-ratelimit-remaining'] ? 
            parseInt(response.headers['x-ratelimit-remaining']) : undefined,
          rateLimitReset: response.headers['x-ratelimit-reset']
        };

        this.requestMetrics.push(metrics);
        this.logger.debug('Request completed', metrics);

        return response;
      },
      (error) => {
        if (error.response) {
          // Server responded with error status
          const errorData = error.response.data;
          const apiError = new APIError(
            errorData.message || 'API request failed',
            error.response.status,
            errorData.code,
            errorData.details
          );

          this.logger.error('API Error', {
            status: error.response.status,
            message: apiError.message,
            code: apiError.code
          });

          return Promise.reject(apiError);
        } else if (error.request) {
          // Network error
          this.logger.error('Network Error', error.message);
          return Promise.reject(new APIError('Network error occurred', 0, 'NETWORK_ERROR'));
        } else {
          // Other error
          this.logger.error('Request Error', error.message);
          return Promise.reject(error);
        }
      }
    );

    return client;
  }

  /**
   * Make authenticated API request
   */
  public async request<T = any>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
    endpoint: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<APIResponse<T>> {
    try {
      const startTime = Date.now();
      
      const response = await this.httpClient.request({
        method,
        url: endpoint,
        data,
        ...config,
        // @ts-ignore
        startTime
      });

      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError('Request failed', 500, 'REQUEST_FAILED', error);
    }
  }

  /**
   * Get request metrics for monitoring
   */
  public getMetrics(): RequestMetrics[] {
    return [...this.requestMetrics];
  }

  /**
   * Clear request metrics
   */
  public clearMetrics(): void {
    this.requestMetrics = [];
  }

  /**
   * Test API connectivity
   */
  public async healthCheck(): Promise<boolean> {
    try {
      const response = await this.request('GET', '/health');
      return response.success;
    } catch (error) {
      this.logger.error('Health check failed', error);
      return false;
    }
  }

  /**
   * Get current client information
   */
  public async getClientInfo() {
    return this.request('GET', '/api/v1/client/info');
  }

  /**
   * Update SDK configuration
   */
  public updateConfig(newConfig: Partial<GridWorksConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // Update HTTP client if needed
    if (newConfig.baseURL || newConfig.timeout || newConfig.headers) {
      this.httpClient = this.createHttpClient();
    }

    this.logger.info('SDK configuration updated');
  }

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `gw_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Validate API key format
   */
  public static validateApiKey(apiKey: string): boolean {
    // GridWorks API keys should follow the pattern: gw_[env]_[32_chars]
    const pattern = /^gw_(dev|stg|prod)_[a-zA-Z0-9]{32}$/;
    return pattern.test(apiKey);
  }

  /**
   * Create SDK instance with environment presets
   */
  public static createForEnvironment(
    environment: 'development' | 'staging' | 'production',
    apiKey: string,
    clientId: string,
    options?: SDKOptions
  ): GridWorksSDK {
    const baseURLs = {
      development: 'https://api-dev.gridworks.com',
      staging: 'https://api-staging.gridworks.com',
      production: 'https://api.gridworks.com'
    };

    const config: GridWorksConfig = {
      baseURL: baseURLs[environment],
      apiKey,
      clientId,
      environment,
      timeout: environment === 'development' ? 60000 : 30000,
      debug: environment === 'development'
    };

    return new GridWorksSDK(config, options);
  }
}