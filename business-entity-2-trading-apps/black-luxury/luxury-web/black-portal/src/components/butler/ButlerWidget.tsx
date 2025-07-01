'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ButlerAI } from '@/services/ButlerAI';
import { ButlerMessage, ButlerNotification, MarketInsight } from '@/types/butler';
import { BlackUser } from '@/types/portal';
import { useLuxuryEffects } from '@/hooks/useLuxuryEffects';

interface ButlerWidgetProps {
  user: BlackUser;
  onOpenChat: () => void;
  isMinimized?: boolean;
}

export function ButlerWidget({ user, onOpenChat, isMinimized = false }: ButlerWidgetProps) {
  const [butler, setButler] = useState<ButlerAI | null>(null);
  const [notifications, setNotifications] = useState<ButlerNotification[]>([]);
  const [insights, setInsights] = useState<MarketInsight[]>([]);
  const [isActive, setIsActive] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [unreadCount, setUnreadCount] = useState(0);

  const { luxuryInteraction, getTierColor } = useLuxuryEffects(user.tier);

  // Initialize Butler AI
  useEffect(() => {
    if (user && !butler) {
      const context = {
        userId: user.userId,
        sessionId: `widget_${Date.now()}`,
        conversationHistory: [],
        userPreferences: {
          communicationStyle: 'brief' as const,
          alertFrequency: 'normal' as const,
          autoExecuteLimit: 100000,
          preferredLanguage: 'en',
          timeZone: 'Asia/Kolkata'
        },
        portfolioContext: {
          totalValue: user.portfolioValue,
          riskProfile: 'moderate' as const,
          activePositions: 25,
          todaysPnL: (Math.random() - 0.5) * user.portfolioValue * 0.02
        }
      };

      const butlerInstance = new ButlerAI(user, context);
      setButler(butlerInstance);
    }
  }, [user, butler]);

  // Update time every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  // Generate periodic insights and notifications
  useEffect(() => {
    if (!butler) return;

    const generateInsights = async () => {
      try {
        const newInsights = await butler.generateMarketInsights();
        setInsights(prev => [...newInsights, ...prev].slice(0, 5)); // Keep latest 5
        
        // Create notification for high-relevance insights
        newInsights.forEach(insight => {
          if (insight.relevanceScore > 0.8) {
            const notification: ButlerNotification = {
              id: `insight_${insight.id}`,
              type: 'market_alert',
              title: 'High-Impact Market Insight',
              message: insight.title,
              actionRequired: insight.relevanceScore > 0.9,
              expiresAt: new Date(Date.now() + 3600000), // 1 hour
              metadata: { insightId: insight.id }
            };
            setNotifications(prev => [notification, ...prev].slice(0, 10));
            setUnreadCount(prev => prev + 1);
          }
        });
      } catch (error) {
        console.error('Error generating insights:', error);
      }
    };

    // Generate insights every 5 minutes
    const interval = setInterval(generateInsights, 300000);
    generateInsights(); // Generate immediately

    return () => clearInterval(interval);
  }, [butler]);

  // Generate random notifications for demo
  useEffect(() => {
    const generateNotification = () => {
      const types: Array<ButlerNotification['type']> = [
        'portfolio_update',
        'service_reminder',
        'luxury_opportunity'
      ];
      
      const messages = {
        portfolio_update: [
          'Your portfolio has gained 2.3% in the last hour',
          'New position automatically optimized',
          'Risk parameters adjusted for market conditions'
        ],
        service_reminder: [
          'Your concierge appointment is in 30 minutes',
          'Private jet maintenance scheduled for tomorrow',
          'Quarterly wealth review meeting available'
        ],
        luxury_opportunity: [
          'Exclusive art auction opportunity detected',
          'Limited edition luxury watch available',
          'Private island investment opportunity'
        ]
      };

      const type = types[Math.floor(Math.random() * types.length)];
      const typeMessages = messages[type];
      const message = typeMessages[Math.floor(Math.random() * typeMessages.length)];

      const notification: ButlerNotification = {
        id: `notif_${Date.now()}_${Math.random()}`,
        type,
        title: type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        message,
        actionRequired: Math.random() > 0.7,
        expiresAt: new Date(Date.now() + 7200000), // 2 hours
        metadata: {}
      };

      setNotifications(prev => [notification, ...prev].slice(0, 10));
      setUnreadCount(prev => prev + 1);
    };

    // Generate notification every 30 seconds to 2 minutes
    const interval = setInterval(generateNotification, 30000 + Math.random() * 90000);
    
    return () => clearInterval(interval);
  }, []);

  const getTierConfig = () => {
    switch (user.tier) {
      case 'void':
        return {
          color: '#FFD700',
          accent: '#FFF700',
          avatar: '⚛️',
          statusText: 'Quantum Active',
          backgroundGlow: 'shadow-yellow-500/20'
        };
      case 'obsidian':
        return {
          color: '#E5E4E2',
          accent: '#F5F5F5',
          avatar: '💎',
          statusText: 'Crystal Clear',
          backgroundGlow: 'shadow-gray-300/20'
        };
      case 'onyx':
        return {
          color: '#C0C0C0',
          accent: '#D0D0D0',
          avatar: '🤖',
          statusText: 'Silver Stream',
          backgroundGlow: 'shadow-gray-400/20'
        };
      default:
        return {
          color: '#C0C0C0',
          accent: '#D0D0D0',
          avatar: '🤖',
          statusText: 'Active',
          backgroundGlow: 'shadow-gray-400/20'
        };
    }
  };

  const tierConfig = getTierConfig();

  const handleWidgetClick = () => {
    luxuryInteraction();
    onOpenChat();
    setUnreadCount(0); // Clear unread count when opening chat
  };

  const markNotificationRead = (notificationId: string) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  if (isMinimized) {
    return (
      <motion.div
        className={`fixed bottom-6 right-6 z-40 w-16 h-16 rounded-full bg-gray-900 border-2 cursor-pointer ${tierConfig.backgroundGlow} shadow-2xl flex items-center justify-center`}
        style={{ borderColor: tierConfig.color }}
        onClick={handleWidgetClick}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        animate={{ 
          boxShadow: `0 0 20px ${tierConfig.color}40`,
        }}
        transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
      >
        <div className="text-2xl">{tierConfig.avatar}</div>
        
        {unreadCount > 0 && (
          <motion.div
            className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 500 }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </motion.div>
        )}
      </motion.div>
    );
  }

  return (
    <motion.div
      className="bg-gray-900 border border-gray-700 rounded-lg p-6 h-full flex flex-col"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <motion.div
            className="text-3xl"
            animate={{ 
              scale: isActive ? [1, 1.1, 1] : 1,
              rotate: user.tier === 'void' ? [0, 360] : 0
            }}
            transition={{ 
              duration: user.tier === 'void' ? 10 : 2, 
              repeat: isActive ? Infinity : 0 
            }}
          >
            {tierConfig.avatar}
          </motion.div>
          <div>
            <h3 className="font-luxury-serif text-lg" style={{ color: tierConfig.color }}>
              {user.dedicatedButler}
            </h3>
            <p className="text-sm text-gray-400 font-luxury-sans">
              {tierConfig.statusText}
            </p>
          </div>
        </div>

        <motion.button
          onClick={handleWidgetClick}
          className="px-4 py-2 border rounded-lg font-luxury-sans text-sm hover:bg-gray-800 transition-colors"
          style={{ borderColor: tierConfig.color, color: tierConfig.color }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Open Chat
        </motion.button>
      </div>

      {/* Status Indicator */}
      <div className="flex items-center space-x-2 mb-4">
        <motion.div
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: tierConfig.color }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <span className="text-sm text-gray-400 font-luxury-sans">
          Last active: {currentTime.toLocaleTimeString()}
        </span>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-3 bg-gray-800/50 rounded-lg">
          <div className="text-lg font-luxury-serif" style={{ color: tierConfig.color }}>
            {insights.length}
          </div>
          <div className="text-xs text-gray-400 font-luxury-sans">Active Insights</div>
        </div>
        <div className="text-center p-3 bg-gray-800/50 rounded-lg">
          <div className="text-lg font-luxury-serif" style={{ color: tierConfig.color }}>
            {notifications.length}
          </div>
          <div className="text-xs text-gray-400 font-luxury-sans">Notifications</div>
        </div>
      </div>

      {/* Recent Notifications */}
      <div className="flex-1 overflow-hidden">
        <h4 className="text-sm font-luxury-sans text-gray-300 mb-3">Recent Activity</h4>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          <AnimatePresence>
            {notifications.slice(0, 5).map((notification) => (
              <motion.div
                key={notification.id}
                className="p-3 bg-gray-800/30 rounded-lg border border-gray-700/50"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="text-xs font-luxury-sans text-gray-300 mb-1">
                      {notification.title}
                    </p>
                    <p className="text-xs text-gray-400 font-luxury-sans leading-relaxed">
                      {notification.message}
                    </p>
                    {notification.actionRequired && (
                      <span className="inline-block mt-1 px-2 py-1 bg-orange-500/20 text-orange-400 text-xs rounded">
                        Action Required
                      </span>
                    )}
                  </div>
                  <motion.button
                    onClick={() => markNotificationRead(notification.id)}
                    className="ml-2 text-gray-500 hover:text-gray-300 transition-colors"
                    whileHover={{ scale: 1.2 }}
                    whileTap={{ scale: 0.8 }}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </motion.button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="grid grid-cols-2 gap-2">
          <motion.button
            className="px-3 py-2 bg-gray-800 text-gray-300 rounded text-xs font-luxury-sans hover:bg-gray-700 transition-colors"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              luxuryInteraction();
              // Generate market insight
              const insight: MarketInsight = {
                id: `quick_${Date.now()}`,
                title: 'Quick Market Analysis',
                summary: 'Rapid market assessment requested',
                content: 'Market conditions analyzed...',
                type: 'analysis',
                relevanceScore: 0.8,
                timeframe: 'immediate',
                confidenceLevel: 0.85,
                sources: ['Quick Analysis Engine'],
                actionableItems: ['Review positions'],
                estimatedImpact: { portfolioPercentage: 2.1, riskAdjustedReturn: 5.3 }
              };
              setInsights(prev => [insight, ...prev].slice(0, 5));
            }}
          >
            Quick Analysis
          </motion.button>
          
          <motion.button
            className="px-3 py-2 bg-gray-800 text-gray-300 rounded text-xs font-luxury-sans hover:bg-gray-700 transition-colors"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleWidgetClick}
          >
            Ask Butler
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}