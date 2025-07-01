/**
 * GridWorks WebSocket Client for Real-time Data
 * Supports market data, trading updates, and real-time notifications
 */

interface WebSocketConfig {
  url: string;
  apiKey: string;
  clientId: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  pingInterval?: number;
}

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  channel?: string;
  requestId?: string;
}

interface Subscription {
  id: string;
  channel: string;
  params: any;
  callback: (data: any) => void;
}

export class GridWorksWebSocketClient {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private subscriptions: Map<string, Subscription> = new Map();
  private reconnectAttempts = 0;
  private isConnected = false;
  private pingInterval: NodeJS.Timeout | null = null;

  constructor(config: WebSocketConfig) {
    this.config = {
      autoReconnect: true,
      reconnectInterval: 5000,
      maxReconnectAttempts: 5,
      pingInterval: 30000,
      ...config
    };
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.config.url}?apiKey=${this.config.apiKey}&clientId=${this.config.clientId}`;
      
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('GridWorks WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startPing();
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onclose = (event) => {
        console.log('GridWorks WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.stopPing();
        
        if (this.config.autoReconnect && this.reconnectAttempts < this.config.maxReconnectAttempts!) {
          setTimeout(() => {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
            this.connect();
          }, this.config.reconnectInterval);
        }
      };

      this.ws.onerror = (error) => {
        console.error('GridWorks WebSocket error:', error);
        reject(error);
      };
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.stopPing();
    this.subscriptions.clear();
  }

  /**
   * Subscribe to market data
   */
  subscribeToMarketData(
    symbols: string[],
    dataTypes: string[] = ['quote'],
    exchange?: string
  ): string {
    const subscriptionId = this.generateSubscriptionId();
    
    const subscription: Subscription = {
      id: subscriptionId,
      channel: 'market_data',
      params: { symbols, dataTypes, exchange },
      callback: (data) => {
        // Default callback - can be overridden
        console.log('Market Data:', data);
      }
    };

    this.subscriptions.set(subscriptionId, subscription);
    
    this.sendMessage({
      type: 'subscribe',
      channel: 'market_data',
      data: {
        subscriptionId,
        symbols,
        dataTypes,
        exchange
      }
    });

    return subscriptionId;
  }

  /**
   * Subscribe to trading updates
   */
  subscribeToTradingUpdates(portfolioId?: string): string {
    const subscriptionId = this.generateSubscriptionId();
    
    const subscription: Subscription = {
      id: subscriptionId,
      channel: 'trading_updates',
      params: { portfolioId },
      callback: (data) => {
        console.log('Trading Update:', data);
      }
    };

    this.subscriptions.set(subscriptionId, subscription);
    
    this.sendMessage({
      type: 'subscribe',
      channel: 'trading_updates',
      data: {
        subscriptionId,
        portfolioId
      }
    });

    return subscriptionId;
  }

  /**
   * Subscribe to payment notifications
   */
  subscribeToPaymentNotifications(accountId?: string): string {
    const subscriptionId = this.generateSubscriptionId();
    
    const subscription: Subscription = {
      id: subscriptionId,
      channel: 'payment_notifications',
      params: { accountId },
      callback: (data) => {
        console.log('Payment Notification:', data);
      }
    };

    this.subscriptions.set(subscriptionId, subscription);
    
    this.sendMessage({
      type: 'subscribe',
      channel: 'payment_notifications',
      data: {
        subscriptionId,
        accountId
      }
    });

    return subscriptionId;
  }

  /**
   * Subscribe to AI intelligence updates
   */
  subscribeToIntelligenceUpdates(analysisTypes: string[] = ['morning_pulse']): string {
    const subscriptionId = this.generateSubscriptionId();
    
    const subscription: Subscription = {
      id: subscriptionId,
      channel: 'intelligence_updates',
      params: { analysisTypes },
      callback: (data) => {
        console.log('Intelligence Update:', data);
      }
    };

    this.subscriptions.set(subscriptionId, subscription);
    
    this.sendMessage({
      type: 'subscribe',
      channel: 'intelligence_updates',
      data: {
        subscriptionId,
        analysisTypes
      }
    });

    return subscriptionId;
  }

  /**
   * Set callback for specific subscription
   */
  setSubscriptionCallback(subscriptionId: string, callback: (data: any) => void): void {
    const subscription = this.subscriptions.get(subscriptionId);
    if (subscription) {
      subscription.callback = callback;
    }
  }

  /**
   * Unsubscribe from channel
   */
  unsubscribe(subscriptionId: string): void {
    const subscription = this.subscriptions.get(subscriptionId);
    if (subscription) {
      this.sendMessage({
        type: 'unsubscribe',
        data: { subscriptionId }
      });
      this.subscriptions.delete(subscriptionId);
    }
  }

  /**
   * Unsubscribe from all channels
   */
  unsubscribeAll(): void {
    for (const subscriptionId of this.subscriptions.keys()) {
      this.unsubscribe(subscriptionId);
    }
  }

  /**
   * Send custom message
   */
  sendMessage(message: Partial<WebSocketMessage>): void {
    if (this.ws && this.isConnected) {
      const fullMessage: WebSocketMessage = {
        type: message.type || 'custom',
        data: message.data || {},
        timestamp: new Date().toISOString(),
        channel: message.channel,
        requestId: message.requestId || this.generateRequestId()
      };

      this.ws.send(JSON.stringify(fullMessage));
    } else {
      console.warn('WebSocket not connected. Message not sent:', message);
    }
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(data: string): void {
    try {
      const message: WebSocketMessage = JSON.parse(data);
      
      switch (message.type) {
        case 'market_data':
          this.handleMarketData(message);
          break;
        case 'trading_update':
          this.handleTradingUpdate(message);
          break;
        case 'payment_notification':
          this.handlePaymentNotification(message);
          break;
        case 'intelligence_update':
          this.handleIntelligenceUpdate(message);
          break;
        case 'system_notification':
          this.handleSystemNotification(message);
          break;
        case 'pong':
          // Handle pong response
          break;
        default:
          console.log('Unknown message type:', message.type, message);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Handle market data updates
   */
  private handleMarketData(message: WebSocketMessage): void {
    // Find relevant subscriptions and call callbacks
    for (const subscription of this.subscriptions.values()) {
      if (subscription.channel === 'market_data') {
        subscription.callback(message.data);
      }
    }
  }

  /**
   * Handle trading updates
   */
  private handleTradingUpdate(message: WebSocketMessage): void {
    for (const subscription of this.subscriptions.values()) {
      if (subscription.channel === 'trading_updates') {
        subscription.callback(message.data);
      }
    }
  }

  /**
   * Handle payment notifications
   */
  private handlePaymentNotification(message: WebSocketMessage): void {
    for (const subscription of this.subscriptions.values()) {
      if (subscription.channel === 'payment_notifications') {
        subscription.callback(message.data);
      }
    }
  }

  /**
   * Handle intelligence updates
   */
  private handleIntelligenceUpdate(message: WebSocketMessage): void {
    for (const subscription of this.subscriptions.values()) {
      if (subscription.channel === 'intelligence_updates') {
        subscription.callback(message.data);
      }
    }
  }

  /**
   * Handle system notifications
   */
  private handleSystemNotification(message: WebSocketMessage): void {
    console.log('System Notification:', message.data);
  }

  /**
   * Start ping interval
   */
  private startPing(): void {
    if (this.config.pingInterval) {
      this.pingInterval = setInterval(() => {
        this.sendMessage({ type: 'ping' });
      }, this.config.pingInterval);
    }
  }

  /**
   * Stop ping interval
   */
  private stopPing(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Generate unique subscription ID
   */
  private generateSubscriptionId(): string {
    return `sub_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Get connection status
   */
  isConnectionOpen(): boolean {
    return this.isConnected && this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get active subscriptions
   */
  getActiveSubscriptions(): Subscription[] {
    return Array.from(this.subscriptions.values());
  }
}

// Usage Examples:

/*
// Initialize WebSocket client
const wsClient = new GridWorksWebSocketClient({
  url: 'wss://ws.gridworks.com',
  apiKey: 'gw_prod_your_api_key',
  clientId: 'your_client_id'
});

// Connect
await wsClient.connect();

// Subscribe to market data
const marketDataSub = wsClient.subscribeToMarketData(
  ['RELIANCE', 'TCS', 'INFOSYS'],
  ['quote', 'trade']
);

// Set custom callback for market data
wsClient.setSubscriptionCallback(marketDataSub, (data) => {
  console.log(`${data.symbol}: ${data.price} (${data.change}%)`);
});

// Subscribe to trading updates
const tradingSub = wsClient.subscribeToTradingUpdates('portfolio_123');
wsClient.setSubscriptionCallback(tradingSub, (data) => {
  if (data.type === 'order_filled') {
    console.log(`Order ${data.orderId} filled at ${data.price}`);
  }
});

// Subscribe to payment notifications
const paymentSub = wsClient.subscribeToPaymentNotifications();
wsClient.setSubscriptionCallback(paymentSub, (data) => {
  console.log(`Payment ${data.paymentId} status: ${data.status}`);
});

// Subscribe to AI intelligence updates
const intelligenceSub = wsClient.subscribeToIntelligenceUpdates(['morning_pulse', 'market_correlation']);
wsClient.setSubscriptionCallback(intelligenceSub, (data) => {
  console.log('New Intelligence Update:', data.analysis.summary);
});

// Later, unsubscribe
wsClient.unsubscribe(marketDataSub);

// Disconnect when done
wsClient.disconnect();
*/