'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { MysteryLanding } from '@/components/landing/MysteryLanding';
import { InvitationPrompt } from '@/components/auth/InvitationPrompt';
import { BiometricAuth } from '@/components/auth/BiometricAuth';
import { TierAssignment } from '@/components/onboarding/TierAssignment';
import { WelcomeCeremony } from '@/components/onboarding/WelcomeCeremony';
import { PortalDashboard } from '@/components/portal/PortalDashboard';
import { LuxuryParticles } from '@/components/3d/LuxuryParticles';
import { RealityDistortion } from '@/components/3d/RealityDistortion';
import { useBlackPortal } from '@/hooks/useBlackPortal';
import { useDeviceFingerprint } from '@/hooks/useDeviceFingerprint';
import { useLuxuryEffects } from '@/hooks/useLuxuryEffects';
import { BlackPortalStage } from '@/types/portal';

export default function BlackPortalHome() {
  const { stage, user, invitation, setStage } = useBlackPortal();
  const { deviceId, isSecureDevice } = useDeviceFingerprint();
  const { playLuxurySound, showLuxuryEffect } = useLuxuryEffects();
  
  const [showReality, setShowReality] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const portalRef = useRef<HTMLDivElement>(null);

  // Track mouse for parallax effects
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Initialize luxury effects
  useEffect(() => {
    showLuxuryEffect('portal-entry');
    playLuxurySound('ambient-void', { loop: true, volume: 0.1 });
  }, []);

  // Handle invitation code entry
  const handleInvitationSubmit = async (code: string) => {
    try {
      showLuxuryEffect('invitation-processing');
      
      // Validate invitation (would connect to backend)
      const response = await fetch('/api/invitations/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          code, 
          deviceId,
          fingerprint: await generateDeviceFingerprint() 
        })
      });
      
      if (response.ok) {
        const invitationData = await response.json();
        playLuxurySound('invitation-accepted');
        showLuxuryEffect('gold-shower');
        setStage(BlackPortalStage.BIOMETRIC_AUTH);
      } else {
        playLuxurySound('invitation-denied');
        showLuxuryEffect('reality-glitch');
      }
    } catch (error) {
      console.error('Invitation validation error:', error);
      showLuxuryEffect('system-error');
    }
  };

  // Handle biometric authentication
  const handleBiometricAuth = async (biometricData: any) => {
    try {
      showLuxuryEffect('biometric-processing');
      
      const response = await fetch('/api/auth/biometric', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          biometricData,
          deviceId,
          invitationCode: invitation?.code
        })
      });
      
      if (response.ok) {
        const authData = await response.json();
        playLuxurySound('biometric-success');
        showLuxuryEffect('tier-reveal');
        setStage(BlackPortalStage.TIER_ASSIGNMENT);
      } else {
        playLuxurySound('biometric-failure');
        showLuxuryEffect('security-alert');
      }
    } catch (error) {
      console.error('Biometric authentication error:', error);
    }
  };

  // Handle tier assignment completion
  const handleTierAssignment = async (tierData: any) => {
    try {
      showLuxuryEffect('tier-assignment');
      playLuxurySound('tier-confirmation');
      setStage(BlackPortalStage.WELCOME_CEREMONY);
      
      // Auto-proceed to portal after ceremony
      setTimeout(() => {
        setStage(BlackPortalStage.PORTAL_DASHBOARD);
        showLuxuryEffect('portal-activation');
        playLuxurySound('portal-entry');
      }, 8000);
    } catch (error) {
      console.error('Tier assignment error:', error);
    }
  };

  // Generate device fingerprint
  const generateDeviceFingerprint = async () => {
    // Comprehensive device fingerprinting for security
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillText('GridWorks Black Portal Device Fingerprint', 2, 2);
    }
    
    return {
      screen: `${screen.width}x${screen.height}x${screen.colorDepth}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      platform: navigator.platform,
      language: navigator.language,
      userAgent: navigator.userAgent,
      canvas: canvas.toDataURL(),
      webgl: getWebGLFingerprint(),
      audio: await getAudioFingerprint(),
      timestamp: Date.now()
    };
  };

  const getWebGLFingerprint = () => {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return 'not-supported';
    
    return {
      vendor: gl.getParameter(gl.VENDOR),
      renderer: gl.getParameter(gl.RENDERER),
      version: gl.getParameter(gl.VERSION),
      extensions: gl.getSupportedExtensions()?.slice(0, 5) // Limit for performance
    };
  };

  const getAudioFingerprint = async () => {
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
      
      const freqData = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(freqData);
      
      oscillator.stop();
      await audioContext.close();
      
      return Array.from(freqData.slice(0, 10)).join(',');
    } catch {
      return 'not-available';
    }
  };

  return (
    <div 
      ref={portalRef}
      className=\"relative min-h-screen bg-void-black overflow-hidden parallax-container\"
      style={{
        background: `radial-gradient(circle at ${50 + mousePosition.x * 10}% ${50 + mousePosition.y * 10}%, rgba(255,215,0,0.03) 0%, transparent 50%)`
      }}
    >
      {/* 3D Background Effects */}
      <div className=\"fixed inset-0 z-0\">
        <Canvas
          camera={{ position: [0, 0, 5], fov: 75 }}
          style={{ background: 'transparent' }}
        >
          <LuxuryParticles 
            count={100} 
            tier={user?.tier || 'mystery'}
            mousePosition={mousePosition}
          />
          {showReality && (
            <RealityDistortion 
              intensity={0.1}
              mousePosition={mousePosition}
            />
          )}
        </Canvas>
      </div>

      {/* Luxury Grid Pattern */}
      <div className=\"fixed inset-0 luxury-grid opacity-20 z-1\" />

      {/* Main Portal Content */}
      <div className=\"relative z-10\">
        <AnimatePresence mode=\"wait\">
          {stage === BlackPortalStage.MYSTERY_LANDING && (
            <motion.div
              key=\"mystery\"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 2, ease: \"easeInOut\" }}
            >
              <MysteryLanding 
                onInvitationPrompt={() => setStage(BlackPortalStage.INVITATION_PROMPT)}
                mousePosition={mousePosition}
              />
            </motion.div>
          )}

          {stage === BlackPortalStage.INVITATION_PROMPT && (
            <motion.div
              key=\"invitation\"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 1, ease: \"easeOut\" }}
            >
              <InvitationPrompt 
                onSubmit={handleInvitationSubmit}
                onBack={() => setStage(BlackPortalStage.MYSTERY_LANDING)}
              />
            </motion.div>
          )}

          {stage === BlackPortalStage.BIOMETRIC_AUTH && (
            <motion.div
              key=\"biometric\"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.1 }}
              transition={{ duration: 1.2, ease: \"easeInOut\" }}
            >
              <BiometricAuth 
                onSuccess={handleBiometricAuth}
                deviceId={deviceId}
                isSecureDevice={isSecureDevice}
              />
            </motion.div>
          )}

          {stage === BlackPortalStage.TIER_ASSIGNMENT && (
            <motion.div
              key=\"tier\"
              initial={{ opacity: 0, rotateY: -90 }}
              animate={{ opacity: 1, rotateY: 0 }}
              exit={{ opacity: 0, rotateY: 90 }}
              transition={{ duration: 1.5, ease: \"easeInOut\" }}
            >
              <TierAssignment 
                invitation={invitation}
                onComplete={handleTierAssignment}
              />
            </motion.div>
          )}

          {stage === BlackPortalStage.WELCOME_CEREMONY && (
            <motion.div
              key=\"welcome\"
              initial={{ opacity: 0, z: -1000 }}
              animate={{ opacity: 1, z: 0 }}
              exit={{ opacity: 0, z: 1000 }}
              transition={{ duration: 2, ease: \"easeInOut\" }}
            >
              <WelcomeCeremony 
                user={user}
                onComplete={() => setStage(BlackPortalStage.PORTAL_DASHBOARD)}
              />
            </motion.div>
          )}

          {stage === BlackPortalStage.PORTAL_DASHBOARD && (
            <motion.div
              key=\"dashboard\"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1.5, ease: \"easeOut\" }}
            >
              <PortalDashboard 
                user={user}
                mousePosition={mousePosition}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Reality Distortion Toggle (Hidden Easter Egg) */}
      <button
        className=\"fixed bottom-4 right-4 w-4 h-4 bg-transparent border-none opacity-0 hover:opacity-10 transition-opacity duration-1000 z-50\"
        onClick={() => setShowReality(!showReality)}
        aria-label=\"Toggle Reality\"
      />

      {/* Security Overlay for Non-Secure Devices */}
      {!isSecureDevice && stage !== BlackPortalStage.MYSTERY_LANDING && (
        <div className=\"fixed inset-0 bg-void-black/90 backdrop-blur-luxury z-90 flex items-center justify-center\">
          <div className=\"text-center max-w-md mx-auto p-8\">
            <div className=\"text-6xl mb-4\">🔒</div>
            <h2 className=\"text-2xl font-luxury-serif mb-4 text-void-gold\">
              Secure Device Required
            </h2>
            <p className=\"text-luxury-body text-gray-300 mb-6\">
              GridWorks Black Portal requires a verified secure device. 
              Please use a registered device or contact your butler for assistance.
            </p>
            <button
              onClick={() => setStage(BlackPortalStage.MYSTERY_LANDING)}
              className=\"btn-void px-6 py-3\"
            >
              Return to Landing
            </button>
          </div>
        </div>
      )}
    </div>
  );
}