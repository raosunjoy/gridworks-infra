/**
 * Logger utility for GridWorks SDK
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  level: LogLevel;
  message: string;
  data?: any;
  timestamp: string;
  requestId?: string;
}

export class Logger {
  private enabled: boolean;
  private logs: LogEntry[] = [];
  private maxLogs = 1000;

  constructor(enabled: boolean = false) {
    this.enabled = enabled;
  }

  /**
   * Log debug message
   */
  debug(message: string, data?: any, requestId?: string): void {
    this.log('debug', message, data, requestId);
  }

  /**
   * Log info message
   */
  info(message: string, data?: any, requestId?: string): void {
    this.log('info', message, data, requestId);
  }

  /**
   * Log warning message
   */
  warn(message: string, data?: any, requestId?: string): void {
    this.log('warn', message, data, requestId);
  }

  /**
   * Log error message
   */
  error(message: string, data?: any, requestId?: string): void {
    this.log('error', message, data, requestId);
  }

  /**
   * Core logging method
   */
  private log(level: LogLevel, message: string, data?: any, requestId?: string): void {
    const entry: LogEntry = {
      level,
      message,
      data,
      timestamp: new Date().toISOString(),
      requestId
    };

    // Add to internal log store
    this.logs.push(entry);
    
    // Trim logs if too many
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Console output if enabled
    if (this.enabled) {
      const prefix = `[GridWorks SDK] [${level.toUpperCase()}] ${entry.timestamp}`;
      const logMessage = requestId ? `${prefix} [${requestId}] ${message}` : `${prefix} ${message}`;

      switch (level) {
        case 'debug':
          console.debug(logMessage, data || '');
          break;
        case 'info':
          console.info(logMessage, data || '');
          break;
        case 'warn':
          console.warn(logMessage, data || '');
          break;
        case 'error':
          console.error(logMessage, data || '');
          break;
      }
    }
  }

  /**
   * Get all logs
   */
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * Get logs by level
   */
  getLogsByLevel(level: LogLevel): LogEntry[] {
    return this.logs.filter(log => log.level === level);
  }

  /**
   * Clear all logs
   */
  clearLogs(): void {
    this.logs = [];
  }

  /**
   * Enable/disable logging
   */
  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  /**
   * Set maximum number of logs to store
   */
  setMaxLogs(maxLogs: number): void {
    this.maxLogs = maxLogs;
    if (this.logs.length > maxLogs) {
      this.logs = this.logs.slice(-maxLogs);
    }
  }

  /**
   * Export logs as JSON
   */
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  /**
   * Get logs for a specific request ID
   */
  getLogsByRequestId(requestId: string): LogEntry[] {
    return this.logs.filter(log => log.requestId === requestId);
  }
}