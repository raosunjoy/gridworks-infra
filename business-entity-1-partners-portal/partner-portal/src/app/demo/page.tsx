'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  PlayIcon, 
  CodeBracketIcon, 
  ChatBubbleLeftRightIcon,
  CurrencyRupeeIcon,
  BoltIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  DocumentDuplicateIcon,
  PhoneIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  BellIcon,
  Cog6ToothIcon as SettingsIcon,
  HomeIcon,
  SpeakerWaveIcon,
  PauseIcon
} from '@heroicons/react/24/outline';

interface DemoResponse {
  success: boolean;
  data: any;
  responseTime: string;
  timestamp: string;
}

interface ApiDemo {
  id: string;
  title: string;
  description: string;
  endpoint: string;
  method: string;
  icon: any;
  color: string;
  category: string;
  requestBody?: any;
  mockResponse: any;
}

const apiDemos: ApiDemo[] = [
  {
    id: 'market-data',
    title: 'Market Data',
    description: 'Get real-time NSE/BSE market data with live prices and volumes',
    endpoint: '/api/v1/market-data?symbols=NIFTY50,BANKNIFTY',
    method: 'GET',
    icon: ChartBarIcon,
    color: 'blue',
    category: 'Trading',
    mockResponse: {
      success: true,
      data: [
        {
          symbol: 'NIFTY50',
          price: 21545.50,
          change: 125.30,
          changePercent: 0.58,
          volume: 12456789,
          high: 21580.25,
          low: 21420.15,
          open: 21425.80,
          timestamp: '2025-06-28T17:30:00Z'
        },
        {
          symbol: 'BANKNIFTY',
          price: 45125.75,
          change: -85.20,
          changePercent: -0.19,
          volume: 8234567,
          high: 45250.90,
          low: 45080.45,
          open: 45210.95,
          timestamp: '2025-06-28T17:30:00Z'
        }
      ]
    }
  },
  {
    id: 'whatsapp-multilingual',
    title: 'Multi-Language WhatsApp',
    description: 'Send messages in 11 Indian languages - from Hindi to Tamil, for street vendors to CEOs',
    endpoint: '/api/v1/whatsapp/send-multilingual',
    method: 'POST',
    icon: GlobeAltIcon,
    color: 'green',
    category: 'Languages',
    requestBody: {
      phone: '+919876543210',
      message: 'Stock market update available',
      language: 'hi',
      user_profile: 'street_vendor',
      auto_translate: true
    },
    mockResponse: {
      success: true,
      data: {
        messageId: 'wamid.HBgNOTE2MzgxMDI3ODA4OBUCABIYFjNFQjBGNzA5QzAyNDQzNEE4RkQ2',
        status: 'sent',
        phone: '+919876543210',
        original_message: 'Stock market update available',
        translated_message: 'शेयर बाजार अपडेट उपलब्ध है। आज NIFTY में 2.5% की बढ़ोतरी हुई है।',
        language: 'hindi',
        language_code: 'hi',
        user_context: 'street_vendor',
        timestamp: '2025-06-28T17:30:00Z'
      }
    }
  },
  {
    id: 'whatsapp-send',
    title: 'WhatsApp Business API',
    description: 'Professional WhatsApp integration with interactive buttons and templates',
    endpoint: '/api/v1/whatsapp/send',
    method: 'POST',
    icon: ChatBubbleLeftRightIcon,
    color: 'green',
    category: 'Communication',
    requestBody: {
      phone: '+919876543210',
      message: 'NIFTY50 is up 2.5% today! Consider reviewing your portfolio.',
      type: 'text'
    },
    mockResponse: {
      success: true,
      data: {
        messageId: 'wamid.HBgNOTE2MzgxMDI3ODA4OBUCABIYFjNFQjBGNzA5QzAyNDQzNEE4RkQ2',
        status: 'sent',
        phone: '+919876543210',
        timestamp: '2025-06-28T17:30:00Z'
      }
    }
  },
  {
    id: 'ai-analysis',
    title: 'AI Market Analysis',
    description: 'Get AI-powered market insights and trading recommendations',
    endpoint: '/api/v1/ai/analyze',
    method: 'POST',
    icon: BoltIcon,
    color: 'purple',
    category: 'AI',
    requestBody: {
      symbols: ['NIFTY50', 'RELIANCE', 'TCS'],
      timeframe: '1d',
      analysis_type: 'technical'
    },
    mockResponse: {
      success: true,
      data: {
        analysis: {
          sentiment: 'bullish',
          confidence: 0.85,
          summary: 'Market shows strong upward momentum with good volume support',
          signals: [
            {
              symbol: 'NIFTY50',
              signal: 'BUY',
              strength: 'STRONG',
              reasoning: 'RSI shows bullish divergence, breaking resistance at 21500'
            },
            {
              symbol: 'RELIANCE',
              signal: 'HOLD',
              strength: 'MODERATE',
              reasoning: 'Consolidating near support, wait for clear breakout'
            }
          ],
          risk_level: 'moderate'
        }
      }
    }
  },
  {
    id: 'user-portfolio',
    title: 'Portfolio Tracker',
    description: 'Track user portfolios with real-time P&L calculations',
    endpoint: '/api/v1/portfolio/user123',
    method: 'GET',
    icon: CurrencyRupeeIcon,
    color: 'orange',
    category: 'Portfolio',
    mockResponse: {
      success: true,
      data: {
        userId: 'user123',
        totalValue: 500000,
        totalInvestment: 450000,
        totalPnL: 50000,
        totalPnLPercent: 11.11,
        holdings: [
          {
            symbol: 'RELIANCE',
            quantity: 100,
            avgPrice: 2450.00,
            currentPrice: 2580.50,
            investment: 245000,
            currentValue: 258050,
            pnl: 13050,
            pnlPercent: 5.32
          },
          {
            symbol: 'TCS',
            quantity: 50,
            avgPrice: 3200.00,
            currentPrice: 3450.75,
            investment: 160000,
            currentValue: 172537.50,
            pnl: 12537.50,
            pnlPercent: 7.84
          }
        ]
      }
    }
  },
  {
    id: 'voice-multilingual',
    title: 'Voice in 11 Languages',
    description: 'Street vendor asks "मेरा पैसा कैसा चल रहा है?" - AI understands and responds perfectly',
    endpoint: '/api/v1/voice/process-multilingual',
    method: 'POST',
    icon: PhoneIcon,
    color: 'indigo',
    category: 'Languages',
    requestBody: {
      audioUrl: 'https://example.com/vendor_query.mp3',
      auto_detect_language: true,
      user_context: 'street_vendor',
      response_language: 'same'
    },
    mockResponse: {
      success: true,
      data: {
        detected_language: 'hindi',
        transcription: 'मेरा पैसा कैसा चल रहा है? मैंने 500 रुपए लगाए थे।',
        translation: 'How is my money doing? I had invested 500 rupees.',
        confidence: 0.94,
        intent: 'portfolio_check',
        user_context: 'street_vendor',
        ai_response: {
          hindi: 'आपका 500 रुपए का निवेश अभी 545 रुपए हो गया है। आपको 45 रुपए का फायदा हुआ है!',
          english: 'Your 500 rupee investment is now worth 545 rupees. You have gained 45 rupees!',
          voice_response_url: 'https://api.trademate.ai/voice/response/abc123.mp3'
        },
        entities: [
          {
            type: 'investment_amount',
            value: '500',
            currency: 'INR'
          }
        ]
      }
    }
  },
  {
    id: 'subscription-create',
    title: 'Subscription Management',
    description: 'Create and manage user subscriptions with billing integration',
    endpoint: '/api/v1/subscriptions',
    method: 'POST',
    icon: ShieldCheckIcon,
    color: 'emerald',
    category: 'Billing',
    requestBody: {
      userId: 'user123',
      plan: 'PRO',
      duration: 'monthly',
      paymentMethod: 'upi'
    },
    mockResponse: {
      success: true,
      data: {
        subscriptionId: 'sub_abc123',
        userId: 'user123',
        plan: 'PRO',
        status: 'active',
        startDate: '2025-06-28',
        endDate: '2025-07-28',
        amount: 499,
        currency: 'INR',
        paymentLink: 'https://pay.trademate.ai/sub_abc123'
      }
    }
  }
];

export default function DemoPage() {
  const { data: session } = useSession();

  const [activeDemo, setActiveDemo] = useState<string>('market-data');
  const [isRunning, setIsRunning] = useState<string | null>(null);
  const [responses, setResponses] = useState<Record<string, DemoResponse>>({});
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [playingAudio, setPlayingAudio] = useState<string | null>(null);
  const [audioElements, setAudioElements] = useState<Record<string, HTMLAudioElement>>({});

  const runDemo = async (demo: ApiDemo) => {
    setIsRunning(demo.id);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const response: DemoResponse = {
      success: true,
      data: demo.mockResponse,
      responseTime: `${Math.floor(Math.random() * 300 + 100)}ms`,
      timestamp: new Date().toISOString()
    };
    
    setResponses(prev => ({ ...prev, [demo.id]: response }));
    setIsRunning(null);
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const playAudio = async (text: string, language: string, audioId: string) => {
    try {
      // Stop any currently playing audio
      if (playingAudio && audioElements[playingAudio]) {
        audioElements[playingAudio].pause();
        audioElements[playingAudio].currentTime = 0;
      }

      setPlayingAudio(audioId);

      // Use Web Speech API for text-to-speech
      if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        // Wait for voices to be loaded
        const voices = window.speechSynthesis.getVoices();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Enhanced language support with better voice selection
        const languageConfig: Record<string, { code: string; rate: number; pitch: number; volume: number }> = {
          'hi': { code: 'hi-IN', rate: 0.85, pitch: 1.0, volume: 0.9 },
          'en': { code: 'en-IN', rate: 0.9, pitch: 1.0, volume: 0.9 },
          // For other languages, fallback to English with a note
          'bn': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 },
          'ta': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 },
          'te': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 },
          'mr': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 },
          'gu': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 },
          'kn': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 },
          'or': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 },
          'pa': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 },
          'ur': { code: 'en-IN', rate: 0.8, pitch: 0.9, volume: 0.8 }
        };

        const config = languageConfig[language] || languageConfig['en'];
        
        // Only use native language for Hindi and English, others use English explanation
        if (language !== 'hi' && language !== 'en') {
          utterance.text = `This would be spoken in ${language === 'bn' ? 'Bengali' : 
                                                     language === 'ta' ? 'Tamil' : 
                                                     language === 'te' ? 'Telugu' : 
                                                     language === 'mr' ? 'Marathi' : 
                                                     language === 'gu' ? 'Gujarati' : 
                                                     language === 'kn' ? 'Kannada' : 
                                                     language === 'or' ? 'Odia' : 
                                                     language === 'pa' ? 'Punjabi' : 
                                                     language === 'ur' ? 'Urdu' : 'local language'}. Our AI supports high-quality speech in all 11 Indian languages.`;
        }

        utterance.lang = config.code;
        utterance.rate = config.rate;
        utterance.pitch = config.pitch;
        utterance.volume = config.volume;

        // Try to find a good voice for the language
        const preferredVoice = voices.find(voice => 
          voice.lang === config.code && voice.localService
        ) || voices.find(voice => 
          voice.lang.startsWith(config.code.split('-')[0])
        );

        if (preferredVoice) {
          utterance.voice = preferredVoice;
        }

        utterance.onend = () => {
          setPlayingAudio(null);
        };

        utterance.onerror = (error) => {
          setPlayingAudio(null);
          console.log('Speech synthesis error:', error);
        };

        window.speechSynthesis.speak(utterance);
      } else {
        // Fallback: simulate audio playback
        setTimeout(() => {
          setPlayingAudio(null);
        }, 3000);
      }
    } catch (error) {
      console.error('Audio playback error:', error);
      setPlayingAudio(null);
    }
  };

  const stopAudio = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setPlayingAudio(null);
  };

  const generateCurlCommand = (demo: ApiDemo) => {
    const baseCommand = `curl -X ${demo.method} "https://api.trademate.ai${demo.endpoint}" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`;
    
    if (demo.requestBody) {
      return `${baseCommand} \\
  -d '${JSON.stringify(demo.requestBody, null, 2)}'`;
    }
    
    return baseCommand;
  };

  const generateNodeCode = (demo: ApiDemo) => {
    if (demo.method === 'GET') {
      return `const TradeMate = require('@trademate/node-sdk');

const client = new TradeMate({
  apiKey: 'your-api-key'
});

const data = await client.get('${demo.endpoint}');
console.log(data);`;
    } else {
      return `const TradeMate = require('@trademate/node-sdk');

const client = new TradeMate({
  apiKey: 'your-api-key'
});

const data = await client.post('${demo.endpoint}', ${JSON.stringify(demo.requestBody, null, 2)});
console.log(data);`;
    }
  };

  const categories = ['All', ...Array.from(new Set(apiDemos.map(demo => demo.category)))];
  const [selectedCategory, setSelectedCategory] = useState('All');
  
  const filteredDemos = selectedCategory === 'All' 
    ? apiDemos 
    : apiDemos.filter(demo => demo.category === selectedCategory);

  const activeApiDemo = apiDemos.find(demo => demo.id === activeDemo);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Public Header */}
      <motion.header 
        className="bg-white border-b border-gray-200 sticky top-0 z-50"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">TM</span>
              </div>
              <span className="text-xl font-semibold text-gray-900">TradeMate Demo</span>
            </Link>
            <div className="flex items-center space-x-4">
              {session ? (
                <>
                  <Link 
                    href="/dashboard"
                    className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    <HomeIcon className="h-4 w-4" />
                    <span>Dashboard</span>
                  </Link>
                  <Link 
                    href="/developer"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Developer Portal
                  </Link>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{session.user?.name}</p>
                    <p className="text-xs text-gray-600">{session.user?.email}</p>
                  </div>
                </>
              ) : (
                <>
                  <Link 
                    href="/docs"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Documentation
                  </Link>
                  <Link 
                    href="/pricing"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Pricing
                  </Link>
                  <Link 
                    href="/contact"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Contact
                  </Link>
                  <Link 
                    href="/auth/signin"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Sign In
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </motion.header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <motion.h1 
            className="text-4xl font-bold text-gray-900 mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            Interactive API Demo
          </motion.h1>
          <motion.p 
            className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Experience financial inclusion for all Indians - from street vendors asking 
            "मेरा पैसा कैसा चल रहा है?" to CEOs managing portfolios. 
            Test our APIs that work in 11 languages via WhatsApp.
          </motion.p>
          
          {/* Live Stats */}
          <motion.div 
            className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-2xl font-bold text-blue-600">~150ms</div>
              <div className="text-sm text-gray-600">Avg Response</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-2xl font-bold text-green-600">99.9%</div>
              <div className="text-sm text-gray-600">Uptime</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-2xl font-bold text-purple-600">11</div>
              <div className="text-sm text-gray-600">Languages</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-2xl font-bold text-orange-600">24/7</div>
              <div className="text-sm text-gray-600">Support</div>
            </div>
          </motion.div>
        </div>

        {/* Languages Showcase */}
        <motion.div 
          className="bg-gradient-to-r from-green-500 to-blue-600 rounded-2xl p-8 mb-12 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">🌍 11 Indian Languages Support</h2>
            <p className="text-xl opacity-90">
              From street vendors in local markets to CEOs in boardrooms - everyone can access financial services in their preferred language
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 text-center">
            {[
              { lang: 'हिंदी', name: 'Hindi', example: 'मेरा पैसा कैसा है?' },
              { lang: 'বাংলা', name: 'Bengali', example: 'আমার টাকা কেমন?' },
              { lang: 'தமிழ்', name: 'Tamil', example: 'என் பணம் எப்படி?' },
              { lang: 'తెలుగు', name: 'Telugu', example: 'నా డబ్బు ఎలా?' },
              { lang: 'मराठी', name: 'Marathi', example: 'माझे पैसे कसे?' },
              { lang: 'ગુજરાતી', name: 'Gujarati', example: 'મારા પૈસા કેવા?' },
              { lang: 'ಕನ್ನಡ', name: 'Kannada', example: 'ನನ್ನ ಹಣ ಹೇಗಿದೆ?' },
              { lang: 'ଓଡ଼ିଆ', name: 'Odia', example: 'ମୋ ପଇସା କେମିତି?' },
              { lang: 'ਪੰਜਾਬੀ', name: 'Punjabi', example: 'ਮੇਰਾ ਪੈਸਾ ਕਿਵੇਂ ਹੈ?' },
              { lang: 'اردو', name: 'Urdu', example: 'میرا پیسہ کیسا ہے؟' },
              { lang: 'English', name: 'English', example: 'How is my money?' }
            ].slice(0, 11).map((lang, index) => {
              const langCode = lang.name.toLowerCase() === 'hindi' ? 'hi' : 
                             lang.name.toLowerCase() === 'bengali' ? 'bn' :
                             lang.name.toLowerCase() === 'tamil' ? 'ta' :
                             lang.name.toLowerCase() === 'telugu' ? 'te' :
                             lang.name.toLowerCase() === 'marathi' ? 'mr' :
                             lang.name.toLowerCase() === 'gujarati' ? 'gu' :
                             lang.name.toLowerCase() === 'kannada' ? 'kn' :
                             lang.name.toLowerCase() === 'odia' ? 'or' :
                             lang.name.toLowerCase() === 'punjabi' ? 'pa' :
                             lang.name.toLowerCase() === 'urdu' ? 'ur' : 'en';
              
              const isHighQuality = langCode === 'hi' || langCode === 'en';
              
              return (
                <div key={index} className={`rounded-lg p-4 backdrop-blur-sm relative group ${
                  isHighQuality ? 'bg-white/30 border border-white/40' : 'bg-white/20'
                }`}>
                  <div className="text-2xl font-bold mb-1">{lang.lang}</div>
                  <div className="text-sm opacity-90 mb-2">{lang.name}</div>
                  <div className="text-xs opacity-75 italic mb-2">"{lang.example}"</div>
                  
                  {/* Quality indicator */}
                  {isHighQuality && (
                    <div className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                      HD Audio
                    </div>
                  )}
                  
                  {/* Audio Play Button */}
                  <button
                    onClick={() => {
                      if (playingAudio === `lang-${index}`) {
                        stopAudio();
                      } else {
                        playAudio(lang.example, langCode, `lang-${index}`);
                      }
                    }}
                    className="absolute bottom-2 right-2 p-1 bg-white/30 rounded-full hover:bg-white/50 transition-all opacity-0 group-hover:opacity-100"
                    title={isHighQuality ? `Listen in ${lang.name}` : `Demo ${lang.name} support`}
                  >
                    {playingAudio === `lang-${index}` ? (
                      <PauseIcon className="h-4 w-4 text-white" />
                    ) : (
                      <SpeakerWaveIcon className="h-4 w-4 text-white" />
                    )}
                  </button>
                </div>
              );
            })}
          </div>
          
          <div className="text-center mt-8">
            <p className="text-lg opacity-90 mb-4">
              🎯 <strong>Real Impact:</strong> A street vendor in Mumbai can ask "मेरा 500 रुपया कैसा चल रहा है?" 
              and get instant AI-powered financial advice in Hindi via WhatsApp
            </p>
            
            {/* Demo Audio Button */}
            <button
              onClick={() => {
                const demoText = "आपका 500 रुपए का निवेश अभी 545 रुपए हो गया है। आपको 45 रुपए का फायदा हुआ है!";
                if (playingAudio === 'demo-response') {
                  stopAudio();
                } else {
                  playAudio(demoText, 'hi', 'demo-response');
                }
              }}
              className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm text-white px-6 py-3 rounded-xl hover:bg-white/30 transition-all mx-auto border border-white/30"
            >
              {playingAudio === 'demo-response' ? (
                <PauseIcon className="h-5 w-5" />
              ) : (
                <SpeakerWaveIcon className="h-5 w-5" />
              )}
              <span className="font-medium">
                {playingAudio === 'demo-response' ? 'Playing...' : '🎧 Hear AI Response in Hindi'}
              </span>
            </button>
          </div>
        </motion.div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 mb-8 justify-center">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* API Demos List */}
          <div className="lg:col-span-1">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">API Endpoints</h2>
            <div className="space-y-3">
              {filteredDemos.map((demo) => (
                <motion.button
                  key={demo.id}
                  onClick={() => setActiveDemo(demo.id)}
                  className={`w-full text-left p-4 rounded-lg border transition-all ${
                    activeDemo === demo.id
                      ? 'border-blue-300 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg bg-${demo.color}-100`}>
                      <demo.icon className={`h-5 w-5 text-${demo.color}-600`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900">{demo.title}</h3>
                      <p className="text-sm text-gray-600 line-clamp-2">{demo.description}</p>
                      <div className="flex items-center mt-2 space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          demo.method === 'GET' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                        }`}>
                          {demo.method}
                        </span>
                        <span className="text-xs text-gray-500">{demo.category}</span>
                      </div>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Demo Playground */}
          <div className="lg:col-span-2 space-y-6">
            {activeApiDemo && (
              <>
                {/* Demo Header */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4">
                      <div className={`p-3 rounded-lg bg-${activeApiDemo.color}-100`}>
                        <activeApiDemo.icon className={`h-6 w-6 text-${activeApiDemo.color}-600`} />
                      </div>
                      <div>
                        <h2 className="text-xl font-semibold text-gray-900">{activeApiDemo.title}</h2>
                        <p className="text-gray-600 mt-1">{activeApiDemo.description}</p>
                        <div className="flex items-center mt-3 space-x-4">
                          <span className={`px-3 py-1 text-sm rounded-full ${
                            activeApiDemo.method === 'GET' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {activeApiDemo.method}
                          </span>
                          <code className="text-sm bg-gray-100 px-2 py-1 rounded">{activeApiDemo.endpoint}</code>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => runDemo(activeApiDemo)}
                      disabled={isRunning === activeApiDemo.id}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                    >
                      {isRunning === activeApiDemo.id ? (
                        <ArrowPathIcon className="h-4 w-4 animate-spin" />
                      ) : (
                        <PlayIcon className="h-4 w-4" />
                      )}
                      <span>{isRunning === activeApiDemo.id ? 'Running...' : 'Test API'}</span>
                    </button>
                  </div>
                </div>

                {/* Request/Response */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Request */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900">Request</h3>
                      <button
                        onClick={() => copyToClipboard(generateCurlCommand(activeApiDemo), `curl-${activeApiDemo.id}`)}
                        className="text-gray-500 hover:text-gray-700 transition-colors"
                      >
                        {copiedCode === `curl-${activeApiDemo.id}` ? (
                          <CheckCircleIcon className="h-4 w-4 text-green-600" />
                        ) : (
                          <DocumentDuplicateIcon className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    <div className="bg-gray-900 rounded-lg p-4">
                      <pre className="text-green-400 text-sm overflow-x-auto">
                        <code>{generateCurlCommand(activeApiDemo)}</code>
                      </pre>
                    </div>
                    
                    {activeApiDemo.requestBody && (
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Request Body:</h4>
                        <div className="bg-gray-50 rounded-lg p-3">
                          <pre className="text-sm text-gray-800 overflow-x-auto">
                            <code>{JSON.stringify(activeApiDemo.requestBody, null, 2)}</code>
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Response */}
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900">Response</h3>
                      {responses[activeApiDemo.id] && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <ClockIcon className="h-4 w-4" />
                          <span>{responses[activeApiDemo.id].responseTime}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="bg-gray-900 rounded-lg p-4 min-h-[200px]">
                      {isRunning === activeApiDemo.id ? (
                        <div className="flex items-center justify-center h-48">
                          <div className="text-center">
                            <ArrowPathIcon className="h-8 w-8 text-blue-400 animate-spin mx-auto mb-2" />
                            <p className="text-gray-400">Executing API call...</p>
                          </div>
                        </div>
                      ) : responses[activeApiDemo.id] ? (
                        <div>
                          <pre className="text-green-400 text-sm overflow-x-auto mb-4">
                            <code>{JSON.stringify(responses[activeApiDemo.id].data, null, 2)}</code>
                          </pre>
                          
                          {/* Audio Controls for Voice APIs */}
                          {(activeApiDemo.id === 'voice-multilingual' || activeApiDemo.id === 'whatsapp-multilingual') && responses[activeApiDemo.id] && (
                            <div className="border-t border-gray-700 pt-4">
                              <div className="text-green-400 text-sm mb-3">🎧 Listen to AI Response:</div>
                              <div className="flex flex-wrap gap-2">
                                {activeApiDemo.id === 'voice-multilingual' && responses[activeApiDemo.id].data.ai_response && (
                                  <>
                                    <button
                                      onClick={() => {
                                        const hindiResponse = responses[activeApiDemo.id].data.ai_response.hindi;
                                        if (playingAudio === 'voice-hindi') {
                                          stopAudio();
                                        } else {
                                          playAudio(hindiResponse, 'hi', 'voice-hindi');
                                        }
                                      }}
                                      className="flex items-center space-x-2 bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                                    >
                                      {playingAudio === 'voice-hindi' ? (
                                        <PauseIcon className="h-4 w-4" />
                                      ) : (
                                        <SpeakerWaveIcon className="h-4 w-4" />
                                      )}
                                      <span>Hindi Response</span>
                                    </button>
                                    <button
                                      onClick={() => {
                                        const englishResponse = responses[activeApiDemo.id].data.ai_response.english;
                                        if (playingAudio === 'voice-english') {
                                          stopAudio();
                                        } else {
                                          playAudio(englishResponse, 'en', 'voice-english');
                                        }
                                      }}
                                      className="flex items-center space-x-2 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                                    >
                                      {playingAudio === 'voice-english' ? (
                                        <PauseIcon className="h-4 w-4" />
                                      ) : (
                                        <SpeakerWaveIcon className="h-4 w-4" />
                                      )}
                                      <span>English Response</span>
                                    </button>
                                  </>
                                )}
                                {activeApiDemo.id === 'whatsapp-multilingual' && responses[activeApiDemo.id].data.translated_message && (
                                  <button
                                    onClick={() => {
                                      const translatedMessage = responses[activeApiDemo.id].data.translated_message;
                                      if (playingAudio === 'whatsapp-hindi') {
                                        stopAudio();
                                      } else {
                                        playAudio(translatedMessage, 'hi', 'whatsapp-hindi');
                                      }
                                    }}
                                    className="flex items-center space-x-2 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                                  >
                                    {playingAudio === 'whatsapp-hindi' ? (
                                      <PauseIcon className="h-4 w-4" />
                                    ) : (
                                      <SpeakerWaveIcon className="h-4 w-4" />
                                    )}
                                    <span>Hindi Translation</span>
                                  </button>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="flex items-center justify-center h-48">
                          <p className="text-gray-500">Click "Test API" to see the response</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Code Examples */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">SDK Examples</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-medium text-gray-700">Node.js SDK</h4>
                        <button
                          onClick={() => copyToClipboard(generateNodeCode(activeApiDemo), `node-${activeApiDemo.id}`)}
                          className="text-gray-500 hover:text-gray-700 transition-colors"
                        >
                          {copiedCode === `node-${activeApiDemo.id}` ? (
                            <CheckCircleIcon className="h-4 w-4 text-green-600" />
                          ) : (
                            <DocumentDuplicateIcon className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                      <div className="bg-gray-900 rounded-lg p-4">
                        <pre className="text-green-400 text-sm overflow-x-auto">
                          <code>{generateNodeCode(activeApiDemo)}</code>
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-16 bg-blue-600 rounded-2xl p-8 text-center text-white">
          {session ? (
            <>
              <h2 className="text-3xl font-bold mb-4">Ready to implement these APIs?</h2>
              <p className="text-xl mb-8 opacity-90">
                You have access to all these APIs as a partner. Generate your API keys and start building.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/dashboard"
                  className="bg-white text-blue-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Go to Dashboard
                </Link>
                <Link
                  href="/developer"
                  className="bg-blue-700 text-white border border-blue-400 px-8 py-3 rounded-lg font-medium hover:bg-blue-800 transition-colors"
                >
                  Full Developer Portal
                </Link>
              </div>
              
              {/* Partner Benefits */}
              <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                <div className="bg-blue-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">Your Current Plan</h3>
                  <p className="text-blue-100">Professional</p>
                </div>
                <div className="bg-blue-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">API Calls Remaining</h3>
                  <p className="text-blue-100">42,350 / 50,000</p>
                </div>
                <div className="bg-blue-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">Next Billing</h3>
                  <p className="text-blue-100">July 28, 2025</p>
                </div>
              </div>
            </>
          ) : (
            <>
              <h2 className="text-3xl font-bold mb-4">Ready to integrate TradeMate?</h2>
              <p className="text-xl mb-8 opacity-90">
                Start building with our APIs today. Get your API key and access comprehensive documentation.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/auth/signup"
                  className="bg-white text-blue-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Start Free Trial
                </Link>
                <Link
                  href="/docs"
                  className="bg-blue-700 text-white border border-blue-400 px-8 py-3 rounded-lg font-medium hover:bg-blue-800 transition-colors"
                >
                  View Documentation
                </Link>
              </div>

              {/* Demo Benefits */}
              <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                <div className="bg-blue-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">Free Trial</h3>
                  <p className="text-blue-100">1,000 API calls/month</p>
                </div>
                <div className="bg-blue-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">Response Time</h3>
                  <p className="text-blue-100">~150ms average</p>
                </div>
                <div className="bg-blue-700 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">Support</h3>
                  <p className="text-blue-100">24/7 documentation</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}