const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  // Test environment
  testEnvironment: 'jsdom',
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.ts'],
  
  // Test patterns
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}',
  ],
  
  // Module name mapping for path aliases
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/services/(.*)$': '<rootDir>/src/services/$1',
    '^@/types/(.*)$': '<rootDir>/src/types/$1',
    '^@/hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@/utils/(.*)$': '<rootDir>/src/utils/$1',
  },
  
  // Transform patterns
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
  },
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/',
    '<rootDir>/build/',
    '<rootDir>/dist/',
  ],
  
  // Coverage configuration
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/test/**',
    '!src/__tests__/**',
    '!src/**/node_modules/**',
    '!src/**/*.config.{js,ts}',
    '!src/app/layout.tsx', // Exclude Next.js layout
    '!src/app/globals.css', // Exclude CSS files
  ],
  
  // Coverage thresholds for 100% coverage mandate
  coverageThreshold: {
    global: {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100,
    },
    // Component-specific thresholds
    'src/components/**/*.{js,jsx,ts,tsx}': {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100,
    },
    // Service-specific thresholds
    'src/services/**/*.{js,ts}': {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100,
    },
    // Hook-specific thresholds
    'src/hooks/**/*.{js,ts}': {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100,
    },
  },
  
  // Coverage reporters
  coverageReporters: [
    'text',
    'text-summary',
    'html',
    'lcov',
    'json',
    'json-summary',
    'cobertura',
  ],
  
  // Coverage output directory
  coverageDirectory: '<rootDir>/coverage',
  
  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  
  // Global setup/teardown
  globalSetup: '<rootDir>/src/test/globalSetup.ts',
  globalTeardown: '<rootDir>/src/test/globalTeardown.ts',
  
  // Test timeout
  testTimeout: 30000, // 30 seconds for comprehensive E2E tests
  
  // Verbose output for detailed test reporting
  verbose: true,
  
  // Watch mode configuration
  watchman: true,
  
  // Clear mocks between tests
  clearMocks: true,
  restoreMocks: true,
  resetMocks: true,
  
  // Error handling
  errorOnDeprecated: true,
  
  // Snapshot configuration
  snapshotSerializers: ['enzyme-to-json/serializer'],
  
  // Performance configuration
  maxWorkers: '50%', // Use 50% of available CPU cores
  
  // Advanced configuration for luxury portal testing
  resolver: '<rootDir>/src/test/jestResolver.js',
  
  // Custom test environment options
  testEnvironmentOptions: {
    url: 'http://localhost:3000',
    pretendToBeVisual: true,
    resources: 'usable',
  },
  
  // Module directories
  moduleDirectories: ['node_modules', '<rootDir>/src'],
  
  // Transform ignore patterns for node_modules
  transformIgnorePatterns: [
    'node_modules/(?!(framer-motion|@testing-library|@babel)/)',
  ],
  
  // Global variables available in tests
  globals: {
    'ts-jest': {
      useESM: true,
      tsconfig: {
        jsx: 'react-jsx',
      },
    },
    TextEncoder: TextEncoder,
    TextDecoder: TextDecoder,
  },
  
  // Security testing configuration
  projects: [
    {
      displayName: 'Unit Tests',
      testMatch: ['<rootDir>/src/**/__tests__/**/*.test.{js,jsx,ts,tsx}'],
      testPathIgnorePatterns: [
        '<rootDir>/src/**/__tests__/**/e2e/',
        '<rootDir>/src/**/__tests__/**/security/',
        '<rootDir>/src/**/__tests__/**/performance/',
        '<rootDir>/src/**/__tests__/**/integration/',
      ],
    },
    {
      displayName: 'Integration Tests',
      testMatch: ['<rootDir>/src/**/__tests__/**/integration/*.test.{js,jsx,ts,tsx}'],
    },
    {
      displayName: 'E2E Tests',
      testMatch: ['<rootDir>/src/**/__tests__/**/e2e/*.test.{js,jsx,ts,tsx}'],
      testTimeout: 60000, // Longer timeout for E2E tests
    },
    {
      displayName: 'Security Tests',
      testMatch: ['<rootDir>/src/**/__tests__/**/security/*.test.{js,jsx,ts,tsx}'],
      testTimeout: 45000, // Extended timeout for security tests
    },
    {
      displayName: 'Performance Tests',
      testMatch: ['<rootDir>/src/**/__tests__/**/performance/*.test.{js,jsx,ts,tsx}'],
      testTimeout: 30000,
    },
  ],
  
  // Custom reporters
  reporters: [
    'default',
    [
      'jest-html-reporters',
      {
        publicPath: './coverage/html-report',
        filename: 'test-report.html',
        expand: true,
        hideIcon: false,
        pageTitle: 'Black Portal Test Report',
        logoImgPath: undefined,
        inlineSource: false,
      },
    ],
    [
      'jest-junit',
      {
        outputDirectory: './coverage/junit',
        outputName: 'junit.xml',
        ancestorSeparator: ' › ',
        uniqueOutputName: 'false',
        suiteNameTemplate: '{filepath}',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
      },
    ],
  ],
  
  // Luxury portal specific configuration
  setupFiles: [
    '<rootDir>/src/test/browserMocks.ts',
    '<rootDir>/src/test/cryptoMocks.ts',
    '<rootDir>/src/test/webglMocks.ts',
    '<rootDir>/src/test/audioMocks.ts',
  ],
  
  // Test result processor
  testResultsProcessor: '<rootDir>/src/test/testResultsProcessor.js',
  
  // Cache configuration
  cacheDirectory: '<rootDir>/.jest-cache',
  
  // Notification configuration
  notify: true,
  notifyMode: 'failure-change',
  
  // Watch plugins
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],
  
  // Force exit after tests complete
  forceExit: true,
  
  // Detect open handles
  detectOpenHandles: true,
  
  // Run tests in band for debugging
  runInBand: false,
  
  // Maximum number of concurrent test files
  maxConcurrency: 5,
  
  // Bail configuration
  bail: 0, // Don't bail on first failure for comprehensive testing
  
  // Silent configuration
  silent: false,
  
  // Pass with no tests
  passWithNoTests: false,
  
  // Log heap usage
  logHeapUsage: true,
  
  // Use stderr for console output
  useStderr: false,
  
  // Test name pattern
  testNamePattern: undefined,
  
  // Update snapshots
  updateSnapshot: false,
  
  // Test sequence configuration
  testSequencer: '<rootDir>/src/test/testSequencer.js',
};

// Create the final Jest configuration
module.exports = createJestConfig(customJestConfig);