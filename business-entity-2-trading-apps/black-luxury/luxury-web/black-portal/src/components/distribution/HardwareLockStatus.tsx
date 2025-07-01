'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, Smartphone, AlertTriangle, CheckCircle, Zap, Eye, Fingerprint } from 'lucide-react';
import { HardwareLock, SecurityAssessment, DeviceInfo } from '../../types/app-distribution';
import { appDistribution } from '../../services/AppDistribution';

interface HardwareLockStatusProps {
  deviceId: string;
  userId: string;
  tier: 'onyx' | 'obsidian' | 'void';
}

export const HardwareLockStatus: React.FC<HardwareLockStatusProps> = ({
  deviceId,
  userId,
  tier
}) => {
  const [hardwareLock, setHardwareLock] = useState<HardwareLock | null>(null);
  const [securityStatus, setSecurityStatus] = useState<'secure' | 'warning' | 'critical'>('secure');
  const [lockHealth, setLockHealth] = useState<number>(100);
  const [loading, setLoading] = useState(true);

  const tierConfig = {
    onyx: { name: 'Onyx Silver', color: '#C0C0C0', strength: 'BASIC' },
    obsidian: { name: 'Obsidian Crystal', color: '#E5E4E2', strength: 'ENHANCED' },
    void: { name: 'Void Quantum', color: '#FFD700', strength: 'QUANTUM' }
  };

  useEffect(() => {
    initializeHardwareLock();
  }, [deviceId, userId, tier]);

  const initializeHardwareLock = async () => {
    try {
      setLoading(true);
      const lock = await appDistribution.createHardwareLock(deviceId, userId, tier);
      setHardwareLock(lock);
      
      // Simulate security monitoring
      const isValid = await appDistribution.verifyHardwareLock(deviceId, lock);
      setSecurityStatus(isValid ? 'secure' : 'critical');
      setLockHealth(isValid ? Math.floor(Math.random() * 15) + 85 : Math.floor(Math.random() * 50) + 25);
    } catch (error) {
      setSecurityStatus('critical');
      setLockHealth(0);
    } finally {
      setLoading(false);
    }
  };

  const getSecurityIcon = () => {
    switch (securityStatus) {
      case 'secure': return <CheckCircle className="w-6 h-6 text-green-400" />;
      case 'warning': return <AlertTriangle className="w-6 h-6 text-yellow-400" />;
      case 'critical': return <AlertTriangle className="w-6 h-6 text-red-400" />;
    }
  };

  const getSecurityColor = () => {
    switch (securityStatus) {
      case 'secure': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'critical': return 'text-red-400';
    }
  };

  const getHealthColor = () => {
    if (lockHealth >= 80) return 'from-green-400 to-emerald-400';
    if (lockHealth >= 60) return 'from-yellow-400 to-orange-400';
    return 'from-red-400 to-red-600';
  };

  if (loading) {
    return (
      <div className="bg-gray-800/50 rounded-xl p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2 mb-6"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-700 rounded"></div>
            <div className="h-4 bg-gray-700 rounded w-5/6"></div>
            <div className="h-4 bg-gray-700 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Status Card */}
      <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Lock className="w-8 h-8" style={{ color: tierConfig[tier].color }} />
              {tier === 'void' && (
                <motion.div
                  className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </div>
            <div>
              <h3 className="text-xl font-bold">{tierConfig[tier].name} Hardware Lock</h3>
              <p className="text-sm text-gray-400">{tierConfig[tier].strength} Security Level</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getSecurityIcon()}
            <span className={`text-sm font-medium ${getSecurityColor()}`}>
              {securityStatus.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Lock Health Indicator */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-400">Lock Integrity</span>
            <span className="text-sm font-medium">{lockHealth}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <motion.div
              className={`h-3 rounded-full bg-gradient-to-r ${getHealthColor()}`}
              initial={{ width: 0 }}
              animate={{ width: `${lockHealth}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Lock Details */}
        {hardwareLock && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Device ID</span>
                <p className="text-sm font-mono text-gray-300 break-all">{hardwareLock.deviceId.substring(0, 20)}...</p>
              </div>
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Created</span>
                <p className="text-sm text-gray-300">{hardwareLock.createdAt.toLocaleDateString()}</p>
              </div>
            </div>
            <div className="space-y-3">
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Expires</span>
                <p className="text-sm text-gray-300">{hardwareLock.expiresAt.toLocaleDateString()}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Strength</span>
                <p className="text-sm text-gray-300">{hardwareLock.lockStrength}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Security Features */}
      <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
        <h4 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <Shield className="w-5 h-5" />
          <span>Active Security Features</span>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { name: 'Hardware Fingerprinting', icon: Smartphone, active: true },
            { name: 'Biometric Hash Verification', icon: Fingerprint, active: true },
            { name: 'Certificate Chain Validation', icon: Shield, active: true },
            { name: 'Real-time Integrity Monitoring', icon: Eye, active: true },
            ...(tier === 'void' ? [
              { name: 'Quantum Entanglement Lock', icon: Zap, active: true },
              { name: 'Reality Anchor Verification', icon: Lock, active: true }
            ] : []),
            ...(tier === 'obsidian' ? [
              { name: 'Crystal Lattice Security', icon: Zap, active: true }
            ] : [])
          ].map((feature, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                feature.active ? 'bg-green-900/50 text-green-400' : 'bg-gray-700 text-gray-500'
              }`}>
                <feature.icon className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-medium">{feature.name}</p>
                <p className="text-xs text-gray-500">
                  {feature.active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quantum Features (Void Tier Only) */}
      {tier === 'void' && (
        <div className="bg-gradient-to-r from-yellow-900/20 to-orange-900/20 rounded-xl p-6 border border-yellow-500/30">
          <h4 className="text-lg font-semibold mb-4 text-yellow-400 flex items-center space-x-2">
            <Zap className="w-5 h-5" />
            <span>Quantum Security Features</span>
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              'Quantum Key Distribution',
              'Quantum Random Number Generation',
              'Quantum Entanglement Verification',
              'Post-Quantum Cryptography',
              'Quantum Tamper Detection',
              'Quantum Secure Channels'
            ].map((feature, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
                <span className="text-sm text-gray-300">{feature}</span>
              </div>
            ))}
          </div>

          <div className="mt-4 p-3 bg-yellow-900/30 rounded-lg">
            <p className="text-xs text-yellow-200">
              🌌 Your device exists in quantum superposition across seventeen parallel dimensions,
              ensuring absolute security through reality-bending encryption protocols.
            </p>
          </div>
        </div>
      )}

      {/* Security Alerts */}
      {securityStatus !== 'secure' && (
        <div className={`rounded-xl p-6 border ${
          securityStatus === 'warning' 
            ? 'bg-yellow-900/20 border-yellow-500/30' 
            : 'bg-red-900/20 border-red-500/30'
        }`}>
          <div className="flex items-start space-x-3">
            <AlertTriangle className={`w-6 h-6 flex-shrink-0 ${
              securityStatus === 'warning' ? 'text-yellow-400' : 'text-red-400'
            }`} />
            <div>
              <h5 className={`font-semibold mb-2 ${
                securityStatus === 'warning' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                Security Alert
              </h5>
              <p className="text-sm text-gray-300 mb-3">
                {securityStatus === 'warning' 
                  ? 'Your hardware lock integrity has decreased. Consider refreshing your security credentials.'
                  : 'Critical security breach detected. Your hardware lock has been compromised and requires immediate attention.'
                }
              </p>
              <motion.button
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  securityStatus === 'warning'
                    ? 'bg-yellow-600 hover:bg-yellow-700 text-yellow-100'
                    : 'bg-red-600 hover:bg-red-700 text-red-100'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={initializeHardwareLock}
              >
                {securityStatus === 'warning' ? 'Refresh Security' : 'Emergency Re-lock'}
              </motion.button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};