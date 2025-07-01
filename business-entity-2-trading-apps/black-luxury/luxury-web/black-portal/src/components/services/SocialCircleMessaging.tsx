'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Shield, 
  Users, 
  MessageCircle, 
  TrendingUp, 
  DollarSign, 
  Star,
  Lock,
  Eye,
  EyeOff,
  BarChart3,
  FileText,
  Image,
  Mic,
  Plus,
  MoreHorizontal,
  Heart,
  ArrowUp,
  AlertTriangle
} from 'lucide-react';
import { zkSocialCircleMessaging } from '../../services/ZKSocialCircleMessaging';

interface SocialCircleMessagingProps {
  anonymousId: string;
  tier: 'onyx' | 'obsidian' | 'void';
  circleId: string;
}

export const SocialCircleMessaging: React.FC<SocialCircleMessagingProps> = ({
  anonymousId,
  tier,
  circleId
}) => {
  const [activeTab, setActiveTab] = useState<'discussions' | 'deals' | 'polls' | 'private'>('discussions');
  const [discussions, setDiscussions] = useState<any[]>([]);
  const [selectedDiscussion, setSelectedDiscussion] = useState<any>(null);
  const [newMessage, setNewMessage] = useState('');
  const [messageType, setMessageType] = useState<'general_discussion' | 'market_insight' | 'deal_opportunity' | 'service_recommendation'>('general_discussion');
  const [showNewDiscussion, setShowNewDiscussion] = useState(false);

  const tierConfig = {
    onyx: {
      name: 'Silver Stream Society',
      color: '#C0C0C0',
      memberCount: '67 active members',
      exclusivity: '₹100+ Cr verified portfolio holders',
      features: ['Market Analysis', 'Deal Sharing', 'Service Recommendations', 'Anonymous Networking']
    },
    obsidian: {
      name: 'Crystal Empire Network',
      color: '#E5E4E2',
      memberCount: '23 active members',
      exclusivity: '₹1,000+ Cr empire builders',
      features: ['Empire Strategy', 'M&A Opportunities', 'Private Equity', 'Global Intelligence']
    },
    void: {
      name: 'Quantum Consciousness Collective',
      color: '#FFD700',
      memberCount: '8 active members',
      exclusivity: '₹8,000+ Cr reality benders',
      features: ['Quantum Philosophy', 'Reality Trading', 'Cosmic Events', 'Interdimensional Deals']
    }
  };

  useEffect(() => {
    loadDiscussions();
  }, [circleId]);

  const loadDiscussions = async () => {
    // Mock data - would be loaded from ZK messaging service
    setDiscussions([
      {
        id: 'disc_1',
        title: tier === 'void' ? 'Quantum Market Fluctuation Analysis' : tier === 'obsidian' ? 'Global Empire Expansion Strategies' : 'Premium Market Opportunities',
        category: 'market_analysis',
        initiator: tier === 'void' ? 'Quantum_Sage_7' : tier === 'obsidian' ? 'Crystal_Emperor_3' : 'Silver_Navigator_12',
        participants: tier === 'void' ? 5 : tier === 'obsidian' ? 12 : 23,
        lastActivity: '2 hours ago',
        messages: 47,
        reputation: 856,
        isPrivate: false
      },
      {
        id: 'disc_2',
        title: tier === 'void' ? 'Interdimensional Asset Allocation' : tier === 'obsidian' ? 'Private Equity Deal Flow' : 'Luxury Service Network',
        category: 'investment_strategy',
        initiator: tier === 'void' ? 'Cosmic_Entity_2' : tier === 'obsidian' ? 'Diamond_Titan_8' : 'Stream_Strategist_5',
        participants: tier === 'void' ? 3 : tier === 'obsidian' ? 8 : 18,
        lastActivity: '4 hours ago',
        messages: 23,
        reputation: 734,
        isPrivate: tier !== 'onyx'
      }
    ]);
  };

  const renderDiscussions = () => (
    <div className="space-y-6">
      {/* New Discussion Button */}
      <motion.button
        onClick={() => setShowNewDiscussion(true)}
        className="w-full p-4 border-2 border-dashed border-gray-600 rounded-xl hover:border-gray-500 transition-all group"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="flex items-center justify-center space-x-2 text-gray-400 group-hover:text-white">
          <Plus className="w-5 h-5" />
          <span>Start Anonymous Discussion</span>
        </div>
      </motion.button>

      {/* Active Discussions */}
      <div className="space-y-4">
        {discussions.map((discussion) => (
          <motion.div
            key={discussion.id}
            className="bg-gray-800/50 rounded-xl p-6 hover:bg-gray-700/50 transition-all cursor-pointer"
            onClick={() => setSelectedDiscussion(discussion)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold text-lg mb-1">{discussion.title}</h3>
                <div className="flex items-center space-x-3 text-sm text-gray-400">
                  <span>by {discussion.initiator}</span>
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4" />
                    <span>{discussion.participants} participants</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MessageCircle className="w-4 h-4" />
                    <span>{discussion.messages} messages</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {discussion.isPrivate && (
                  <Lock className="w-4 h-4 text-yellow-400" />
                )}
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4" style={{ color: tierConfig[tier].color }} />
                  <span className="text-sm">{discussion.reputation}</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-xs bg-gray-700 px-2 py-1 rounded-full capitalize">
                {discussion.category.replace('_', ' ')}
              </span>
              <span className="text-xs text-gray-500">{discussion.lastActivity}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );

  const renderDeals = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 rounded-xl p-6 border border-green-500/30">
        <div className="flex items-start space-x-3">
          <Shield className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-semibold text-green-400 mb-2">Anonymous Deal Flow</h4>
            <p className="text-sm text-gray-300 mb-3">
              Share and discover investment opportunities while maintaining complete anonymity. 
              All deal details are encrypted and only accessible to verified circle members.
            </p>
          </div>
        </div>
      </div>

      {/* Deal Opportunities */}
      <div className="space-y-4">
        {[
          {
            type: tier === 'void' ? 'Quantum Computing Startup' : tier === 'obsidian' ? 'Private Equity Fund' : 'Tech Startup',
            sector: tier === 'void' ? 'Quantum Technology' : tier === 'obsidian' ? 'Infrastructure' : 'FinTech',
            size: tier === 'void' ? '₹2,000+ Cr' : tier === 'obsidian' ? '₹1,500+ Cr' : '₹500+ Cr',
            stage: 'Due Diligence',
            sharedBy: tier === 'void' ? 'Infinite_Consciousness_1' : tier === 'obsidian' ? 'Empire_Oracle_4' : 'Silver_Visionary_9',
            timeAgo: '3 hours ago',
            interested: tier === 'void' ? 2 : tier === 'obsidian' ? 5 : 12
          },
          {
            type: tier === 'void' ? 'Interdimensional Real Estate' : tier === 'obsidian' ? 'Commercial Real Estate' : 'Luxury Properties',
            sector: 'Real Estate',
            size: tier === 'void' ? '₹5,000+ Cr' : tier === 'obsidian' ? '₹800+ Cr' : '₹200+ Cr',
            stage: 'Negotiation',
            sharedBy: tier === 'void' ? 'Cosmic_Architect_5' : tier === 'obsidian' ? 'Crystal_Sovereign_2' : 'Stream_Builder_7',
            timeAgo: '1 day ago',
            interested: tier === 'void' ? 4 : tier === 'obsidian' ? 7 : 8
          }
        ].map((deal, index) => (
          <motion.div
            key={index}
            className="bg-gray-800/50 rounded-xl p-6 hover:bg-gray-700/50 transition-all"
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="font-semibold text-lg mb-1">{deal.type}</h4>
                <div className="flex items-center space-x-4 text-sm text-gray-400">
                  <span>{deal.sector}</span>
                  <span className="font-medium" style={{ color: tierConfig[tier].color }}>{deal.size}</span>
                  <span className="bg-blue-900/30 px-2 py-1 rounded-full text-blue-400">{deal.stage}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-400 mb-1">Shared by</div>
                <div className="text-sm font-medium">{deal.sharedBy}</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4 text-sm text-gray-400">
                <span>{deal.timeAgo}</span>
                <div className="flex items-center space-x-1">
                  <Heart className="w-4 h-4" />
                  <span>{deal.interested} interested</span>
                </div>
              </div>
              <motion.button
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-all"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Express Interest
              </motion.button>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.button
        className="w-full py-3 border border-gray-600 hover:border-gray-500 rounded-xl transition-all"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        Share Anonymous Deal Opportunity
      </motion.button>
    </div>
  );

  const renderPolls = () => (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">Anonymous Circle Polls</h3>
        
        {/* Active Poll */}
        <div className="bg-gray-700/50 rounded-xl p-6 mb-4">
          <h4 className="font-semibold mb-3">
            {tier === 'void' ? 'What quantum market dimension shows most promise?' : 
             tier === 'obsidian' ? 'Which emerging market offers best empire expansion?' : 
             'What sector will outperform in next quarter?'}
          </h4>
          
          <div className="space-y-3 mb-4">
            {[
              { option: tier === 'void' ? 'Parallel Reality Trading' : tier === 'obsidian' ? 'Asian Markets' : 'Technology', votes: 45 },
              { option: tier === 'void' ? 'Time-Space Arbitrage' : tier === 'obsidian' ? 'European Expansion' : 'Healthcare', votes: 32 },
              { option: tier === 'void' ? 'Consciousness Tokens' : tier === 'obsidian' ? 'African Infrastructure' : 'Energy', votes: 28 },
              { option: tier === 'void' ? 'Quantum Entanglement Assets' : tier === 'obsidian' ? 'Latin America' : 'Finance', votes: 15 }
            ].map((option, index) => {
              const percentage = (option.votes / 120) * 100;
              return (
                <motion.div
                  key={index}
                  className="cursor-pointer hover:bg-gray-600/50 rounded-lg p-3 transition-all"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm">{option.option}</span>
                    <span className="text-xs text-gray-400">{percentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2">
                    <motion.div
                      className="h-2 rounded-full"
                      style={{ backgroundColor: tierConfig[tier].color }}
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                    />
                  </div>
                </motion.div>
              );
            })}
          </div>

          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>120 anonymous votes • 2 days left</span>
            <div className="flex items-center space-x-2">
              <EyeOff className="w-4 h-4" />
              <span>Fully Anonymous</span>
            </div>
          </div>
        </div>

        <motion.button
          className="w-full py-3 border border-gray-600 hover:border-gray-500 rounded-xl transition-all"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Create Anonymous Poll
        </motion.button>
      </div>
    </div>
  );

  const renderPrivateMessages = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 rounded-xl p-6 border border-purple-500/30">
        <div className="flex items-start space-x-3">
          <Shield className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-semibold text-purple-400 mb-2">End-to-End Encrypted Messaging</h4>
            <p className="text-sm text-gray-300">
              Private conversations with other circle members using quantum-level encryption. 
              Messages are automatically purged after 30 days.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Conversations */}
      <div className="space-y-4">
        {[
          {
            with: tier === 'void' ? 'Ethereal_Being_9' : tier === 'obsidian' ? 'Diamond_Oracle_6' : 'Silver_Sage_11',
            lastMessage: tier === 'void' ? 'The quantum fluctuations you mentioned...' : tier === 'obsidian' ? 'That empire strategy discussion...' : 'The market analysis was brilliant...',
            timestamp: '1 hour ago',
            unread: 2,
            online: true
          },
          {
            with: tier === 'void' ? 'Quantum_Visionary_3' : tier === 'obsidian' ? 'Crystal_Mastermind_1' : 'Stream_Architect_8',
            lastMessage: tier === 'void' ? 'Interdimensional deal opportunity...' : tier === 'obsidian' ? 'Private equity syndication...' : 'Luxury service recommendation...',
            timestamp: '3 hours ago',
            unread: 0,
            online: false
          }
        ].map((conversation, index) => (
          <motion.div
            key={index}
            className="bg-gray-800/50 rounded-xl p-4 hover:bg-gray-700/50 transition-all cursor-pointer"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 bg-gradient-to-br from-gray-600 to-gray-800 rounded-full flex items-center justify-center">
                    <Shield className="w-5 h-5 text-gray-300" />
                  </div>
                  {conversation.online && (
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-gray-900" />
                  )}
                </div>
                <div>
                  <div className="font-medium">{conversation.with}</div>
                  <div className="text-sm text-gray-400 truncate max-w-xs">
                    {conversation.lastMessage}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">{conversation.timestamp}</div>
                {conversation.unread > 0 && (
                  <div className="w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center text-xs text-white mt-1 ml-auto">
                    {conversation.unread}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );

  const renderSelectedDiscussion = () => {
    if (!selectedDiscussion) return null;

    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        className="bg-gray-800/50 rounded-xl p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold">{selectedDiscussion.title}</h3>
            <div className="flex items-center space-x-3 text-sm text-gray-400 mt-1">
              <span>by {selectedDiscussion.initiator}</span>
              <div className="flex items-center space-x-1">
                <Users className="w-4 h-4" />
                <span>{selectedDiscussion.participants} participants</span>
              </div>
            </div>
          </div>
          <motion.button
            onClick={() => setSelectedDiscussion(null)}
            className="p-2 hover:bg-gray-700 rounded-lg transition-all"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            ×
          </motion.button>
        </div>

        {/* Messages Area */}
        <div className="h-64 bg-gray-700/30 rounded-xl p-4 mb-4 overflow-y-auto">
          <div className="space-y-4">
            {/* Sample messages */}
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Shield className="w-4 h-4 text-white" />
              </div>
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-medium">{selectedDiscussion.initiator}</span>
                  <span className="text-xs text-gray-500">2 hours ago</span>
                </div>
                <div className="text-sm text-gray-300">
                  {tier === 'void' 
                    ? "I've been analyzing quantum market fluctuations across seventeen parallel dimensions and noticed some fascinating patterns emerging..."
                    : tier === 'obsidian'
                    ? "The current geopolitical landscape presents unprecedented opportunities for empire expansion, particularly in emerging markets..."
                    : "Market volatility has created some interesting arbitrage opportunities. Here's my analysis of the current situation..."
                  }
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Message Input */}
        <div className="space-y-3">
          <div className="flex space-x-2">
            {(['general_discussion', 'market_insight', 'deal_opportunity', 'service_recommendation'] as const).map((type) => (
              <motion.button
                key={type}
                onClick={() => setMessageType(type)}
                className={`px-3 py-1 rounded-full text-xs transition-all ${
                  messageType === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {type.replace('_', ' ')}
              </motion.button>
            ))}
          </div>

          <div className="flex space-x-3">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your anonymous message..."
              className="flex-1 bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 focus:border-blue-500 focus:outline-none transition-all"
            />
            <motion.button
              className="p-3 bg-blue-600 hover:bg-blue-700 rounded-xl transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>

          <div className="flex items-center justify-between text-xs text-gray-400">
            <div className="flex items-center space-x-2">
              <Shield className="w-3 h-3" />
              <span>End-to-end encrypted • Auto-purge after 30 days</span>
            </div>
            <div className="flex items-center space-x-1">
              <span>Reputation required: 500+</span>
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{tierConfig[tier].name}</h1>
        <div className="flex items-center justify-between">
          <p className="text-gray-400">{tierConfig[tier].exclusivity}</p>
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4" style={{ color: tierConfig[tier].color }} />
              <span>{tierConfig[tier].memberCount}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-green-400" />
              <span>Quantum Anonymous</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-8 bg-gray-800/50 rounded-xl p-1">
        {[
          { id: 'discussions', name: 'Discussions', icon: MessageCircle },
          { id: 'deals', name: 'Deal Flow', icon: TrendingUp },
          { id: 'polls', name: 'Polls', icon: BarChart3 },
          { id: 'private', name: 'Private', icon: Lock }
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

      {/* Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'discussions' && !selectedDiscussion && renderDiscussions()}
              {activeTab === 'discussions' && selectedDiscussion && renderSelectedDiscussion()}
              {activeTab === 'deals' && renderDeals()}
              {activeTab === 'polls' && renderPolls()}
              {activeTab === 'private' && renderPrivateMessages()}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Circle Stats */}
          <div className="bg-gray-800/50 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Circle Activity</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Active Discussions</span>
                <span className="text-sm font-medium">12</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Messages Today</span>
                <span className="text-sm font-medium">156</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Deal Opportunities</span>
                <span className="text-sm font-medium">3</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Your Reputation</span>
                <span className="text-sm font-medium" style={{ color: tierConfig[tier].color }}>847</span>
              </div>
            </div>
          </div>

          {/* Privacy Features */}
          <div className="bg-gray-800/50 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span>Privacy Features</span>
            </h3>
            <div className="space-y-3 text-sm">
              {tierConfig[tier].features.map((feature, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: tierConfig[tier].color }} />
                  <span className="text-gray-300">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};