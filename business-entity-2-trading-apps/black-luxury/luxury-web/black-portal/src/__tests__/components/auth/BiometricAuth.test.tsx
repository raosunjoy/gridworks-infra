import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BiometricAuth } from '../../../components/auth/BiometricAuth';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    svg: ({ children, ...props }: any) => <svg {...props}>{children}</svg>,
    circle: ({ children, ...props }: any) => <circle {...props}>{children}</circle>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Fingerprint: () => <div data-testid="fingerprint-icon">Fingerprint</div>,
  Camera: () => <div data-testid="camera-icon">Camera</div>,
  Mic: () => <div data-testid="mic-icon">Mic</div>,
  Shield: () => <div data-testid="shield-icon">Shield</div>,
  CheckCircle: () => <div data-testid="check-circle-icon">CheckCircle</div>,
  XCircle: () => <div data-testid="x-circle-icon">XCircle</div>,
  AlertTriangle: () => <div data-testid="alert-triangle-icon">AlertTriangle</div>,
  Eye: () => <div data-testid="eye-icon">Eye</div>,
  Zap: () => <div data-testid="zap-icon">Zap</div>,
}));

// Mock WebGL and Canvas APIs
const mockWebGLContext = {
  getParameter: jest.fn(),
  getExtension: jest.fn(),
  getSupportedExtensions: jest.fn(() => ['WEBGL_debug_renderer_info']),
};

const mockCanvas = {
  getContext: jest.fn(() => mockWebGLContext),
  toDataURL: jest.fn(() => 'data:image/png;base64,mock-canvas-data'),
  width: 200,
  height: 50,
};

// Mock getUserMedia
const mockGetUserMedia = jest.fn();
global.navigator.mediaDevices = {
  getUserMedia: mockGetUserMedia,
} as any;

// Mock AudioContext
global.AudioContext = jest.fn().mockImplementation(() => ({
  createOscillator: jest.fn(() => ({
    connect: jest.fn(),
    start: jest.fn(),
    stop: jest.fn(),
    frequency: { value: 0 },
  })),
  createAnalyser: jest.fn(() => ({
    connect: jest.fn(),
    getFloatFrequencyData: jest.fn(),
    fftSize: 2048,
  })),
  createGain: jest.fn(() => ({
    connect: jest.fn(),
    gain: { value: 0 },
  })),
  destination: {},
  close: jest.fn(),
}));

// Mock device fingerprinting hook
jest.mock('../../../hooks/useDeviceFingerprint', () => ({
  useDeviceFingerprint: () => ({
    fingerprint: {
      deviceId: 'mock-device-id',
      userAgent: 'mock-user-agent',
      screenResolution: '1920x1080',
      timezone: 'America/New_York',
      language: 'en-US',
      platform: 'MacIntel',
      cookiesEnabled: true,
      doNotTrack: null,
      canvasFingerprint: 'mock-canvas-fingerprint',
      webglFingerprint: 'mock-webgl-fingerprint',
      audioFingerprint: 'mock-audio-fingerprint',
      hardwareProfile: {
        cores: 8,
        memory: 16,
        gpu: 'Intel Iris Pro'
      },
      networkProfile: {
        connection: 'wifi',
        downlink: 10,
        rtt: 50
      },
      securityAssessment: {
        score: 95,
        factors: ['Modern browser', 'Secure connection', 'No suspicious activity'],
        riskLevel: 'low'
      }
    },
    isLoading: false,
    error: null,
    regenerateFingerprint: jest.fn(),
  }),
}));

describe('BiometricAuth Component', () => {
  const mockOnAuthSuccess = jest.fn();
  const mockOnAuthFailure = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock createElement to return our mock canvas
    document.createElement = jest.fn((tagName) => {
      if (tagName === 'canvas') {
        return mockCanvas as any;
      }
      return document.createElement(tagName);
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  const renderBiometricAuth = (props = {}) => {
    const defaultProps = {
      tier: 'void' as const,
      onAuthSuccess: mockOnAuthSuccess,
      onAuthFailure: mockOnAuthFailure,
    };
    return render(<BiometricAuth {...defaultProps} {...props} />);
  };

  describe('Rendering', () => {
    test('renders biometric authentication title', () => {
      renderBiometricAuth();
      expect(screen.getByText('Biometric Authentication')).toBeInTheDocument();
    });

    test('renders tier-specific welcome message for void', () => {
      renderBiometricAuth({ tier: 'void' });
      expect(screen.getByText(/Welcome to the Quantum Realm/)).toBeInTheDocument();
    });

    test('renders tier-specific welcome message for obsidian', () => {
      renderBiometricAuth({ tier: 'obsidian' });
      expect(screen.getByText(/Enter the Crystal Empire/)).toBeInTheDocument();
    });

    test('renders tier-specific welcome message for onyx', () => {
      renderBiometricAuth({ tier: 'onyx' });
      expect(screen.getByText(/Join the Silver Stream/)).toBeInTheDocument();
    });

    test('renders all biometric method buttons', () => {
      renderBiometricAuth();
      expect(screen.getByText('Facial Recognition')).toBeInTheDocument();
      expect(screen.getByText('Fingerprint Scan')).toBeInTheDocument();
      expect(screen.getByText('Voice Recognition')).toBeInTheDocument();
    });

    test('renders device security assessment', () => {
      renderBiometricAuth();
      expect(screen.getByText('Device Security Assessment')).toBeInTheDocument();
      expect(screen.getByText('Security Score: 95/100')).toBeInTheDocument();
    });

    test('renders required icons', () => {
      renderBiometricAuth();
      expect(screen.getByTestId('camera-icon')).toBeInTheDocument();
      expect(screen.getByTestId('fingerprint-icon')).toBeInTheDocument();
      expect(screen.getByTestId('mic-icon')).toBeInTheDocument();
    });
  });

  describe('Face Recognition', () => {
    test('initiates face recognition when button clicked', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      
      fireEvent.click(faceButton);
      
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        video: { facingMode: 'user' },
      });
    });

    test('shows scanning state during face recognition', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      
      fireEvent.click(faceButton);
      
      await waitFor(() => {
        expect(screen.getByText('Scanning...')).toBeInTheDocument();
      });
    });

    test('handles face recognition success', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      
      fireEvent.click(faceButton);
      
      await waitFor(() => {
        expect(mockOnAuthSuccess).toHaveBeenCalledWith({
          method: 'face',
          confidence: expect.any(Number),
          deviceFingerprint: expect.any(Object),
        });
      }, { timeout: 4000 });
    });

    test('handles face recognition camera permission denied', async () => {
      mockGetUserMedia.mockRejectedValue(new Error('Permission denied'));

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      
      fireEvent.click(faceButton);
      
      await waitFor(() => {
        expect(screen.getByText('Camera access denied')).toBeInTheDocument();
      });
    });
  });

  describe('Fingerprint Recognition', () => {
    test('initiates fingerprint scan when button clicked', async () => {
      // Mock navigator.credentials for WebAuthn
      global.navigator.credentials = {
        create: jest.fn().mockResolvedValue({}),
        get: jest.fn().mockResolvedValue({}),
      } as any;

      renderBiometricAuth();
      const fingerprintButton = screen.getByText('Fingerprint Scan');
      
      fireEvent.click(fingerprintButton);
      
      await waitFor(() => {
        expect(screen.getByText('Place finger on sensor')).toBeInTheDocument();
      });
    });

    test('shows scanning progress during fingerprint scan', async () => {
      global.navigator.credentials = {
        create: jest.fn().mockResolvedValue({}),
      } as any;

      renderBiometricAuth();
      const fingerprintButton = screen.getByText('Fingerprint Scan');
      
      fireEvent.click(fingerprintButton);
      
      await waitFor(() => {
        expect(screen.getByText('Scanning...')).toBeInTheDocument();
      });
    });

    test('handles successful fingerprint authentication', async () => {
      global.navigator.credentials = {
        create: jest.fn().mockResolvedValue({
          id: 'credential-id',
          response: { clientDataJSON: 'mock-data' },
        }),
      } as any;

      renderBiometricAuth();
      const fingerprintButton = screen.getByText('Fingerprint Scan');
      
      fireEvent.click(fingerprintButton);
      
      await waitFor(() => {
        expect(mockOnAuthSuccess).toHaveBeenCalledWith({
          method: 'fingerprint',
          confidence: expect.any(Number),
          deviceFingerprint: expect.any(Object),
        });
      }, { timeout: 4000 });
    });

    test('handles fingerprint authentication failure', async () => {
      global.navigator.credentials = {
        create: jest.fn().mockRejectedValue(new Error('Authentication failed')),
      } as any;

      renderBiometricAuth();
      const fingerprintButton = screen.getByText('Fingerprint Scan');
      
      fireEvent.click(fingerprintButton);
      
      await waitFor(() => {
        expect(screen.getByText('Fingerprint scan failed')).toBeInTheDocument();
      });
    });
  });

  describe('Voice Recognition', () => {
    test('initiates voice recognition when button clicked', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const voiceButton = screen.getByText('Voice Recognition');
      
      fireEvent.click(voiceButton);
      
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        audio: true,
      });
    });

    test('shows voice prompt during recognition', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const voiceButton = screen.getByText('Voice Recognition');
      
      fireEvent.click(voiceButton);
      
      await waitFor(() => {
        expect(screen.getByText(/Please say:/)).toBeInTheDocument();
      });
    });

    test('handles successful voice authentication', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const voiceButton = screen.getByText('Voice Recognition');
      
      fireEvent.click(voiceButton);
      
      await waitFor(() => {
        expect(mockOnAuthSuccess).toHaveBeenCalledWith({
          method: 'voice',
          confidence: expect.any(Number),
          deviceFingerprint: expect.any(Object),
        });
      }, { timeout: 6000 });
    });

    test('handles voice recognition microphone permission denied', async () => {
      mockGetUserMedia.mockRejectedValue(new Error('Permission denied'));

      renderBiometricAuth();
      const voiceButton = screen.getByText('Voice Recognition');
      
      fireEvent.click(voiceButton);
      
      await waitFor(() => {
        expect(screen.getByText('Microphone access denied')).toBeInTheDocument();
      });
    });
  });

  describe('Device Security Assessment', () => {
    test('displays security score and factors', () => {
      renderBiometricAuth();
      
      expect(screen.getByText('Security Score: 95/100')).toBeInTheDocument();
      expect(screen.getByText('Modern browser')).toBeInTheDocument();
      expect(screen.getByText('Secure connection')).toBeInTheDocument();
    });

    test('shows hardware profile information', () => {
      renderBiometricAuth();
      
      expect(screen.getByText('Hardware Profile')).toBeInTheDocument();
      expect(screen.getByText('8 cores, 16GB RAM')).toBeInTheDocument();
      expect(screen.getByText('Intel Iris Pro')).toBeInTheDocument();
    });

    test('displays network information', () => {
      renderBiometricAuth();
      
      expect(screen.getByText('Network: wifi (10 Mbps, 50ms RTT)')).toBeInTheDocument();
    });

    test('shows device fingerprint data', () => {
      renderBiometricAuth();
      
      expect(screen.getByText('Device ID: mock-device-id')).toBeInTheDocument();
      expect(screen.getByText('Screen: 1920x1080')).toBeInTheDocument();
      expect(screen.getByText('Platform: MacIntel')).toBeInTheDocument();
    });
  });

  describe('Tier-Specific Behavior', () => {
    test('shows void tier specific styling and effects', () => {
      renderBiometricAuth({ tier: 'void' });
      
      expect(screen.getByText(/Quantum-level biometric verification/)).toBeInTheDocument();
      expect(screen.getByText(/Accessing the multiverse requires/)).toBeInTheDocument();
    });

    test('shows obsidian tier specific content', () => {
      renderBiometricAuth({ tier: 'obsidian' });
      
      expect(screen.getByText(/Crystal-clear identity verification/)).toBeInTheDocument();
      expect(screen.getByText(/Your empire awaits/)).toBeInTheDocument();
    });

    test('shows onyx tier specific content', () => {
      renderBiometricAuth({ tier: 'onyx' });
      
      expect(screen.getByText(/Premium biometric security/)).toBeInTheDocument();
      expect(screen.getByText(/Enter the exclusive Silver Stream/)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('displays general error for unsupported biometric method', async () => {
      // Mock unsupported environment
      delete (global.navigator as any).credentials;
      delete (global.navigator as any).mediaDevices;

      renderBiometricAuth();
      const fingerprintButton = screen.getByText('Fingerprint Scan');
      
      fireEvent.click(fingerprintButton);
      
      await waitFor(() => {
        expect(screen.getByText('Biometric authentication not supported')).toBeInTheDocument();
      });
    });

    test('shows retry option after failed authentication', async () => {
      mockGetUserMedia.mockRejectedValue(new Error('Permission denied'));

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      
      fireEvent.click(faceButton);
      
      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });
    });

    test('allows retry after error', async () => {
      mockGetUserMedia
        .mockRejectedValueOnce(new Error('Permission denied'))
        .mockResolvedValue({
          getTracks: () => [{ stop: jest.fn() }],
        });

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      
      // First attempt fails
      fireEvent.click(faceButton);
      
      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });

      // Retry
      const retryButton = screen.getByText('Try Again');
      fireEvent.click(retryButton);
      
      await waitFor(() => {
        expect(mockOnAuthSuccess).toHaveBeenCalled();
      }, { timeout: 4000 });
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels for biometric buttons', () => {
      renderBiometricAuth();
      
      const faceButton = screen.getByRole('button', { name: /facial recognition/i });
      const fingerprintButton = screen.getByRole('button', { name: /fingerprint scan/i });
      const voiceButton = screen.getByRole('button', { name: /voice recognition/i });
      
      expect(faceButton).toHaveAttribute('aria-label');
      expect(fingerprintButton).toHaveAttribute('aria-label');
      expect(voiceButton).toHaveAttribute('aria-label');
    });

    test('supports keyboard navigation', () => {
      renderBiometricAuth();
      
      const faceButton = screen.getByText('Facial Recognition');
      
      faceButton.focus();
      expect(faceButton).toHaveFocus();
      
      fireEvent.keyPress(faceButton, { key: 'Enter', code: 'Enter' });
      expect(mockGetUserMedia).toHaveBeenCalled();
    });

    test('provides screen reader announcements for state changes', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      
      fireEvent.click(faceButton);
      
      await waitFor(() => {
        expect(screen.getByText('Scanning...')).toHaveAttribute('aria-live', 'polite');
      });
    });
  });

  describe('Security Features', () => {
    test('prevents multiple simultaneous authentication attempts', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      const fingerprintButton = screen.getByText('Fingerprint Scan');
      
      fireEvent.click(faceButton);
      fireEvent.click(fingerprintButton);
      
      // Only one getUserMedia call should be made
      expect(mockGetUserMedia).toHaveBeenCalledTimes(1);
    });

    test('includes device fingerprint in authentication result', async () => {
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      });

      renderBiometricAuth();
      const faceButton = screen.getByText('Facial Recognition');
      
      fireEvent.click(faceButton);
      
      await waitFor(() => {
        expect(mockOnAuthSuccess).toHaveBeenCalledWith({
          method: 'face',
          confidence: expect.any(Number),
          deviceFingerprint: expect.objectContaining({
            deviceId: 'mock-device-id',
            securityAssessment: expect.objectContaining({
              score: 95,
            }),
          }),
        });
      }, { timeout: 4000 });
    });
  });
});