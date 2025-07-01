'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BlackTier, BlackUser } from '@/types/portal';

interface TierAssignmentProps {
  invitationCode: string;
  biometricData: any;
  onComplete: (user: BlackUser) => void;
}

export function TierAssignment({ invitationCode, biometricData, onComplete }: TierAssignmentProps) {
  const [phase, setPhase] = useState<'analyzing' | 'revealing' | 'ceremony' | 'complete'>('analyzing');
  const [assignedTier, setAssignedTier] = useState<BlackTier | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [showTierDetails, setShowTierDetails] = useState(false);

  // Tier determination logic
  useEffect(() => {
    setTimeout(() => {
      determineTier();
    }, 2000);
  }, []);

  const determineTier = () => {
    let tier: BlackTier;
    
    // Determine tier based on invitation code and other factors
    if (invitationCode.startsWith('VOID')) {
      tier = BlackTier.VOID;
    } else if (invitationCode.startsWith('OBSIDIAN')) {
      tier = BlackTier.OBSIDIAN;
    } else if (invitationCode.startsWith('ONYX')) {
      tier = BlackTier.ONYX;
    } else {
      // Demo/test codes get random premium tier
      const tiers = [BlackTier.ONYX, BlackTier.OBSIDIAN, BlackTier.VOID];
      tier = tiers[Math.floor(Math.random() * tiers.length)];
    }

    setAssignedTier(tier);
    
    // Start analysis animation
    const interval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setPhase('revealing'), 1000);
          return 100;
        }
        return prev + 2;
      });
    }, 100);
  };

  const getTierConfig = (tier: BlackTier) => {
    switch (tier) {
      case BlackTier.VOID:
        return {
          name: 'VOID',
          subtitle: 'The Ultimate Tier',
          color: '#FFD700',
          description: 'Reserved for those who transcend conventional wealth. You control reality itself.',
          benefits: [
            'Unlimited portfolio value',
            'Dedicated quantum AI butler',
            'Reality distortion trading algorithms',
            'Access to parallel market dimensions',
            'Personal time manipulation features',
            'Exclusive cosmic trading pairs'
          ],
          memberCount: '17 Members Globally',
          minWealth: '₹8,000+ Cr Portfolio'
        };
      case BlackTier.OBSIDIAN:
        return {
          name: 'OBSIDIAN',
          subtitle: 'Crystalline Perfection',
          color: '#E5E4E2',
          description: 'For the architectural minds who build empires and reshape industries.',
          benefits: [
            '₹1,000+ Cr portfolio management',
            'Diamond-tier AI analytics',
            'Crystal-clear market predictions',
            'Exclusive enterprise trading tools',
            'Private banking integration',
            'Global market access'
          ],
          memberCount: '147 Members Globally',
          minWealth: '₹1,000+ Cr Portfolio'
        };
      case BlackTier.ONYX:
        return {
          name: 'ONYX',
          subtitle: 'Flowing Excellence',
          color: '#C0C0C0',
          description: 'The entry point to true luxury trading. Where success flows like liquid silver.',
          benefits: [
            '₹100+ Cr portfolio access',
            'Premium AI assistance',
            'Advanced analytics suite',
            'Priority customer support',
            'Exclusive market insights',
            'White-glove onboarding'
          ],
          memberCount: '2,847 Members Globally',
          minWealth: '₹100+ Cr Portfolio'
        };
      default:
        return getTierConfig(BlackTier.ONYX);
    }
  };

  const proceedToCeremony = () => {
    setPhase('ceremony');
    setTimeout(() => {
      setPhase('complete');
      setTimeout(() => {
        const user: BlackUser = {
          userId: `user_${Date.now()}`,
          tier: assignedTier!,
          portfolioValue: generatePortfolioValue(assignedTier!),
          dedicatedButler: generateButlerName(assignedTier!),
          joinedAt: new Date(),
          lastActive: new Date(),
          deviceIds: [biometricData?.deviceId || 'unknown'],
          securityLevel: biometricData?.confidence > 0.9 ? 'MAXIMUM' : 'HIGH',
          privileges: generatePrivileges(assignedTier!),
          personalizations: {
            preferredTheme: assignedTier!,
            language: 'en',
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            notifications: {
              trading: true,
              market: true,
              personal: true
            }
          }
        };
        onComplete(user);
      }, 3000);
    }, 4000);
  };

  const generatePortfolioValue = (tier: BlackTier): number => {
    switch (tier) {
      case BlackTier.VOID:
        return 8000 + Math.random() * 20000; // 8,000-28,000 Cr
      case BlackTier.OBSIDIAN:
        return 1000 + Math.random() * 5000; // 1,000-6,000 Cr
      case BlackTier.ONYX:
        return 100 + Math.random() * 500; // 100-600 Cr
      default:
        return 100;
    }
  };

  const generateButlerName = (tier: BlackTier): string => {
    const voidNames = ['Quantum-7', 'Nexus Prime', 'Infinity Core', 'Cosmos AI'];
    const obsidianNames = ['Diamond Mind', 'Crystal Logic', 'Platinum AI', 'Sapphire Core'];
    const onyxNames = ['Silver Stream', 'Onyx Assistant', 'Pearl AI', 'Mercury Core'];

    switch (tier) {
      case BlackTier.VOID:
        return voidNames[Math.floor(Math.random() * voidNames.length)];
      case BlackTier.OBSIDIAN:
        return obsidianNames[Math.floor(Math.random() * obsidianNames.length)];
      case BlackTier.ONYX:
        return onyxNames[Math.floor(Math.random() * onyxNames.length)];
      default:
        return 'AI Butler';
    }
  };

  const generatePrivileges = (tier: BlackTier): string[] => {
    const base = ['trading', 'analytics', 'support'];
    const premium = [...base, 'private_banking', 'concierge'];
    const ultimate = [...premium, 'quantum_trading', 'reality_distortion', 'time_manipulation'];

    switch (tier) {
      case BlackTier.VOID:
        return ultimate;
      case BlackTier.OBSIDIAN:
        return premium;
      case BlackTier.ONYX:
        return base;
      default:
        return base;
    }
  };

  if (!assignedTier) return null;

  const tierConfig = getTierConfig(assignedTier);

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
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(circle at 50% 50%, ${tierConfig.color}20, transparent 70%)`
          }}
          animate={{
            scale: phase === 'ceremony' ? [1, 1.5, 1] : 1,
            opacity: phase === 'ceremony' ? [0.3, 0.6, 0.3] : 0.3
          }}
          transition={{ duration: 2, repeat: phase === 'ceremony' ? Infinity : 0 }}
        />
      </div>

      <div className="relative z-10 w-full max-w-2xl text-center">

        {phase === 'analyzing' && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
          >
            <h1 className="text-4xl font-luxury-serif text-void-gold mb-8 tracking-wider">
              ANALYZING CREDENTIALS
            </h1>
            
            <div className="w-32 h-32 mx-auto mb-8 relative">
              <motion.div
                className="absolute inset-0 border-2 border-void-gold/30 rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              />
              <motion.div
                className="absolute inset-2 border border-void-gold/60 rounded-full"
                animate={{ rotate: -360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-2xl font-luxury-mono text-void-gold">
                  {Math.floor(analysisProgress)}%
                </div>
              </div>
            </div>

            <div className="space-y-3 text-gray-400 font-luxury-sans">
              <p>Verifying invitation authenticity...</p>
              <p>Analyzing biometric patterns...</p>
              <p>Assessing wealth indicators...</p>
              <p>Determining tier eligibility...</p>
            </div>
          </motion.div>
        )}

        {phase === 'revealing' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 1.5 }}
          >
            <motion.h1
              className="text-6xl font-luxury-serif mb-4 tracking-widest"
              style={{ color: tierConfig.color }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 1 }}
            >
              {tierConfig.name}
            </motion.h1>
            
            <motion.p
              className="text-xl text-gray-300 font-luxury-sans mb-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 1 }}
            >
              {tierConfig.subtitle}
            </motion.p>

            <motion.button
              onClick={() => setShowTierDetails(true)}
              className="btn-void px-8 py-4 text-lg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              EXPLORE YOUR TIER
            </motion.button>
          </motion.div>
        )}

        {/* Tier Details Modal */}
        <AnimatePresence>
          {showTierDetails && (
            <motion.div
              className="fixed inset-0 bg-void-black/90 flex items-center justify-center z-50 p-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div
                className="bg-gray-900 border border-gray-700 rounded-lg p-8 w-full max-w-2xl max-h-screen overflow-y-auto"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-luxury-serif mb-2" style={{ color: tierConfig.color }}>
                    {tierConfig.name} TIER
                  </h2>
                  <p className="text-gray-400 font-luxury-sans">
                    {tierConfig.description}
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-8 mb-8">
                  <div>
                    <h3 className="text-lg font-luxury-sans text-gray-300 mb-4">Exclusive Benefits</h3>
                    <ul className="space-y-2 text-sm text-gray-400">
                      {tierConfig.benefits.map((benefit, index) => (
                        <li key={index} className="flex items-center">
                          <span className="w-2 h-2 rounded-full mr-3" style={{ backgroundColor: tierConfig.color }} />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-lg font-luxury-sans text-gray-300 mb-4">Tier Details</h3>
                    <div className="space-y-3 text-sm text-gray-400">
                      <div>
                        <span className="text-gray-500">Members:</span> {tierConfig.memberCount}
                      </div>
                      <div>
                        <span className="text-gray-500">Minimum Wealth:</span> {tierConfig.minWealth}
                      </div>
                      <div>
                        <span className="text-gray-500">Access Level:</span> ULTRA-PREMIUM
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => setShowTierDetails(false)}
                    className="px-6 py-2 border border-gray-600 text-gray-400 rounded-lg hover:border-gray-500 transition-colors"
                  >
                    BACK
                  </button>
                  <button
                    onClick={proceedToCeremony}
                    className="btn-void px-8 py-2"
                  >
                    ACCEPT TIER
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {phase === 'ceremony' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center"
          >
            <motion.div
              className="w-40 h-40 mx-auto mb-8 relative"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 2, ease: "easeOut" }}
            >
              {/* Tier Symbol */}
              <motion.div
                className="absolute inset-0 border-4 rounded-full"
                style={{ borderColor: tierConfig.color }}
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              />
              
              <motion.div
                className="absolute inset-4 flex items-center justify-center text-4xl font-luxury-serif"
                style={{ color: tierConfig.color }}
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {assignedTier === BlackTier.VOID ? '∞' : 
                 assignedTier === BlackTier.OBSIDIAN ? '◊' : '○'}
              </motion.div>
            </motion.div>

            <motion.h1
              className="text-5xl font-luxury-serif mb-6 tracking-widest"
              style={{ color: tierConfig.color }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1 }}
            >
              WELCOME TO {tierConfig.name}
            </motion.h1>

            <motion.p
              className="text-xl text-gray-300 font-luxury-sans"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5 }}
            >
              Your luxury trading experience begins now
            </motion.p>
          </motion.div>
        )}

        {phase === 'complete' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <motion.div
              className="w-20 h-20 mx-auto mb-8 text-green-400"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </motion.div>

            <h1 className="text-4xl font-luxury-serif text-void-gold mb-4">
              INITIALIZATION COMPLETE
            </h1>
            
            <p className="text-gray-400 font-luxury-sans">
              Preparing your personalized experience...
            </p>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}