export interface HardwareLock {
  deviceId: string;
  hardwareFingerprint: string;
  secureEnclaveId?: string;  // iOS Secure Enclave
  teeId?: string;           // Android Trusted Execution Environment
  biometricHash: string;
  certificateChain: string[];
  lockStrength: 'BASIC' | 'ENHANCED' | 'QUANTUM';
  createdAt: Date;
  expiresAt: Date;
}

export interface AppPackage {
  packageId: string;
  version: string;
  tier: 'onyx' | 'obsidian' | 'void';
  platform: 'ios' | 'android' | 'web';
  packageType: 'pwa' | 'native' | 'hybrid';
  size: number;
  checksum: string;
  signature: string;
  encryptionKey: string;
  distributionMethod: 'direct_download' | 'enterprise_store' | 'private_testflight';
  buildDate: Date;
  minimumOS: string;
  requiredFeatures: string[];
}

export interface DeviceRegistration {
  registrationId: string;
  userId: string;
  deviceId: string;
  deviceName: string;
  platform: 'ios' | 'android';
  osVersion: string;
  hardwareLock: HardwareLock;
  approvalStatus: 'pending' | 'approved' | 'rejected' | 'revoked';
  approvedBy?: string;
  approvedAt?: Date;
  lastVerified: Date;
  trustScore: number;
  riskFactors: string[];
}

export interface AppDistributionRequest {
  requestId: string;
  userId: string;
  tier: 'onyx' | 'obsidian' | 'void';
  deviceRegistration: DeviceRegistration;
  requestedPackage: AppPackage;
  securityAssessment: SecurityAssessment;
  emergencyContact: string;
  businessJustification: string;
  requestedAt: Date;
  approvalWorkflow: ApprovalWorkflow;
}

export interface SecurityAssessment {
  assessmentId: string;
  deviceSecurity: {
    bootloaderLocked: boolean;
    rootDetection: boolean;
    debuggingEnabled: boolean;
    screenRecordingBlocked: boolean;
    malwareDetection: boolean;
  };
  networkSecurity: {
    vpnDetection: boolean;
    proxyDetection: boolean;
    locationSpoofing: boolean;
    networkIntegrity: boolean;
  };
  biometricSecurity: {
    biometricEnabled: boolean;
    multipleFingerprints: boolean;
    faceIdEnabled: boolean;
    voiceIdEnabled: boolean;
  };
  overallScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  recommendations: string[];
}

export interface ApprovalWorkflow {
  workflowId: string;
  currentStage: 'security_review' | 'compliance_check' | 'executive_approval' | 'final_approval';
  stages: ApprovalStage[];
  autoApprovalEligible: boolean;
  escalationRequired: boolean;
  finalDecision?: 'approved' | 'rejected';
  decisionReason?: string;
}

export interface ApprovalStage {
  stageId: string;
  stageName: string;
  assignedTo: string;
  status: 'pending' | 'in_review' | 'approved' | 'rejected';
  comments?: string;
  completedAt?: Date;
  requiredBy: Date;
}

export interface DistributionChannel {
  channelId: string;
  name: string;
  type: 'enterprise_mdm' | 'private_testflight' | 'direct_install' | 'secure_portal';
  platform: 'ios' | 'android' | 'universal';
  tier: 'onyx' | 'obsidian' | 'void';
  securityLevel: 'STANDARD' | 'ENHANCED' | 'QUANTUM';
  configuration: {
    requiresCertificate: boolean;
    allowedDevices: string[];
    geofencing?: GeofenceConfig;
    timeRestrictions?: TimeRestriction[];
  };
}

export interface GeofenceConfig {
  allowedRegions: GeographicRegion[];
  blockedRegions: GeographicRegion[];
  monitoring: boolean;
  alertOnViolation: boolean;
}

export interface GeographicRegion {
  name: string;
  countryCode: string;
  coordinates?: {
    latitude: number;
    longitude: number;
    radius: number;
  };
}

export interface TimeRestriction {
  name: string;
  allowedHours: {
    start: string; // HH:MM format
    end: string;   // HH:MM format
  };
  allowedDays: number[]; // 0-6, Sunday-Saturday
  timezone: string;
}

export interface InstallationPackage {
  packageId: string;
  encryptedPayload: string;
  installationKey: string;
  verificationSignature: string;
  installationInstructions: InstallationStep[];
  securityChecks: SecurityCheck[];
  rollbackPlan: RollbackInstruction[];
}

export interface InstallationStep {
  stepId: string;
  stepType: 'verification' | 'extraction' | 'installation' | 'configuration' | 'validation';
  description: string;
  command?: string;
  expectedResult: string;
  failureAction: 'abort' | 'retry' | 'continue' | 'escalate';
  timeoutSeconds: number;
}

export interface SecurityCheck {
  checkId: string;
  checkType: 'integrity' | 'signature' | 'hardware' | 'network' | 'runtime';
  description: string;
  criticalityLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  checkFunction: string;
  passThreshold: number;
}

export interface RollbackInstruction {
  instructionId: string;
  trigger: 'failure' | 'security_breach' | 'manual' | 'timeout';
  action: 'uninstall' | 'revert_version' | 'disable_features' | 'wipe_data';
  executionOrder: number;
  requiresConfirmation: boolean;
}

export interface DistributionMetrics {
  totalDistributions: number;
  successfulInstallations: number;
  failedInstallations: number;
  securityIncidents: number;
  averageInstallTime: number;
  tierBreakdown: {
    onyx: number;
    obsidian: number;
    void: number;
  };
  platformBreakdown: {
    ios: number;
    android: number;
    web: number;
  };
}

export interface AppUsageAnalytics {
  userId: string;
  deviceId: string;
  sessionId: string;
  startTime: Date;
  endTime?: Date;
  features: FeatureUsage[];
  securityEvents: SecurityEvent[];
  performanceMetrics: PerformanceMetric[];
  crashReports: CrashReport[];
}

export interface FeatureUsage {
  featureId: string;
  featureName: string;
  usageCount: number;
  totalTimeSpent: number;
  lastUsed: Date;
  tier: 'onyx' | 'obsidian' | 'void';
}

export interface SecurityEvent {
  eventId: string;
  eventType: 'authentication' | 'authorization' | 'data_access' | 'network' | 'device';
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  description: string;
  metadata: Record<string, any>;
  timestamp: Date;
  resolved: boolean;
}

export interface PerformanceMetric {
  metricType: 'startup_time' | 'response_time' | 'memory_usage' | 'battery_usage' | 'network_usage';
  value: number;
  unit: string;
  timestamp: Date;
  context?: string;
}

export interface CrashReport {
  crashId: string;
  crashType: 'exception' | 'signal' | 'oom' | 'anr';
  stackTrace: string;
  deviceInfo: DeviceInfo;
  appVersion: string;
  timestamp: Date;
  reproduced: boolean;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface DeviceInfo {
  manufacturer: string;
  model: string;
  osVersion: string;
  screenSize: string;
  memory: number;
  storage: number;
  networkType: string;
  batteryLevel: number;
  orientation: 'portrait' | 'landscape';
}

export interface RemoteConfiguration {
  configId: string;
  userId: string;
  deviceId: string;
  tier: 'onyx' | 'obsidian' | 'void';
  configuration: {
    features: Record<string, boolean>;
    limits: Record<string, number>;
    ui: Record<string, any>;
    security: SecurityConfiguration;
  };
  version: number;
  lastUpdated: Date;
  appliedAt?: Date;
}

export interface SecurityConfiguration {
  biometricRequired: boolean;
  sessionTimeout: number;
  maxFailedAttempts: number;
  screenshotBlocked: boolean;
  screenRecordingBlocked: boolean;
  debuggingBlocked: boolean;
  rootDetectionEnabled: boolean;
  networkSecurityRequired: boolean;
  geofencingEnabled: boolean;
  emergencyWipeEnabled: boolean;
}

export interface AppDistributionEvent {
  eventId: string;
  eventType: 'request_created' | 'approval_granted' | 'package_generated' | 'installation_started' | 'installation_completed' | 'installation_failed' | 'security_violation' | 'device_compromised';
  userId: string;
  deviceId: string;
  packageId?: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  details: Record<string, any>;
  timestamp: Date;
  actionTaken?: string;
  escalated: boolean;
}

export interface QuantumSecurityFeatures {
  quantumKeyDistribution: boolean;
  quantumRandomNumberGeneration: boolean;
  quantumEntanglementVerification: boolean;
  postQuantumCryptography: boolean;
  quantumTamperDetection: boolean;
  quantumSecureChannels: boolean;
}

export interface VoidTierFeatures extends QuantumSecurityFeatures {
  realityDistortionInterface: boolean;
  interdimensionalTrading: boolean;
  timeSpaceArbitrage: boolean;
  quantumPortfolioManagement: boolean;
  parallelDimensionAnalysis: boolean;
  cosmicMarketAccess: boolean;
}

export interface AppDistributionConfig {
  environment: 'development' | 'staging' | 'production';
  securityLevel: 'STANDARD' | 'ENHANCED' | 'QUANTUM';
  distributionChannels: DistributionChannel[];
  approvalWorkflow: {
    autoApprovalThreshold: number;
    escalationTiers: string[];
    timeoutHours: number;
  };
  monitoring: {
    realTimeAlerts: boolean;
    securityScanning: boolean;
    usageAnalytics: boolean;
    performanceMonitoring: boolean;
  };
  quantumFeatures?: QuantumSecurityFeatures;
}