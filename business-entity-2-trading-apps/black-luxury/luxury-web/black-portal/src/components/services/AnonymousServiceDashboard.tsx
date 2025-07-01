'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  Eye, 
  EyeOff, 
  Users, 
  Plane, 
  Utensils, 
  Building, 
  Palette,
  AlertTriangle,
  Phone,
  Heart,
  Scale,
  DollarSign,
  Clock,
  Lock,
  Zap,
  Star
} from 'lucide-react';
import { anonymousServiceCoordinator } from '../../services/AnonymousServiceCoordinator';

interface AnonymousServiceDashboardProps {
  userId: string;
  tier: 'onyx' | 'obsidian' | 'void';
  anonymousId: string;
}

export const AnonymousServiceDashboard: React.FC<AnonymousServiceDashboardProps> = ({
  userId,
  tier,
  anonymousId
}) => {
  const [activeTab, setActiveTab] = useState<'concierge' | 'emergency' | 'social' | 'analytics'>('concierge');
  const [anonymityLevel, setAnonymityLevel] = useState<'full' | 'partial' | 'minimal'>('full');
  const [activeServices, setActiveServices] = useState<any[]>([]);
  const [socialCircle, setSocialCircle] = useState<any>(null);

  const tierConfig = {
    onyx: {
      name: 'Silver Stream Society',
      color: '#C0C0C0',
      anonymousPrefix: 'silver_stream',
      services: ['Premium Concierge', 'Emergency Response', 'Luxury Services', 'Social Circle'],
      anonymityFeatures: ['Device Encryption', 'Secure Communications', 'Identity Masking']
    },
    obsidian: {
      name: 'Crystal Empire Network',
      color: '#E5E4E2',
      anonymousPrefix: 'crystal_empire',
      services: ['Diamond Concierge', 'Priority Emergency', 'Empire Services', 'Elite Circle'],
      anonymityFeatures: ['Quantum Encryption', 'Zero-Knowledge Proofs', 'Advanced Masking', 'Anonymous Deals']
    },
    void: {
      name: 'Quantum Consciousness Collective',
      color: '#FFD700',
      anonymousPrefix: 'quantum_sage',
      services: ['Quantum Concierge', 'Reality Emergency', 'Cosmic Services', 'Consciousness Circle'],
      anonymityFeatures: ['Reality Distortion', 'Quantum Tunneling', 'Dimensional Privacy', 'Cosmic Anonymity']
    }
  };

  useEffect(() => {
    loadActiveServices();
    loadSocialCircle();
  }, []);

  const loadActiveServices = async () => {
    // Load user's active anonymous services
    setActiveServices([
      {
        id: 'service_1',
        type: 'concierge',
        category: 'Private Aviation',
        status: 'in_progress',
        anonymityLevel: 'full',
        provider: 'Anonymous Provider Alpha',
        startTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
        estimatedCompletion: new Date(Date.now() + 4 * 60 * 60 * 1000)
      }
    ]);
  };

  const loadSocialCircle = async () => {
    setSocialCircle({
      memberCount: tier === 'void' ? 8 : tier === 'obsidian' ? 23 : 67,
      activeDiscussions: 4,
      dealOpportunities: tier === 'void' ? 3 : tier === 'obsidian' ? 5 : 2,
      reputation: 847
    });
  };

  const renderAnonymityControls = () => (
    <div className="bg-gray-800/50 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center space-x-2">
          <Shield className="w-5 h-5" style={{ color: tierConfig[tier].color }} />
          <span>Anonymity Controls</span>
        </h3>
        <div className="flex items-center space-x-2">
          <Lock className="w-4 h-4 text-green-400" />
          <span className="text-sm text-green-400">Quantum Secure</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {['full', 'partial', 'minimal'].map((level) => (
          <motion.button
            key={level}
            onClick={() => setAnonymityLevel(level as any)}
            className={`p-3 rounded-lg border transition-all ${
              anonymityLevel === level
                ? 'border-blue-500 bg-blue-500/20'
                : 'border-gray-600 hover:border-gray-500'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center justify-center mb-2">
              {level === 'full' ? (
                <EyeOff className="w-6 h-6" />
              ) : level === 'partial' ? (
                <Eye className="w-6 h-6 opacity-50" />
              ) : (
                <Eye className="w-6 h-6" />
              )}
            </div>
            <div className="text-sm font-medium capitalize">{level} Anonymity</div>
            <div className="text-xs text-gray-400 mt-1">
              {level === 'full' && 'Complete identity protection'}
              {level === 'partial' && 'Service-required info only'}
              {level === 'minimal' && 'Name for delivery only'}
            </div>
          </motion.button>
        ))}
      </div>

      <div className="bg-gray-700/50 rounded-lg p-4">
        <h4 className="text-sm font-semibold mb-2">Your Anonymous Identity</h4>
        <div className="font-mono text-sm" style={{ color: tierConfig[tier].color }}>
          {anonymousId}
        </div>
        <div className="text-xs text-gray-400 mt-1">
          This identity is cryptographically verified but completely anonymous
        </div>
      </div>
    </div>
  );

  const renderConciergeServices = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Plane, name: 'Private Aviation', category: 'transport', description: 'Anonymous jet booking' },
          { icon: Utensils, name: 'Exclusive Dining', category: 'dining', description: 'Private chef & restaurants' },
          { icon: Building, name: 'Luxury Hospitality', category: 'hospitality', description: 'Anonymous hotel booking' },
          { icon: Palette, name: 'Art & Experiences', category: 'entertainment', description: 'Cultural experiences' }
        ].map((service, index) => (
          <motion.button
            key={service.name}
            className="p-6 bg-gray-800/50 rounded-xl hover:bg-gray-700/50 transition-all group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <service.icon 
              className="w-8 h-8 mb-3 group-hover:scale-110 transition-transform" 
              style={{ color: tierConfig[tier].color }} 
            />
            <h4 className="font-semibold mb-2">{service.name}</h4>
            <p className="text-sm text-gray-400">{service.description}</p>
            <div className="mt-3 flex items-center text-xs text-green-400">
              <Shield className="w-3 h-3 mr-1" />
              Full Anonymity
            </div>
          </motion.button>
        ))}
      </div>

      <div className="bg-gray-800/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">Active Anonymous Services</h3>
        {activeServices.length > 0 ? (
          <div className="space-y-4">
            {activeServices.map((service) => (
              <div key={service.id} className="bg-gray-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{service.category}</h4>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
                    <span className="text-sm text-yellow-400 capitalize">{service.status}</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm text-gray-400">
                  <div>
                    <span className="text-gray-500">Provider:</span> {service.provider}
                  </div>
                  <div>
                    <span className="text-gray-500">Anonymity:</span> {service.anonymityLevel}
                  </div>
                  <div>
                    <span className="text-gray-500">Started:</span> {service.startTime.toLocaleTimeString()}
                  </div>
                  <div>
                    <span className="text-gray-500">ETA:</span> {service.estimatedCompletion.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">
            <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No active services. All your requests remain completely anonymous.</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderEmergencyServices = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Heart, name: 'Medical Emergency', severity: 'critical', responseTime: tier === 'void' ? '<1 min' : tier === 'obsidian' ? '<3 min' : '<5 min' },
          { icon: Shield, name: 'Security Crisis', severity: 'high', responseTime: tier === 'void' ? '<2 min' : tier === 'obsidian' ? '<5 min' : '<8 min' },
          { icon: Scale, name: 'Legal Support', severity: 'medium', responseTime: tier === 'void' ? '<5 min' : tier === 'obsidian' ? '<10 min' : '<15 min' },
          { icon: DollarSign, name: 'Financial Crisis', severity: 'high', responseTime: tier === 'void' ? '<2 min' : tier === 'obsidian' ? '<5 min' : '<5 min' }
        ].map((emergency, index) => (
          <motion.button
            key={emergency.name}
            className="p-6 bg-red-900/20 border border-red-500/30 rounded-xl hover:bg-red-800/30 transition-all group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <emergency.icon className="w-8 h-8 mb-3 text-red-400 group-hover:scale-110 transition-transform" />
            <h4 className="font-semibold mb-2">{emergency.name}</h4>
            <div className="text-sm text-gray-400 mb-2">Response: {emergency.responseTime}</div>
            <div className="flex items-center text-xs text-green-400">
              <Shield className="w-3 h-3 mr-1" />
              Anonymous Until Required
            </div>
          </motion.button>
        ))}
      </div>

      <div className="bg-gradient-to-r from-red-900/20 to-orange-900/20 rounded-xl p-6 border border-red-500/30">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-semibold text-red-400 mb-2">Emergency Identity Reveal Protocol</h4>
            <p className="text-sm text-gray-300 mb-3">
              In life-threatening emergencies, your identity may be progressively revealed to emergency responders:
            </p>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• <strong>Step 1:</strong> Location only (immediate)</li>
              <li>• <strong>Step 2:</strong> Medical information if needed</li>
              <li>• <strong>Step 3:</strong> Emergency contacts</li>
              <li>• <strong>Step 4:</strong> Full identity only if legally required</li>
            </ul>
            <div className="mt-3 text-xs text-green-400">
              <Shield className="w-3 h-3 mr-1 inline" />
              All data is purged after emergency resolution
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSocialCircle = () => (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{tierConfig[tier].name}</h3>
          <div className="flex items-center space-x-2">
            <Users className="w-5 h-5" style={{ color: tierConfig[tier].color }} />
            <span className="text-sm">{socialCircle?.memberCount} Members</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold" style={{ color: tierConfig[tier].color }}>
              {socialCircle?.activeDiscussions}
            </div>
            <div className="text-sm text-gray-400">Active Discussions</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold" style={{ color: tierConfig[tier].color }}>
              {socialCircle?.dealOpportunities}
            </div>
            <div className="text-sm text-gray-400">Deal Opportunities</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold" style={{ color: tierConfig[tier].color }}>
              {socialCircle?.reputation}
            </div>
            <div className="text-sm text-gray-400">Your Reputation</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800/50 rounded-xl p-6">
          <h4 className="font-semibold mb-4 flex items-center space-x-2">
            <Users className="w-5 h-5" />
            <span>Anonymous Networking</span>
          </h4>
          <div className="space-y-3">
            {[
              { title: 'Market Philosophy Discussion', participants: 5, lastActivity: '2 hours ago' },
              { title: 'Global Investment Opportunities', participants: 8, lastActivity: '4 hours ago' },
              { title: 'Luxury Service Recommendations', participants: 12, lastActivity: '6 hours ago' }
            ].map((discussion, index) => (
              <div key={index} className="bg-gray-700/50 rounded-lg p-3">
                <div className="font-medium text-sm">{discussion.title}</div>
                <div className="text-xs text-gray-400 mt-1">
                  {discussion.participants} participants • {discussion.lastActivity}
                </div>
              </div>
            ))}
          </div>
          <motion.button
            className="w-full mt-4 py-2 rounded-lg border border-gray-600 hover:border-gray-500 transition-all"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Join Anonymous Discussion
          </motion.button>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6">
          <h4 className="font-semibold mb-4 flex items-center space-x-2">
            <DollarSign className="w-5 h-5" />
            <span>Anonymous Deal Flow</span>
          </h4>
          <div className="space-y-3">
            {[
              { type: 'Private Equity', sector: 'Technology', size: '₹500+ Cr', stage: 'Due Diligence' },
              { type: 'Real Estate', sector: 'Commercial', size: '₹200+ Cr', stage: 'Negotiation' },
              { type: 'Art Acquisition', sector: 'Contemporary', size: '₹50+ Cr', stage: 'Available' }
            ].map((deal, index) => (
              <div key={index} className="bg-gray-700/50 rounded-lg p-3">
                <div className="flex justify-between items-start mb-1">
                  <div className="font-medium text-sm">{deal.type}</div>
                  <div className="text-xs text-green-400">{deal.stage}</div>
                </div>
                <div className="text-xs text-gray-400">
                  {deal.sector} • {deal.size}
                </div>
              </div>
            ))}
          </div>
          <motion.button
            className="w-full mt-4 py-2 rounded-lg border border-gray-600 hover:border-gray-500 transition-all"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Browse Anonymous Deals
          </motion.button>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-xl p-6 border border-blue-500/30">
        <div className="flex items-start space-x-3">
          <Shield className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-semibold text-blue-400 mb-2">Zero-Knowledge Social Circle</h4>
            <p className="text-sm text-gray-300 mb-3">
              Connect with peers in your wealth tier while maintaining complete anonymity. 
              Share insights, discover opportunities, and build relationships without revealing your identity.
            </p>
            <div className="text-xs text-gray-400">
              <strong>Privacy Features:</strong> Anonymous messaging • Encrypted communications • 
              Reputation-based trust • Zero identity correlation • Quantum-secure for Void tier
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800/50 rounded-xl p-6">
          <h4 className="font-semibold mb-4 flex items-center space-x-2">
            <Clock className="w-5 h-5" />
            <span>Service Usage</span>
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Concierge Requests</span>
              <span className="text-sm font-medium">12 this month</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Emergency Activations</span>
              <span className="text-sm font-medium">0 this month</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Social Interactions</span>
              <span className="text-sm font-medium">47 this week</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6">
          <h4 className="font-semibold mb-4 flex items-center space-x-2">
            <Shield className="w-5 h-5" />
            <span>Privacy Metrics</span>
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Anonymity Level</span>
              <span className="text-sm font-medium text-green-400">100%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Identity Reveals</span>
              <span className="text-sm font-medium">0 lifetime</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Data Retention</span>
              <span className="text-sm font-medium text-green-400">Zero</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6">
          <h4 className="font-semibold mb-4 flex items-center space-x-2">
            <Star className="w-5 h-5" />
            <span>Service Quality</span>
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Average Rating</span>
              <span className="text-sm font-medium">4.9/5.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Response Time</span>
              <span className="text-sm font-medium">
                {tier === 'void' ? '<2 min' : tier === 'obsidian' ? '<5 min' : '<10 min'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Success Rate</span>
              <span className="text-sm font-medium text-green-400">100%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800/50 rounded-xl p-6">
        <h4 className="font-semibold mb-4">Anonymity Breakdown by Service</h4>
        <div className="space-y-4">
          {[
            { service: 'Concierge Services', anonymity: 95, identityRequired: 5 },
            { service: 'Emergency Response', anonymity: 70, identityRequired: 30 },
            { service: 'Social Circle', anonymity: 100, identityRequired: 0 },
            { service: 'Deal Flow', anonymity: 90, identityRequired: 10 }
          ].map((item, index) => (
            <div key={index}>
              <div className="flex justify-between text-sm mb-2">
                <span>{item.service}</span>
                <span>{item.anonymity}% Anonymous</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-400 h-2 rounded-full"
                  style={{ width: `${item.anonymity}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Anonymous Services Dashboard</h1>
        <p className="text-gray-400">
          Access luxury services while maintaining complete anonymity and privacy
        </p>
      </div>

      {/* Anonymity Controls */}
      {renderAnonymityControls()}

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-8 bg-gray-800/50 rounded-xl p-1">
        {[
          { id: 'concierge', name: 'Concierge', icon: Plane },
          { id: 'emergency', name: 'Emergency', icon: AlertTriangle },
          { id: 'social', name: 'Social Circle', icon: Users },
          { id: 'analytics', name: 'Analytics', icon: Zap }
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

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'concierge' && renderConciergeServices()}
          {activeTab === 'emergency' && renderEmergencyServices()}
          {activeTab === 'social' && renderSocialCircle()}
          {activeTab === 'analytics' && renderAnalytics()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};