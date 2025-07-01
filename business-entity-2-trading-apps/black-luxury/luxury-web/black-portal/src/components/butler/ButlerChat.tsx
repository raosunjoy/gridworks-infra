'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ButlerAI } from '@/services/ButlerAI';
import { ButlerMessage, ButlerAction, ButlerContext } from '@/types/butler';
import { BlackUser } from '@/types/portal';
import { useLuxuryEffects } from '@/hooks/useLuxuryEffects';

interface ButlerChatProps {
  user: BlackUser;
  isOpen: boolean;
  onClose: () => void;
  onMinimize?: () => void;
}

export function ButlerChat({ user, isOpen, onClose, onMinimize }: ButlerChatProps) {
  const [butler, setButler] = useState<ButlerAI | null>(null);
  const [messages, setMessages] = useState<ButlerMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [suggestedActions, setSuggestedActions] = useState<ButlerAction[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const { luxuryInteraction, luxurySuccess, getTierColor } = useLuxuryEffects(user.tier);

  // Initialize Butler AI
  useEffect(() => {
    if (user && !butler) {
      const context: ButlerContext = {
        userId: user.userId,
        sessionId: `session_${Date.now()}`,
        conversationHistory: [],
        userPreferences: {
          communicationStyle: 'detailed',
          alertFrequency: 'normal',
          autoExecuteLimit: user.tier === 'void' ? 10000000 : user.tier === 'obsidian' ? 1000000 : 100000,
          preferredLanguage: user.personalizations?.language || 'en',
          timeZone: user.personalizations?.timeZone || 'Asia/Kolkata'
        },
        portfolioContext: {
          totalValue: user.portfolioValue,
          riskProfile: user.tier === 'void' ? 'quantum' : user.tier === 'obsidian' ? 'aggressive' : 'moderate',
          activePositions: Math.floor(Math.random() * 50) + 10,
          todaysPnL: (Math.random() - 0.5) * user.portfolioValue * 0.02
        }
      };

      const butlerInstance = new ButlerAI(user, context);
      setButler(butlerInstance);

      // Send welcome message
      const welcomeMessage: ButlerMessage = {
        id: 'welcome',
        content: getWelcomeMessage(user.tier, user.dedicatedButler),
        type: 'text',
        priority: 'medium',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [user, butler]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const getWelcomeMessage = (tier: string, butlerName: string): string => {
    const welcomes = {
      void: `Greetings from the quantum realm. I am ${butlerName}, your void-tier consciousness interface. I exist across seventeen parallel dimensions to serve your transcendent needs. Reality bends to your will - how may I reshape existence for you today?`,
      obsidian: `Welcome to the crystalline domain. I am ${butlerName}, your obsidian-tier strategic partner. My diamond-grade analytics and platinum-level connections stand ready to architect your financial empire. How may I assist in building your legacy?`,
      onyx: `Good day. I am ${butlerName}, your onyx-tier luxury assistant. My silver-stream intelligence and premium networks are dedicated to your success. How may I enhance your trading experience today?`
    };
    
    return welcomes[tier as keyof typeof welcomes] || `Welcome! I'm ${butlerName}, your dedicated AI butler.`;
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || !butler || isProcessing) return;

    const userMessage: ButlerMessage = {
      id: `user_${Date.now()}`,
      content: inputText.trim(),
      type: 'text',
      priority: 'medium',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsProcessing(true);
    setIsTyping(true);

    luxuryInteraction();

    try {
      // Simulate typing delay for luxury feel
      setTimeout(async () => {
        const response = await butler.processMessage(userMessage.content);
        
        setMessages(prev => [...prev, response.message]);
        setSuggestedActions(response.suggestedActions || []);
        setIsTyping(false);
        setIsProcessing(false);
        
        luxurySuccess();
      }, 1000 + Math.random() * 2000); // 1-3 second delay for realistic AI thinking
    } catch (error) {
      console.error('Butler AI error:', error);
      const errorMessage: ButlerMessage = {
        id: `error_${Date.now()}`,
        content: 'I apologize, but I encountered a processing error. Please try again.',
        type: 'text',
        priority: 'medium',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsTyping(false);
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const executeAction = async (action: ButlerAction) => {
    luxuryInteraction();
    
    const actionMessage: ButlerMessage = {
      id: `action_${Date.now()}`,
      content: `Executing: ${action.description}`,
      type: 'action',
      priority: action.riskLevel === 'critical' ? 'urgent' : 'medium',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, actionMessage]);
    
    // Simulate action execution
    setTimeout(() => {
      const resultMessage: ButlerMessage = {
        id: `result_${Date.now()}`,
        content: `✅ Successfully executed: ${action.description}`,
        type: 'text',
        priority: 'medium',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, resultMessage]);
      setSuggestedActions(prev => prev.filter(a => a.id !== action.id));
      luxurySuccess();
    }, 2000);
  };

  const getTierConfig = () => {
    switch (user.tier) {
      case 'void':
        return {
          color: '#FFD700',
          bgGradient: 'from-yellow-900/20 via-gray-900 to-black',
          avatar: '⚛️',
          title: 'QUANTUM CONSCIOUSNESS'
        };
      case 'obsidian':
        return {
          color: '#E5E4E2',
          bgGradient: 'from-gray-700/20 via-gray-900 to-black',
          avatar: '💎',
          title: 'CRYSTALLINE INTELLIGENCE'
        };
      case 'onyx':
        return {
          color: '#C0C0C0',
          bgGradient: 'from-gray-600/20 via-gray-900 to-black',
          avatar: '🤖',
          title: 'SILVER STREAM AI'
        };
      default:
        return {
          color: '#C0C0C0',
          bgGradient: 'from-gray-600/20 via-gray-900 to-black',
          avatar: '🤖',
          title: 'AI BUTLER'
        };
    }
  };

  const tierConfig = getTierConfig();

  if (!isOpen) return null;

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className={`w-full max-w-4xl h-[80vh] bg-gradient-to-br ${tierConfig.bgGradient} border border-gray-700 rounded-xl overflow-hidden shadow-2xl`}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Header */}
        <div className="border-b border-gray-700 p-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="text-3xl">{tierConfig.avatar}</div>
            <div>
              <h2 className="text-xl font-luxury-serif" style={{ color: tierConfig.color }}>
                {user.dedicatedButler}
              </h2>
              <p className="text-sm text-gray-400 font-luxury-sans">
                {tierConfig.title}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {onMinimize && (
              <motion.button
                onClick={onMinimize}
                className="p-2 text-gray-400 hover:text-white transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              </motion.button>
            )}
            
            <motion.button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.button>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                className={`flex ${message.id.startsWith('user_') ? 'justify-end' : 'justify-start'}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-lg ${
                    message.id.startsWith('user_')
                      ? 'bg-blue-600 text-white'
                      : message.type === 'action'
                      ? 'bg-green-600/20 border border-green-500/30'
                      : 'bg-gray-800 border border-gray-700'
                  }`}
                >
                  <p className="font-luxury-sans leading-relaxed">{message.content}</p>
                  <p className="text-xs text-gray-400 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          {isTyping && (
            <motion.div
              className="flex justify-start"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="bg-gray-800 border border-gray-700 p-4 rounded-lg flex items-center space-x-2">
                <div className="flex space-x-1">
                  <motion.div
                    className="w-2 h-2 bg-gray-400 rounded-full"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-gray-400 rounded-full"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-gray-400 rounded-full"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
                <span className="text-gray-400 font-luxury-sans">
                  {user.dedicatedButler} is processing...
                </span>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Actions */}
        {suggestedActions.length > 0 && (
          <div className="border-t border-gray-700 p-4">
            <h3 className="text-sm font-luxury-sans text-gray-400 mb-3">Suggested Actions:</h3>
            <div className="flex flex-wrap gap-2">
              {suggestedActions.map((action) => (
                <motion.button
                  key={action.id}
                  onClick={() => executeAction(action)}
                  className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg text-sm font-luxury-sans hover:bg-gray-600 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {action.description}
                </motion.button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-700 p-4">
          <div className="flex space-x-4">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Ask ${user.dedicatedButler} anything...`}
              className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-gray-500 focus:outline-none font-luxury-sans"
              disabled={isProcessing}
            />
            
            <motion.button
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isProcessing}
              className="px-6 py-3 rounded-lg font-luxury-sans font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              style={{ 
                backgroundColor: tierConfig.color,
                color: '#000'
              }}
              whileHover={!isProcessing ? { scale: 1.05 } : {}}
              whileTap={!isProcessing ? { scale: 0.95 } : {}}
            >
              {isProcessing ? 'Processing...' : 'Send'}
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}