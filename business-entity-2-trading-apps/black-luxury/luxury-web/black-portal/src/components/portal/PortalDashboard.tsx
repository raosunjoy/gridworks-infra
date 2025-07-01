'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BlackUser } from '@/types/portal';

interface PortalDashboardProps {
  user: BlackUser;
  onLogout: () => void;
}

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

interface ButlerMessage {
  id: string;
  message: string;
  timestamp: Date;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

export function PortalDashboard({ user, onLogout }: PortalDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'trading' | 'butler' | 'settings'>('overview');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [butlerMessages, setButlerMessages] = useState<ButlerMessage[]>([]);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Tier-specific configurations
  const getTierConfig = () => {
    switch (user.tier) {
      case 'void':
        return {
          color: '#FFD700',
          accent: '#FFF700',
          background: 'bg-gradient-to-br from-yellow-900/20 via-gray-900 to-black',
          cardBg: 'bg-yellow-900/10 border-yellow-500/30',
          title: 'VOID COMMAND CENTER',
          greeting: 'Reality Architect',
          features: ['Quantum Trading', 'Reality Distortion', 'Time Manipulation', 'Cosmic Markets']
        };
      case 'obsidian':
        return {
          color: '#E5E4E2',
          accent: '#F5F5F5',
          background: 'bg-gradient-to-br from-gray-700/20 via-gray-900 to-black',
          cardBg: 'bg-gray-700/10 border-gray-400/30',
          title: 'OBSIDIAN CONTROL ROOM',
          greeting: 'Empire Builder',
          features: ['Diamond Analytics', 'Enterprise Tools', 'Private Banking', 'Global Markets']
        };
      case 'onyx':
        return {
          color: '#C0C0C0',
          accent: '#D0D0D0',
          background: 'bg-gradient-to-br from-gray-600/20 via-gray-900 to-black',
          cardBg: 'bg-gray-600/10 border-gray-500/30',
          title: 'ONYX TRADING SUITE',
          greeting: 'Success Navigator',
          features: ['Premium AI', 'Analytics Suite', 'Priority Support', 'Market Insights']
        };
      default:
        return getTierConfig();
    }
  };

  const tierConfig = getTierConfig();

  // Initialize dashboard data
  useEffect(() => {
    generateMarketData();
    generateButlerMessages();
    
    // Update time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    // Update market data every 5 seconds
    const marketInterval = setInterval(() => {
      updateMarketData();
    }, 5000);

    return () => {
      clearInterval(timeInterval);
      clearInterval(marketInterval);
    };
  }, []);

  const generateMarketData = () => {
    const symbols = user.tier === 'void' 
      ? ['QUANTUM-X', 'REALITY-0', 'TIME-∞', 'VOID-Ω', 'COSMOS-7']
      : user.tier === 'obsidian'
      ? ['DIAMOND-D', 'CRYSTAL-C', 'PLATINUM-P', 'EMPIRE-E', 'OBSIDIAN-O']
      : ['ONYX-O', 'SILVER-S', 'PREMIUM-P', 'ELITE-E', 'LUXURY-L'];

    const data: MarketData[] = symbols.map(symbol => ({
      symbol,
      price: Math.random() * 10000 + 1000,
      change: (Math.random() - 0.5) * 200,
      changePercent: (Math.random() - 0.5) * 10
    }));

    setMarketData(data);
  };

  const updateMarketData = () => {
    setMarketData(prev => prev.map(item => ({
      ...item,
      price: item.price + (Math.random() - 0.5) * 50,
      change: (Math.random() - 0.5) * 200,
      changePercent: (Math.random() - 0.5) * 10
    })));
  };

  const generateButlerMessages = () => {
    const messages: ButlerMessage[] = [
      {
        id: '1',
        message: `Good ${getTimeOfDay()}, ${tierConfig.greeting}. Your portfolio has grown 12.7% overnight.`,
        timestamp: new Date(Date.now() - 300000),
        priority: 'medium'
      },
      {
        id: '2',
        message: 'Quantum algorithms detected unusual market patterns. Initiating protective protocols.',
        timestamp: new Date(Date.now() - 600000),
        priority: 'high'
      },
      {
        id: '3',
        message: 'Your private banking session is ready. Shall I connect you with your relationship manager?',
        timestamp: new Date(Date.now() - 900000),
        priority: 'low'
      }
    ];

    setButlerMessages(messages);
  };

  const getTimeOfDay = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'morning';
    if (hour < 17) return 'afternoon';
    return 'evening';
  };

  const formatCurrency = (value: number): string => {
    if (Math.abs(value) >= 1000) {
      return `₹${(value / 1000).toFixed(2)}K`;
    }
    return `₹${value.toFixed(2)}`;
  };

  const formatPortfolio = (value: number): string => {
    if (value >= 1000) {
      return `₹${(value / 1000).toFixed(1)}K Cr`;
    }
    return `₹${value.toFixed(1)} Cr`;
  };

  const NavButton = ({ tab, children }: { tab: typeof activeTab, children: React.ReactNode }) => (
    <motion.button
      onClick={() => setActiveTab(tab)}
      className={`px-6 py-3 rounded-lg font-luxury-sans tracking-wide transition-all duration-300 ${
        activeTab === tab 
          ? `text-black shadow-lg` 
          : 'text-gray-400 hover:text-white'
      }`}
      style={{ 
        backgroundColor: activeTab === tab ? tierConfig.color : 'transparent',
        borderColor: tierConfig.color
      }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {children}
    </motion.button>
  );

  return (
    <motion.div
      className={`min-h-screen ${tierConfig.background} text-white`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      {/* Header */}
      <motion.header
        className="border-b border-gray-800 p-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-luxury-serif tracking-wider" style={{ color: tierConfig.color }}>
              {tierConfig.title}
            </h1>
            <p className="text-gray-400 font-luxury-sans mt-1">
              {currentTime.toLocaleString('en-IN', { 
                timeZone: 'Asia/Kolkata',
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
              })}
            </p>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="text-right">
              <p className="text-sm text-gray-400">Welcome back,</p>
              <p className="text-lg font-luxury-sans" style={{ color: tierConfig.color }}>
                {tierConfig.greeting}
              </p>
            </div>
            
            <motion.button
              onClick={onLogout}
              className="px-4 py-2 border border-gray-600 text-gray-400 rounded-lg hover:border-gray-500 hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Logout
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Navigation */}
      <motion.nav
        className="p-6 border-b border-gray-800"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex space-x-4">
          <NavButton tab="overview">OVERVIEW</NavButton>
          <NavButton tab="trading">TRADING</NavButton>
          <NavButton tab="butler">BUTLER</NavButton>
          <NavButton tab="settings">SETTINGS</NavButton>
        </div>
      </motion.nav>

      {/* Main Content */}
      <main className="p-6">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              {/* Portfolio Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className={`p-6 rounded-lg border ${tierConfig.cardBg}`}>
                  <h3 className="text-lg font-luxury-sans text-gray-300 mb-2">Portfolio Value</h3>
                  <p className="text-3xl font-luxury-serif" style={{ color: tierConfig.color }}>
                    {formatPortfolio(user.portfolioValue)}
                  </p>
                  <p className="text-sm text-green-400 mt-1">+12.7% (24h)</p>
                </div>
                
                <div className={`p-6 rounded-lg border ${tierConfig.cardBg}`}>
                  <h3 className="text-lg font-luxury-sans text-gray-300 mb-2">Active Trades</h3>
                  <p className="text-3xl font-luxury-serif" style={{ color: tierConfig.color }}>
                    {Math.floor(Math.random() * 50) + 10}
                  </p>
                  <p className="text-sm text-blue-400 mt-1">Auto-managed by {user.dedicatedButler}</p>
                </div>
                
                <div className={`p-6 rounded-lg border ${tierConfig.cardBg}`}>
                  <h3 className="text-lg font-luxury-sans text-gray-300 mb-2">Security Level</h3>
                  <p className="text-3xl font-luxury-serif" style={{ color: tierConfig.color }}>
                    {user.securityLevel}
                  </p>
                  <p className="text-sm text-green-400 mt-1">All systems secure</p>
                </div>
              </div>

              {/* Market Data */}
              <div className={`p-6 rounded-lg border ${tierConfig.cardBg}`}>
                <h3 className="text-xl font-luxury-sans mb-4" style={{ color: tierConfig.color }}>
                  {user.tier === 'void' ? 'Quantum Markets' : 
                   user.tier === 'obsidian' ? 'Global Markets' : 'Premium Markets'}
                </h3>
                <div className="space-y-3">
                  {marketData.map((item, index) => (
                    <motion.div
                      key={item.symbol}
                      className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <span className="font-luxury-mono text-white">{item.symbol}</span>
                      <div className="text-right">
                        <div className="font-luxury-mono text-white">
                          {formatCurrency(item.price)}
                        </div>
                        <div className={`text-sm ${item.changePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {item.changePercent >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'trading' && (
            <motion.div
              key="trading"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <div className="text-center py-20">
                <h2 className="text-3xl font-luxury-serif mb-4" style={{ color: tierConfig.color }}>
                  Advanced Trading Interface
                </h2>
                <p className="text-gray-400 font-luxury-sans mb-8">
                  Your tier-specific trading tools are being prepared...
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                  {tierConfig.features.map((feature, index) => (
                    <div key={index} className={`p-6 rounded-lg border ${tierConfig.cardBg}`}>
                      <h3 className="text-lg font-luxury-sans text-white mb-2">{feature}</h3>
                      <p className="text-gray-400 text-sm">Coming soon in your personalized interface</p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'butler' && (
            <motion.div
              key="butler"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              <div className={`p-6 rounded-lg border ${tierConfig.cardBg}`}>
                <h3 className="text-xl font-luxury-sans mb-4" style={{ color: tierConfig.color }}>
                  {user.dedicatedButler} - Your AI Butler
                </h3>
                
                <div className="space-y-4">
                  {butlerMessages.map((message) => (
                    <motion.div
                      key={message.id}
                      className="p-4 bg-gray-800/50 rounded-lg"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          message.priority === 'urgent' ? 'bg-red-500 text-white' :
                          message.priority === 'high' ? 'bg-orange-500 text-white' :
                          message.priority === 'medium' ? 'bg-blue-500 text-white' :
                          'bg-gray-500 text-white'
                        }`}>
                          {message.priority.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-gray-300 font-luxury-sans">{message.message}</p>
                    </motion.div>
                  ))}
                </div>
                
                <div className="mt-6 p-4 border border-gray-700 rounded-lg">
                  <input
                    type="text"
                    placeholder={`Ask ${user.dedicatedButler} anything...`}
                    className="w-full bg-transparent text-white placeholder-gray-500 outline-none font-luxury-sans"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'settings' && (
            <motion.div
              key="settings"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              <div className={`p-6 rounded-lg border ${tierConfig.cardBg}`}>
                <h3 className="text-xl font-luxury-sans mb-6" style={{ color: tierConfig.color }}>
                  Account Settings
                </h3>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-gray-300 font-luxury-sans mb-2">User ID</label>
                    <div className="text-gray-500 font-luxury-mono">{user.userId}</div>
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 font-luxury-sans mb-2">Tier</label>
                    <div style={{ color: tierConfig.color }} className="font-luxury-serif text-lg">
                      {user.tier.toUpperCase()}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 font-luxury-sans mb-2">Joined</label>
                    <div className="text-gray-500">{user.joinedAt.toLocaleDateString()}</div>
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 font-luxury-sans mb-2">Security Level</label>
                    <div className="text-green-400">{user.securityLevel}</div>
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 font-luxury-sans mb-2">Privileges</label>
                    <div className="flex flex-wrap gap-2">
                      {user.privileges.map((privilege) => (
                        <span
                          key={privilege}
                          className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-sm font-luxury-sans"
                        >
                          {privilege.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </motion.div>
  );
}