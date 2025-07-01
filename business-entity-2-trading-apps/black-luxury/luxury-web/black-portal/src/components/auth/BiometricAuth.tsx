'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDeviceFingerprint } from '@/hooks/useDeviceFingerprint';

interface BiometricAuthProps {
  onSuccess: (biometricData: BiometricResult) => void;
  onFallback: () => void;
  tier: 'onyx' | 'obsidian' | 'void';
}

interface BiometricResult {
  type: 'fingerprint' | 'face' | 'voice' | 'fallback';
  confidence: number;
  deviceTrust: number;
  timestamp: Date;
}

export function BiometricAuth({ onSuccess, onFallback, tier }: BiometricAuthProps) {
  const [authStep, setAuthStep] = useState<'scanning' | 'processing' | 'verifying' | 'success' | 'failed'>('scanning');
  const [biometricType, setBiometricType] = useState<'fingerprint' | 'face' | 'voice' | null>(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [availableMethods, setAvailableMethods] = useState<string[]>([]);
  const { deviceId, fingerprint, isSecureDevice } = useDeviceFingerprint();

  // Tier-specific configurations
  const tierConfig = {
    void: {
      color: '#FFD700',
      scanDuration: 3000,
      minConfidence: 0.95,
      title: 'VOID VERIFICATION',
      subtitle: 'Ultimate biometric authentication required'
    },
    obsidian: {
      color: '#E5E4E2',
      scanDuration: 2500,
      minConfidence: 0.90,
      title: 'OBSIDIAN VERIFICATION',
      subtitle: 'Advanced biometric scanning in progress'
    },
    onyx: {
      color: '#C0C0C0',
      scanDuration: 2000,
      minConfidence: 0.85,
      title: 'ONYX VERIFICATION',
      subtitle: 'Biometric authentication required'
    }
  };

  const config = tierConfig[tier];

  // Check available biometric methods
  useEffect(() => {
    checkBiometricCapabilities();
  }, []);

  const checkBiometricCapabilities = async () => {
    const methods: string[] = [];

    // Check for Web Authentication API (WebAuthn)
    if ('credentials' in navigator && 'create' in navigator.credentials) {
      try {
        const available = await (navigator.credentials as any).get({
          publicKey: {
            challenge: new Uint8Array(32),
            timeout: 1000,
            userVerification: 'required'
          }
        }).catch(() => null);
        
        if (available) methods.push('fingerprint');
      } catch (e) {
        // WebAuthn not available or no authenticators
      }
    }

    // Check for camera (face recognition simulation)
    try {
      await navigator.mediaDevices.getUserMedia({ video: true });
      methods.push('face');
    } catch (e) {
      // Camera not available
    }

    // Check for microphone (voice recognition simulation)
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      methods.push('voice');
    } catch (e) {
      // Microphone not available
    }

    setAvailableMethods(methods);
    
    // Auto-select best available method
    if (methods.includes('fingerprint')) {
      setBiometricType('fingerprint');
    } else if (methods.includes('face')) {
      setBiometricType('face');
    } else if (methods.includes('voice')) {
      setBiometricType('voice');
    }
  };

  const startBiometricScan = async () => {
    if (!biometricType) return;

    setAuthStep('processing');
    setScanProgress(0);

    // Simulate biometric scanning progress
    const interval = setInterval(() => {
      setScanProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setAuthStep('verifying');
          setTimeout(() => performBiometricAuth(), 1000);
          return 100;
        }
        return prev + (100 / (config.scanDuration / 50));
      });
    }, 50);
  };

  const performBiometricAuth = async () => {
    try {
      let confidence = 0;
      let authSuccess = false;

      switch (biometricType) {
        case 'fingerprint':
          authSuccess = await performFingerprintAuth();
          confidence = authSuccess ? 0.95 + Math.random() * 0.05 : 0.3 + Math.random() * 0.4;
          break;
        case 'face':
          authSuccess = await performFaceAuth();
          confidence = authSuccess ? 0.88 + Math.random() * 0.07 : 0.2 + Math.random() * 0.4;
          break;
        case 'voice':
          authSuccess = await performVoiceAuth();
          confidence = authSuccess ? 0.85 + Math.random() * 0.1 : 0.25 + Math.random() * 0.4;
          break;
        default:
          authSuccess = false;
      }

      // Device trust factor
      const deviceTrust = isSecureDevice ? 0.9 + Math.random() * 0.1 : 0.5 + Math.random() * 0.3;

      if (authSuccess && confidence >= config.minConfidence && deviceTrust >= 0.7) {
        setAuthStep('success');
        setTimeout(() => {
          onSuccess({
            type: biometricType!,
            confidence,
            deviceTrust,
            timestamp: new Date()
          });
        }, 1500);
      } else {
        setAuthStep('failed');
        setTimeout(() => {
          onFallback();
        }, 3000);
      }
    } catch (error) {
      console.error('Biometric authentication error:', error);
      setAuthStep('failed');
      setTimeout(() => onFallback(), 3000);
    }
  };

  const performFingerprintAuth = async (): Promise<boolean> => {
    // In a real implementation, this would use WebAuthn
    // For demo, simulate success 80% of the time
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(Math.random() > 0.2);
      }, 1000);
    });
  };

  const performFaceAuth = async (): Promise<boolean> => {
    // In a real implementation, this would use camera + ML models
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(Math.random() > 0.25);
      }, 1500);
    });
  };

  const performVoiceAuth = async (): Promise<boolean> => {
    // In a real implementation, this would use microphone + voice ML
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(Math.random() > 0.3);
      }, 2000);
    });
  };

  const getBiometricIcon = () => {
    switch (biometricType) {
      case 'fingerprint':
        return (
          <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
              d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4" />
          </svg>
        );
      case 'face':
        return (
          <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        );
      case 'voice':
        return (
          <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        );
      default:
        return null;
    }
  };

  const getStatusMessage = () => {
    switch (authStep) {
      case 'scanning':
        return 'Position yourself for scanning';
      case 'processing':
        return `Analyzing ${biometricType} data...`;
      case 'verifying':
        return 'Verifying identity...';
      case 'success':
        return 'Authentication successful';
      case 'failed':
        return 'Authentication failed';
      default:
        return '';
    }
  };

  if (availableMethods.length === 0) {
    return (
      <motion.div
        className="min-h-screen flex items-center justify-center bg-void-black px-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="text-center">
          <h2 className="text-2xl font-luxury-serif text-void-gold mb-4">
            Biometric Authentication Unavailable
          </h2>
          <p className="text-gray-400 mb-8">
            Your device does not support the required biometric features.
          </p>
          <button
            onClick={onFallback}
            className="btn-void px-8 py-3"
          >
            Use Alternative Method
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="min-h-screen flex items-center justify-center bg-void-black px-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute inset-0 opacity-20"
          style={{
            background: `radial-gradient(circle at 50% 50%, ${config.color}20, transparent 70%)`
          }}
          animate={{
            scale: authStep === 'processing' ? [1, 1.2, 1] : 1,
            opacity: authStep === 'processing' ? [0.2, 0.4, 0.2] : 0.2
          }}
          transition={{ duration: 2, repeat: authStep === 'processing' ? Infinity : 0 }}
        />
      </div>

      <div className="relative z-10 w-full max-w-md text-center">
        
        {/* Header */}
        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          <h1 className="text-3xl md:text-4xl font-luxury-serif mb-4 tracking-wider"
              style={{ color: config.color }}>
            {config.title}
          </h1>
          <p className="text-gray-400 font-luxury-sans tracking-wide">
            {config.subtitle}
          </p>
        </motion.div>

        {/* Biometric Scanner */}
        <motion.div
          className="relative w-48 h-48 mx-auto mb-8"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.3 }}
        >
          {/* Outer scanning ring */}
          <motion.div
            className="absolute inset-0 border-2 rounded-full"
            style={{ borderColor: `${config.color}40` }}
            animate={authStep === 'processing' ? { rotate: 360 } : {}}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Inner progress ring */}
          <motion.div
            className="absolute inset-4 border-2 rounded-full"
            style={{ 
              borderColor: config.color,
              background: `conic-gradient(${config.color} ${scanProgress * 3.6}deg, transparent 0deg)`
            }}
          />
          
          {/* Center biometric icon */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            style={{ color: config.color }}
            animate={authStep === 'processing' ? { scale: [1, 1.1, 1] } : {}}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            {getBiometricIcon()}
          </motion.div>

          {/* Success/Failure overlay */}
          <AnimatePresence>
            {authStep === 'success' && (
              <motion.div
                className="absolute inset-0 flex items-center justify-center bg-green-500/20 rounded-full"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
              >
                <svg className="w-12 h-12 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </motion.div>
            )}
            
            {authStep === 'failed' && (
              <motion.div
                className="absolute inset-0 flex items-center justify-center bg-red-500/20 rounded-full"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
              >
                <svg className="w-12 h-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Progress indicator */}
        {authStep === 'processing' && (
          <motion.div
            className="w-full bg-gray-800 rounded-full h-2 mb-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <motion.div
              className="h-2 rounded-full"
              style={{ backgroundColor: config.color }}
              initial={{ width: '0%' }}
              animate={{ width: `${scanProgress}%` }}
              transition={{ duration: 0.1 }}
            />
          </motion.div>
        )}

        {/* Status message */}
        <motion.p
          className="text-gray-300 font-luxury-sans mb-8"
          key={authStep}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {getStatusMessage()}
        </motion.p>

        {/* Action buttons */}
        <div className="space-y-4">
          {authStep === 'scanning' && biometricType && (
            <motion.button
              onClick={startBiometricScan}
              className="w-full btn-void py-4 text-lg font-luxury-sans tracking-widest"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              START {biometricType.toUpperCase()} SCAN
            </motion.button>
          )}

          {/* Fallback option */}
          <motion.button
            onClick={onFallback}
            className="w-full bg-transparent border border-gray-600 text-gray-400 py-3 rounded-lg font-luxury-sans tracking-wide hover:border-gray-500 transition-colors"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Use Alternative Authentication
          </motion.button>
        </div>

        {/* Device security indicator */}
        {deviceId && (
          <motion.div
            className="mt-8 text-xs text-gray-600 font-luxury-mono"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
          >
            Device ID: {deviceId.slice(-8)}
            <br />
            Security Level: {isSecureDevice ? 'HIGH' : 'MEDIUM'}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}