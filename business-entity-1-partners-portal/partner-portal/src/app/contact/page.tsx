'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  BoltIcon,
  PhoneIcon,
  ClockIcon,
  SparklesIcon,
  HeartIcon,
  CheckCircleIcon,
  PlayIcon
} from '@heroicons/react/24/outline';

const aiSupportMethods = [
  {
    icon: ChatBubbleLeftRightIcon,
    title: 'WhatsApp AI Support',
    description: 'Chat with our AI in 11 Indian languages',
    contact: '+91 98765 43210',
    action: 'Start WhatsApp Chat',
    href: 'https://wa.me/919876543210?text=Hi,%20I%20need%20support%20with%20TradeMate',
    responseTime: '<30 seconds',
    available: true,
    highlight: true,
    features: ['24/7 Instant Response', '11 Languages', 'Zero-Knowledge Secure', 'Voice Messages Supported']
  },
  {
    icon: SparklesIcon,
    title: 'AI Butler Assistant',
    description: 'Enterprise AI assistant for complex queries',
    contact: 'Available for Pro+ customers',
    action: 'Launch AI Butler',
    href: '#ai-butler',
    responseTime: '<10 seconds',
    available: true,
    features: ['Advanced Problem Solving', 'Code Analysis', 'Custom Solutions', 'Predictive Support']
  },
  {
    icon: GlobeAltIcon,
    title: 'Multilingual AI Chat',
    description: 'Web-based AI chat in your language',
    contact: 'Available in Hindi, Tamil, Telugu, Bengali...',
    action: 'Start Chat',
    href: '#web-chat',
    responseTime: '<15 seconds',
    available: true,
    features: ['11 Indian Languages', 'Technical Support', 'Integration Help', 'Smart Routing']
  },
  {
    icon: BoltIcon,
    title: 'Self-Healing Support',
    description: 'Autonomous issue detection & resolution',
    contact: '91.5% issues resolved automatically',
    action: 'View System Status',
    href: '/dashboard/health',
    responseTime: 'Instant',
    available: true,
    features: ['Predictive Detection', 'Auto-Resolution', 'Zero Downtime', 'Proactive Alerts']
  }
];

const supportTiers = [
  {
    tier: 'Community',
    plan: 'LITE Plan',
    description: 'AI-powered self-service support',
    responseTime: 'Instant AI + 4-8 hours human',
    price: 'Free',
    channels: ['WhatsApp AI Bot', 'Community Forum', 'Documentation AI'],
    features: [
      'AI instant responses in 11 languages',
      'Self-healing system alerts', 
      'Basic troubleshooting automation',
      'Community-driven solutions'
    ]
  },
  {
    tier: 'Professional',
    plan: 'PRO + ELITE Plans',
    description: 'Advanced AI + Human hybrid support',
    responseTime: 'Instant AI + 1-2 hours human',
    price: 'Included',
    channels: ['Priority WhatsApp AI', 'AI Butler', 'Video Calls', 'Slack Integration'],
    features: [
      'Advanced AI problem-solving',
      'Predictive issue prevention',
      'Custom integration assistance',
      'Priority human escalation',
      'Zero-knowledge secure sessions'
    ]
  },
  {
    tier: 'Enterprise',
    plan: 'BLACK Tier',
    description: 'Dedicated AI + 24/7 human team',
    responseTime: 'Instant AI + <30 min human',
    price: 'Premium',
    channels: ['Dedicated AI Assistant', '24/7 Human Team', 'Private WhatsApp', 'Emergency Hotline'],
    features: [
      'Personal AI assistant trained on your data',
      'Dedicated account manager',
      '99.98% uptime SLA with self-healing',
      'Custom AI model fine-tuning',
      'Emergency response team',
      'On-premise deployment support'
    ]
  }
];

const languages = [
  { name: 'Hindi', native: 'हिंदी', flag: '🇮🇳' },
  { name: 'English', native: 'English', flag: '🇬🇧' },
  { name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳' },
  { name: 'Telugu', native: 'తెలుగు', flag: '🇮🇳' },
  { name: 'Bengali', native: 'বাংলা', flag: '🇮🇳' },
  { name: 'Marathi', native: 'मराठी', flag: '🇮🇳' },
  { name: 'Gujarati', native: 'ગુજરાતી', flag: '🇮🇳' },
  { name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { name: 'Malayalam', native: 'മലയാളം', flag: '🇮🇳' },
  { name: 'Punjabi', native: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
  { name: 'Urdu', native: 'اردو', flag: '🇮🇳' }
];

export default function ContactPage() {
  const [selectedLanguage, setSelectedLanguage] = useState('English');
  const [showAIDemo, setShowAIDemo] = useState(false);

  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 }
  };

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <span className="text-xl font-semibold text-gray-900">TradeMate</span>
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                AI Support
              </span>
            </Link>
            <Link 
              href="/auth/signin"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <motion.div 
          className="text-center mb-16"
          initial="initial"
          animate="animate"
          variants={staggerChildren}
        >
          <motion.div
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 rounded-full text-sm font-medium mb-8"
          >
            <SparklesIcon className="w-4 h-4 mr-2" />
            Experience our AI-powered support yourself!
          </motion.div>
          
          <motion.h1 
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="text-4xl lg:text-6xl font-bold text-gray-900 mb-4"
          >
            AI-First Support
            <br />
            <span className="gradient-text">Zero Human Wait Time</span>
          </motion.h1>
          
          <motion.p 
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed"
          >
            Get instant support in 11 Indian languages through our AI-powered WhatsApp assistant. 
            <strong>91.5% of issues resolved automatically</strong> with <strong>zero-knowledge privacy</strong>.
          </motion.p>

          <motion.div 
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8"
          >
            <a
              href="https://wa.me/919876543210?text=Hi,%20I%20need%20support%20with%20TradeMate"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-green-700 transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center"
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
              Start WhatsApp Support
            </a>
            <button
              onClick={() => setShowAIDemo(true)}
              className="bg-white text-gray-900 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-all duration-200 border border-gray-200 shadow-lg flex items-center"
            >
              <PlayIcon className="w-5 h-5 mr-2" />
              Try AI Demo
            </button>
          </motion.div>

          {/* Live Stats */}
          <motion.div 
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto"
          >
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">91.5%</div>
              <div className="text-gray-600">Auto-Resolved</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">&lt;30s</div>
              <div className="text-gray-600">Response Time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">24/7</div>
              <div className="text-gray-600">AI Availability</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">11</div>
              <div className="text-gray-600">Languages</div>
            </div>
          </motion.div>
        </motion.div>

        {/* AI Support Methods */}
        <motion.div 
          className="mb-16"
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={staggerChildren}
        >
          <motion.h2 
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="text-3xl font-bold text-center text-gray-900 mb-12"
          >
            Choose Your AI Support Method
          </motion.h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {aiSupportMethods.map((method, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
            transition={{ duration: 0.6 }}
                className={`relative p-8 rounded-2xl transition-all duration-300 hover:shadow-xl ${
                  method.highlight 
                    ? 'bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200' 
                    : 'bg-white border border-gray-200 hover:border-blue-200'
                }`}
              >
                {method.highlight && (
                  <div className="absolute -top-3 left-6">
                    <span className="bg-green-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg ${method.highlight ? 'bg-green-600' : 'bg-blue-600'}`}>
                    <method.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{method.title}</h3>
                    <p className="text-gray-600 mb-3">{method.description}</p>
                    <p className="text-sm text-gray-900 mb-4">{method.contact}</p>
                    
                    <div className="mb-4">
                      <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
                        {method.responseTime} response
                      </span>
                    </div>
                    
                    <ul className="space-y-2 mb-6">
                      {method.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center text-sm text-gray-600">
                          <CheckCircleIcon className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    
                    <a
                      href={method.href}
                      target={method.href.startsWith('http') ? '_blank' : '_self'}
                      rel={method.href.startsWith('http') ? 'noopener noreferrer' : ''}
                      className={`inline-flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                        method.highlight
                          ? 'bg-green-600 text-white hover:bg-green-700'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {method.action}
                    </a>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Language Support Showcase */}
        <motion.div 
          className="mb-16 bg-white rounded-2xl p-8 border border-gray-200"
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={fadeInUp}
            transition={{ duration: 0.6 }}
        >
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Speak to our AI in your language
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
            {languages.map((language, index) => (
              <button
                key={index}
                onClick={() => setSelectedLanguage(language.name)}
                className={`p-4 rounded-lg text-center transition-all duration-200 ${
                  selectedLanguage === language.name
                    ? 'bg-blue-100 border-2 border-blue-500 text-blue-900'
                    : 'bg-gray-50 border border-gray-200 hover:bg-gray-100 text-gray-700'
                }`}
              >
                <div className="text-2xl mb-2">{language.flag}</div>
                <div className="font-medium text-sm">{language.name}</div>
                <div className="text-xs text-gray-500">{language.native}</div>
              </button>
            ))}
          </div>
          
          <div className="text-center">
            <a
              href={`https://wa.me/919876543210?text=नमस्ते,%20मुझे%20TradeMate%20के%20साथ%20सहायता%20चाहिए`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors inline-flex items-center"
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
              Start chat in {selectedLanguage}
            </a>
          </div>
        </motion.div>

        {/* Support Tiers */}
        <motion.div 
          className="mb-16"
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={staggerChildren}
        >
          <motion.h2 
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="text-3xl font-bold text-center text-gray-900 mb-12"
          >
            AI Support Levels
          </motion.h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {supportTiers.map((tier, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
            transition={{ duration: 0.6 }}
                className={`p-8 rounded-2xl border transition-all duration-300 hover:shadow-xl ${
                  tier.tier === 'Professional'
                    ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-blue-100 transform scale-105'
                    : 'border-gray-200 bg-white hover:border-blue-200'
                }`}
              >
                {tier.tier === 'Professional' && (
                  <div className="text-center mb-4">
                    <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                      Recommended
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900">{tier.tier}</h3>
                  <p className="text-blue-600 font-medium">{tier.plan}</p>
                  <p className="text-gray-600 mt-2">{tier.description}</p>
                  <div className="mt-4">
                    <span className="text-3xl font-bold text-gray-900">{tier.price}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">{tier.responseTime}</p>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">AI + Human Channels:</h4>
                    <div className="text-sm text-gray-600">
                      {tier.channels.join(' • ')}
                    </div>
                  </div>
                  
                  <ul className="space-y-2">
                    {tier.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start text-sm text-gray-600">
                        <CheckCircleIcon className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div className="mt-8">
                  <Link
                    href="/pricing"
                    className={`w-full inline-flex items-center justify-center px-4 py-3 rounded-lg font-medium transition-colors ${
                      tier.tier === 'Professional'
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    }`}
                  >
                    Get Started
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* System Status */}
        <motion.div 
          className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-8 border border-green-200"
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={fadeInUp}
            transition={{ duration: 0.6 }}
        >
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Live System Status - Self-Healing Active
            </h3>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-700 font-medium">All Systems Operational</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <BoltIcon className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="font-medium text-gray-900">AI Response</h4>
              <p className="text-2xl font-bold text-green-600">98.7%</p>
              <p className="text-sm text-gray-600">Success Rate</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <ShieldCheckIcon className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="font-medium text-gray-900">Zero-Knowledge</h4>
              <p className="text-2xl font-bold text-blue-600">100%</p>
              <p className="text-sm text-gray-600">Privacy Protected</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <HeartIcon className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="font-medium text-gray-900">Self-Healing</h4>
              <p className="text-2xl font-bold text-purple-600">24/7</p>
              <p className="text-sm text-gray-600">Active Monitoring</p>
            </div>
          </div>
          
          <div className="text-center mt-8">
            <Link
              href="/dashboard/health"
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors inline-flex items-center"
            >
              <BoltIcon className="w-5 h-5 mr-2" />
              View Detailed Health Status
            </Link>
          </div>
        </motion.div>

        {/* Emergency Contact - Human Escalation */}
        <motion.div 
          className="mt-16 bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-2xl p-8 text-center"
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={fadeInUp}
            transition={{ duration: 0.6 }}
        >
          <h2 className="text-xl font-bold text-red-900 mb-4">Human Escalation</h2>
          <p className="text-red-700 mb-4">
            For critical issues that our AI cannot resolve (BLACK Tier customers only)
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="tel:+918045678999"
              className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center"
            >
              <PhoneIcon className="w-5 h-5 mr-2" />
              Emergency: +91 80 4567 8999
            </a>
            <a
              href="https://wa.me/919876543210?text=URGENT:%20Critical%20issue%20requiring%20human%20support"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white text-red-600 border border-red-600 px-6 py-3 rounded-lg hover:bg-red-50 transition-colors flex items-center justify-center"
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
              Urgent WhatsApp
            </a>
          </div>
          <p className="text-xs text-red-600 mt-4">
            Average human escalation rate: &lt;8.5% • AI resolves 91.5% automatically
          </p>
        </motion.div>
      </div>
    </div>
  );
}