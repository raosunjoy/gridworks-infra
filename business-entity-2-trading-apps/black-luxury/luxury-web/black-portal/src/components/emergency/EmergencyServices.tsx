'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { EmergencyContact } from '@/types/butler';
import { BlackUser } from '@/types/portal';
import { useLuxuryEffects } from '@/hooks/useLuxuryEffects';

interface EmergencyServicesProps {
  user: BlackUser;
  isOpen: boolean;
  onClose: () => void;
  emergencyType?: 'medical' | 'security' | 'legal' | 'financial' | 'general';
}

interface EmergencyResponse {
  id: string;
  type: string;
  status: 'connecting' | 'connected' | 'dispatched' | 'resolved';
  timestamp: Date;
  responderName: string;
  estimatedArrival?: string;
  instructions: string[];
}

export function EmergencyServices({ user, isOpen, onClose, emergencyType = 'general' }: EmergencyServicesProps) {
  const [activeEmergency, setActiveEmergency] = useState<EmergencyResponse | null>(null);
  const [emergencyContacts, setEmergencyContacts] = useState<EmergencyContact[]>([]);
  const [selectedType, setSelectedType] = useState<string>(emergencyType);
  const [isConnecting, setIsConnecting] = useState(false);
  const [userLocation, setUserLocation] = useState<string>('Mumbai, Maharashtra');

  const { luxurySuccess, luxuryError, getTierColor } = useLuxuryEffects(user.tier);

  useEffect(() => {
    initializeEmergencyContacts();
    if (emergencyType !== 'general') {
      handleEmergencyActivation(emergencyType);
    }
  }, [emergencyType]);

  const initializeEmergencyContacts = () => {
    const contacts: EmergencyContact[] = [
      {
        id: 'medical_primary',
        name: user.tier === 'void' ? 'Quantum Medical Response' : 
              user.tier === 'obsidian' ? 'Diamond Medical Services' : 'Onyx Health Emergency',
        type: 'medical',
        phoneNumber: '+91-911-MEDICAL',
        email: 'emergency@luxury-medical.com',
        priority: 1,
        available24x7: true,
        responseTime: user.tier === 'void' ? '< 2 minutes' : '< 5 minutes'
      },
      {
        id: 'security_primary',
        name: user.tier === 'void' ? 'Interdimensional Security' : 
              user.tier === 'obsidian' ? 'Platinum Protection Services' : 'Silver Shield Security',
        type: 'security',
        phoneNumber: '+91-911-SECURITY',
        priority: 1,
        available24x7: true,
        responseTime: user.tier === 'void' ? '< 1 minute' : '< 3 minutes'
      },
      {
        id: 'legal_primary',
        name: user.tier === 'void' ? 'Cosmic Legal Consortium' : 
              user.tier === 'obsidian' ? 'Crystal Legal Associates' : 'Onyx Law Partners',
        type: 'legal',
        phoneNumber: '+91-911-LEGAL',
        email: 'urgent@luxury-legal.com',
        priority: 2,
        available24x7: user.tier === 'void',
        responseTime: '< 10 minutes'
      },
      {
        id: 'financial_primary',
        name: user.tier === 'void' ? 'Quantum Financial Crisis Team' : 
              user.tier === 'obsidian' ? 'Diamond Financial Emergency' : 'Platinum Financial Response',
        type: 'financial',
        phoneNumber: '+91-911-FINANCE',
        email: 'crisis@luxury-finance.com',
        priority: 2,
        available24x7: true,
        responseTime: '< 5 minutes'
      },
      {
        id: 'concierge_primary',
        name: `${user.dedicatedButler} Emergency Protocol`,
        type: 'concierge',
        phoneNumber: '+91-911-CONCIERGE',
        priority: 3,
        available24x7: true,
        responseTime: 'Immediate'
      }
    ];

    setEmergencyContacts(contacts);
  };

  const handleEmergencyActivation = async (type: string) => {
    setIsConnecting(true);
    setSelectedType(type);

    // Find appropriate contact
    const contact = emergencyContacts.find(c => c.type === type) || emergencyContacts[0];
    
    // Simulate emergency response
    setTimeout(() => {
      const response: EmergencyResponse = {
        id: `emergency_${Date.now()}`,
        type,
        status: 'connecting',
        timestamp: new Date(),
        responderName: contact?.name || 'Emergency Response Team',
        instructions: getEmergencyInstructions(type)
      };

      setActiveEmergency(response);
      setIsConnecting(false);
      luxurySuccess();

      // Simulate connection progression
      setTimeout(() => {
        setActiveEmergency(prev => prev ? { ...prev, status: 'connected' } : null);
        
        setTimeout(() => {
          setActiveEmergency(prev => prev ? { 
            ...prev, 
            status: 'dispatched',
            estimatedArrival: getEstimatedArrival(type)
          } : null);
        }, 3000);
      }, 2000);
      
    }, 1500);
  };

  const getEmergencyInstructions = (type: string): string[] => {
    const instructions = {
      medical: [
        'Stay calm and remain in your current location',
        'If conscious, describe your symptoms clearly',
        'Our medical team is being dispatched immediately',
        'Keep your communication device nearby',
        'Do not take any medication unless instructed'
      ],
      security: [
        'Move to a secure location immediately',
        'Do not confront any threats directly',
        'Keep communication open with our team',
        'Security personnel are en route to your location',
        'Follow all instructions from responding officers'
      ],
      legal: [
        'Do not make any statements without counsel present',
        'Document all relevant information if safe to do so',
        'Our legal team is being notified immediately',
        'Remain calm and cooperative with authorities',
        'Legal representation is being arranged'
      ],
      financial: [
        'All accounts are being secured immediately',
        'Do not authorize any further transactions',
        'Our crisis team is analyzing the situation',
        'Emergency credit lines are being activated',
        'Full financial audit is being initiated'
      ],
      general: [
        'Help is on the way',
        'Stay calm and remain safe',
        'Keep communication open',
        'Follow all safety protocols',
        'Emergency services have been notified'
      ]
    };

    return instructions[type as keyof typeof instructions] || instructions.general;
  };

  const getEstimatedArrival = (type: string): string => {
    const times = {
      medical: user.tier === 'void' ? '2-3 minutes' : '5-8 minutes',
      security: user.tier === 'void' ? '1-2 minutes' : '3-5 minutes',
      legal: '10-15 minutes',
      financial: '5-10 minutes',
      general: '5-10 minutes'
    };

    return times[type as keyof typeof times] || times.general;
  };

  const getTierConfig = () => {
    switch (user.tier) {
      case 'void':
        return {
          color: '#FFD700',
          emergencyColor: '#FF0000',
          bg: 'bg-gradient-to-br from-red-900/40 via-gray-900 to-black'
        };
      case 'obsidian':
        return {
          color: '#E5E4E2',
          emergencyColor: '#FF4444',
          bg: 'bg-gradient-to-br from-red-800/30 via-gray-900 to-black'
        };
      case 'onyx':
        return {
          color: '#C0C0C0',
          emergencyColor: '#FF6666',
          bg: 'bg-gradient-to-br from-red-700/20 via-gray-900 to-black'
        };
      default:
        return {
          color: '#C0C0C0',
          emergencyColor: '#FF6666',
          bg: 'bg-gradient-to-br from-red-700/20 via-gray-900 to-black'
        };
    }
  };

  const tierConfig = getTierConfig();

  const EmergencyButton = ({ type, icon, label, description }: {
    type: string;
    icon: string;
    label: string;
    description: string;
  }) => (
    <motion.button
      onClick={() => handleEmergencyActivation(type)}
      disabled={isConnecting || activeEmergency !== null}
      className="p-6 bg-gray-800 border-2 border-red-600 rounded-lg text-left hover:bg-red-900/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      whileHover={{ scale: 1.02, borderColor: tierConfig.emergencyColor }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex items-center space-x-4">
        <div className="text-4xl">{icon}</div>
        <div>
          <h3 className="text-xl font-luxury-serif text-white mb-1">{label}</h3>
          <p className="text-sm text-gray-400 font-luxury-sans">{description}</p>
        </div>
      </div>
    </motion.button>
  );

  if (!isOpen) return null;

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className={`w-full max-w-4xl h-[80vh] ${tierConfig.bg} border-2 border-red-600 rounded-xl overflow-hidden shadow-2xl`}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Header */}
        <div className="border-b-2 border-red-600 p-6 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <motion.div
              className="text-4xl"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              🚨
            </motion.div>
            <div>
              <h1 className="text-3xl font-luxury-serif text-red-400">
                EMERGENCY SERVICES
              </h1>
              <p className="text-gray-300 font-luxury-sans">
                {user.tier.toUpperCase()} Tier Emergency Response
              </p>
            </div>
          </div>
          
          {!activeEmergency && (
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
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {!activeEmergency ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Location Info */}
              <div className="bg-gray-800 border border-gray-600 rounded-lg p-4">
                <h3 className="text-lg font-luxury-serif text-white mb-2">Current Location</h3>
                <p className="text-gray-300 font-luxury-sans">📍 {userLocation}</p>
                <p className="text-sm text-gray-400 mt-1">
                  Location verified via secure GPS • Last updated: {new Date().toLocaleTimeString()}
                </p>
              </div>

              {/* Emergency Type Selection */}
              <div>
                <h3 className="text-xl font-luxury-serif text-white mb-4">Select Emergency Type</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <EmergencyButton
                    type="medical"
                    icon="🏥"
                    label="Medical Emergency"
                    description="Health, injury, or medical crisis"
                  />
                  <EmergencyButton
                    type="security"
                    icon="🛡️"
                    label="Security Emergency"
                    description="Personal safety or security threat"
                  />
                  <EmergencyButton
                    type="legal"
                    icon="⚖️"
                    label="Legal Emergency"
                    description="Legal crisis or urgent counsel needed"
                  />
                  <EmergencyButton
                    type="financial"
                    icon="💰"
                    label="Financial Emergency"
                    description="Financial crisis or security breach"
                  />
                </div>
              </div>

              {/* Quick Contact */}
              <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
                <h3 className="text-lg font-luxury-serif text-red-400 mb-3">Emergency Contacts</h3>
                <div className="space-y-2">
                  {emergencyContacts.slice(0, 3).map((contact) => (
                    <div key={contact.id} className="flex justify-between items-center">
                      <div>
                        <span className="text-white font-luxury-sans">{contact.name}</span>
                        <span className="text-gray-400 text-sm ml-2">({contact.type})</span>
                      </div>
                      <div className="text-red-400 font-luxury-mono text-sm">
                        {contact.responseTime}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Emergency Status */}
              <div className="bg-red-900/30 border-2 border-red-500 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-luxury-serif text-red-400">
                    EMERGENCY ACTIVE
                  </h2>
                  <motion.div
                    className="flex items-center space-x-2"
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                    <span className="text-red-400 font-luxury-sans uppercase">
                      {activeEmergency.status}
                    </span>
                  </motion.div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-luxury-serif text-white mb-3">Response Details</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Emergency Type:</span>
                        <span className="text-white capitalize">{activeEmergency.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Response Team:</span>
                        <span className="text-white">{activeEmergency.responderName}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Activated:</span>
                        <span className="text-white">{activeEmergency.timestamp.toLocaleTimeString()}</span>
                      </div>
                      {activeEmergency.estimatedArrival && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">ETA:</span>
                          <span className="text-green-400">{activeEmergency.estimatedArrival}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-luxury-serif text-white mb-3">Instructions</h3>
                    <ul className="space-y-1 text-sm text-gray-300">
                      {activeEmergency.instructions.map((instruction, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-red-400 mr-2">•</span>
                          {instruction}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Communication Panel */}
              <div className="bg-gray-800 border border-gray-600 rounded-lg p-6">
                <h3 className="text-lg font-luxury-serif text-white mb-4">Emergency Communication</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <motion.button
                      className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-luxury-sans"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      📞 Call Response Team
                    </motion.button>
                    <motion.button
                      className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-luxury-sans"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      💬 Open Chat
                    </motion.button>
                  </div>
                  
                  <motion.button
                    onClick={() => {
                      setActiveEmergency(prev => prev ? { ...prev, status: 'resolved' } : null);
                      setTimeout(() => {
                        setActiveEmergency(null);
                        onClose();
                      }, 2000);
                    }}
                    className="w-full bg-gray-700 text-gray-300 px-6 py-3 rounded-lg font-luxury-sans hover:bg-gray-600 transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Mark as Resolved
                  </motion.button>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}