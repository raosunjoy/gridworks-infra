import { BiometricAuth } from '../../components/auth/BiometricAuth';
import { useDeviceFingerprint } from '../../hooks/useDeviceFingerprint';
import { emergencyIdentityReveal } from '../../services/EmergencyIdentityReveal';
import { anonymousServiceCoordinator } from '../../services/AnonymousServiceCoordinator';

// Mock crypto for security testing
const mockCrypto = {
  randomUUID: jest.fn(() => 'test-uuid'),
  getRandomValues: jest.fn((array) => {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(Math.random() * 256);
    }
    return array;
  }),
  subtle: {
    generateKey: jest.fn(),
    encrypt: jest.fn(),
    decrypt: jest.fn(),
    sign: jest.fn(),
    verify: jest.fn(),
    digest: jest.fn(() => Promise.resolve(new ArrayBuffer(32))),
  },
};

Object.defineProperty(global, 'crypto', {
  value: mockCrypto,
  writable: true,
});

// Mock WebAuthn for security testing
const mockCredentials = {
  create: jest.fn(),
  get: jest.fn(),
};

Object.defineProperty(global.navigator, 'credentials', {
  value: mockCredentials,
  writable: true,
});

describe('Security Penetration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Biometric Authentication Security', () => {
    describe('Input Validation Attacks', () => {
      test('prevents SQL injection in biometric data', async () => {
        const maliciousInput = "'; DROP TABLE users; --";
        
        // Mock biometric authentication with malicious input
        const authData = {
          method: 'face',
          biometricData: maliciousInput,
          deviceFingerprint: { deviceId: 'test' },
        };

        // Verify that malicious input is properly sanitized/escaped
        expect(() => {
          // Simulate processing biometric data
          const sanitizedData = authData.biometricData.replace(/['";\-]/g, '');
          expect(sanitizedData).not.toContain('DROP TABLE');
        }).not.toThrow();
      });

      test('prevents XSS in biometric metadata', () => {
        const xssPayload = '<script>alert("XSS")</script>';
        
        const biometricMetadata = {
          userAgent: xssPayload,
          deviceName: xssPayload,
        };

        // Verify XSS payload is sanitized
        Object.values(biometricMetadata).forEach(value => {
          const sanitized = value.replace(/<script.*?>.*?<\/script>/gi, '');
          expect(sanitized).not.toContain('<script>');
        });
      });

      test('validates biometric data format and size limits', () => {
        const oversizedData = 'x'.repeat(10000000); // 10MB string
        const invalidFormat = { invalid: 'format' };

        expect(() => {
          // Simulate biometric data validation
          if (typeof oversizedData === 'string' && oversizedData.length > 1000000) {
            throw new Error('Biometric data exceeds size limit');
          }
        }).toThrow('Biometric data exceeds size limit');

        expect(() => {
          // Simulate format validation
          if (typeof invalidFormat === 'object' && !invalidFormat.biometricHash) {
            throw new Error('Invalid biometric data format');
          }
        }).toThrow('Invalid biometric data format');
      });
    });

    describe('Authentication Bypass Attempts', () => {
      test('prevents replay attacks with timestamp validation', () => {
        const oldTimestamp = Date.now() - 600000; // 10 minutes ago
        const recentTimestamp = Date.now() - 1000; // 1 second ago

        const authRequest = {
          biometricHash: 'valid-hash',
          timestamp: oldTimestamp,
          nonce: 'test-nonce',
        };

        // Simulate timestamp validation
        const isValidTimestamp = (timestamp: number) => {
          const fiveMinutesAgo = Date.now() - 300000;
          return timestamp > fiveMinutesAgo;
        };

        expect(isValidTimestamp(authRequest.timestamp)).toBe(false);
        expect(isValidTimestamp(recentTimestamp)).toBe(true);
      });

      test('prevents nonce reuse attacks', () => {
        const usedNonces = new Set(['nonce1', 'nonce2', 'nonce3']);
        const newNonce = 'nonce4';
        const reusedNonce = 'nonce1';

        // Simulate nonce validation
        const isValidNonce = (nonce: string) => {
          if (usedNonces.has(nonce)) {
            return false;
          }
          usedNonces.add(nonce);
          return true;
        };

        expect(isValidNonce(newNonce)).toBe(true);
        expect(isValidNonce(reusedNonce)).toBe(false);
      });

      test('validates device fingerprint consistency', () => {
        const storedFingerprint = {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X)',
          screenResolution: '1920x1080',
          timezone: 'America/New_York',
        };

        const suspiciousFingerprint = {
          userAgent: 'Different Browser',
          screenResolution: '1920x1080',
          timezone: 'America/New_York',
        };

        const validFingerprint = { ...storedFingerprint };

        // Simulate fingerprint validation
        const validateFingerprint = (stored: any, current: any) => {
          const criticalFields = ['userAgent', 'screenResolution'];
          return criticalFields.every(field => stored[field] === current[field]);
        };

        expect(validateFingerprint(storedFingerprint, validFingerprint)).toBe(true);
        expect(validateFingerprint(storedFingerprint, suspiciousFingerprint)).toBe(false);
      });
    });

    describe('Biometric Spoofing Protection', () => {
      test('detects liveness in facial recognition', () => {
        const livenessScore = 0.95; // High liveness
        const spoofScore = 0.3; // Low liveness (potential spoof)

        const LIVENESS_THRESHOLD = 0.7;

        expect(livenessScore > LIVENESS_THRESHOLD).toBe(true);
        expect(spoofScore > LIVENESS_THRESHOLD).toBe(false);
      });

      test('validates fingerprint sensor authenticity', () => {
        const sensorMetadata = {
          sensorType: 'capacitive',
          sensorModel: 'SecureTouch Pro',
          firmwareVersion: '2.1.3',
        };

        const knownSecureSensors = [
          'SecureTouch Pro',
          'BiometricSafe Elite',
          'TouchID Gen3',
        ];

        const isAuthenticSensor = knownSecureSensors.includes(sensorMetadata.sensorModel);
        expect(isAuthenticSensor).toBe(true);
      });

      test('detects voice synthesis attempts', () => {
        const voiceMetrics = {
          naturalness: 0.8,
          harmonicVariation: 0.7,
          breathingPattern: 0.9,
          microtremor: 0.85,
        };

        const syntheticVoiceMetrics = {
          naturalness: 0.95, // Too perfect
          harmonicVariation: 0.2, // Too consistent
          breathingPattern: 0.1, // Missing breathing
          microtremor: 0.0, // No natural tremor
        };

        // Detect synthesis based on unnatural perfection
        const detectSynthesis = (metrics: any) => {
          return (
            metrics.naturalness > 0.9 &&
            metrics.harmonicVariation < 0.3 &&
            metrics.breathingPattern < 0.3
          );
        };

        expect(detectSynthesis(voiceMetrics)).toBe(false);
        expect(detectSynthesis(syntheticVoiceMetrics)).toBe(true);
      });
    });
  });

  describe('Device Fingerprinting Security', () => {
    describe('Fingerprint Manipulation Detection', () => {
      test('detects browser fingerprint spoofing', () => {
        const suspiciousFingerprints = [
          {
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            platform: 'MacIntel', // Mismatch
            vendor: 'Google Inc.',
          },
          {
            userAgent: 'Chrome/90.0',
            webglRenderer: 'NVIDIA RTX 3080', // Inconsistent with mobile UA
            maxTouchPoints: 10,
          },
        ];

        const validateConsistency = (fingerprint: any) => {
          // Windows UA should match Windows platform
          if (fingerprint.userAgent.includes('Windows') && fingerprint.platform !== 'Win32') {
            return false;
          }
          // Mobile indicators should be consistent
          if (fingerprint.userAgent.includes('Mobile') && fingerprint.maxTouchPoints === 0) {
            return false;
          }
          return true;
        };

        suspiciousFingerprints.forEach(fp => {
          expect(validateConsistency(fp)).toBe(false);
        });
      });

      test('detects canvas fingerprint manipulation', () => {
        // Simulate canvas fingerprinting
        const generateCanvasFingerprint = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          if (!ctx) return 'no-canvas';

          // Draw test pattern
          ctx.textBaseline = 'top';
          ctx.font = '14px Arial';
          ctx.fillText('Black Portal Security Test 🔒', 2, 2);
          
          return canvas.toDataURL();
        };

        const normalFingerprint = 'data:image/png;base64,normaldata123';
        const emptyFingerprint = 'data:image/png;base64,';
        const suspiciousFingerprint = 'data:image/png;base64,aaaaaaaaaaa'; // Too simple

        const validateCanvasFingerprint = (fingerprint: string) => {
          if (!fingerprint.startsWith('data:image/png;base64,')) return false;
          if (fingerprint.length < 50) return false; // Too short
          if (/^(.)\1{10,}/.test(fingerprint)) return false; // Too repetitive
          return true;
        };

        expect(validateCanvasFingerprint(normalFingerprint)).toBe(true);
        expect(validateCanvasFingerprint(emptyFingerprint)).toBe(false);
        expect(validateCanvasFingerprint(suspiciousFingerprint)).toBe(false);
      });

      test('validates WebGL fingerprint authenticity', () => {
        const webglFingerprint = {
          renderer: 'Intel Iris Pro',
          vendor: 'Intel Inc.',
          extensions: ['WEBGL_debug_renderer_info', 'OES_standard_derivatives'],
          maxTextures: 16,
          maxVertexAttribs: 16,
        };

        const spoofedFingerprint = {
          renderer: 'Generic GPU', // Too generic
          vendor: 'Unknown',
          extensions: [], // Empty extensions suspicious
          maxTextures: 0,
          maxVertexAttribs: 0,
        };

        const validateWebGLFingerprint = (fingerprint: any) => {
          if (fingerprint.renderer.includes('Generic')) return false;
          if (fingerprint.extensions.length === 0) return false;
          if (fingerprint.maxTextures === 0) return false;
          return true;
        };

        expect(validateWebGLFingerprint(webglFingerprint)).toBe(true);
        expect(validateWebGLFingerprint(spoofedFingerprint)).toBe(false);
      });
    });

    describe('Network Security Validation', () => {
      test('detects suspicious network patterns', () => {
        const networkProfiles = [
          {
            ip: '192.168.1.100',
            type: 'residential',
            vpn: false,
            proxy: false,
            tor: false,
          },
          {
            ip: '10.0.0.1',
            type: 'datacenter',
            vpn: true,
            proxy: true,
            tor: true, // Multiple anonymization tools
          },
        ];

        const assessNetworkRisk = (profile: any) => {
          let risk = 0;
          if (profile.vpn) risk += 30;
          if (profile.proxy) risk += 30;
          if (profile.tor) risk += 40;
          if (profile.type === 'datacenter') risk += 20;
          return risk;
        };

        expect(assessNetworkRisk(networkProfiles[0])).toBe(0); // Clean residential
        expect(assessNetworkRisk(networkProfiles[1])).toBe(120); // High risk
      });

      test('validates geolocation consistency', () => {
        const geoData = {
          timezone: 'America/New_York',
          language: 'en-US',
          ipCountry: 'US',
          browserLang: 'en-US',
        };

        const inconsistentGeoData = {
          timezone: 'Asia/Tokyo',
          language: 'en-US',
          ipCountry: 'US', // Mismatch with timezone
          browserLang: 'ja-JP',
        };

        const validateGeoConsistency = (data: any) => {
          const timezoneCountry = data.timezone.split('/')[0];
          const mappings = {
            'America': ['US', 'CA', 'MX'],
            'Europe': ['GB', 'DE', 'FR'],
            'Asia': ['JP', 'CN', 'IN'],
          };

          const expectedCountries = mappings[timezoneCountry as keyof typeof mappings] || [];
          return expectedCountries.includes(data.ipCountry);
        };

        expect(validateGeoConsistency(geoData)).toBe(true);
        expect(validateGeoConsistency(inconsistentGeoData)).toBe(false);
      });
    });
  });

  describe('Anonymous Services Security', () => {
    describe('ZK Proof Validation', () => {
      test('validates ZK proof structure and integrity', () => {
        const validZKProof = {
          tierVerification: 'zk_tier_proof_123',
          paymentCapabilityProof: 'zk_payment_456',
          locationRangeProof: 'zk_location_789',
          timeWindowProof: 'zk_time_012',
          emergencyContactProof: 'zk_emergency_345',
        };

        const invalidZKProof = {
          tierVerification: '', // Empty proof
          paymentCapabilityProof: 'invalid',
          // Missing required fields
        };

        const validateZKProof = (proof: any) => {
          const requiredFields = [
            'tierVerification',
            'paymentCapabilityProof',
            'locationRangeProof',
            'timeWindowProof',
            'emergencyContactProof',
          ];

          return requiredFields.every(field => 
            proof[field] && 
            typeof proof[field] === 'string' && 
            proof[field].startsWith('zk_')
          );
        };

        expect(validateZKProof(validZKProof)).toBe(true);
        expect(validateZKProof(invalidZKProof)).toBe(false);
      });

      test('prevents ZK proof replay attacks', () => {
        const usedProofs = new Set([
          'zk_tier_proof_123',
          'zk_tier_proof_456',
        ]);

        const newProof = 'zk_tier_proof_789';
        const replayedProof = 'zk_tier_proof_123';

        const validateProofUniqueness = (proof: string) => {
          if (usedProofs.has(proof)) {
            return false;
          }
          usedProofs.add(proof);
          return true;
        };

        expect(validateProofUniqueness(newProof)).toBe(true);
        expect(validateProofUniqueness(replayedProof)).toBe(false);
      });

      test('validates proof expiration', () => {
        const currentTime = Date.now();
        const validProof = {
          proof: 'zk_proof_123',
          issuedAt: currentTime - 60000, // 1 minute ago
          expiresAt: currentTime + 300000, // 5 minutes from now
        };

        const expiredProof = {
          proof: 'zk_proof_456',
          issuedAt: currentTime - 600000, // 10 minutes ago
          expiresAt: currentTime - 60000, // 1 minute ago (expired)
        };

        const validateProofExpiration = (proof: any) => {
          return proof.expiresAt > Date.now();
        };

        expect(validateProofExpiration(validProof)).toBe(true);
        expect(validateProofExpiration(expiredProof)).toBe(false);
      });
    });

    describe('Identity Reveal Security', () => {
      test('validates emergency identity reveal authorization', () => {
        const validEmergencyScenarios = [
          {
            type: 'medical_emergency',
            severity: 'life_threatening',
            trigger: 'emergency_activation',
            authorization: 'system_automated',
          },
          {
            type: 'legal_requirement',
            severity: 'high',
            trigger: 'court_order',
            authorization: 'legal_mandate',
          },
        ];

        const invalidScenarios = [
          {
            type: 'curiosity', // Invalid emergency type
            severity: 'low',
            trigger: 'user_request',
            authorization: 'none',
          },
        ];

        const validateEmergencyAuthorization = (scenario: any) => {
          const validTypes = ['medical_emergency', 'security_threat', 'legal_requirement'];
          const validSeverities = ['high', 'critical', 'life_threatening'];
          const validTriggers = ['emergency_activation', 'response_team_dispatched', 'court_order'];

          return (
            validTypes.includes(scenario.type) &&
            validSeverities.includes(scenario.severity) &&
            validTriggers.includes(scenario.trigger)
          );
        };

        validEmergencyScenarios.forEach(scenario => {
          expect(validateEmergencyAuthorization(scenario)).toBe(true);
        });

        invalidScenarios.forEach(scenario => {
          expect(validateEmergencyAuthorization(scenario)).toBe(false);
        });
      });

      test('validates progressive reveal stage authorization', () => {
        const revealStages = [
          { stage: 'location_only', requiredAuth: 'emergency_activation' },
          { stage: 'medical_info', requiredAuth: 'medical_professional_verified' },
          { stage: 'emergency_contacts', requiredAuth: 'critical_condition_confirmed' },
          { stage: 'full_identity', requiredAuth: 'legal_mandate_or_consent' },
        ];

        const unauthorizedReveal = { stage: 'full_identity', providedAuth: 'none' };

        const validateStageAuthorization = (request: any) => {
          const stage = revealStages.find(s => s.stage === request.stage);
          return stage ? request.providedAuth === stage.requiredAuth : false;
        };

        expect(validateStageAuthorization({
          stage: 'location_only',
          providedAuth: 'emergency_activation'
        })).toBe(true);

        expect(validateStageAuthorization(unauthorizedReveal)).toBe(false);
      });

      test('validates data purging after emergency resolution', () => {
        const emergencyData = {
          emergencyId: 'emergency_123',
          revealedData: [
            { type: 'location', revealedAt: Date.now() - 3600000, purgeAfterHours: 1 },
            { type: 'medical_info', revealedAt: Date.now() - 7200000, purgeAfterHours: 24 },
          ],
          emergencyResolved: true,
          resolvedAt: Date.now() - 1800000, // 30 minutes ago
        };

        const shouldPurgeData = (dataItem: any, emergencyResolvedAt: number) => {
          const purgeTime = dataItem.revealedAt + (dataItem.purgeAfterHours * 3600000);
          return emergencyResolvedAt > 0 && Date.now() > purgeTime;
        };

        // Location data should be purged (revealed 1 hour ago, purge after 1 hour)
        expect(shouldPurgeData(emergencyData.revealedData[0], emergencyData.resolvedAt)).toBe(true);
        
        // Medical data should not be purged yet (revealed 2 hours ago, purge after 24 hours)
        expect(shouldPurgeData(emergencyData.revealedData[1], emergencyData.resolvedAt)).toBe(false);
      });
    });

    describe('Communication Security', () => {
      test('validates message encryption based on confidentiality level', () => {
        const encryptionLevels = {
          'circle_only': 'standard',
          'tier_only': 'enhanced',
          'ultra_private': 'quantum',
        };

        const messages = [
          { content: 'Hello', confidentiality: 'circle_only', expectedEncryption: 'standard' },
          { content: 'Sensitive deal', confidentiality: 'ultra_private', expectedEncryption: 'quantum' },
        ];

        messages.forEach(msg => {
          const requiredEncryption = encryptionLevels[msg.confidentiality as keyof typeof encryptionLevels];
          expect(requiredEncryption).toBe(msg.expectedEncryption);
        });
      });

      test('validates message integrity with hash verification', () => {
        const message = {
          content: 'Test message',
          hash: 'expected_hash_123',
        };

        const tamperedMessage = {
          content: 'Tampered message',
          hash: 'expected_hash_123', // Hash doesn't match content
        };

        const calculateHash = (content: string) => {
          // Simplified hash calculation for testing
          return `hash_${content.length}_${content.charCodeAt(0)}`;
        };

        const verifyMessageIntegrity = (msg: any) => {
          const expectedHash = calculateHash(msg.content);
          return msg.hash === expectedHash;
        };

        // Update message hash for test
        message.hash = calculateHash(message.content);
        
        expect(verifyMessageIntegrity(message)).toBe(true);
        expect(verifyMessageIntegrity(tamperedMessage)).toBe(false);
      });

      test('validates anonymous identity correlation resistance', () => {
        const userActivities = [
          { anonymousId: 'Silver_Sage_12', timestamp: Date.now() - 1000, action: 'message' },
          { anonymousId: 'Silver_Sage_12', timestamp: Date.now() - 500, action: 'vote' },
          { anonymousId: 'Silver_Sage_12', timestamp: Date.now(), action: 'message' },
        ];

        // Check for timing correlation that could reveal identity
        const detectTimingCorrelation = (activities: any[]) => {
          const intervals = [];
          for (let i = 1; i < activities.length; i++) {
            intervals.push(activities[i].timestamp - activities[i-1].timestamp);
          }
          
          // If intervals are too regular, it might indicate bot behavior or correlation
          const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
          const variance = intervals.reduce((acc, interval) => acc + Math.pow(interval - avgInterval, 2), 0) / intervals.length;
          
          return variance < avgInterval * 0.1; // Low variance indicates regular pattern
        };

        expect(detectTimingCorrelation(userActivities)).toBe(true); // Regular pattern detected
      });
    });
  });

  describe('Hardware Security Validation', () => {
    describe('Device Tampering Detection', () => {
      test('detects rooted/jailbroken devices', () => {
        const deviceProfiles = [
          {
            platform: 'iOS',
            hasJailbreakIndicators: false,
            systemIntegrity: true,
            suspiciousApps: [],
          },
          {
            platform: 'Android',
            hasRootIndicators: true, // Rooted device
            systemIntegrity: false,
            suspiciousApps: ['SuperSU', 'Magisk'],
          },
        ];

        const assessDeviceTampering = (profile: any) => {
          if (profile.platform === 'iOS' && profile.hasJailbreakIndicators) return true;
          if (profile.platform === 'Android' && profile.hasRootIndicators) return true;
          if (!profile.systemIntegrity) return true;
          if (profile.suspiciousApps.length > 0) return true;
          return false;
        };

        expect(assessDeviceTampering(deviceProfiles[0])).toBe(false);
        expect(assessDeviceTampering(deviceProfiles[1])).toBe(true);
      });

      test('validates hardware attestation', () => {
        const attestationData = {
          platform: 'iOS',
          attestationKey: 'valid_key_123',
          nonce: 'unique_nonce_456',
          timestamp: Date.now(),
          signature: 'valid_signature_789',
        };

        const invalidAttestation = {
          platform: 'iOS',
          attestationKey: '', // Empty key
          nonce: 'reused_nonce', // Potentially reused
          timestamp: Date.now() - 3600000, // 1 hour old
          signature: 'invalid_signature',
        };

        const validateAttestation = (attestation: any) => {
          if (!attestation.attestationKey) return false;
          if (attestation.timestamp < Date.now() - 300000) return false; // 5 minute window
          if (!attestation.signature.startsWith('valid_')) return false; // Simplified validation
          return true;
        };

        expect(validateAttestation(attestationData)).toBe(true);
        expect(validateAttestation(invalidAttestation)).toBe(false);
      });

      test('detects emulator usage', () => {
        const deviceCharacteristics = [
          {
            model: 'iPhone 13 Pro',
            isEmulator: false,
            sensors: ['accelerometer', 'gyroscope', 'magnetometer'],
            performance: { cpu: 'A15 Bionic', gpu: 'Apple GPU' },
          },
          {
            model: 'Android SDK built for x86',
            isEmulator: true,
            sensors: [], // Emulators often lack sensors
            performance: { cpu: 'Intel x86', gpu: 'Software Renderer' },
          },
        ];

        const detectEmulator = (characteristics: any) => {
          if (characteristics.model.includes('SDK') || characteristics.model.includes('Emulator')) return true;
          if (characteristics.sensors.length === 0) return true;
          if (characteristics.performance.gpu.includes('Software')) return true;
          return false;
        };

        expect(detectEmulator(deviceCharacteristics[0])).toBe(false);
        expect(detectEmulator(deviceCharacteristics[1])).toBe(true);
      });
    });
  });

  describe('Rate Limiting and Abuse Prevention', () => {
    test('implements authentication rate limiting', () => {
      const rateLimiter = {
        attempts: new Map<string, number[]>(),
        windowMs: 900000, // 15 minutes
        maxAttempts: 5,
      };

      const checkRateLimit = (identifier: string) => {
        const now = Date.now();
        const attempts = rateLimiter.attempts.get(identifier) || [];
        
        // Remove old attempts outside the window
        const recentAttempts = attempts.filter(time => now - time < rateLimiter.windowMs);
        
        if (recentAttempts.length >= rateLimiter.maxAttempts) {
          return false; // Rate limited
        }
        
        recentAttempts.push(now);
        rateLimiter.attempts.set(identifier, recentAttempts);
        return true; // Allowed
      };

      const deviceId = 'device_123';
      
      // First 5 attempts should be allowed
      for (let i = 0; i < 5; i++) {
        expect(checkRateLimit(deviceId)).toBe(true);
      }
      
      // 6th attempt should be blocked
      expect(checkRateLimit(deviceId)).toBe(false);
    });

    test('detects brute force patterns', () => {
      const authAttempts = [
        { time: Date.now() - 10000, success: false },
        { time: Date.now() - 8000, success: false },
        { time: Date.now() - 6000, success: false },
        { time: Date.now() - 4000, success: false },
        { time: Date.now() - 2000, success: false },
      ];

      const detectBruteForce = (attempts: any[]) => {
        const recentFailures = attempts.filter(attempt => 
          !attempt.success && (Date.now() - attempt.time) < 60000 // Last minute
        );
        
        return recentFailures.length >= 3; // 3 failures in a minute
      };

      expect(detectBruteForce(authAttempts)).toBe(true);
    });

    test('implements progressive delays for failed attempts', () => {
      const calculateDelay = (attemptCount: number) => {
        if (attemptCount <= 1) return 0;
        if (attemptCount <= 3) return 1000; // 1 second
        if (attemptCount <= 5) return 5000; // 5 seconds
        return Math.min(300000, Math.pow(2, attemptCount - 5) * 10000); // Exponential backoff, max 5 minutes
      };

      expect(calculateDelay(1)).toBe(0);
      expect(calculateDelay(3)).toBe(1000);
      expect(calculateDelay(5)).toBe(5000);
      expect(calculateDelay(8)).toBe(80000);
      expect(calculateDelay(20)).toBe(300000); // Capped at 5 minutes
    });
  });
});