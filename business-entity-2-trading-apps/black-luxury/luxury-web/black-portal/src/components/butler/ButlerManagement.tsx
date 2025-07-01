'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ButlerPersonality, ButlerCapability, ButlerAnalytics, EmergencyContact, LuxuryService } from '@/types/butler';
import { BlackUser } from '@/types/portal';
import { useLuxuryEffects } from '@/hooks/useLuxuryEffects';

interface ButlerManagementProps {
  user: BlackUser;
  onClose: () => void;
}

export function ButlerManagement({ user, onClose }: ButlerManagementProps) {
  const [activeTab, setActiveTab] = useState<'personality' | 'capabilities' | 'analytics' | 'emergency' | 'services'>('personality');
  const [personality, setPersonality] = useState<ButlerPersonality | null>(null);
  const [capabilities, setCapabilities] = useState<ButlerCapability[]>([]);
  const [analytics, setAnalytics] = useState<ButlerAnalytics | null>(null);
  const [emergencyContacts, setEmergencyContacts] = useState<EmergencyContact[]>([]);
  const [luxuryServices, setLuxuryServices] = useState<LuxuryService[]>([]);

  const { luxuryInteraction, luxurySuccess, getTierColor } = useLuxuryEffects(user.tier);

  useEffect(() => {
    initializeButlerData();
  }, [user]);

  const initializeButlerData = () => {
    // Initialize personality
    const personalityData: ButlerPersonality = {
      name: user.dedicatedButler,
      tier: user.tier,
      personality: user.tier === 'void' ? 'quantum' : user.tier === 'obsidian' ? 'mystical' : 'professional',
      expertise: getExpertiseForTier(user.tier),
      voiceProfile: {
        tone: user.tier === 'void' ? 'cosmic' : user.tier === 'obsidian' ? 'authoritative' : 'warm',
        speed: 'normal',
        formality: user.tier === 'void' ? 'ultra-formal' : 'formal'
      },
      capabilities: getCapabilitiesForTier(user.tier)
    };
    setPersonality(personalityData);
    setCapabilities(personalityData.capabilities);

    // Initialize analytics
    setAnalytics({
      totalInteractions: 1247 + Math.floor(Math.random() * 500),
      successfulExecutions: 1156 + Math.floor(Math.random() * 400),
      averageResponseTime: 1.2 + Math.random() * 0.8,
      userSatisfactionScore: 0.94 + Math.random() * 0.05,
      mostUsedCapabilities: ['market_analysis', 'portfolio_management', 'luxury_concierge'],
      emergencyInterventions: Math.floor(Math.random() * 5)
    });

    // Initialize emergency contacts
    setEmergencyContacts([
      {
        id: 'medical_1',
        name: 'Dr. Platinum Medical Services',
        type: 'medical',
        phoneNumber: '+91-911-PLATINUM',
        email: 'emergency@platinummedical.luxury',
        priority: 1,
        available24x7: true,
        responseTime: '< 3 minutes'
      },
      {
        id: 'security_1',
        name: 'Diamond Security Response',
        type: 'security',
        phoneNumber: '+91-911-DIAMOND',
        priority: 2,
        available24x7: true,
        responseTime: '< 5 minutes'
      },
      {
        id: 'legal_1',
        name: 'Onyx Legal Consultancy',
        type: 'legal',
        phoneNumber: '+91-911-LEGAL',
        email: 'urgent@onyxlegal.elite',
        priority: 3,
        available24x7: false,
        responseTime: '< 15 minutes'
      }
    ]);

    // Initialize luxury services
    setLuxuryServices([
      {
        id: 'transport_1',
        name: 'Quantum Jet Services',
        category: 'transport',
        tier: user.tier,
        provider: 'Cosmic Aviation Elite',
        description: 'Transcendent travel experiences beyond conventional luxury',
        priceRange: '₹50L - ₹2Cr per journey',
        availability: '24/7',
        bookingMethod: 'instant',
        location: 'Global'
      },
      {
        id: 'dining_1',
        name: 'Void Cuisine Experiences',
        category: 'dining',
        tier: user.tier,
        provider: 'Interdimensional Culinary Arts',
        description: 'Gastronomic journeys that reshape reality',
        priceRange: '₹5L - ₹25L per experience',
        availability: 'by_appointment',
        bookingMethod: 'concierge_arranged'
      }
    ]);
  };

  const getExpertiseForTier = (tier: string): string[] => {
    const expertise = {
      void: [
        'Quantum Market Analysis',
        'Reality Distortion Trading',
        'Interdimensional Portfolio Management',
        'Cosmic Event Prediction',
        'Time-Space Arbitrage',
        'Universal Concierge Services'
      ],
      obsidian: [
        'Diamond-Tier Analytics',
        'Enterprise Strategy',
        'Private Banking Integration',
        'Global Market Intelligence',
        'Crystalline Precision Trading',
        'Platinum Lifestyle Management'
      ],
      onyx: [
        'Premium Market Analysis',
        'Portfolio Optimization',
        'Risk Management',
        'Luxury Lifestyle Curation',
        'Intelligent Automation',
        'Silver-Stream Analytics'
      ]
    };
    return expertise[tier as keyof typeof expertise] || expertise.onyx;
  };

  const getCapabilitiesForTier = (tier: string): ButlerCapability[] => {
    const baseCapabilities = [
      {
        id: 'market_analysis',
        name: 'Market Analysis',
        description: 'Advanced market insights and predictions',
        tier: tier as any,
        category: 'analysis' as const,
        enabled: true
      },
      {
        id: 'portfolio_management',
        name: 'Portfolio Management',
        description: 'Intelligent portfolio optimization',
        tier: tier as any,
        category: 'trading' as const,
        enabled: true
      },
      {
        id: 'concierge_services',
        name: 'Concierge Services',
        description: 'Luxury lifestyle management',
        tier: tier as any,
        category: 'luxury' as const,
        enabled: true
      },
      {
        id: 'security_monitoring',
        name: 'Security Monitoring',
        description: '24/7 security and risk assessment',
        tier: tier as any,
        category: 'security' as const,
        enabled: true
      }
    ];

    if (tier === 'void') {
      baseCapabilities.push({
        id: 'quantum_trading',
        name: 'Quantum Trading',
        description: 'Trade across parallel market dimensions',
        tier: 'void',
        category: 'trading',
        enabled: true
      });
    }

    return baseCapabilities;
  };

  const getTierConfig = () => {
    switch (user.tier) {
      case 'void':
        return {
          color: '#FFD700',
          accent: '#FFF700',
          bg: 'bg-gradient-to-br from-yellow-900/20 via-gray-900 to-black'
        };
      case 'obsidian':
        return {
          color: '#E5E4E2',
          accent: '#F5F5F5',
          bg: 'bg-gradient-to-br from-gray-700/20 via-gray-900 to-black'
        };
      case 'onyx':
        return {
          color: '#C0C0C0',
          accent: '#D0D0D0',
          bg: 'bg-gradient-to-br from-gray-600/20 via-gray-900 to-black'
        };
      default:
        return {
          color: '#C0C0C0',
          accent: '#D0D0D0',
          bg: 'bg-gradient-to-br from-gray-600/20 via-gray-900 to-black'
        };
    }
  };

  const tierConfig = getTierConfig();

  const toggleCapability = (capabilityId: string) => {
    setCapabilities(prev => 
      prev.map(cap => 
        cap.id === capabilityId 
          ? { ...cap, enabled: !cap.enabled }
          : cap
      )
    );
    luxuryInteraction();
  };

  const TabButton = ({ tab, children }: { tab: typeof activeTab, children: React.ReactNode }) => (
    <motion.button
      onClick={() => {
        setActiveTab(tab);
        luxuryInteraction();
      }}
      className={`px-6 py-3 rounded-lg font-luxury-sans tracking-wide transition-all duration-300 ${
        activeTab === tab 
          ? 'text-black shadow-lg' 
          : 'text-gray-400 hover:text-white'
      }`}
      style={{ 
        backgroundColor: activeTab === tab ? tierConfig.color : 'transparent',
        borderColor: tierConfig.color
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {children}
    </motion.button>
  );

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className={`w-full max-w-6xl h-[90vh] ${tierConfig.bg} border border-gray-700 rounded-xl overflow-hidden shadow-2xl`}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Header */}
        <div className="border-b border-gray-700 p-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-luxury-serif" style={{ color: tierConfig.color }}>
              Butler Management
            </h1>
            <p className="text-gray-400 font-luxury-sans mt-1">
              Configure {user.dedicatedButler} for optimal performance
            </p>
          </div>
          
          <motion.button
            onClick={onClose}
            className="p-3 text-gray-400 hover:text-white transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </motion.button>
        </div>

        {/* Navigation */}
        <div className="border-b border-gray-700 p-6">
          <div className="flex space-x-4 overflow-x-auto">
            <TabButton tab="personality">Personality</TabButton>
            <TabButton tab="capabilities">Capabilities</TabButton>
            <TabButton tab="analytics">Analytics</TabButton>
            <TabButton tab="emergency">Emergency</TabButton>
            <TabButton tab="services">Services</TabButton>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <AnimatePresence mode="wait">
            {activeTab === 'personality' && personality && (
              <motion.div
                key="personality"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                      Core Personality
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-gray-300 font-luxury-sans mb-2">Name</label>
                        <input
                          type="text"
                          value={personality.name}
                          readOnly
                          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-gray-300 font-luxury-sans mb-2">Personality Type</label>
                        <div className="px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white capitalize">
                          {personality.personality}
                        </div>
                      </div>
                      <div>
                        <label className="block text-gray-300 font-luxury-sans mb-2">Tier Level</label>
                        <div 
                          className="px-4 py-2 bg-gray-800 border rounded-lg font-bold uppercase"
                          style={{ color: tierConfig.color, borderColor: tierConfig.color }}
                        >
                          {personality.tier}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                      Voice Profile
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-gray-300 font-luxury-sans mb-2">Tone</label>
                        <select 
                          value={personality.voiceProfile.tone}
                          onChange={(e) => setPersonality(prev => prev ? {
                            ...prev,
                            voiceProfile: { ...prev.voiceProfile, tone: e.target.value as any }
                          } : null)}
                          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        >
                          <option value="warm">Warm</option>
                          <option value="authoritative">Authoritative</option>
                          <option value="ethereal">Ethereal</option>
                          <option value="cosmic">Cosmic</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-gray-300 font-luxury-sans mb-2">Speed</label>
                        <select 
                          value={personality.voiceProfile.speed}
                          onChange={(e) => setPersonality(prev => prev ? {
                            ...prev,
                            voiceProfile: { ...prev.voiceProfile, speed: e.target.value as any }
                          } : null)}
                          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        >
                          <option value="slow">Slow</option>
                          <option value="normal">Normal</option>
                          <option value="fast">Fast</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-gray-300 font-luxury-sans mb-2">Formality</label>
                        <select 
                          value={personality.voiceProfile.formality}
                          onChange={(e) => setPersonality(prev => prev ? {
                            ...prev,
                            voiceProfile: { ...prev.voiceProfile, formality: e.target.value as any }
                          } : null)}
                          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        >
                          <option value="casual">Casual</option>
                          <option value="formal">Formal</option>
                          <option value="ultra-formal">Ultra-Formal</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-luxury-serif mb-4" style={{ color: tierConfig.color }}>
                    Areas of Expertise
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {personality.expertise.map((skill) => (
                      <div
                        key={skill}
                        className="px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-gray-300 font-luxury-sans"
                      >
                        {skill}
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'capabilities' && (
              <motion.div
                key="capabilities"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <h3 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                  Butler Capabilities
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {capabilities.map((capability) => (
                    <motion.div
                      key={capability.id}
                      className="p-4 bg-gray-800 border border-gray-600 rounded-lg"
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-luxury-sans text-white mb-1">{capability.name}</h4>
                          <p className="text-sm text-gray-400">{capability.description}</p>
                        </div>
                        <motion.button
                          onClick={() => toggleCapability(capability.id)}
                          className={`w-12 h-6 rounded-full transition-colors ${
                            capability.enabled ? 'bg-green-500' : 'bg-gray-600'
                          }`}
                          whileTap={{ scale: 0.95 }}
                        >
                          <motion.div
                            className="w-5 h-5 bg-white rounded-full shadow"
                            animate={{ x: capability.enabled ? 24 : 2 }}
                            transition={{ type: "spring", stiffness: 500, damping: 30 }}
                          />
                        </motion.button>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500 uppercase">{capability.category}</span>
                        <span 
                          className="text-xs font-bold uppercase"
                          style={{ color: tierConfig.color }}
                        >
                          {capability.tier}
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'analytics' && analytics && (
              <motion.div
                key="analytics"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <h3 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                  Performance Analytics
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="p-6 bg-gray-800 border border-gray-600 rounded-lg text-center">
                    <div className="text-3xl font-luxury-serif mb-2" style={{ color: tierConfig.color }}>
                      {analytics.totalInteractions.toLocaleString()}
                    </div>
                    <div className="text-gray-400 font-luxury-sans">Total Interactions</div>
                  </div>
                  <div className="p-6 bg-gray-800 border border-gray-600 rounded-lg text-center">
                    <div className="text-3xl font-luxury-serif mb-2" style={{ color: tierConfig.color }}>
                      {(analytics.userSatisfactionScore * 100).toFixed(1)}%
                    </div>
                    <div className="text-gray-400 font-luxury-sans">Satisfaction Score</div>
                  </div>
                  <div className="p-6 bg-gray-800 border border-gray-600 rounded-lg text-center">
                    <div className="text-3xl font-luxury-serif mb-2" style={{ color: tierConfig.color }}>
                      {analytics.averageResponseTime.toFixed(1)}s
                    </div>
                    <div className="text-gray-400 font-luxury-sans">Avg Response Time</div>
                  </div>
                  <div className="p-6 bg-gray-800 border border-gray-600 rounded-lg text-center">
                    <div className="text-3xl font-luxury-serif mb-2" style={{ color: tierConfig.color }}>
                      {analytics.successfulExecutions.toLocaleString()}
                    </div>
                    <div className="text-gray-400 font-luxury-sans">Successful Executions</div>
                  </div>
                  <div className="p-6 bg-gray-800 border border-gray-600 rounded-lg text-center">
                    <div className="text-3xl font-luxury-serif mb-2" style={{ color: tierConfig.color }}>
                      {analytics.emergencyInterventions}
                    </div>
                    <div className="text-gray-400 font-luxury-sans">Emergency Interventions</div>
                  </div>
                  <div className="p-6 bg-gray-800 border border-gray-600 rounded-lg">
                    <div className="text-lg font-luxury-serif mb-3" style={{ color: tierConfig.color }}>
                      Most Used
                    </div>
                    <div className="space-y-2">
                      {analytics.mostUsedCapabilities.map((capability, index) => (
                        <div key={capability} className="text-sm text-gray-400 font-luxury-sans">
                          {index + 1}. {capability.replace('_', ' ')}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'emergency' && (
              <motion.div
                key="emergency"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <h3 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                  Emergency Contacts
                </h3>
                <div className="space-y-4">
                  {emergencyContacts.map((contact) => (
                    <div key={contact.id} className="p-4 bg-gray-800 border border-gray-600 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-luxury-sans text-white mb-1">{contact.name}</h4>
                          <p className="text-sm text-gray-400 mb-2 capitalize">{contact.type} Services</p>
                          <div className="space-y-1 text-sm">
                            <div className="text-gray-300">📞 {contact.phoneNumber}</div>
                            {contact.email && (
                              <div className="text-gray-300">✉️ {contact.email}</div>
                            )}
                            <div className="text-gray-400">⏱️ Response: {contact.responseTime}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`px-2 py-1 rounded text-xs ${
                            contact.available24x7 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                          }`}>
                            {contact.available24x7 ? '24/7' : 'Business Hours'}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">Priority: {contact.priority}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'services' && (
              <motion.div
                key="services"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <h3 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                  Luxury Services
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {luxuryServices.map((service) => (
                    <div key={service.id} className="p-6 bg-gray-800 border border-gray-600 rounded-lg">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="font-luxury-serif text-white text-lg">{service.name}</h4>
                        <span 
                          className="px-2 py-1 rounded text-xs font-bold uppercase"
                          style={{ backgroundColor: `${tierConfig.color}20`, color: tierConfig.color }}
                        >
                          {service.tier}
                        </span>
                      </div>
                      <p className="text-gray-300 font-luxury-sans mb-4">{service.description}</p>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Provider:</span>
                          <span className="text-gray-300">{service.provider}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Price Range:</span>
                          <span className="text-gray-300">{service.priceRange}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Availability:</span>
                          <span className="text-gray-300 capitalize">{service.availability.replace('_', ' ')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Booking:</span>
                          <span className="text-gray-300 capitalize">{service.bookingMethod.replace('_', ' ')}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
}