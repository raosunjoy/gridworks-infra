'use client';

import { useState, useEffect } from 'react';
import { BlackPortalStage, BlackUser, BlackInvitation } from '@/types/portal';

interface BlackPortalState {
  stage: BlackPortalStage;
  user: BlackUser | null;
  invitation: BlackInvitation | null;
  deviceId: string | null;
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
}

export function useBlackPortal() {
  const [state, setState] = useState<BlackPortalState>({
    stage: BlackPortalStage.MYSTERY_LANDING,
    user: null,
    invitation: null,
    deviceId: null,
    sessionId: null,
    isLoading: false,
    error: null
  });

  // Initialize portal state
  useEffect(() => {
    // Check for existing session
    const storedSession = localStorage.getItem('black-portal-session');
    if (storedSession) {
      try {
        const sessionData = JSON.parse(storedSession);
        setState(prev => ({
          ...prev,
          ...sessionData,
          // Reset to landing if session is expired
          stage: isSessionValid(sessionData) ? sessionData.stage : BlackPortalStage.MYSTERY_LANDING
        }));
      } catch (error) {
        console.warn('Invalid session data, starting fresh');
        localStorage.removeItem('black-portal-session');
      }
    }

    // Generate device ID if not exists
    const deviceId = localStorage.getItem('black-portal-device-id') || generateDeviceId();
    localStorage.setItem('black-portal-device-id', deviceId);
    setState(prev => ({ ...prev, deviceId }));
  }, []);

  // Save session state
  useEffect(() => {
    if (state.sessionId) {
      const sessionData = {
        stage: state.stage,
        user: state.user,
        invitation: state.invitation,
        sessionId: state.sessionId,
        timestamp: Date.now()
      };
      localStorage.setItem('black-portal-session', JSON.stringify(sessionData));
    }
  }, [state.stage, state.user, state.invitation, state.sessionId]);

  const setStage = (stage: BlackPortalStage) => {
    setState(prev => ({ ...prev, stage }));
  };

  const setUser = (user: BlackUser | null) => {
    setState(prev => ({ ...prev, user }));
  };

  const setInvitation = (invitation: BlackInvitation | null) => {
    setState(prev => ({ ...prev, invitation }));
  };

  const setLoading = (isLoading: boolean) => {
    setState(prev => ({ ...prev, isLoading }));
  };

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }));
  };

  const createSession = () => {
    const sessionId = `black_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setState(prev => ({ ...prev, sessionId }));
    return sessionId;
  };

  const clearSession = () => {
    localStorage.removeItem('black-portal-session');
    setState(prev => ({
      ...prev,
      stage: BlackPortalStage.MYSTERY_LANDING,
      user: null,
      invitation: null,
      sessionId: null,
      error: null
    }));
  };

  const logout = () => {
    clearSession();
    localStorage.removeItem('black-portal-device-id');
    // Could also clear device fingerprint if needed
  };

  return {
    ...state,
    setStage,
    setUser,
    setInvitation,
    setLoading,
    setError,
    createSession,
    clearSession,
    logout
  };
}

// Helper functions
function isSessionValid(sessionData: any): boolean {
  if (!sessionData.timestamp) return false;
  
  // Session expires after 24 hours
  const sessionAge = Date.now() - sessionData.timestamp;
  const maxAge = 24 * 60 * 60 * 1000; // 24 hours
  
  return sessionAge < maxAge;
}

function generateDeviceId(): string {
  // Generate a unique device identifier
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substr(2, 9);
  const browserInfo = [
    navigator.userAgent.length,
    navigator.language,
    screen.width,
    screen.height,
    new Date().getTimezoneOffset()
  ].join('');
  
  const browserHash = hashString(browserInfo).toString(36);
  
  return `dev_${timestamp}_${randomPart}_${browserHash}`;
}

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}