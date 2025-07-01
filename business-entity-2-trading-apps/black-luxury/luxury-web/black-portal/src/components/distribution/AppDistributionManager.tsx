'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Download, Smartphone, Lock, AlertTriangle, CheckCircle, Clock, Zap } from 'lucide-react';
import { appDistribution } from '../../services/AppDistribution';
import { 
  AppDistributionRequest, 
  DeviceRegistration, 
  AppPackage, 
  SecurityAssessment,
  AppDistributionEvent 
} from '../../types/app-distribution';

interface AppDistributionManagerProps {
  userId: string;
  tier: 'onyx' | 'obsidian' | 'void';
  deviceId: string;
}

export const AppDistributionManager: React.FC<AppDistributionManagerProps> = ({
  userId,
  tier,
  deviceId
}) => {
  const [currentStep, setCurrentStep] = useState<'device-register' | 'security-assessment' | 'app-request' | 'approval' | 'download'>('device-register');
  const [deviceRegistration, setDeviceRegistration] = useState<DeviceRegistration | null>(null);
  const [securityAssessment, setSecurityAssessment] = useState<SecurityAssessment | null>(null);
  const [distributionRequest, setDistributionRequest] = useState<AppDistributionRequest | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const tierConfig = {
    onyx: {
      name: 'Onyx Silver',
      color: '#C0C0C0',
      description: 'Premium mobile experience with silver-tier luxury',
      features: ['Premium Analytics', 'Luxury Concierge', 'Emergency Services', 'Butler AI Assistant']
    },
    obsidian: {
      name: 'Obsidian Crystal',
      color: '#E5E4E2',
      description: 'Diamond-tier mobile platform with crystalline perfection',
      features: ['Diamond Analytics', 'Empire Management', 'Crystal Concierge', 'Mystical AI Butler']
    },
    void: {
      name: 'Void Quantum',
      color: '#FFD700',
      description: 'Quantum-tier mobile app with reality-bending capabilities',
      features: ['Quantum Trading', 'Reality Distortion', 'Interdimensional Access', 'Quantum AI Butler']
    }
  };

  const handleDeviceRegistration = async () => {
    setLoading(true);
    setError(null);

    try {
      const hardwareLock = await appDistribution.createHardwareLock(deviceId, userId, tier);
      
      const registration: DeviceRegistration = {
        registrationId: `reg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        userId,
        deviceId,
        deviceName: `${navigator.platform} Device`,
        platform: navigator.platform.includes('iPhone') || navigator.platform.includes('iPad') ? 'ios' : 'android',
        osVersion: navigator.userAgent,
        hardwareLock,
        approvalStatus: 'approved',
        lastVerified: new Date(),
        trustScore: 0.95,
        riskFactors: []
      };

      setDeviceRegistration(registration);
      setCurrentStep('security-assessment');
    } catch (err) {
      setError('Failed to register device. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSecurityAssessment = async () => {
    if (!deviceRegistration) return;

    setLoading(true);
    setError(null);

    try {
      const assessment = await appDistribution.performSecurityAssessment(deviceRegistration, tier);
      setSecurityAssessment(assessment);
      setCurrentStep('app-request');
    } catch (err) {
      setError('Security assessment failed. Please check your device security settings.');
    } finally {
      setLoading(false);
    }
  };

  const handleAppRequest = async () => {
    if (!deviceRegistration || !securityAssessment) return;

    setLoading(true);
    setError(null);

    try {
      const appPackage: AppPackage = {
        packageId: `black-portal-${tier}`,
        version: '2.0.0',
        tier,
        platform: deviceRegistration.platform,
        packageType: 'native',
        size: tier === 'void' ? 2048 : tier === 'obsidian' ? 1536 : 1024,
        checksum: 'sha256:abc123...',
        signature: 'signature123...',
        encryptionKey: 'key123...',
        distributionMethod: tier === 'void' ? 'enterprise_store' : 'private_testflight',
        buildDate: new Date(),
        minimumOS: deviceRegistration.platform === 'ios' ? '15.0' : '11.0',
        requiredFeatures: ['biometric_auth', 'secure_enclave']
      };

      const request: AppDistributionRequest = {
        requestId: '',
        userId,
        tier,
        deviceRegistration,
        requestedPackage: appPackage,
        securityAssessment,
        emergencyContact: '+91-9876543210',
        businessJustification: `${tierConfig[tier].name} tier access for billionaire trading platform`,
        requestedAt: new Date(),
        approvalWorkflow: {
          workflowId: '',
          currentStage: 'security_review',
          stages: [],
          autoApprovalEligible: true
        }
      };

      const requestId = await appDistribution.requestAppDistribution(request);
      setDistributionRequest({ ...request, requestId });
      setCurrentStep('approval');
    } catch (err) {
      setError('Failed to submit app distribution request.');
    } finally {
      setLoading(false);
    }
  };

  const renderDeviceRegistration = () => (
    <div className="space-y-6">
      <div className="text-center">
        <Smartphone className="w-16 h-16 mx-auto mb-4" style={{ color: tierConfig[tier].color }} />
        <h3 className="text-2xl font-bold mb-2">Device Registration</h3>
        <p className="text-gray-400">Secure your device for {tierConfig[tier].name} tier access</p>
      </div>

      <div className="bg-gray-800/50 rounded-xl p-6">
        <h4 className="text-lg font-semibold mb-4">Device Security Requirements</h4>
        <div className="space-y-3">
          {[
            'Hardware security module enabled',
            'Biometric authentication configured',
            'Screen lock protection active',
            'Device encryption enabled',
            'Secure boot verification'
          ].map((requirement, index) => (
            <div key={index} className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span className="text-sm text-gray-300">{requirement}</span>
            </div>
          ))}
        </div>
      </div>

      <motion.button
        onClick={handleDeviceRegistration}
        disabled={loading}
        className={`w-full py-4 rounded-xl font-semibold transition-all ${
          loading 
            ? 'bg-gray-600 cursor-not-allowed' 
            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
        }`}
        whileHover={!loading ? { scale: 1.02 } : {}}
        whileTap={!loading ? { scale: 0.98 } : {}}
      >
        {loading ? 'Registering Device...' : 'Register Device'}
      </motion.button>
    </div>
  );

  const renderSecurityAssessment = () => (
    <div className="space-y-6">
      <div className="text-center">
        <Shield className="w-16 h-16 mx-auto mb-4" style={{ color: tierConfig[tier].color }} />
        <h3 className="text-2xl font-bold mb-2">Security Assessment</h3>
        <p className="text-gray-400">Comprehensive security evaluation for {tierConfig[tier].name} tier</p>
      </div>

      {securityAssessment && (
        <div className="bg-gray-800/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold">Security Score</h4>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${securityAssessment.riskLevel === 'LOW' ? 'bg-green-400' : securityAssessment.riskLevel === 'MEDIUM' ? 'bg-yellow-400' : 'bg-red-400'}`} />
              <span className="text-sm font-medium">{securityAssessment.riskLevel} RISK</span>
            </div>
          </div>
          
          <div className="mb-4">
            <div className="flex justify-between mb-2">
              <span className="text-sm text-gray-400">Overall Score</span>
              <span className="text-sm font-medium">{Math.round(securityAssessment.overallScore * 100)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-green-400 to-blue-400 h-2 rounded-full"
                style={{ width: `${securityAssessment.overallScore * 100}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">✓</div>
              <div className="text-sm text-gray-400">Device Security</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">✓</div>
              <div className="text-sm text-gray-400">Network Security</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">✓</div>
              <div className="text-sm text-gray-400">Biometric Security</div>
            </div>
          </div>
        </div>
      )}

      <motion.button
        onClick={handleSecurityAssessment}
        disabled={loading}
        className={`w-full py-4 rounded-xl font-semibold transition-all ${
          loading 
            ? 'bg-gray-600 cursor-not-allowed' 
            : 'bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700'
        }`}
        whileHover={!loading ? { scale: 1.02 } : {}}
        whileTap={!loading ? { scale: 0.98 } : {}}
      >
        {loading ? 'Assessing Security...' : 'Start Security Assessment'}
      </motion.button>
    </div>
  );

  const renderAppRequest = () => (
    <div className="space-y-6">
      <div className="text-center">
        <Download className="w-16 h-16 mx-auto mb-4" style={{ color: tierConfig[tier].color }} />
        <h3 className="text-2xl font-bold mb-2">App Distribution Request</h3>
        <p className="text-gray-400">Request {tierConfig[tier].name} tier mobile application</p>
      </div>

      <div className="bg-gray-800/50 rounded-xl p-6">
        <h4 className="text-lg font-semibold mb-4">{tierConfig[tier].name} Features</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {tierConfig[tier].features.map((feature, index) => (
            <div key={index} className="flex items-center space-x-3">
              <Zap className="w-4 h-4" style={{ color: tierConfig[tier].color }} />
              <span className="text-sm text-gray-300">{feature}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-800/50 rounded-xl p-6">
        <h4 className="text-lg font-semibold mb-4">Distribution Details</h4>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Platform:</span>
            <span className="text-white">{deviceRegistration?.platform === 'ios' ? 'iOS' : 'Android'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Distribution Method:</span>
            <span className="text-white">{tier === 'void' ? 'Enterprise Store' : 'Private TestFlight'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Security Level:</span>
            <span className="text-white">{tier === 'void' ? 'Quantum' : tier === 'obsidian' ? 'Enhanced' : 'Standard'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Hardware Lock:</span>
            <span className="text-white">Required</span>
          </div>
        </div>
      </div>

      <motion.button
        onClick={handleAppRequest}
        disabled={loading}
        className={`w-full py-4 rounded-xl font-semibold transition-all ${
          loading 
            ? 'bg-gray-600 cursor-not-allowed' 
            : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
        }`}
        whileHover={!loading ? { scale: 1.02 } : {}}
        whileTap={!loading ? { scale: 0.98 } : {}}
      >
        {loading ? 'Submitting Request...' : 'Request App Distribution'}
      </motion.button>
    </div>
  );

  const renderApproval = () => (
    <div className="space-y-6">
      <div className="text-center">
        <Clock className="w-16 h-16 mx-auto mb-4" style={{ color: tierConfig[tier].color }} />
        <h3 className="text-2xl font-bold mb-2">Approval Process</h3>
        <p className="text-gray-400">Your {tierConfig[tier].name} app request is being processed</p>
      </div>

      <div className="bg-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold">Request Status</h4>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse" />
            <span className="text-sm font-medium text-green-400">AUTO-APPROVED</span>
          </div>
        </div>

        <div className="space-y-4">
          {[
            { stage: 'Security Review', status: 'completed', time: '< 1 minute' },
            { stage: 'Compliance Check', status: 'completed', time: '< 2 minutes' },
            ...(tier === 'void' ? [{ stage: 'Executive Approval', status: 'completed', time: '< 3 minutes' }] : []),
            { stage: 'Package Generation', status: 'in_progress', time: '< 5 minutes' }
          ].map((stage, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {stage.status === 'completed' ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <Clock className="w-5 h-5 text-yellow-400" />
                )}
                <span className="text-sm">{stage.stage}</span>
              </div>
              <span className="text-xs text-gray-400">{stage.time}</span>
            </div>
          ))}
        </div>
      </div>

      <motion.button
        onClick={() => setCurrentStep('download')}
        className="w-full py-4 rounded-xl font-semibold bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 transition-all"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        Continue to Download
      </motion.button>
    </div>
  );

  const renderDownload = () => (
    <div className="space-y-6">
      <div className="text-center">
        <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-400" />
        <h3 className="text-2xl font-bold mb-2">Ready for Installation</h3>
        <p className="text-gray-400">Your {tierConfig[tier].name} app is ready for secure installation</p>
      </div>

      <div className="bg-gray-800/50 rounded-xl p-6">
        <h4 className="text-lg font-semibold mb-4">Installation Package</h4>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Package ID:</span>
            <span className="text-white font-mono">black-portal-{tier}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Version:</span>
            <span className="text-white">2.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Size:</span>
            <span className="text-white">{tier === 'void' ? '2.0' : tier === 'obsidian' ? '1.5' : '1.0'} GB</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Hardware Lock:</span>
            <span className="text-white">✓ Secured</span>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-xl p-6 border border-blue-500/30">
        <div className="flex items-start space-x-3">
          <Lock className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
          <div>
            <h5 className="font-semibold text-blue-400 mb-2">Quantum Security Notice</h5>
            <p className="text-sm text-gray-300">
              This application is hardware-locked to your device. Installation requires biometric verification 
              and will create an unbreakable quantum entanglement between your device and the GridWorks Black Portal.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <motion.button
          className="w-full py-4 rounded-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Download & Install {tierConfig[tier].name} App
        </motion.button>
        
        <motion.button
          className="w-full py-3 rounded-xl font-medium border border-gray-600 hover:border-gray-500 transition-all"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Send Installation Link via Email
        </motion.button>
      </div>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          {['device-register', 'security-assessment', 'app-request', 'approval', 'download'].map((step, index) => (
            <div
              key={step}
              className={`flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium transition-all ${
                currentStep === step
                  ? 'bg-blue-600 text-white'
                  : index < ['device-register', 'security-assessment', 'app-request', 'approval', 'download'].indexOf(currentStep)
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-400'
              }`}
            >
              {index + 1}
            </div>
          ))}
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-400 to-purple-400 h-2 rounded-full transition-all duration-500"
            style={{ 
              width: `${((['device-register', 'security-assessment', 'app-request', 'approval', 'download'].indexOf(currentStep) + 1) / 5) * 100}%` 
            }}
          />
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/50 border border-red-500/50 rounded-xl">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <p className="text-sm text-red-200">{error}</p>
          </div>
        </div>
      )}

      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {currentStep === 'device-register' && renderDeviceRegistration()}
          {currentStep === 'security-assessment' && renderSecurityAssessment()}
          {currentStep === 'app-request' && renderAppRequest()}
          {currentStep === 'approval' && renderApproval()}
          {currentStep === 'download' && renderDownload()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};