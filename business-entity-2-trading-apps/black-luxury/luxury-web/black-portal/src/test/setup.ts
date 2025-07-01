import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Polyfills for Node.js test environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
    back: jest.fn(),
    beforePopState: jest.fn(),
    prefetch: jest.fn(() => Promise.resolve()),
    reload: jest.fn(),
    route: '/',
    events: {
      on: jest.fn(),
      off: jest.fn(),
      emit: jest.fn(),
    },
  }),
}));

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock Web APIs for luxury portal
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock WebGL context for Three.js
const mockWebGLContext = {
  getParameter: jest.fn((param) => {
    switch (param) {
      case 7936: return 'Mock Vendor'; // VENDOR
      case 7937: return 'Mock Renderer'; // RENDERER
      case 7938: return 'WebGL 1.0'; // VERSION
      default: return null;
    }
  }),
  getSupportedExtensions: jest.fn(() => ['WEBGL_debug_renderer_info']),
};

Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
  writable: true,
  value: jest.fn((contextType) => {
    if (contextType === 'webgl' || contextType === 'experimental-webgl') {
      return mockWebGLContext;
    }
    if (contextType === '2d') {
      return {
        fillRect: jest.fn(),
        clearRect: jest.fn(),
        getImageData: jest.fn(() => ({ data: new Array(4) })),
        putImageData: jest.fn(),
        createImageData: jest.fn(() => ({ data: new Array(4) })),
        setTransform: jest.fn(),
        drawImage: jest.fn(),
        save: jest.fn(),
        fillText: jest.fn(),
        restore: jest.fn(),
        beginPath: jest.fn(),
        moveTo: jest.fn(),
        lineTo: jest.fn(),
        closePath: jest.fn(),
        stroke: jest.fn(),
        translate: jest.fn(),
        scale: jest.fn(),
        rotate: jest.fn(),
        arc: jest.fn(),
        fill: jest.fn(),
        measureText: jest.fn(() => ({ width: 0 })),
        transform: jest.fn(),
        rect: jest.fn(),
        clip: jest.fn(),
      };
    }
    return null;
  }),
});

// Mock HTMLCanvasElement.toDataURL
Object.defineProperty(HTMLCanvasElement.prototype, 'toDataURL', {
  writable: true,
  value: jest.fn(() => 'data:image/png;base64,mock-canvas-data'),
});

// Mock Web Audio API for biometric/device fingerprinting
Object.defineProperty(window, 'AudioContext', {
  writable: true,
  value: jest.fn().mockImplementation(() => ({
    createOscillator: jest.fn(() => ({
      connect: jest.fn(),
      start: jest.fn(),
      stop: jest.fn(),
      frequency: { value: 0 },
    })),
    createAnalyser: jest.fn(() => ({
      connect: jest.fn(),
      getByteFrequencyData: jest.fn(),
      frequencyBinCount: 1024,
    })),
    createGain: jest.fn(() => ({
      connect: jest.fn(),
      gain: { value: 0 },
    })),
    destination: {},
    close: jest.fn(() => Promise.resolve()),
  })),
});

// Mock webkitAudioContext for Safari
Object.defineProperty(window, 'webkitAudioContext', {
  writable: true,
  value: window.AudioContext,
});

// Mock Geolocation API
Object.defineProperty(navigator, 'geolocation', {
  writable: true,
  value: {
    getCurrentPosition: jest.fn((success) => {
      success({
        coords: {
          latitude: 19.0760,
          longitude: 72.8777,
          accuracy: 100,
          altitude: null,
          altitudeAccuracy: null,
          heading: null,
          speed: null,
        },
        timestamp: Date.now(),
      });
    }),
    watchPosition: jest.fn(),
    clearWatch: jest.fn(),
  },
});

// Mock device orientation for mobile testing
Object.defineProperty(window, 'DeviceOrientationEvent', {
  writable: true,
  value: class DeviceOrientationEvent extends Event {
    alpha: number = 0;
    beta: number = 0;
    gamma: number = 0;
    constructor(type: string, eventInitDict?: any) {
      super(type, eventInitDict);
      this.alpha = eventInitDict?.alpha || 0;
      this.beta = eventInitDict?.beta || 0;
      this.gamma = eventInitDict?.gamma || 0;
    }
  },
});

// Mock Touch events for mobile testing
Object.defineProperty(window, 'TouchEvent', {
  writable: true,
  value: class TouchEvent extends Event {
    touches: TouchList = [] as any;
    targetTouches: TouchList = [] as any;
    changedTouches: TouchList = [] as any;
    constructor(type: string, eventInitDict?: any) {
      super(type, eventInitDict);
    }
  },
});

// Mock crypto.subtle for security functions
Object.defineProperty(window, 'crypto', {
  writable: true,
  value: {
    subtle: {
      generateKey: jest.fn(() => Promise.resolve({})),
      exportKey: jest.fn(() => Promise.resolve(new ArrayBuffer(32))),
      importKey: jest.fn(() => Promise.resolve({})),
      encrypt: jest.fn(() => Promise.resolve(new ArrayBuffer(16))),
      decrypt: jest.fn(() => Promise.resolve(new ArrayBuffer(16))),
      sign: jest.fn(() => Promise.resolve(new ArrayBuffer(64))),
      verify: jest.fn(() => Promise.resolve(true)),
      digest: jest.fn(() => Promise.resolve(new ArrayBuffer(32))),
    },
    getRandomValues: jest.fn((array) => {
      for (let i = 0; i < array.length; i++) {
        array[i] = Math.floor(Math.random() * 256);
      }
      return array;
    }),
    randomUUID: jest.fn(() => 'mock-uuid-v4'),
  },
});

// Mock localStorage for session management
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  writable: true,
  value: localStorageMock,
});

Object.defineProperty(window, 'sessionStorage', {
  writable: true,
  value: localStorageMock,
});

// Mock IndexedDB for offline capability
const mockIDBRequest = {
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  result: {},
  error: null,
  onsuccess: null,
  onerror: null,
};

Object.defineProperty(window, 'indexedDB', {
  writable: true,
  value: {
    open: jest.fn(() => mockIDBRequest),
    deleteDatabase: jest.fn(() => mockIDBRequest),
    databases: jest.fn(() => Promise.resolve([])),
  },
});

// Mock ResizeObserver for responsive components
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver for scroll effects
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
  root: null,
  rootMargin: '',
  thresholds: [],
}));

// Mock performance API for metrics
Object.defineProperty(window, 'performance', {
  writable: true,
  value: {
    now: jest.fn(() => Date.now()),
    mark: jest.fn(),
    measure: jest.fn(),
    getEntriesByType: jest.fn(() => []),
    getEntriesByName: jest.fn(() => []),
    clearMarks: jest.fn(),
    clearMeasures: jest.fn(),
    navigation: {
      type: 0,
      redirectCount: 0,
    },
    timing: {
      navigationStart: Date.now(),
      loadEventEnd: Date.now() + 1000,
    },
  },
});

// Mock navigator properties for device fingerprinting
Object.defineProperty(navigator, 'platform', {
  writable: true,
  value: 'MacIntel',
});

Object.defineProperty(navigator, 'language', {
  writable: true,
  value: 'en-US',
});

Object.defineProperty(navigator, 'languages', {
  writable: true,
  value: ['en-US', 'en'],
});

Object.defineProperty(navigator, 'userAgent', {
  writable: true,
  value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
});

Object.defineProperty(navigator, 'hardwareConcurrency', {
  writable: true,
  value: 8,
});

Object.defineProperty(navigator, 'deviceMemory', {
  writable: true,
  value: 8,
});

Object.defineProperty(navigator, 'connection', {
  writable: true,
  value: {
    effectiveType: '4g',
    downlink: 10,
    rtt: 100,
  },
});

// Mock screen properties
Object.defineProperty(screen, 'width', { value: 1920 });
Object.defineProperty(screen, 'height', { value: 1080 });
Object.defineProperty(screen, 'colorDepth', { value: 24 });

// Mock Intl for timezone detection
Object.defineProperty(Intl, 'DateTimeFormat', {
  writable: true,
  value: jest.fn().mockImplementation(() => ({
    resolvedOptions: jest.fn(() => ({
      timeZone: 'Asia/Kolkata',
    })),
  })),
});

// Mock requestAnimationFrame for animations
global.requestAnimationFrame = jest.fn((callback) => {
  setTimeout(callback, 0);
  return 1;
});

global.cancelAnimationFrame = jest.fn();

// Mock Framer Motion
jest.mock('framer-motion', () => ({
  motion: {
    div: 'div',
    button: 'button',
    span: 'span',
    img: 'img',
    section: 'section',
    article: 'article',
    header: 'header',
    footer: 'footer',
    nav: 'nav',
    aside: 'aside',
    main: 'main',
    h1: 'h1',
    h2: 'h2',
    h3: 'h3',
    h4: 'h4',
    h5: 'h5',
    h6: 'h6',
    p: 'p',
    a: 'a',
    ul: 'ul',
    ol: 'ol',
    li: 'li',
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
  useAnimation: () => ({
    start: jest.fn(),
    stop: jest.fn(),
    set: jest.fn(),
  }),
  useMotionValue: (initial: any) => ({
    get: () => initial,
    set: jest.fn(),
    on: jest.fn(),
  }),
  useTransform: () => ({}),
  useSpring: () => ({}),
}));

// Mock Three.js components
jest.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => <div data-testid=\"three-canvas\">{children}</div>,
  useFrame: jest.fn(),
  useThree: () => ({
    camera: { position: { x: 0, y: 0, z: 5 } },
    scene: {},
    gl: {},
    size: { width: 1920, height: 1080 },
  }),
  extend: jest.fn(),
}));

jest.mock('@react-three/drei', () => ({
  OrbitControls: () => null,
  Sphere: () => null,
  Box: () => null,
  Plane: () => null,
  Text: () => null,
  Html: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useGLTF: () => ({ scene: {} }),
  useTexture: () => ({}),
  Environment: () => null,
  ContactShadows: () => null,
  PresentationControls: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock luxury audio for testing
const mockAudio = {
  play: jest.fn(() => Promise.resolve()),
  pause: jest.fn(),
  load: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  currentTime: 0,
  duration: 100,
  volume: 0.5,
  muted: false,
  paused: true,
  ended: false,
  readyState: 4,
};

Object.defineProperty(window, 'Audio', {
  writable: true,
  value: jest.fn(() => mockAudio),
});

// Mock notifications for emergency services
Object.defineProperty(window, 'Notification', {
  writable: true,
  value: jest.fn(() => ({
    permission: 'granted',
    requestPermission: jest.fn(() => Promise.resolve('granted')),
  })),
});

// Mock vibration API for haptic feedback
Object.defineProperty(navigator, 'vibrate', {
  writable: true,
  value: jest.fn(),
});

// Mock file system access for app downloads
Object.defineProperty(window, 'showSaveFilePicker', {
  writable: true,
  value: jest.fn(() => Promise.resolve({
    createWritable: () => Promise.resolve({
      write: jest.fn(),
      close: jest.fn(),
    }),
  })),
});

// Mock fetch for API calls
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ success: true, data: {} }),
    text: () => Promise.resolve(''),
    blob: () => Promise.resolve(new Blob()),
    headers: new Map(),
  })
) as jest.Mock;

// Console warnings suppression for cleaner test output
const originalWarn = console.warn;
const originalError = console.error;

beforeEach(() => {
  console.warn = jest.fn();
  console.error = jest.fn();
});

afterEach(() => {
  console.warn = originalWarn;
  console.error = originalError;
  jest.clearAllMocks();
});

// Global test utilities
export const createMockUser = (tier: 'onyx' | 'obsidian' | 'void' = 'onyx') => ({
  userId: `user_${tier}_001`,
  tier,
  accessLevel: tier === 'void' ? 'exclusive' : tier === 'obsidian' ? 'concierge' : 'premium',
  name: 'Test User',
  email: 'test@example.com',
  portfolioValue: tier === 'void' ? 50000000000 : tier === 'obsidian' ? 2000000000 : 5000000000,
  invitationCode: `${tier.toUpperCase()}2024001`,
  dedicatedButler: `butler_${tier}_001`,
  isActive: true,
  lastActivity: new Date(),
  sessionCount: 10,
  totalTrades: 100,
  totalVolume: 1000000000,
});

export const createMockSession = () => ({
  sessionId: 'session_test_001',
  userId: 'user_test_001',
  deviceId: 'device_test_001',
  startTime: new Date(),
  lastActivity: new Date(),
  sessionDuration: 1800,
  authenticationMethod: 'biometric',
  deviceFingerprint: 'test_fingerprint',
  biometricVerified: true,
  riskScore: 0.1,
  screensVisited: ['mystery_landing', 'invitation_prompt'],
  actionsPerformed: [],
  tradesExecuted: 0,
  volumeTraded: 0,
  butlerConversations: [],
  supportInteractions: 0,
  conciergeRequests: 0,
  responseTimes: [100, 150, 120],
  errorCount: 0,
  securityEvents: [],
  anomaliesDetected: [],
  isSecure: true,
});

export const mockPortalResponse = <T>(data: T) => ({
  success: true,
  data,
  timestamp: new Date(),
  requestId: 'test_request_001',
  tier: 'onyx' as const,
  securityLevel: 'secure' as const,
});

// Test environment setup complete
console.log('🧪 Black Portal test environment initialized with 100% coverage requirements');