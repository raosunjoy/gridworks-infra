/**
 * Custom error classes for GridWorks SDK
 */

export class APIError extends Error {
  public readonly statusCode: number;
  public readonly code: string;
  public readonly details?: any;

  constructor(message: string, statusCode: number, code: string = 'API_ERROR', details?: any) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;

    // Ensure proper prototype chain
    Object.setPrototypeOf(this, APIError.prototype);
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      statusCode: this.statusCode,
      code: this.code,
      details: this.details
    };
  }
}

export class AuthenticationError extends APIError {
  constructor(message: string = 'Authentication failed', details?: any) {
    super(message, 401, 'AUTHENTICATION_ERROR', details);
    this.name = 'AuthenticationError';
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

export class ValidationError extends APIError {
  public readonly field?: string;

  constructor(message: string, field?: string, details?: any) {
    super(message, 400, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
    this.field = field;
    Object.setPrototypeOf(this, ValidationError.prototype);
  }

  toJSON() {
    return {
      ...super.toJSON(),
      field: this.field
    };
  }
}

export class RateLimitError extends APIError {
  public readonly retryAfter?: number;

  constructor(message: string = 'Rate limit exceeded', retryAfter?: number, details?: any) {
    super(message, 429, 'RATE_LIMIT_ERROR', details);
    this.name = 'RateLimitError';
    this.retryAfter = retryAfter;
    Object.setPrototypeOf(this, RateLimitError.prototype);
  }

  toJSON() {
    return {
      ...super.toJSON(),
      retryAfter: this.retryAfter
    };
  }
}

export class ServiceUnavailableError extends APIError {
  constructor(message: string = 'Service temporarily unavailable', details?: any) {
    super(message, 503, 'SERVICE_UNAVAILABLE', details);
    this.name = 'ServiceUnavailableError';
    Object.setPrototypeOf(this, ServiceUnavailableError.prototype);
  }
}

export class NetworkError extends APIError {
  constructor(message: string = 'Network error occurred', details?: any) {
    super(message, 0, 'NETWORK_ERROR', details);
    this.name = 'NetworkError';
    Object.setPrototypeOf(this, NetworkError.prototype);
  }
}

export class TimeoutError extends APIError {
  constructor(message: string = 'Request timeout', details?: any) {
    super(message, 408, 'TIMEOUT_ERROR', details);
    this.name = 'TimeoutError';
    Object.setPrototypeOf(this, TimeoutError.prototype);
  }
}

/**
 * Factory function to create appropriate error from API response
 */
export function createErrorFromResponse(response: any): APIError {
  const { status, data } = response;
  const message = data?.message || 'An error occurred';
  const code = data?.code || 'UNKNOWN_ERROR';
  const details = data?.details;

  switch (status) {
    case 400:
      return new ValidationError(message, data?.field, details);
    case 401:
      return new AuthenticationError(message, details);
    case 429:
      return new RateLimitError(message, data?.retryAfter, details);
    case 503:
      return new ServiceUnavailableError(message, details);
    case 408:
      return new TimeoutError(message, details);
    default:
      return new APIError(message, status, code, details);
  }
}