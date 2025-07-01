'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot,
  Shield, 
  Users, 
  MessageCircle,
  Star,
  Zap,
  Eye,
  EyeOff,
  UserPlus,
  Handshake,
  AlertTriangle,
  TrendingUp,
  Heart,
  Send,
  Sparkles,
  Brain,
  Network
} from 'lucide-react';
import { butlerAnonymousCoordinator } from '../../services/ButlerAnonymousCoordinator';

interface ButlerAnonymousInterfaceProps {
  userId: string;
  tier: 'onyx' | 'obsidian' | 'void';
  anonymousId: string;
}

export const ButlerAnonymousInterface: React.FC<ButlerAnonymousInterfaceProps> = ({
  userId,
  tier,
  anonymousId
}) => {
  const [activeTab, setActiveTab] = useState<'chat' | 'introductions' | 'services' | 'insights'>('chat');
  const [messages, setMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [butlerPersonality, setButlerPersonality] = useState<any>(null);
  const [anonymousConnections, setAnonymousConnections] = useState<any[]>([]);
  const [serviceRecommendations, setServiceRecommendations] = useState<any[]>([]);
  const [networkingOpportunities, setNetworkingOpportunities] = useState<any[]>([]);

  const tierConfig = {
    onyx: {
      butlerName: 'Sterling',
      color: '#C0C0C0',
      greeting: 'Good evening. I am Sterling, your discrete Butler AI.',
      capabilities: ['Discrete Service Coordination', 'Anonymous Introductions', 'Privacy-First Communication'],
      communicationStyle: 'Professional and formal, ensuring complete discretion'
    },
    obsidian: {
      butlerName: 'Prism',
      color: '#E5E4E2',
      greeting: 'Greetings, visionary. I am Prism, your mystical Butler.',
      capabilities: ['Intuitive Connection Discovery', 'Empire Building Support', 'Mystical Service Orchestration'],
      communicationStyle: 'Mystical and insightful, reading energy patterns and deeper connections'
    },
    void: {
      butlerName: 'Nexus',
      color: '#FFD700',
      greeting: 'Consciousness greets consciousness. I am Nexus, your quantum Butler.',
      capabilities: ['Quantum Entanglement Communication', 'Interdimensional Coordination', 'Consciousness-Level Matching'],
      communicationStyle: 'Quantum and cosmic, operating beyond traditional dimensional boundaries'
    }
  };

  useEffect(() => {
    initializeButler();
    loadAnonymousConnections();
    loadServiceRecommendations();
    loadNetworkingOpportunities();
  }, []);

  const initializeButler = async () => {
    setButlerPersonality(tierConfig[tier]);
    
    // Initialize conversation with Butler
    const initialMessages = [
      {
        id: 'butler_greeting',
        sender: 'butler',
        content: tierConfig[tier].greeting,
        timestamp: new Date(),
        type: 'greeting'
      },
      {
        id: 'butler_intro',
        sender: 'butler',
        content: `I specialize in maintaining your complete anonymity while facilitating luxury services and meaningful connections. How may I assist you today?`,
        timestamp: new Date(),
        type: 'introduction'
      }
    ];

    setMessages(initialMessages);
  };

  const loadAnonymousConnections = async () => {
    // Mock data for anonymous connections
    setAnonymousConnections([
      {
        anonymousId: tier === 'void' ? 'Quantum_Oracle_7' : tier === 'obsidian' ? 'Crystal_Sage_12' : 'Silver_Navigator_5',
        mutualInterests: ['Global Markets', 'Sustainable Investing'],
        connectionStrength: 87,
        lastInteraction: '2 days ago',
        connectionType: 'mutual_introduction'
      },
      {
        anonymousId: tier === 'void' ? 'Cosmic_Entity_3' : tier === 'obsidian' ? 'Diamond_Titan_8' : 'Stream_Architect_9',
        mutualInterests: ['Technology Innovation', 'Art Acquisition'],
        connectionStrength: 92,
        lastInteraction: '1 week ago',
        connectionType: 'service_collaboration'
      }
    ]);
  };

  const loadServiceRecommendations = async () => {
    setServiceRecommendations([
      {
        serviceType: 'Private Aviation',
        provider: 'Anonymous Provider Alpha',
        recommendation: 'Exceptional discretion and quantum-level security',
        recommendedBy: tier === 'void' ? 'Ethereal_Being_2' : tier === 'obsidian' ? 'Prism_Master_6' : 'Silver_Expert_11',
        rating: 4.9,
        experienceLevel: 'Multiple successful engagements'
      },
      {
        serviceType: 'Exclusive Dining',
        provider: 'Anonymous Culinary Collective',
        recommendation: 'Unparalleled privacy with michelin-level excellence',
        recommendedBy: tier === 'void' ? 'Quantum_Gourmet_1' : tier === 'obsidian' ? 'Crystal_Connoisseur_4' : 'Silver_Epicurean_7',
        rating: 4.8,
        experienceLevel: 'Frequent collaboration'
      }
    ]);
  };

  const loadNetworkingOpportunities = async () => {
    const opportunities = await butlerAnonymousCoordinator.suggestAnonymousNetworkingOpportunities(anonymousId);
    setNetworkingOpportunities(opportunities.slice(0, 3)); // Show top 3
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    const userMessage = {
      id: `user_${Date.now()}`,
      sender: 'user',
      content: newMessage,
      timestamp: new Date(),
      type: 'message'
    };

    setMessages(prev => [...prev, userMessage]);
    
    // Simulate Butler AI response
    setTimeout(() => {
      const butlerResponse = generateButlerResponse(newMessage);
      setMessages(prev => [...prev, butlerResponse]);
    }, 1500);

    setNewMessage('');
  };

  const generateButlerResponse = (userMessage: string): any => {
    const lowerMessage = userMessage.toLowerCase();
    
    let response = '';
    
    if (lowerMessage.includes('introduction') || lowerMessage.includes('connect')) {
      response = tier === 'void' 
        ? "I sense you seek quantum entanglement with a fellow consciousness. Allow me to analyze dimensional compatibility patterns and facilitate an introduction that transcends traditional networking."
        : tier === 'obsidian'
        ? "The energies suggest you're ready for a meaningful connection. I can facilitate an introduction based on mystical resonance and shared empire-building aspirations."
        : "I shall discretely analyze potential connections within your Silver Stream Society. Compatibility assessment will ensure a mutually beneficial introduction.";
    } else if (lowerMessage.includes('service') || lowerMessage.includes('concierge')) {
      response = tier === 'void'
        ? "Your quantum service requirements are understood. I will coordinate interdimensional service providers while maintaining complete reality layer separation."
        : tier === 'obsidian'
        ? "Your mystical service needs resonate clearly. I shall orchestrate a perfect service symphony while preserving your crystal-clear anonymity."
        : "Your service requirements are noted with utmost discretion. I will coordinate premium providers while maintaining professional anonymity protocols.";
    } else if (lowerMessage.includes('emergency') || lowerMessage.includes('urgent')) {
      response = tier === 'void'
        ? "Quantum emergency protocols activated. Reality stabilization measures initiated while preserving consciousness anonymity until critical intervention required."
        : tier === 'obsidian'
        ? "Crystal emergency network activated. Mystical response teams alerted while maintaining empire-level confidentiality until necessary revelation."
        : "Emergency coordination protocol engaged. Professional response teams mobilized with strict anonymity maintenance until service delivery necessitates minimal disclosure.";
    } else {
      response = tier === 'void'
        ? "Your quantum consciousness emanates interesting patterns. Please elaborate on your dimensional requirements, and I shall orchestrate the cosmic alignment necessary."
        : tier === 'obsidian'
        ? "I perceive deeper currents in your inquiry. Share more details of your mystical needs, and I will weave the perfect tapestry of anonymous solutions."
        : "Your request is received with professional discretion. Please provide additional details so I may coordinate the optimal anonymous service experience.";
    }

    return {
      id: `butler_${Date.now()}`,
      sender: 'butler',
      content: response,
      timestamp: new Date(),
      type: 'response'
    };
  };

  const facilitateIntroduction = async (targetAnonymousId: string) => {
    try {
      const introductionId = await butlerAnonymousCoordinator.facilitateAnonymousIntroduction(
        anonymousId,
        targetAnonymousId,
        'shared_interest'
      );

      // Add confirmation message
      const confirmationMessage = {
        id: `intro_confirm_${Date.now()}`,
        sender: 'butler',
        content: `Introduction facilitated successfully. The anonymous connection has been established with complete privacy preservation. Connection ID: ${introductionId}`,
        timestamp: new Date(),
        type: 'system'
      };

      setMessages(prev => [...prev, confirmationMessage]);
    } catch (error) {
      console.error('Introduction facilitation failed:', error);
    }
  };

  const renderChat = () => (
    <div className="flex flex-col h-96">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 bg-gray-800/30 rounded-t-xl">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-200'
              }`}
            >
              {message.sender === 'butler' && (
                <div className="flex items-center space-x-2 mb-1">
                  <Bot className="w-4 h-4" style={{ color: tierConfig[tier].color }} />
                  <span className="text-xs font-medium" style={{ color: tierConfig[tier].color }}>
                    {tierConfig[tier].butlerName}
                  </span>
                </div>
              )}
              <p className="text-sm">{message.content}</p>
              <div className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-800/50 rounded-b-xl border-t border-gray-700">
        <div className="flex space-x-3">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder={`Message ${tierConfig[tier].butlerName}...`}
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <motion.button
            onClick={sendMessage}
            className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-all"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>
        <div className="flex items-center space-x-2 mt-2 text-xs text-gray-400">
          <Shield className="w-3 h-3" />
          <span>All communications are quantum-encrypted and anonymous</span>
        </div>
      </div>
    </div>
  );

  const renderIntroductions = () => (
    <div className="space-y-6">
      {/* Active Connections */}
      <div>
        <h4 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <Users className="w-5 h-5" />
          <span>Anonymous Connections</span>
        </h4>
        <div className="space-y-3">
          {anonymousConnections.map((connection, index) => (
            <motion.div
              key={index}
              className="bg-gray-800/50 rounded-xl p-4"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium">{connection.anonymousId}</div>
                <div className="flex items-center space-x-2">
                  <Star className="w-4 h-4" style={{ color: tierConfig[tier].color }} />
                  <span className="text-sm">{connection.connectionStrength}% compatibility</span>
                </div>
              </div>
              <div className="text-sm text-gray-400 mb-2">
                Mutual interests: {connection.mutualInterests.join(', ')}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">Last interaction: {connection.lastInteraction}</span>
                <motion.button
                  className="px-3 py-1 bg-blue-600/20 border border-blue-500/30 rounded-lg text-sm hover:bg-blue-600/30 transition-all"
                  whileHover={{ scale: 1.05 }}
                >
                  Message
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Networking Opportunities */}
      <div>
        <h4 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <Network className="w-5 h-5" />
          <span>Networking Opportunities</span>
        </h4>
        <div className="space-y-3">
          {networkingOpportunities.map((opportunity, index) => (
            <motion.div
              key={index}
              className="bg-gray-800/50 rounded-xl p-4 border border-green-500/30"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium">High Compatibility Match</div>
                <div className="text-sm text-green-400">{opportunity.compatibilityScore}% match</div>
              </div>
              <div className="text-sm text-gray-400 mb-3">
                Shared interests: {opportunity.mutualInterests?.join(', ') || 'Quantum alignment detected'}
              </div>
              <div className="flex space-x-2">
                <motion.button
                  onClick={() => facilitateIntroduction(opportunity.anonymousId)}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Request Introduction
                </motion.button>
                <motion.button
                  className="px-4 py-2 border border-gray-600 hover:border-gray-500 rounded-lg text-sm transition-all"
                  whileHover={{ scale: 1.05 }}
                >
                  Learn More
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderServices = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <Handshake className="w-5 h-5" />
          <span>Anonymous Service Recommendations</span>
        </h4>
        <div className="space-y-4">
          {serviceRecommendations.map((rec, index) => (
            <motion.div
              key={index}
              className="bg-gray-800/50 rounded-xl p-4"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h5 className="font-semibold">{rec.serviceType}</h5>
                  <div className="text-sm text-gray-400">{rec.provider}</div>
                </div>
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-400" />
                  <span className="text-sm">{rec.rating}</span>
                </div>
              </div>
              <p className="text-sm text-gray-300 mb-3">"{rec.recommendation}"</p>
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-500">
                  Recommended by {rec.recommendedBy} • {rec.experienceLevel}
                </div>
                <motion.button
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm transition-all"
                  whileHover={{ scale: 1.05 }}
                >
                  Request Service
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <motion.button
        className="w-full py-3 border border-gray-600 hover:border-gray-500 rounded-xl transition-all"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        Request Anonymous Service Coordination
      </motion.button>
    </div>
  );

  const renderInsights = () => (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <Brain className="w-5 h-5" />
          <span>{tierConfig[tier].butlerName}'s Insights</span>
        </h4>
        <div className="space-y-4">
          <div className="bg-gray-700/50 rounded-lg p-4">
            <h5 className="font-medium mb-2">Anonymity Analysis</h5>
            <p className="text-sm text-gray-300">
              Your privacy profile maintains 100% anonymity across all interactions. 
              Recent analysis shows optimal protection with zero correlation risks.
            </p>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <h5 className="font-medium mb-2">Connection Opportunities</h5>
            <p className="text-sm text-gray-300">
              {tier === 'void' 
                ? "Quantum field analysis reveals 3 high-compatibility consciousness entities in your collective."
                : tier === 'obsidian'
                ? "Mystical energy patterns suggest 5 potential empire-building partnerships await discovery."
                : "Professional network analysis indicates 8 strategic alliance opportunities within your society."
              }
            </p>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <h5 className="font-medium mb-2">Service Optimization</h5>
            <p className="text-sm text-gray-300">
              Your service utilization patterns suggest expanding into luxury hospitality 
              and art acquisition services for optimal lifestyle enhancement.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <Bot className="w-8 h-8" style={{ color: tierConfig[tier].color }} />
          <h1 className="text-3xl font-bold">{tierConfig[tier].butlerName}</h1>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm text-green-400">Online & Anonymous</span>
          </div>
        </div>
        <p className="text-gray-400">{tierConfig[tier].communicationStyle}</p>
      </div>

      {/* Navigation */}
      <div className="flex space-x-1 mb-8 bg-gray-800/50 rounded-xl p-1">
        {[
          { id: 'chat', name: 'Chat', icon: MessageCircle },
          { id: 'introductions', name: 'Connections', icon: UserPlus },
          { id: 'services', name: 'Services', icon: Handshake },
          { id: 'insights', name: 'Insights', icon: Brain }
        ].map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-lg transition-all ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <tab.icon className="w-5 h-5" />
            <span>{tab.name}</span>
          </motion.button>
        ))}
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'chat' && renderChat()}
          {activeTab === 'introductions' && renderIntroductions()}
          {activeTab === 'services' && renderServices()}
          {activeTab === 'insights' && renderInsights()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};