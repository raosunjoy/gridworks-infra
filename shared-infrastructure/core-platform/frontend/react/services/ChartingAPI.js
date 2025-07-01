/**
 * GridWorks Charting API Client
 * 
 * JavaScript client for interacting with the GridWorks charting backend API.
 * Provides methods for session management, chart operations, and real-time features.
 */

class ChartingAPI {
  constructor({ baseURL, authToken, timeout = 30000 }) {
    this.baseURL = baseURL.replace(/\/$/, ''); // Remove trailing slash
    this.authToken = authToken;
    this.timeout = timeout;
    this.apiVersion = 'v1';
  }

  // Private method for making HTTP requests
  async _request(method, endpoint, data = null, options = {}) {
    const url = `${this.baseURL}/api/${this.apiVersion}/charting${endpoint}`;
    
    const config = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.authToken}`,
        ...options.headers
      },
      ...options
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      config.body = JSON.stringify(data);
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);
      
      config.signal = controller.signal;
      
      const response = await fetch(url, config);
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
      }
      
      // Handle different response types
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else if (contentType && contentType.includes('image/')) {
        return await response.blob();
      } else {
        return await response.text();
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  // Session Management
  async createSession(preferences = {}) {
    return await this._request('POST', '/sessions', preferences);
  }

  async getSession(sessionId) {
    return await this._request('GET', `/sessions/${sessionId}`);
  }

  // Chart Management
  async createChart(sessionId, chartConfig) {
    return await this._request('POST', `/sessions/${sessionId}/charts`, chartConfig);
  }

  async getChartData(chartId, limit = 1000) {
    return await this._request('GET', `/charts/${chartId}/data?limit=${limit}`);
  }

  async getChartImage(chartId, { width = 800, height = 600, format = 'png' } = {}) {
    return await this._request('GET', `/charts/${chartId}/image?width=${width}&height=${height}&format=${format}`);
  }

  // Indicators
  async addIndicator(chartId, indicatorConfig) {
    return await this._request('POST', `/charts/${chartId}/indicators`, indicatorConfig);
  }

  async removeIndicator(chartId, indicatorId) {
    return await this._request('DELETE', `/charts/${chartId}/indicators/${indicatorId}`);
  }

  // Drawing Tools
  async addDrawing(chartId, drawingConfig) {
    return await this._request('POST', `/charts/${chartId}/drawings`, drawingConfig);
  }

  async removeDrawing(chartId, drawingId) {
    return await this._request('DELETE', `/charts/${chartId}/drawings/${drawingId}`);
  }

  // Voice Commands
  async executeVoiceCommand(sessionId, command) {
    return await this._request('POST', `/sessions/${sessionId}/voice`, { command });
  }

  // Pattern Detection
  async detectPatterns(chartId) {
    return await this._request('GET', `/charts/${chartId}/patterns`);
  }

  // Alerts
  async createAlert(chartId, alertConfig) {
    return await this._request('POST', `/charts/${chartId}/alerts`, alertConfig);
  }

  // Sharing
  async shareChart(chartId, shareOptions) {
    return await this._request('POST', `/charts/${chartId}/share`, shareOptions);
  }

  // Layouts
  async updateLayout(sessionId, layoutType) {
    return await this._request('PUT', `/sessions/${sessionId}/layout`, { layout_type: layoutType });
  }

  async getAvailableLayouts() {
    return await this._request('GET', '/layouts');
  }

  // Templates
  async saveChartTemplate(chartId, templateName) {
    return await this._request('POST', `/charts/${chartId}/template`, { template_name: templateName });
  }

  async applyChartTemplate(chartId, templateId) {
    return await this._request('POST', `/charts/${chartId}/template/${templateId}/apply`);
  }

  // Health and Metrics
  async getHealth() {
    return await this._request('GET', '/health');
  }

  async getMetrics() {
    return await this._request('GET', '/metrics');
  }

  // Utility methods
  setAuthToken(token) {
    this.authToken = token;
  }

  setTimeout(timeout) {
    this.timeout = timeout;
  }
}

export default ChartingAPI;
export { ChartingAPI };