'use client';

import { useState, useEffect } from 'react';
import { DeviceFingerprint } from '@/types/portal';

export function useDeviceFingerprint() {
  const [deviceId, setDeviceId] = useState<string | null>(null);
  const [fingerprint, setFingerprint] = useState<DeviceFingerprint | null>(null);
  const [isSecureDevice, setIsSecureDevice] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    generateDeviceFingerprint();
  }, []);

  const generateDeviceFingerprint = async () => {
    setIsGenerating(true);
    
    try {
      // Get or create device ID
      let storedDeviceId = localStorage.getItem('black-portal-device-id');
      if (!storedDeviceId) {
        storedDeviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('black-portal-device-id', storedDeviceId);
      }
      setDeviceId(storedDeviceId);

      // Generate comprehensive fingerprint
      const fp = await createFingerprint(storedDeviceId);
      setFingerprint(fp);
      
      // Assess device security
      const isSecure = assessDeviceSecurity(fp);
      setIsSecureDevice(isSecure);
      
      // Store fingerprint for comparison
      const storedFingerprint = localStorage.getItem('black-portal-fingerprint');
      if (storedFingerprint) {
        const previousFp = JSON.parse(storedFingerprint);
        if (fingerprintChanged(previousFp, fp)) {
          console.warn('Device fingerprint changed - potential security issue');
          setIsSecureDevice(false);
        }
      } else {
        localStorage.setItem('black-portal-fingerprint', JSON.stringify(fp));
      }
      
    } catch (error) {
      console.error('Error generating device fingerprint:', error);
      setIsSecureDevice(false);
    } finally {
      setIsGenerating(false);
    }
  };

  const validateDevice = (storedFingerprint: DeviceFingerprint): boolean => {
    if (!fingerprint) return false;
    
    // Check key fingerprint components
    const criticalMatch = (
      fingerprint.platform === storedFingerprint.platform &&
      fingerprint.screenResolution === storedFingerprint.screenResolution &&
      fingerprint.timezone === storedFingerprint.timezone &&
      fingerprint.language === storedFingerprint.language
    );
    
    return criticalMatch;
  };

  return {
    deviceId,
    fingerprint,
    isSecureDevice,
    isGenerating,
    generateDeviceFingerprint,
    validateDevice
  };
}

// Create comprehensive device fingerprint
async function createFingerprint(deviceId: string): Promise<DeviceFingerprint> {
  const fingerprint: Partial<DeviceFingerprint> = {
    deviceId,
    createdAt: new Date(),
    lastSeen: new Date()
  };

  // Basic device info
  fingerprint.platform = navigator.platform;
  fingerprint.browser = getBrowserInfo();
  fingerprint.screenResolution = `${screen.width}x${screen.height}x${screen.colorDepth}`;
  fingerprint.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  fingerprint.language = navigator.language;

  // Canvas fingerprinting
  fingerprint.canvasFingerprint = await getCanvasFingerprint();
  
  // WebGL fingerprinting
  fingerprint.webglFingerprint = getWebGLFingerprint();
  
  // Audio fingerprinting
  fingerprint.audioFingerprint = await getAudioFingerprint();
  
  // Touch support
  fingerprint.touchSupport = 'ontouchstart' in window;
  
  // Cookie support
  fingerprint.cookiesEnabled = navigator.cookieEnabled;
  
  // Do Not Track
  fingerprint.doNotTrack = navigator.doNotTrack === '1';
  
  // Generate unique fingerprint string
  const fpString = [
    fingerprint.platform,
    fingerprint.browser,
    fingerprint.screenResolution,
    fingerprint.timezone,
    fingerprint.language,
    fingerprint.canvasFingerprint,
    JSON.stringify(fingerprint.webglFingerprint),
    fingerprint.audioFingerprint,
    fingerprint.touchSupport,
    fingerprint.cookiesEnabled,
    fingerprint.doNotTrack
  ].join('|');
  
  fingerprint.fingerprint = await hashString(fpString);
  
  return fingerprint as DeviceFingerprint;
}

function getBrowserInfo(): string {
  const ua = navigator.userAgent;
  
  if (ua.includes('Chrome') && !ua.includes('Edg')) return 'Chrome';
  if (ua.includes('Firefox')) return 'Firefox';
  if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Safari';
  if (ua.includes('Edg')) return 'Edge';
  if (ua.includes('Opera')) return 'Opera';
  
  return 'Unknown';
}

async function getCanvasFingerprint(): Promise<string> {
  try {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return 'canvas-not-supported';
    
    // Set canvas size
    canvas.width = 300;
    canvas.height = 150;
    
    // Draw complex pattern for fingerprinting
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    
    ctx.fillStyle = '#069';
    ctx.fillText('GridWorks Black Portal 🖤', 2, 15);
    
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.fillText('Device Fingerprint Security', 4, 45);
    
    // Add gradient
    const gradient = ctx.createLinearGradient(0, 0, 300, 150);
    gradient.addColorStop(0, '#FFD700');
    gradient.addColorStop(1, '#000000');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 50, 300, 100);
    
    // Add geometric shapes
    ctx.fillStyle = '#FFD700';
    ctx.beginPath();
    ctx.arc(50, 75, 20, 0, 2 * Math.PI);
    ctx.fill();
    
    return canvas.toDataURL();
  } catch (error) {
    return 'canvas-error';
  }
}

function getWebGLFingerprint(): any {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    
    if (!gl) return { error: 'webgl-not-supported' };
    
    return {
      vendor: gl.getParameter(gl.VENDOR),
      renderer: gl.getParameter(gl.RENDERER),
      version: gl.getParameter(gl.VERSION),
      shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
      extensions: gl.getSupportedExtensions()?.slice(0, 10) || [] // Limit for performance
    };
  } catch (error) {
    return { error: 'webgl-error' };
  }
}

async function getAudioFingerprint(): Promise<string> {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const analyser = audioContext.createAnalyser();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(analyser);
    analyser.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 1000;
    gainNode.gain.value = 0; // Silent
    
    oscillator.start();
    
    // Analyze frequency data
    const freqData = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(freqData);
    
    oscillator.stop();
    await audioContext.close();
    
    // Return first 20 values as fingerprint
    return Array.from(freqData.slice(0, 20)).join(',');
  } catch (error) {
    return 'audio-not-available';
  }
}

async function hashString(str: string): Promise<string> {
  if ('crypto' in window && 'subtle' in crypto) {
    try {
      const encoder = new TextEncoder();
      const data = encoder.encode(str);
      const hashBuffer = await crypto.subtle.digest('SHA-256', data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (error) {
      console.warn('Web Crypto API not available, using fallback hash');
    }
  }
  
  // Fallback hash for older browsers
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(16);
}

function assessDeviceSecurity(fp: DeviceFingerprint): boolean {
  let securityScore = 0;
  
  // Browser security features
  if (fp.browser === 'Chrome' || fp.browser === 'Firefox' || fp.browser === 'Safari') {
    securityScore += 2;
  }
  
  // HTTPS support (assumed in modern browsers)
  if ('crypto' in window && 'subtle' in crypto) {
    securityScore += 2;
  }
  
  // Local storage support
  if ('localStorage' in window) {
    securityScore += 1;
  }
  
  // WebGL support (indicates modern device)
  if (!fp.webglFingerprint.error) {
    securityScore += 1;
  }
  
  // Touch support (mobile devices are generally more secure)
  if (fp.touchSupport) {
    securityScore += 1;
  }
  
  // Do Not Track respect (indicates privacy-conscious user)
  if (fp.doNotTrack) {
    securityScore += 1;
  }
  
  return securityScore >= 5; // Require at least 5/8 security points
}

function fingerprintChanged(previous: DeviceFingerprint, current: DeviceFingerprint): boolean {
  // Check if critical components have changed
  const criticalComponents = [
    'platform',
    'browser',
    'screenResolution',
    'timezone',
    'canvasFingerprint'
  ];
  
  for (const component of criticalComponents) {
    if (previous[component as keyof DeviceFingerprint] !== current[component as keyof DeviceFingerprint]) {
      return true;
    }
  }
  
  return false;
}