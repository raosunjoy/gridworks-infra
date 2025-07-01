'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BlackUser } from '@/types/portal';

interface WelcomeCeremonyProps {
  user: BlackUser;
  onComplete: () => void;
}

export function WelcomeCeremony({ user, onComplete }: WelcomeCeremonyProps) {
  const [phase, setPhase] = useState<'greeting' | 'butler' | 'features' | 'ready'>('greeting');
  const [currentFeature, setCurrentFeature] = useState(0);

  // Tier-specific configurations
  const getTierConfig = () => {
    switch (user.tier) {
      case 'void':
        return {
          color: '#FFD700',
          gradient: 'from-yellow-500/20 via-yellow-400/10 to-transparent',
          title: 'THE VOID AWAITS',
          subtitle: 'Reality bends to your will',
          features: [
            {
              title: 'Quantum Trading',
              description: 'Trade across parallel market dimensions',
              icon: '⚛️'
            },
            {
              title: 'Reality Distortion',
              description: 'Algorithms that transcend conventional analysis',
              icon: '🌌'
            },
            {
              title: 'Time Manipulation',
              description: 'Execute trades before they happen',
              icon: '⏰'
            },
            {
              title: 'Cosmic Markets',
              description: 'Access to interdimensional trading pairs',
              icon: '🪐'
            }
          ]
        };
      case 'obsidian':
        return {
          color: '#E5E4E2',
          gradient: 'from-gray-300/20 via-gray-200/10 to-transparent',
          title: 'OBSIDIAN EXCELLENCE',
          subtitle: 'Crystalline perfection in every trade',
          features: [
            {
              title: 'Diamond Analytics',
              description: 'Crystal-clear market predictions',
              icon: '💎'
            },
            {
              title: 'Enterprise Tools',
              description: 'Build and manage financial empires',
              icon: '🏛️'
            },
            {
              title: 'Private Banking',
              description: 'Exclusive institutional access',
              icon: '🏦'
            },
            {
              title: 'Global Markets',
              description: 'Worldwide trading opportunities',
              icon: '🌍'
            }
          ]
        };
      case 'onyx':
        return {
          color: '#C0C0C0',
          gradient: 'from-gray-400/20 via-gray-300/10 to-transparent',
          title: 'ONYX ELEGANCE',
          subtitle: 'Where success flows like liquid silver',
          features: [
            {
              title: 'Premium AI',
              description: 'Advanced trading assistance',
              icon: '🤖'
            },
            {
              title: 'Analytics Suite',
              description: 'Professional market analysis',
              icon: '📊'
            },
            {
              title: 'Priority Support',
              description: 'White-glove customer service',
              icon: '👥'
            },
            {
              title: 'Market Insights',
              description: 'Exclusive trading intelligence',
              icon: '🔍'
            }
          ]
        };
      default:
        return getTierConfig();
    }
  };

  const tierConfig = getTierConfig();

  // Auto-progress through phases
  useEffect(() => {
    const timer = setTimeout(() => {
      if (phase === 'greeting') {
        setPhase('butler');
      } else if (phase === 'butler') {
        setPhase('features');
      }
    }, 4000);

    return () => clearTimeout(timer);
  }, [phase]);

  // Cycle through features
  useEffect(() => {
    if (phase === 'features') {
      const interval = setInterval(() => {
        setCurrentFeature(prev => {
          if (prev >= tierConfig.features.length - 1) {
            setTimeout(() => setPhase('ready'), 1000);
            return prev;
          }
          return prev + 1;
        });
      }, 2500);

      return () => clearInterval(interval);
    }
  }, [phase, tierConfig.features.length]);

  const formatPortfolioValue = (value: number): string => {
    if (value >= 1000) {
      return `₹${(value / 1000).toFixed(1)}K Cr`;
    }
    return `₹${value.toFixed(1)} Cr`;
  };

  return (
    <motion.div
      className="min-h-screen flex items-center justify-center bg-void-black px-8 overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Background Effects */}
      <div className="absolute inset-0">
        <motion.div
          className={`absolute inset-0 bg-gradient-radial ${tierConfig.gradient}`}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        />
        
        {/* Floating particles */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 rounded-full opacity-40"
            style={{ backgroundColor: tierConfig.color }}
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              y: [null, -50, null],
              opacity: [0.4, 0.8, 0.4],
              scale: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: Math.random() * 2
            }}
          />
        ))}
      </div>

      <div className="relative z-10 w-full max-w-4xl text-center">

        {/* Greeting Phase */}
        <AnimatePresence mode="wait">
          {phase === 'greeting' && (
            <motion.div
              key="greeting"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 1 }}
            >
              <motion.div
                className="w-32 h-32 mx-auto mb-8 relative"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <div
                  className="absolute inset-0 border-4 rounded-full opacity-60"
                  style={{ borderColor: tierConfig.color }}
                />
                <div
                  className="absolute inset-4 border-2 rounded-full opacity-80"
                  style={{ borderColor: tierConfig.color }}
                />
                <div
                  className="absolute inset-8 rounded-full opacity-40"
                  style={{ backgroundColor: tierConfig.color }}
                />
              </motion.div>

              <motion.h1
                className="text-5xl md:text-7xl font-luxury-serif mb-6 tracking-widest"
                style={{ color: tierConfig.color }}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5, duration: 1 }}
              >
                {tierConfig.title}
              </motion.h1>

              <motion.p
                className="text-2xl text-gray-300 font-luxury-sans mb-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1, duration: 1 }}
              >
                {tierConfig.subtitle}
              </motion.p>

              <motion.div
                className="text-lg text-gray-400 font-luxury-mono"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5, duration: 1 }}
              >
                Portfolio: {formatPortfolioValue(user.portfolioValue)}
              </motion.div>
            </motion.div>
          )}

          {/* Butler Introduction */}
          {phase === 'butler' && (
            <motion.div
              key="butler"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 1 }}
            >
              <motion.div
                className="w-40 h-40 mx-auto mb-8 relative"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 100, delay: 0.3 }}
              >
                {/* Butler Avatar */}
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 border-4" 
                     style={{ borderColor: tierConfig.color }}>
                  <div className="absolute inset-4 rounded-full bg-gradient-to-br from-gray-600 to-gray-800 flex items-center justify-center">
                    <motion.div
                      className="text-4xl"
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      🤖
                    </motion.div>
                  </div>
                </div>
                
                {/* Pulsing ring */}
                <motion.div
                  className="absolute -inset-2 border-2 rounded-full opacity-50"
                  style={{ borderColor: tierConfig.color }}
                  animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </motion.div>

              <motion.h2
                className="text-4xl font-luxury-serif mb-4"
                style={{ color: tierConfig.color }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                MEET YOUR BUTLER
              </motion.h2>

              <motion.h3
                className="text-3xl font-luxury-sans text-white mb-6"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
              >
                {user.dedicatedButler}
              </motion.h3>

              <motion.p
                className="text-xl text-gray-300 font-luxury-sans max-w-2xl mx-auto"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.1 }}
              >
                Your dedicated AI butler will anticipate your needs, execute complex strategies, 
                and provide insights that transcend conventional analysis.
              </motion.p>
            </motion.div>
          )}

          {/* Features Showcase */}
          {phase === 'features' && (
            <motion.div
              key="features"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8 }}
            >
              <motion.h2
                className="text-4xl font-luxury-serif mb-12"
                style={{ color: tierConfig.color }}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
              >
                EXCLUSIVE FEATURES
              </motion.h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                {tierConfig.features.map((feature, index) => (
                  <motion.div
                    key={index}
                    className={`relative p-6 rounded-lg border transition-all duration-500 ${
                      index === currentFeature 
                        ? 'border-white/50 bg-white/5 shadow-lg' 
                        : 'border-gray-700 bg-gray-900/30'
                    }`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ 
                      opacity: index <= currentFeature ? 1 : 0.3,
                      y: 0,
                      scale: index === currentFeature ? 1.05 : 1
                    }}
                    transition={{ delay: index * 0.1 }}
                  >
                    {/* Feature highlight effect */}
                    {index === currentFeature && (
                      <motion.div
                        className="absolute inset-0 border-2 rounded-lg"
                        style={{ borderColor: tierConfig.color }}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3 }}
                      />
                    )}

                    <div className="relative z-10">
                      <div className="text-4xl mb-4">{feature.icon}</div>
                      <h3 className="text-xl font-luxury-sans text-white mb-3">
                        {feature.title}
                      </h3>
                      <p className="text-gray-400 font-luxury-sans">
                        {feature.description}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Progress indicator */}
              <motion.div
                className="flex justify-center mt-12 space-x-2"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
              >
                {tierConfig.features.map((_, index) => (
                  <motion.div
                    key={index}
                    className="w-3 h-3 rounded-full"
                    style={{ 
                      backgroundColor: index <= currentFeature ? tierConfig.color : '#374151'
                    }}
                    animate={{ scale: index === currentFeature ? 1.2 : 1 }}
                  />
                ))}
              </motion.div>
            </motion.div>
          )}

          {/* Ready Phase */}
          {phase === 'ready' && (
            <motion.div
              key="ready"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 1 }}
            >
              <motion.div
                className="w-32 h-32 mx-auto mb-8"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, delay: 0.3 }}
              >
                <div className="w-full h-full rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center">
                  <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </motion.div>

              <motion.h2
                className="text-5xl font-luxury-serif mb-6"
                style={{ color: tierConfig.color }}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                WELCOME TO THE FUTURE
              </motion.h2>

              <motion.p
                className="text-xl text-gray-300 font-luxury-sans mb-12 max-w-2xl mx-auto"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
              >
                Your Black Portal experience has been personalized and is ready. 
                Prepare to redefine what trading means.
              </motion.p>

              <motion.button
                onClick={onComplete}
                className="btn-void px-12 py-4 text-xl font-luxury-sans tracking-widest"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.1 }}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: `0 0 30px ${tierConfig.color}40`
                }}
                whileTap={{ scale: 0.95 }}
              >
                ENTER THE PORTAL
              </motion.button>

              {/* Final decorative elements */}
              <motion.div
                className="mt-12 text-sm text-gray-600 font-luxury-mono"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5 }}
              >
                Session ID: {user.userId}
                <br />
                Joined: {user.joinedAt.toLocaleDateString()}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}