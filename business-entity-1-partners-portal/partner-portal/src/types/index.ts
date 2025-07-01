// Core Partner Portal Types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: UserRole;
  partnerId?: string;
  permissions: Permission[];
  lastActivity: Date;
  preferences: UserPreferences;
}

export interface Partner {
  id: string;
  name: string;
  companyName: string;
  email: string;
  phone: string;
  website?: string;
  logo?: string;
  status: PartnerStatus;
  tier: PartnerTier;
  billingInfo: BillingInfo;
  apiKeys: ApiKeys;
  settings: PartnerSettings;
  createdAt: Date;
  updatedAt: Date;
}

export interface ApiKeys {
  apiKey: string;
  secretKey: string;
  webhookUrl?: string;
  sandboxApiKey?: string;
  sandboxSecretKey?: string;
}

export interface BillingInfo {
  plan: BillingPlan;
  monthlyLimit: number;
  currentUsage: number;
  billingCycle: 'monthly' | 'annual';
  nextBillingDate: Date;
  paymentMethod?: PaymentMethod;
}

export interface PaymentMethod {
  type: 'card' | 'bank';
  last4: string;
  brand?: string;
  expiryMonth?: number;
  expiryYear?: number;
}

export interface PartnerSettings {
  webhookUrl?: string;
  allowedOrigins: string[];
  rateLimits: RateLimits;
  features: FeatureFlags;
  branding: BrandingConfig;
}

export interface RateLimits {
  requestsPerMinute: number;
  requestsPerHour: number;
  requestsPerDay: number;
}

export interface FeatureFlags {
  sandbox: boolean;
  webhooks: boolean;
  analytics: boolean;
  customBranding: boolean;
  prioritySupport: boolean;
}

export interface BrandingConfig {
  primaryColor?: string;
  logo?: string;
  favicon?: string;
  customDomain?: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  timezone: string;
  notifications: NotificationSettings;
}

export interface NotificationSettings {
  email: boolean;
  browser: boolean;
  slack: boolean;
  webhook: boolean;
}

// Enums
export enum UserRole {
  ADMIN = 'admin',
  DEVELOPER = 'developer',
  BUSINESS_USER = 'business_user',
  VIEWER = 'viewer'
}

export enum PartnerStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  PENDING = 'pending',
  CANCELLED = 'cancelled'
}

export enum PartnerTier {
  STARTER = 'starter',
  PROFESSIONAL = 'professional',
  ENTERPRISE = 'enterprise'
}

export enum BillingPlan {
  STARTER = 'starter',
  PROFESSIONAL = 'professional', 
  ENTERPRISE = 'enterprise',
  CUSTOM = 'custom'
}

export enum Permission {
  // API Management
  API_READ = 'api:read',
  API_WRITE = 'api:write',
  API_DELETE = 'api:delete',
  
  // User Management
  USER_READ = 'user:read',
  USER_WRITE = 'user:write',
  USER_DELETE = 'user:delete',
  
  // Billing
  BILLING_READ = 'billing:read',
  BILLING_WRITE = 'billing:write',
  
  // Analytics
  ANALYTICS_READ = 'analytics:read',
  ANALYTICS_EXPORT = 'analytics:export',
  
  // Admin
  ADMIN_READ = 'admin:read',
  ADMIN_WRITE = 'admin:write',
  
  // Support
  SUPPORT_READ = 'support:read',
  SUPPORT_WRITE = 'support:write'
}

// Self-Healing Types
export interface HealthMetric {
  service: string;
  status: HealthStatus;
  responseTime: number;
  errorRate: number;
  memoryUsage: number;
  cpuUsage: number;
  timestamp: Date;
}

export enum HealthStatus {
  HEALTHY = 'healthy',
  DEGRADED = 'degraded',
  CRITICAL = 'critical',
  UNKNOWN = 'unknown'
}

export interface SelfHealingState {
  healingStatus: {
    overall: HealthStatus;
    services: ServiceHealth[];
    lastUpdate: Date;
  };
  metrics: {
    autoRecoveryRate: number;
    incidentsPrevented: number;
    recoveryTrend: 'up' | 'down' | 'stable';
    predictions: PredictiveInsight[];
  };
  incidents: HealingIncident[];
  updateHealingStatus: (status: any) => Promise<void>;
  triggerAutoRecovery: () => Promise<void>;
}

export interface ServiceHealth {
  name: string;
  status: HealthStatus;
  lastCheck: Date;
  responseTime: number;
  errorRate: number;
  uptime: number;
}

export interface PredictiveInsight {
  type: 'warning' | 'info' | 'critical';
  message: string;
  probability: number;
  timeframe: string;
  suggestedAction?: string;
}

export interface HealingIncident {
  id: string;
  type: 'auto_recovery' | 'preventive_action' | 'manual_intervention';
  service: string;
  description: string;
  status: 'resolved' | 'in_progress' | 'failed';
  timestamp: Date;
  duration?: number;
  actions: string[];
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
  timestamp: Date;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date;
  userId?: string;
  partnerId?: string;
}

// Analytics Types
export interface Analytics {
  overview: AnalyticsOverview;
  usage: UsageMetrics;
  performance: PerformanceMetrics;
  errors: ErrorMetrics;
}

export interface AnalyticsOverview {
  totalRequests: number;
  successRate: number;
  avgResponseTime: number;
  activeUsers: number;
  topEndpoints: EndpointUsage[];
}

export interface UsageMetrics {
  daily: UsageData[];
  monthly: UsageData[];
  yearly: UsageData[];
}

export interface UsageData {
  date: string;
  requests: number;
  users: number;
  errors: number;
}

export interface PerformanceMetrics {
  responseTime: {
    p50: number;
    p95: number;
    p99: number;
  };
  throughput: number;
  errorRate: number;
}

export interface ErrorMetrics {
  total: number;
  byCode: Record<string, number>;
  byEndpoint: Record<string, number>;
  recent: ErrorEvent[];
}

export interface ErrorEvent {
  id: string;
  code: string;
  message: string;
  endpoint: string;
  timestamp: Date;
  userId?: string;
}

export interface EndpointUsage {
  endpoint: string;
  requests: number;
  avgResponseTime: number;
  errorRate: number;
}

// Support Types
export interface SupportTicket {
  id: string;
  title: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  category: TicketCategory;
  userId: string;
  partnerId: string;
  assignedTo?: string;
  createdAt: Date;
  updatedAt: Date;
  messages: TicketMessage[];
  tags: string[];
}

export enum TicketStatus {
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved',
  CLOSED = 'closed'
}

export enum TicketPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum TicketCategory {
  API = 'api',
  BILLING = 'billing',
  TECHNICAL = 'technical',
  FEATURE_REQUEST = 'feature_request',
  BUG_REPORT = 'bug_report',
  OTHER = 'other'
}

export interface TicketMessage {
  id: string;
  content: string;
  userId: string;
  userType: 'partner' | 'support';
  timestamp: Date;
  attachments?: Attachment[];
}

export interface Attachment {
  id: string;
  filename: string;
  url: string;
  size: number;
  mimeType: string;
}