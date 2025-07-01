import { performance } from 'perf_hooks';

/**
 * Global Jest setup for Black Portal testing
 * Initializes test environment with luxury portal specific configurations
 */
export default async function globalSetup(): Promise<void> {
  const setupStartTime = performance.now();

  console.log('🖤 Initializing Black Portal Test Environment...');

  // Set global test environment variables
  process.env.NODE_ENV = 'test';
  process.env.NEXT_PUBLIC_ENV = 'test';
  process.env.NEXT_PUBLIC_PORTAL_MODE = 'testing';

  // Configure test-specific URLs and endpoints
  process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:3001';
  process.env.NEXT_PUBLIC_PORTAL_URL = 'http://localhost:3000';
  process.env.NEXT_PUBLIC_WEBSOCKET_URL = 'ws://localhost:3002';

  // Luxury portal test configuration
  process.env.NEXT_PUBLIC_TEST_MODE = 'true';
  process.env.NEXT_PUBLIC_SKIP_BIOMETRIC_REAL_AUTH = 'true';
  process.env.NEXT_PUBLIC_MOCK_DEVICE_FINGERPRINT = 'true';
  process.env.NEXT_PUBLIC_MOCK_ZK_PROOFS = 'true';

  // Butler AI test configuration
  process.env.BUTLER_AI_MOCK_MODE = 'true';
  process.env.BUTLER_AI_RESPONSE_DELAY = '100'; // 100ms for faster tests
  process.env.BUTLER_AI_LEARNING_DISABLED = 'true'; // Disable learning in tests

  // Anonymous services test configuration
  process.env.ZK_PROOF_GENERATION_MOCK = 'true';
  process.env.ANONYMOUS_IDENTITY_REAL_GENERATION = 'false';
  process.env.EMERGENCY_SERVICES_MOCK = 'true';

  // Security test configuration
  process.env.BIOMETRIC_AUTH_BYPASS = 'true';
  process.env.DEVICE_FINGERPRINT_MOCK = 'true';
  process.env.HARDWARE_LOCK_SIMULATION = 'true';

  // Performance test configuration
  process.env.PERFORMANCE_MONITORING = 'true';
  process.env.MEMORY_LEAK_DETECTION = 'true';
  process.env.RENDER_PERFORMANCE_TRACKING = 'true';

  // Database and external service mocking
  process.env.DATABASE_URL = 'mock://test-database';
  process.env.REDIS_URL = 'mock://test-redis';
  process.env.ELASTICSEARCH_URL = 'mock://test-elasticsearch';

  // Third-party service mocking
  process.env.TWILIO_MOCK = 'true';
  process.env.AWS_MOCK = 'true';
  process.env.STRIPE_MOCK = 'true';

  // Tier-specific test configuration
  process.env.TEST_TIER_ONYX_CODE = 'ONYX_PREMIUM';
  process.env.TEST_TIER_OBSIDIAN_CODE = 'OBSIDIAN_ELITE';
  process.env.TEST_TIER_VOID_CODE = 'VOID_ACCESS';

  // Anonymous services test data
  process.env.TEST_ANONYMOUS_IDENTITY_ONYX = 'Silver_Navigator_42';
  process.env.TEST_ANONYMOUS_IDENTITY_OBSIDIAN = 'Crystal_Emperor_17';
  process.env.TEST_ANONYMOUS_IDENTITY_VOID = 'Quantum_Sage_99';

  // Security test scenarios
  process.env.PENETRATION_TEST_MODE = 'true';
  process.env.RATE_LIMITING_TEST = 'true';
  process.env.INJECTION_TEST_ENABLED = 'true';

  // Performance benchmarks
  process.env.PERFORMANCE_BENCHMARK_BUTLER_RESPONSE = '2000'; // 2 seconds
  process.env.PERFORMANCE_BENCHMARK_AUTH_COMPLETE = '3000'; // 3 seconds
  process.env.PERFORMANCE_BENCHMARK_FINGERPRINT = '3000'; // 3 seconds
  process.env.PERFORMANCE_BENCHMARK_ZK_PROOF = '1000'; // 1 second

  // Coverage configuration
  process.env.COVERAGE_THRESHOLD_STATEMENTS = '100';
  process.env.COVERAGE_THRESHOLD_BRANCHES = '100';
  process.env.COVERAGE_THRESHOLD_FUNCTIONS = '100';
  process.env.COVERAGE_THRESHOLD_LINES = '100';

  // E2E test configuration
  process.env.E2E_TEST_TIMEOUT = '30000'; // 30 seconds
  process.env.E2E_SCREENSHOT_ON_FAILURE = 'true';
  process.env.E2E_VIDEO_RECORDING = 'true';

  // Initialize test-specific global objects
  setupGlobalTestObjects();

  // Setup crypto API mocking
  setupCryptoMocks();

  // Setup WebGL and Canvas mocking
  setupWebGLMocks();

  // Setup Audio API mocking
  setupAudioMocks();

  // Setup media devices mocking
  setupMediaDevicesMocks();

  // Setup performance monitoring
  setupPerformanceMonitoring();

  // Initialize test database
  await initializeTestDatabase();

  // Warm up test environment
  await warmupTestEnvironment();

  const setupEndTime = performance.now();
  const setupDuration = setupEndTime - setupStartTime;

  console.log(`✅ Black Portal Test Environment Ready (${setupDuration.toFixed(2)}ms)`);
  console.log('🔒 Security tests enabled');
  console.log('⚡ Performance monitoring active');
  console.log('🎭 Anonymous services mocked');
  console.log('🤖 Butler AI in test mode');
  console.log('📊 100% coverage enforced');
}

/**
 * Setup global test objects available across all tests
 */
function setupGlobalTestObjects(): void {
  // Global test utilities
  (global as any).testUtils = {
    generateMockDeviceFingerprint: () => ({
      deviceId: 'test-device-123',
      userAgent: 'Mozilla/5.0 (Test Environment)',
      screenResolution: '1920x1080',
      timezone: 'America/New_York',
      canvasFingerprint: 'mock-canvas-fingerprint',
      webglFingerprint: 'mock-webgl-fingerprint',
      audioFingerprint: 'mock-audio-fingerprint',
      securityAssessment: {
        score: 95,
        factors: ['Mock environment', 'Test security'],
        riskLevel: 'low',
      },
    }),
    
    generateMockZKProof: (tier: string) => ({
      tierVerification: `zk_tier_${tier}_test`,
      paymentCapabilityProof: `zk_payment_${tier}_test`,
      locationRangeProof: 'zk_location_test',
      timeWindowProof: 'zk_time_test',
      emergencyContactProof: 'zk_emergency_test',
    }),
    
    generateMockAnonymousIdentity: (tier: string) => {
      const prefixes = {
        onyx: 'Silver_Navigator',
        obsidian: 'Crystal_Emperor',
        void: 'Quantum_Sage',
      };
      const number = Math.floor(Math.random() * 99) + 1;
      return `${prefixes[tier as keyof typeof prefixes]}_${number}`;
    },
    
    mockButlerResponse: (tier: string, message: string) => ({
      response: `Mock Butler (${tier}): Processed "${message}"`,
      confidence: 0.95,
      personality: tier === 'void' ? 'quantum' : tier === 'obsidian' ? 'mystical' : 'professional',
      processingTime: 100,
    }),
  };

  // Global performance tracking
  (global as any).performanceTracker = {
    measurements: new Map(),
    start: (name: string) => {
      (global as any).performanceTracker.measurements.set(name, performance.now());
    },
    end: (name: string) => {
      const startTime = (global as any).performanceTracker.measurements.get(name);
      if (startTime) {
        const duration = performance.now() - startTime;
        (global as any).performanceTracker.measurements.delete(name);
        return duration;
      }
      return 0;
    },
    clear: () => {
      (global as any).performanceTracker.measurements.clear();
    },
  };
}

/**
 * Setup crypto API mocks for security testing
 */
function setupCryptoMocks(): void {
  const mockCrypto = {
    randomUUID: jest.fn(() => 'test-uuid-123'),
    getRandomValues: jest.fn((array: any) => {
      for (let i = 0; i < array.length; i++) {
        array[i] = Math.floor(Math.random() * 256);
      }
      return array;
    }),
    subtle: {
      generateKey: jest.fn(() => Promise.resolve({})),
      encrypt: jest.fn(() => Promise.resolve(new ArrayBuffer(16))),
      decrypt: jest.fn(() => Promise.resolve(new ArrayBuffer(16))),
      sign: jest.fn(() => Promise.resolve(new ArrayBuffer(32))),
      verify: jest.fn(() => Promise.resolve(true)),
      digest: jest.fn(() => Promise.resolve(new ArrayBuffer(32))),
      importKey: jest.fn(() => Promise.resolve({})),
      exportKey: jest.fn(() => Promise.resolve(new ArrayBuffer(32))),
    },
  };

  Object.defineProperty(global, 'crypto', {
    value: mockCrypto,
    writable: true,
  });
}

/**
 * Setup WebGL and Canvas mocking for fingerprinting tests
 */
function setupWebGLMocks(): void {
  const mockWebGLContext = {
    getParameter: jest.fn((param) => {
      const params = {
        7936: 'Intel Inc.', // VENDOR
        7937: 'Intel Iris Pro', // RENDERER
        7938: '4.1 Intel Iris Pro OpenGL Engine', // VERSION
        34047: ['WEBGL_debug_renderer_info'], // EXTENSIONS
      };
      return params[param as keyof typeof params] || 'mock-value';
    }),
    getExtension: jest.fn(() => ({})),
    getSupportedExtensions: jest.fn(() => ['WEBGL_debug_renderer_info']),
    canvas: {
      width: 300,
      height: 150,
    },
  };

  const mockCanvas = {
    getContext: jest.fn((type) => {
      if (type === 'webgl' || type === 'experimental-webgl') {
        return mockWebGLContext;
      }
      if (type === '2d') {
        return {
          textBaseline: 'top',
          font: '14px Arial',
          fillText: jest.fn(),
          fillStyle: '#000000',
          canvas: mockCanvas,
        };
      }
      return null;
    }),
    toDataURL: jest.fn(() => 'data:image/png;base64,mock-canvas-data'),
    width: 300,
    height: 150,
  };

  // Mock document.createElement for canvas
  const originalCreateElement = document.createElement;
  document.createElement = jest.fn((tagName) => {
    if (tagName === 'canvas') {
      return mockCanvas as any;
    }
    return originalCreateElement.call(document, tagName);
  });
}

/**
 * Setup Audio API mocking for fingerprinting and effects
 */
function setupAudioMocks(): void {
  const mockOscillator = {
    connect: jest.fn(),
    start: jest.fn(),
    stop: jest.fn(),
    frequency: { value: 440 },
    type: 'sine',
  };

  const mockAnalyser = {
    connect: jest.fn(),
    getFloatFrequencyData: jest.fn(),
    fftSize: 2048,
    frequencyBinCount: 1024,
  };

  const mockGain = {
    connect: jest.fn(),
    gain: { value: 1 },
  };

  const mockAudioContext = {
    createOscillator: jest.fn(() => mockOscillator),
    createAnalyser: jest.fn(() => mockAnalyser),
    createGain: jest.fn(() => mockGain),
    destination: {},
    sampleRate: 44100,
    currentTime: 0,
    state: 'running',
    close: jest.fn(),
    resume: jest.fn(),
    suspend: jest.fn(),
  };

  (global as any).AudioContext = jest.fn(() => mockAudioContext);
  (global as any).webkitAudioContext = jest.fn(() => mockAudioContext);

  // Mock Audio constructor
  (global as any).Audio = jest.fn().mockImplementation(() => ({
    play: jest.fn(),
    pause: jest.fn(),
    load: jest.fn(),
    volume: 1,
    currentTime: 0,
    duration: 0,
    paused: true,
    ended: false,
  }));
}

/**
 * Setup media devices mocking for biometric authentication
 */
function setupMediaDevicesMocks(): void {
  const mockMediaStream = {
    getTracks: jest.fn(() => [
      {
        stop: jest.fn(),
        kind: 'video',
        label: 'Mock Camera',
        enabled: true,
      },
    ]),
    getVideoTracks: jest.fn(() => []),
    getAudioTracks: jest.fn(() => []),
  };

  const mockMediaDevices = {
    getUserMedia: jest.fn(() => Promise.resolve(mockMediaStream)),
    enumerateDevices: jest.fn(() => Promise.resolve([
      {
        deviceId: 'camera1',
        kind: 'videoinput',
        label: 'Mock Camera',
        groupId: 'group1',
      },
      {
        deviceId: 'mic1',
        kind: 'audioinput',
        label: 'Mock Microphone',
        groupId: 'group1',
      },
    ])),
    getSupportedConstraints: jest.fn(() => ({
      facingMode: true,
      width: true,
      height: true,
    })),
  };

  Object.defineProperty(navigator, 'mediaDevices', {
    value: mockMediaDevices,
    writable: true,
  });

  // Mock WebAuthn for fingerprint auth
  const mockCredentials = {
    create: jest.fn(() => Promise.resolve({
      id: 'mock-credential-id',
      rawId: new ArrayBuffer(32),
      response: {
        clientDataJSON: new ArrayBuffer(16),
        attestationObject: new ArrayBuffer(64),
      },
      type: 'public-key',
    })),
    get: jest.fn(() => Promise.resolve({
      id: 'mock-credential-id',
      rawId: new ArrayBuffer(32),
      response: {
        clientDataJSON: new ArrayBuffer(16),
        authenticatorData: new ArrayBuffer(32),
        signature: new ArrayBuffer(64),
      },
      type: 'public-key',
    })),
  };

  Object.defineProperty(navigator, 'credentials', {
    value: mockCredentials,
    writable: true,
  });
}

/**
 * Setup performance monitoring for tests
 */
function setupPerformanceMonitoring(): void {
  // Global performance observer
  (global as any).PerformanceObserver = class MockPerformanceObserver {
    constructor(callback: any) {
      this.callback = callback;
    }
    
    observe() {
      // Mock implementation
    }
    
    disconnect() {
      // Mock implementation
    }
  };

  // Performance measurement utilities
  (global as any).measurePerformance = {
    markStart: (name: string) => performance.mark(`${name}-start`),
    markEnd: (name: string) => performance.mark(`${name}-end`),
    measure: (name: string) => {
      try {
        performance.measure(name, `${name}-start`, `${name}-end`);
        const measure = performance.getEntriesByName(name)[0];
        return measure ? measure.duration : 0;
      } catch {
        return 0;
      }
    },
    clear: () => {
      performance.clearMarks();
      performance.clearMeasures();
    },
  };
}

/**
 * Initialize test database with mock data
 */
async function initializeTestDatabase(): Promise<void> {
  // Mock database initialization
  console.log('📦 Initializing test database...');

  // Create mock test data
  const mockTestData = {
    users: [
      {
        id: 'test-user-1',
        tier: 'void',
        anonymousId: 'Quantum_Sage_42',
        portfolio: '₹10,000+ Cr',
      },
      {
        id: 'test-user-2',
        tier: 'obsidian',
        anonymousId: 'Crystal_Emperor_17',
        portfolio: '₹5,000+ Cr',
      },
      {
        id: 'test-user-3',
        tier: 'onyx',
        anonymousId: 'Silver_Navigator_88',
        portfolio: '₹500+ Cr',
      },
    ],
    invitationCodes: [
      { code: 'VOID_ACCESS', tier: 'void', active: true },
      { code: 'OBSIDIAN_ELITE', tier: 'obsidian', active: true },
      { code: 'ONYX_PREMIUM', tier: 'onyx', active: true },
    ],
    socialCircles: [
      { id: 'void_circle', name: 'Quantum Consciousness Collective', memberCount: 8 },
      { id: 'obsidian_circle', name: 'Crystal Empire Network', memberCount: 23 },
      { id: 'onyx_circle', name: 'Silver Stream Society', memberCount: 67 },
    ],
  };

  // Store in global for test access
  (global as any).mockTestData = mockTestData;

  console.log('✅ Test database initialized');
}

/**
 * Warm up test environment for optimal performance
 */
async function warmupTestEnvironment(): Promise<void> {
  console.log('🔥 Warming up test environment...');

  // Pre-load critical modules
  require('react');
  require('react-dom');
  require('@testing-library/react');
  require('@testing-library/jest-dom');
  require('framer-motion');

  // Initialize performance measurements
  (global as any).measurePerformance.clear();

  // Warm up crypto operations
  if (global.crypto?.subtle) {
    try {
      await global.crypto.subtle.digest('SHA-256', new TextEncoder().encode('warmup'));
    } catch {
      // Ignore warmup errors
    }
  }

  console.log('✅ Test environment warmed up');
}