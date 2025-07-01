'use client';

import { useEffect, useRef, useState } from 'react';
import { BlackTier } from '@/types/portal';

interface LuxuryEffectsConfig {
  enableSounds: boolean;
  enableHaptics: boolean;
  enableParticles: boolean;
  intensity: number;
}

interface SoundEffect {
  name: string;
  url?: string;
  frequency?: number;
  duration?: number;
  volume?: number;
}

export function useLuxuryEffects(tier: BlackTier, config: LuxuryEffectsConfig = {
  enableSounds: true,
  enableHaptics: true,
  enableParticles: true,
  intensity: 1.0
}) {
  const audioContextRef = useRef<AudioContext | null>(null);
  const soundCacheRef = useRef<Map<string, AudioBuffer>>(new Map());
  const [isInitialized, setIsInitialized] = useState(false);

  // Tier-specific sound profiles
  const getSoundProfile = () => {
    switch (tier) {
      case 'void':
        return {
          ambient: { frequency: 40, volume: 0.1 }, // Deep void hum
          interaction: { frequency: 880, volume: 0.3 }, // Golden tone
          success: { frequency: 1320, volume: 0.4 }, // Triumphant chime
          error: { frequency: 220, volume: 0.2 }, // Low warning
          transition: { frequency: 660, volume: 0.3 } // Smooth transition
        };
      case 'obsidian':
        return {
          ambient: { frequency: 60, volume: 0.08 }, // Crystal resonance
          interaction: { frequency: 784, volume: 0.25 }, // Platinum tone
          success: { frequency: 1175, volume: 0.35 }, // Clear chime
          error: { frequency: 247, volume: 0.18 }, // Controlled warning
          transition: { frequency: 587, volume: 0.25 } // Crystalline shift
        };
      case 'onyx':
        return {
          ambient: { frequency: 80, volume: 0.06 }, // Silver flow
          interaction: { frequency: 698, volume: 0.2 }, // Silver tone
          success: { frequency: 1047, volume: 0.3 }, // Gentle chime
          error: { frequency: 294, volume: 0.15 }, // Soft warning
          transition: { frequency: 523, volume: 0.2 } // Flowing transition
        };
      default:
        return getSoundProfile();
    }
  };

  const soundProfile = getSoundProfile();

  // Initialize audio context
  useEffect(() => {
    if (config.enableSounds && !audioContextRef.current) {
      try {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        setIsInitialized(true);
      } catch (error) {
        console.warn('Audio context not available:', error);
      }
    }

    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [config.enableSounds]);

  // Generate synthetic sound
  const generateSyntheticSound = async (effect: SoundEffect): Promise<AudioBuffer | null> => {
    if (!audioContextRef.current) return null;

    const context = audioContextRef.current;
    const duration = effect.duration || 0.3;
    const sampleRate = context.sampleRate;
    const frameCount = sampleRate * duration;
    
    const buffer = context.createBuffer(2, frameCount, sampleRate);
    
    for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
      const channelData = buffer.getChannelData(channel);
      
      for (let i = 0; i < frameCount; i++) {
        const t = i / sampleRate;
        const frequency = effect.frequency || 440;
        const volume = (effect.volume || 0.3) * config.intensity;
        
        // Create luxury waveform (combination of sine and harmonics)
        let sample = Math.sin(2 * Math.PI * frequency * t) * volume;
        
        // Add harmonics for richness
        sample += Math.sin(2 * Math.PI * frequency * 2 * t) * volume * 0.3;
        sample += Math.sin(2 * Math.PI * frequency * 3 * t) * volume * 0.1;
        
        // Apply envelope (attack, decay, sustain, release)
        const attackTime = 0.05;
        const decayTime = 0.1;
        const sustainLevel = 0.7;
        const releaseTime = 0.15;
        
        let envelope = 1;
        if (t < attackTime) {
          envelope = t / attackTime;
        } else if (t < attackTime + decayTime) {
          envelope = 1 - (1 - sustainLevel) * (t - attackTime) / decayTime;
        } else if (t > duration - releaseTime) {
          envelope = sustainLevel * (duration - t) / releaseTime;
        } else {
          envelope = sustainLevel;
        }
        
        channelData[i] = sample * envelope;
      }
    }
    
    return buffer;
  };

  // Play sound effect
  const playSound = async (effectName: keyof typeof soundProfile) => {
    if (!config.enableSounds || !audioContextRef.current || !isInitialized) return;

    try {
      const context = audioContextRef.current;
      const soundConfig = soundProfile[effectName];
      
      let buffer = soundCacheRef.current.get(effectName);
      
      if (!buffer) {
        buffer = await generateSyntheticSound({
          name: effectName,
          ...soundConfig
        });
        
        if (buffer) {
          soundCacheRef.current.set(effectName, buffer);
        }
      }
      
      if (buffer) {
        const source = context.createBufferSource();
        const gainNode = context.createGain();
        
        source.buffer = buffer;
        source.connect(gainNode);
        gainNode.connect(context.destination);
        
        // Apply tier-specific filters
        if (tier === 'void') {
          // Add reverb for void tier
          const convolver = context.createConvolver();
          const reverbBuffer = await createReverbBuffer(context, 2, 0.3);
          convolver.buffer = reverbBuffer;
          
          source.connect(convolver);
          convolver.connect(gainNode);
        }
        
        gainNode.gain.setValueAtTime(soundConfig.volume * config.intensity, context.currentTime);
        source.start();
      }
    } catch (error) {
      console.warn('Error playing sound:', error);
    }
  };

  // Create reverb buffer for luxury effects
  const createReverbBuffer = async (context: AudioContext, duration: number, decay: number): Promise<AudioBuffer> => {
    const sampleRate = context.sampleRate;
    const length = sampleRate * duration;
    const buffer = context.createBuffer(2, length, sampleRate);
    
    for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
      const channelData = buffer.getChannelData(channel);
      for (let i = 0; i < length; i++) {
        const n = length - i;
        channelData[i] = (Math.random() * 2 - 1) * Math.pow(n / length, decay);
      }
    }
    
    return buffer;
  };

  // Haptic feedback
  const triggerHaptic = (intensity: 'light' | 'medium' | 'heavy' = 'medium') => {
    if (!config.enableHaptics) return;

    if ('vibrate' in navigator) {
      const patterns = {
        light: [50],
        medium: [100],
        heavy: [200]
      };
      
      navigator.vibrate(patterns[intensity]);
    }
  };

  // Visual effects
  const createParticleEffect = (element: HTMLElement, type: 'success' | 'error' | 'interaction') => {
    if (!config.enableParticles) return;

    const colors = {
      void: {
        success: '#FFD700',
        error: '#FF6B6B',
        interaction: '#FFF700'
      },
      obsidian: {
        success: '#E5E4E2',
        error: '#FF8A80',
        interaction: '#F5F5F5'
      },
      onyx: {
        success: '#C0C0C0',
        error: '#FFAB91',
        interaction: '#D0D0D0'
      }
    };

    const color = colors[tier][type];
    const particleCount = Math.floor(10 * config.intensity);

    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.style.cssText = `
        position: absolute;
        width: 4px;
        height: 4px;
        background: ${color};
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        left: ${Math.random() * element.offsetWidth}px;
        top: ${Math.random() * element.offsetHeight}px;
        opacity: 1;
        transition: all 1s ease-out;
      `;
      
      element.appendChild(particle);
      
      // Animate particle
      requestAnimationFrame(() => {
        particle.style.transform = `translate(${(Math.random() - 0.5) * 100}px, ${-50 - Math.random() * 50}px)`;
        particle.style.opacity = '0';
        particle.style.transform += ' scale(0)';
      });
      
      // Clean up
      setTimeout(() => {
        if (particle.parentNode) {
          particle.parentNode.removeChild(particle);
        }
      }, 1000);
    }
  };

  // Screen flash effect
  const screenFlash = (color: string, duration: number = 100) => {
    if (!config.enableParticles) return;

    const flash = document.createElement('div');
    flash.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: ${color};
      opacity: 0.1;
      pointer-events: none;
      z-index: 9998;
      transition: opacity ${duration}ms ease-out;
    `;
    
    document.body.appendChild(flash);
    
    requestAnimationFrame(() => {
      flash.style.opacity = '0';
    });
    
    setTimeout(() => {
      if (flash.parentNode) {
        flash.parentNode.removeChild(flash);
      }
    }, duration);
  };

  // Combined effect triggers
  const luxuryInteraction = (element?: HTMLElement) => {
    playSound('interaction');
    triggerHaptic('light');
    if (element) {
      createParticleEffect(element, 'interaction');
    }
  };

  const luxurySuccess = (element?: HTMLElement) => {
    playSound('success');
    triggerHaptic('medium');
    if (element) {
      createParticleEffect(element, 'success');
    }
    screenFlash(soundProfile.success.frequency > 1000 ? '#4ADE80' : '#10B981', 150);
  };

  const luxuryError = (element?: HTMLElement) => {
    playSound('error');
    triggerHaptic('heavy');
    if (element) {
      createParticleEffect(element, 'error');
    }
    screenFlash('#EF4444', 200);
  };

  const luxuryTransition = () => {
    playSound('transition');
    triggerHaptic('light');
  };

  // Ambient background sound
  const startAmbientSound = () => {
    if (!config.enableSounds || !audioContextRef.current) return;

    // Create a continuous ambient tone
    const context = audioContextRef.current;
    const oscillator = context.createOscillator();
    const gainNode = context.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(context.destination);
    
    oscillator.frequency.setValueAtTime(soundProfile.ambient.frequency, context.currentTime);
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0, context.currentTime);
    gainNode.gain.linearRampToValueAtTime(
      soundProfile.ambient.volume * config.intensity, 
      context.currentTime + 2
    );
    
    oscillator.start();
    
    return () => {
      gainNode.gain.linearRampToValueAtTime(0, context.currentTime + 1);
      setTimeout(() => oscillator.stop(), 1000);
    };
  };

  return {
    // Individual effects
    playSound,
    triggerHaptic,
    createParticleEffect,
    screenFlash,
    
    // Combined luxury effects
    luxuryInteraction,
    luxurySuccess,
    luxuryError,
    luxuryTransition,
    
    // Ambient effects
    startAmbientSound,
    
    // State
    isInitialized,
    
    // Configuration
    soundProfile,
    
    // Tier-specific utilities
    getTierColor: () => {
      const colors = {
        void: '#FFD700',
        obsidian: '#E5E4E2',
        onyx: '#C0C0C0'
      };
      return colors[tier];
    }
  };
}