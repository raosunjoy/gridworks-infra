'use client';

import React, { useState } from 'react';
import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  Code, 
  Book, 
  PlayCircle, 
  Key, 
  Zap, 
  Shield, 
  Download,
  ExternalLink,
  Copy,
  Check,
  Terminal,
  Database,
  Webhook,
  Settings,
  Bell,
  LogOut,
  Home
} from 'lucide-react';

const DeveloperPortal: React.FC = () => {
  const { data: session, status } = useSession();

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (status === 'unauthenticated') {
    redirect('/auth/signin');
  }
  const [activeTab, setActiveTab] = useState('overview');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(label);
    setTimeout(() => setCopiedCode(null), 2000);
  };

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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <motion.header 
        className="bg-white border-b border-slate-200 sticky top-0 z-50"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Terminal className="h-8 w-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-slate-900">TradeMate Developer Portal</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/dashboard"
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <Home className="h-4 w-4" />
                <span>Dashboard</span>
              </Link>
              <div className="text-right">
                <p className="text-sm font-medium text-slate-900">{session?.user?.name}</p>
                <p className="text-xs text-slate-600">{session?.user?.email}</p>
              </div>
              <div className="flex items-center space-x-2">
                <button className="p-2 text-slate-600 hover:text-slate-900 transition-colors">
                  <Bell className="h-5 w-5" />
                </button>
                <button className="p-2 text-slate-600 hover:text-slate-900 transition-colors">
                  <Settings className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Quick Navigation */}
      <motion.div 
        className="bg-blue-50 border-b border-blue-200"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center space-x-6 text-sm">
            <Link href="/dashboard" className="text-blue-600 hover:text-blue-800 transition-colors">Dashboard</Link>
            <span className="text-blue-300">•</span>
            <Link href="/dashboard/analytics" className="text-blue-600 hover:text-blue-800 transition-colors">Analytics</Link>
            <span className="text-blue-300">•</span>
            <Link href="/dashboard/billing" className="text-blue-600 hover:text-blue-800 transition-colors">Billing</Link>
            <span className="text-blue-300">•</span>
            <span className="text-blue-800 font-medium">Developer Portal</span>
          </div>
        </div>
      </motion.div>

      {/* Navigation Tabs */}
      <motion.div 
        className="bg-white border-b border-slate-200"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: Book },
              { id: 'api-docs', label: 'API Reference', icon: Code },
              { id: 'sandbox', label: 'API Sandbox', icon: PlayCircle },
              { id: 'sdks', label: 'SDKs', icon: Download },
              { id: 'webhooks', label: 'Webhooks', icon: Webhook },
              { id: 'guides', label: 'Guides', icon: Settings }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </motion.div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <motion.div {...fadeInUp} className="space-y-8">
            {/* Hero Section */}
            <div className="text-center py-12">
              <h2 className="text-4xl font-bold text-slate-900 mb-4">
                Build with TradeMate API
              </h2>
              <p className="text-xl text-slate-600 max-w-3xl mx-auto">
                Integrate powerful trading capabilities, AI-driven insights, and WhatsApp automation 
                into your applications with our comprehensive API suite.
              </p>
            </div>

            {/* Quick Start */}
            <motion.div 
              className="bg-white rounded-xl border border-slate-200 p-8"
              variants={staggerChildren}
              initial="initial"
              animate="animate"
            >
              <h3 className="text-2xl font-bold text-slate-900 mb-6">Quick Start</h3>
              
              <div className="grid md:grid-cols-3 gap-6">
                <motion.div variants={fadeInUp} transition={{ duration: 0.6 }} className="text-center">
                  <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <Key className="h-8 w-8 text-blue-600" />
                  </div>
                  <h4 className="font-semibold text-slate-900 mb-2">1. Get API Key</h4>
                  <p className="text-slate-600 text-sm">
                    Sign up and get your API credentials to start building
                  </p>
                </motion.div>

                <motion.div variants={fadeInUp} transition={{ duration: 0.6 }} className="text-center">
                  <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <Code className="h-8 w-8 text-green-600" />
                  </div>
                  <h4 className="font-semibold text-slate-900 mb-2">2. Make API Call</h4>
                  <p className="text-slate-600 text-sm">
                    Use our RESTful API to access trading data and services
                  </p>
                </motion.div>

                <motion.div variants={fadeInUp} transition={{ duration: 0.6 }} className="text-center">
                  <div className="bg-purple-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <Zap className="h-8 w-8 text-purple-600" />
                  </div>
                  <h4 className="font-semibold text-slate-900 mb-2">3. Go Live</h4>
                  <p className="text-slate-600 text-sm">
                    Deploy your integration and start serving your users
                  </p>
                </motion.div>
              </div>
            </motion.div>

            {/* API Capabilities */}
            <motion.div 
              className="bg-white rounded-xl border border-slate-200 p-8"
              variants={fadeInUp} transition={{ duration: 0.6 }}
            >
              <h3 className="text-2xl font-bold text-slate-900 mb-6">API Capabilities</h3>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  {
                    icon: Database,
                    title: 'Trading Data',
                    description: 'Real-time market data, historical prices, and trading signals',
                    endpoints: ['GET /api/v1/market-data', 'GET /api/v1/signals']
                  },
                  {
                    icon: Zap,
                    title: 'AI Insights',
                    description: 'ML-powered market analysis and personalized recommendations',
                    endpoints: ['POST /api/v1/analyze', 'GET /api/v1/insights']
                  },
                  {
                    icon: Webhook,
                    title: 'WhatsApp Integration',
                    description: 'Send trading alerts and manage WhatsApp conversations',
                    endpoints: ['POST /api/v1/whatsapp/send', 'GET /api/v1/conversations']
                  },
                  {
                    icon: Shield,
                    title: 'Billing & Payments',
                    description: 'Subscription management and payment processing',
                    endpoints: ['POST /api/v1/subscriptions', 'GET /api/v1/billing']
                  },
                  {
                    icon: Settings,
                    title: 'User Management',
                    description: 'User authentication, profiles, and permissions',
                    endpoints: ['POST /api/v1/users', 'GET /api/v1/profile']
                  },
                  {
                    icon: Terminal,
                    title: 'Analytics',
                    description: 'Usage analytics, performance metrics, and reporting',
                    endpoints: ['GET /api/v1/analytics', 'POST /api/v1/events']
                  }
                ].map((capability, index) => (
                  <div key={index} className="border border-slate-200 rounded-lg p-6">
                    <capability.icon className="h-8 w-8 text-blue-600 mb-3" />
                    <h4 className="font-semibold text-slate-900 mb-2">{capability.title}</h4>
                    <p className="text-slate-600 text-sm mb-4">{capability.description}</p>
                    <div className="space-y-1">
                      {capability.endpoints.map((endpoint, idx) => (
                        <code key={idx} className="block text-xs bg-slate-100 px-2 py-1 rounded">
                          {endpoint}
                        </code>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Sample Code */}
            <motion.div 
              className="bg-white rounded-xl border border-slate-200 p-8"
              variants={fadeInUp} transition={{ duration: 0.6 }}
            >
              <h3 className="text-2xl font-bold text-slate-900 mb-6">Sample Code</h3>
              
              <div className="bg-slate-900 rounded-lg p-6 relative">
                <button
                  onClick={() => copyToClipboard(sampleCode, 'sample')}
                  className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
                >
                  {copiedCode === 'sample' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </button>
                <pre className="text-green-400 text-sm overflow-x-auto">
                  <code>{sampleCode}</code>
                </pre>
              </div>
            </motion.div>
          </motion.div>
        )}

        {activeTab === 'api-docs' && (
          <motion.div {...fadeInUp} className="space-y-8">
            <div className="flex justify-between items-center">
              <h2 className="text-3xl font-bold text-slate-900">API Reference</h2>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-slate-600">API Version: v1.0</span>
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                  Production Ready
                </span>
              </div>
            </div>

            {/* API Endpoints */}
            <div className="space-y-6">
              {apiEndpoints.map((section, index) => (
                <motion.div 
                  key={index}
                  className="bg-white rounded-xl border border-slate-200 p-8"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                >
                  <h3 className="text-xl font-bold text-slate-900 mb-4">{section.title}</h3>
                  <p className="text-slate-600 mb-6">{section.description}</p>
                  
                  <div className="space-y-4">
                    {section.endpoints.map((endpoint, idx) => (
                      <div key={idx} className="border border-slate-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              endpoint.method === 'GET' ? 'bg-blue-100 text-blue-800' :
                              endpoint.method === 'POST' ? 'bg-green-100 text-green-800' :
                              endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {endpoint.method}
                            </span>
                            <code className="text-sm font-mono">{endpoint.path}</code>
                          </div>
                          <button className="text-blue-600 hover:text-blue-800 text-sm">
                            Try it out →
                          </button>
                        </div>
                        <p className="text-sm text-slate-600 mb-3">{endpoint.description}</p>
                        
                        {endpoint.parameters && (
                          <div className="mb-3">
                            <h5 className="text-sm font-medium text-slate-900 mb-2">Parameters:</h5>
                            <div className="space-y-1">
                              {endpoint.parameters.map((param, paramIdx) => (
                                <div key={paramIdx} className="text-xs">
                                  <code className="bg-slate-100 px-1 py-0.5 rounded">{param.name}</code>
                                  <span className="text-slate-600 ml-2">{param.description}</span>
                                  {param.required && (
                                    <span className="text-red-500 ml-1">*required</span>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="bg-slate-50 rounded p-3">
                          <div className="flex items-center justify-between mb-2">
                            <h5 className="text-sm font-medium text-slate-900">Response Example:</h5>
                            <button
                              onClick={() => copyToClipboard(JSON.stringify(endpoint.response, null, 2), `response-${idx}`)}
                              className="text-slate-500 hover:text-slate-700"
                            >
                              {copiedCode === `response-${idx}` ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                            </button>
                          </div>
                          <pre className="text-xs text-slate-700 overflow-x-auto">
                            <code>{JSON.stringify(endpoint.response, null, 2)}</code>
                          </pre>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'sandbox' && (
          <APISandbox copiedCode={copiedCode} copyToClipboard={copyToClipboard} />
        )}

        {activeTab === 'sdks' && (
          <SDKsSection copiedCode={copiedCode} copyToClipboard={copyToClipboard} />
        )}

        {activeTab === 'webhooks' && (
          <WebhooksSection />
        )}

        {activeTab === 'guides' && (
          <GuidesSection />
        )}
      </div>
    </div>
  );
};

// Sample code for the overview
const sampleCode = `curl -X GET "https://api.trademate.com/v1/market-data" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"

// Response
{
  "success": true,
  "data": {
    "symbol": "NIFTY50",
    "price": 21545.50,
    "change": "+125.30",
    "changePercent": "+0.58%",
    "volume": 12456789,
    "timestamp": "2025-06-28T17:30:00Z"
  }
}`;

// API Endpoints data
const apiEndpoints = [
  {
    title: 'Market Data',
    description: 'Access real-time and historical market data for various instruments.',
    endpoints: [
      {
        method: 'GET',
        path: '/api/v1/market-data',
        description: 'Get real-time market data for specified symbols',
        parameters: [
          { name: 'symbols', description: 'Comma-separated list of symbols', required: true },
          { name: 'fields', description: 'Comma-separated list of fields to return', required: false }
        ],
        response: {
          success: true,
          data: [
            {
              symbol: 'NIFTY50',
              price: 21545.50,
              change: 125.30,
              changePercent: 0.58,
              volume: 12456789,
              timestamp: '2025-06-28T17:30:00Z'
            }
          ]
        }
      },
      {
        method: 'GET',
        path: '/api/v1/historical',
        description: 'Get historical price data with various time intervals',
        parameters: [
          { name: 'symbol', description: 'Symbol to fetch data for', required: true },
          { name: 'interval', description: 'Time interval (1m, 5m, 1h, 1d)', required: true },
          { name: 'from', description: 'Start date (ISO 8601)', required: true },
          { name: 'to', description: 'End date (ISO 8601)', required: false }
        ],
        response: {
          success: true,
          data: {
            symbol: 'NIFTY50',
            interval: '1h',
            candles: [
              {
                timestamp: '2025-06-28T09:00:00Z',
                open: 21420.00,
                high: 21580.50,
                low: 21395.25,
                close: 21545.50,
                volume: 1234567
              }
            ]
          }
        }
      }
    ]
  },
  {
    title: 'AI Insights',
    description: 'Get AI-powered market analysis and trading recommendations.',
    endpoints: [
      {
        method: 'POST',
        path: '/api/v1/analyze',
        description: 'Analyze market data and get AI-powered insights',
        parameters: [
          { name: 'symbols', description: 'Array of symbols to analyze', required: true },
          { name: 'timeframe', description: 'Analysis timeframe (1d, 1w, 1m)', required: false },
          { name: 'riskProfile', description: 'Risk profile (conservative, moderate, aggressive)', required: false }
        ],
        response: {
          success: true,
          data: {
            analysis: {
              sentiment: 'bullish',
              confidence: 0.85,
              signals: [
                {
                  type: 'buy',
                  symbol: 'NIFTY50',
                  strength: 'strong',
                  reasoning: 'Technical indicators show strong upward momentum'
                }
              ],
              riskLevel: 'moderate'
            }
          }
        }
      }
    ]
  },
  {
    title: 'WhatsApp Integration',
    description: 'Send messages and manage WhatsApp conversations.',
    endpoints: [
      {
        method: 'POST',
        path: '/api/v1/whatsapp/send',
        description: 'Send a WhatsApp message to a user',
        parameters: [
          { name: 'phone', description: 'Phone number in international format', required: true },
          { name: 'message', description: 'Message content', required: true },
          { name: 'type', description: 'Message type (text, template)', required: false }
        ],
        response: {
          success: true,
          data: {
            messageId: 'msg_123456789',
            status: 'sent',
            timestamp: '2025-06-28T17:30:00Z'
          }
        }
      }
    ]
  }
];

// API Sandbox Component
const APISandbox: React.FC<{ copiedCode: string | null; copyToClipboard: (text: string, label: string) => void }> = ({ copiedCode, copyToClipboard }) => {
  const [selectedEndpoint, setSelectedEndpoint] = useState('/api/v1/market-data');
  const [method, setMethod] = useState('GET');
  const [headers, setHeaders] = useState('{"Authorization": "Bearer YOUR_API_KEY", "Content-Type": "application/json"}');
  const [body, setBody] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTestAPI = async () => {
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const mockResponse = {
        success: true,
        data: {
          symbol: 'NIFTY50',
          price: 21545.50,
          change: 125.30,
          changePercent: 0.58,
          volume: 12456789,
          timestamp: new Date().toISOString()
        },
        requestId: 'req_' + Math.random().toString(36).substr(2, 9),
        responseTime: '142ms'
      };
      
      setResponse(JSON.stringify(mockResponse, null, 2));
      setLoading(false);
    }, 1000);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-8"
    >
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-slate-900">API Sandbox</h2>
        <div className="text-sm text-slate-600">
          Test API endpoints directly from your browser
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Request Panel */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Request</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Endpoint</label>
              <div className="flex space-x-2">
                <select 
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                  className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="DELETE">DELETE</option>
                </select>
                <input
                  type="text"
                  value={selectedEndpoint}
                  onChange={(e) => setSelectedEndpoint(e.target.value)}
                  className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="/api/v1/endpoint"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Headers</label>
              <textarea
                value={headers}
                onChange={(e) => setHeaders(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                placeholder='{"Authorization": "Bearer YOUR_API_KEY"}'
              />
            </div>

            {(method === 'POST' || method === 'PUT') && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Request Body</label>
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                  placeholder='{"key": "value"}'
                />
              </div>
            )}

            <button
              onClick={handleTestAPI}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Testing...' : 'Test API'}
            </button>
          </div>
        </div>

        {/* Response Panel */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Response</h3>
            {response && (
              <button
                onClick={() => copyToClipboard(response, 'sandbox-response')}
                className="text-slate-500 hover:text-slate-700 transition-colors"
              >
                {copiedCode === 'sandbox-response' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </button>
            )}
          </div>
          
          <div className="bg-slate-900 rounded-lg p-4 min-h-[300px]">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
              </div>
            ) : response ? (
              <pre className="text-green-400 text-sm overflow-auto">
                <code>{response}</code>
              </pre>
            ) : (
              <div className="flex items-center justify-center h-64 text-slate-500">
                Click "Test API" to see the response
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Examples */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Examples</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {[
            {
              title: 'Get Market Data',
              method: 'GET',
              endpoint: '/api/v1/market-data?symbols=NIFTY50,BANKNIFTY',
              description: 'Fetch real-time market data for multiple symbols'
            },
            {
              title: 'Send WhatsApp Message',
              method: 'POST',
              endpoint: '/api/v1/whatsapp/send',
              description: 'Send a trading alert via WhatsApp',
              body: '{"phone": "+919876543210", "message": "NIFTY50 is up 2.5% today!"}'
            },
            {
              title: 'Get AI Analysis',
              method: 'POST',
              endpoint: '/api/v1/analyze',
              description: 'Get AI-powered market analysis',
              body: '{"symbols": ["NIFTY50"], "timeframe": "1d"}'
            },
            {
              title: 'Create Subscription',
              method: 'POST',
              endpoint: '/api/v1/subscriptions',
              description: 'Create a new subscription for a user',
              body: '{"userId": "user_123", "plan": "PRO", "duration": "monthly"}'
            }
          ].map((example, index) => (
            <button
              key={index}
              onClick={() => {
                setMethod(example.method);
                setSelectedEndpoint(example.endpoint);
                if (example.body) setBody(example.body);
              }}
              className="text-left p-4 border border-slate-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div className="flex items-center space-x-2 mb-1">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  example.method === 'GET' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                }`}>
                  {example.method}
                </span>
                <span className="font-medium text-sm">{example.title}</span>
              </div>
              <p className="text-xs text-slate-600">{example.description}</p>
            </button>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

// SDKs Section Component
const SDKsSection: React.FC<{ copiedCode: string | null; copyToClipboard: (text: string, label: string) => void }> = ({ copiedCode, copyToClipboard }) => {
  const sdks = [
    {
      name: 'Node.js',
      description: 'Official Node.js SDK for server-side applications',
      install: 'npm install @trademate/node-sdk',
      example: `const TradeMate = require('@trademate/node-sdk');

const client = new TradeMate({
  apiKey: 'your-api-key'
});

// Get market data
const data = await client.marketData.get(['NIFTY50']);
console.log(data);`,
      github: 'https://github.com/trademate/node-sdk',
      docs: '/docs/sdks/nodejs'
    },
    {
      name: 'Python',
      description: 'Python SDK for data science and algorithmic trading',
      install: 'pip install trademate-python',
      example: `import trademate

client = trademate.Client(api_key='your-api-key')

# Get market data
data = client.market_data.get(['NIFTY50'])
print(data)`,
      github: 'https://github.com/trademate/python-sdk',
      docs: '/docs/sdks/python'
    },
    {
      name: 'React',
      description: 'React hooks and components for web applications',
      install: 'npm install @trademate/react',
      example: `import { useTradeMateMarketData } from '@trademate/react';

function MarketWidget() {
  const { data, loading } = useTradeMateMarketData(['NIFTY50']);
  
  if (loading) return <div>Loading...</div>;
  
  return <div>NIFTY50: {data.price}</div>;
}`,
      github: 'https://github.com/trademate/react-sdk',
      docs: '/docs/sdks/react'
    },
    {
      name: 'PHP',
      description: 'PHP SDK for Laravel and other PHP applications',
      install: 'composer require trademate/php-sdk',
      example: `<?php
use TradeMate\\Client;

$client = new Client('your-api-key');

// Get market data
$data = $client->marketData()->get(['NIFTY50']);
echo json_encode($data);`,
      github: 'https://github.com/trademate/php-sdk',
      docs: '/docs/sdks/php'
    }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-8"
    >
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-slate-900">SDKs & Libraries</h2>
        <div className="text-sm text-slate-600">
          Official SDKs for popular programming languages
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {sdks.map((sdk, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="bg-white rounded-xl border border-slate-200 p-6"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900">{sdk.name}</h3>
                <p className="text-slate-600 text-sm mt-1">{sdk.description}</p>
              </div>
              <div className="flex space-x-2">
                <a 
                  href={sdk.github}
                  className="text-slate-500 hover:text-slate-700 transition-colors"
                  title="View on GitHub"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-slate-900 mb-2">Installation</h4>
                <div className="bg-slate-900 rounded-lg p-3 relative">
                  <button
                    onClick={() => copyToClipboard(sdk.install, `install-${index}`)}
                    className="absolute top-2 right-2 text-slate-400 hover:text-white transition-colors"
                  >
                    {copiedCode === `install-${index}` ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                  </button>
                  <code className="text-green-400 text-sm">{sdk.install}</code>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-slate-900 mb-2">Example Usage</h4>
                <div className="bg-slate-900 rounded-lg p-3 relative">
                  <button
                    onClick={() => copyToClipboard(sdk.example, `example-${index}`)}
                    className="absolute top-2 right-2 text-slate-400 hover:text-white transition-colors"
                  >
                    {copiedCode === `example-${index}` ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                  </button>
                  <pre className="text-green-400 text-xs overflow-x-auto">
                    <code>{sdk.example}</code>
                  </pre>
                </div>
              </div>

              <div className="flex space-x-3">
                <a
                  href={sdk.docs}
                  className="flex-1 bg-blue-600 text-white text-center py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Documentation
                </a>
                <a
                  href={sdk.github}
                  className="flex-1 border border-slate-300 text-slate-700 text-center py-2 px-4 rounded-lg hover:bg-slate-50 transition-colors text-sm"
                >
                  GitHub
                </a>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Community SDKs */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="text-xl font-bold text-slate-900 mb-4">Community SDKs</h3>
        <p className="text-slate-600 mb-4">
          SDKs maintained by the community. Want to contribute? 
          <a href="#" className="text-blue-600 hover:text-blue-800 ml-1">Submit your SDK →</a>
        </p>
        
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { name: 'Go', author: 'community', status: 'Active' },
            { name: 'Rust', author: 'community', status: 'Beta' },
            { name: 'Swift', author: 'community', status: 'Coming Soon' },
            { name: 'C#', author: 'community', status: 'Active' },
            { name: 'Java', author: 'community', status: 'Beta' },
            { name: 'Flutter', author: 'community', status: 'Coming Soon' }
          ].map((sdk, index) => (
            <div key={index} className="border border-slate-200 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <h4 className="font-medium text-slate-900">{sdk.name}</h4>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  sdk.status === 'Active' ? 'bg-green-100 text-green-800' :
                  sdk.status === 'Beta' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-slate-100 text-slate-600'
                }`}>
                  {sdk.status}
                </span>
              </div>
              <p className="text-sm text-slate-600 mt-1">by {sdk.author}</p>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

// Webhooks Section Component
const WebhooksSection: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-8"
    >
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-slate-900">Webhooks</h2>
        <div className="text-sm text-slate-600">
          Real-time notifications for your applications
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        <h3 className="text-xl font-bold text-slate-900 mb-4">What are Webhooks?</h3>
        <p className="text-slate-600 mb-6">
          Webhooks allow TradeMate to notify your application when specific events occur. 
          Instead of polling our API, we'll send HTTP POST requests to your specified endpoint 
          whenever relevant events happen.
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Available Events</h4>
            <ul className="space-y-2">
              {[
                'market.price_alert',
                'subscription.created',
                'subscription.cancelled',
                'payment.completed',
                'payment.failed',
                'signal.generated',
                'user.registered',
                'whatsapp.message_received'
              ].map((event, index) => (
                <li key={index} className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                  <code className="text-sm">{event}</code>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Example Payload</h4>
            <div className="bg-slate-900 rounded-lg p-4">
              <pre className="text-green-400 text-xs overflow-x-auto">
                <code>{`{
  "event": "market.price_alert",
  "timestamp": "2025-06-28T17:30:00Z",
  "data": {
    "symbol": "NIFTY50",
    "price": 21545.50,
    "alertType": "price_above",
    "threshold": 21500.00,
    "userId": "user_123"
  },
  "webhook_id": "wh_abc123"
}`}</code>
              </pre>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        <h3 className="text-xl font-bold text-slate-900 mb-4">Webhook Configuration</h3>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Webhook URL</label>
            <input
              type="url"
              placeholder="https://yourapp.com/webhooks/trademate"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-sm text-slate-600 mt-1">
              The URL where we'll send webhook notifications
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Events</label>
            <div className="grid md:grid-cols-2 gap-2">
              {[
                'market.price_alert',
                'subscription.created',
                'subscription.cancelled',
                'payment.completed',
                'payment.failed',
                'signal.generated',
                'user.registered',
                'whatsapp.message_received'
              ].map((event, index) => (
                <label key={index} className="flex items-center space-x-2">
                  <input type="checkbox" className="rounded border-slate-300" />
                  <span className="text-sm">{event}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Secret Key</label>
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="wh_sec_..."
                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                readOnly
              />
              <button className="bg-slate-600 text-white px-4 py-2 rounded-lg hover:bg-slate-700 transition-colors">
                Generate
              </button>
            </div>
            <p className="text-sm text-slate-600 mt-1">
              Use this to verify webhook authenticity
            </p>
          </div>

          <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            Save Webhook Configuration
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        <h3 className="text-xl font-bold text-slate-900 mb-4">Testing Webhooks</h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Test Events</h4>
            <p className="text-slate-600 text-sm mb-4">
              Send test webhook events to verify your endpoint is working correctly.
            </p>
            
            <div className="space-y-3">
              <select className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <option>market.price_alert</option>
                <option>subscription.created</option>
                <option>payment.completed</option>
                <option>signal.generated</option>
              </select>
              
              <button className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                Send Test Event
              </button>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Recent Deliveries</h4>
            <div className="space-y-2">
              {[
                { event: 'market.price_alert', status: 'delivered', time: '2 mins ago' },
                { event: 'subscription.created', status: 'delivered', time: '5 mins ago' },
                { event: 'payment.completed', status: 'failed', time: '10 mins ago' }
              ].map((delivery, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div>
                    <code className="text-sm">{delivery.event}</code>
                    <p className="text-xs text-slate-600">{delivery.time}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    delivery.status === 'delivered' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {delivery.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// Guides Section Component
const GuidesSection: React.FC = () => {
  const guides = [
    {
      title: 'Getting Started',
      description: 'Complete guide to setting up your first TradeMate integration',
      readTime: '10 min read',
      category: 'Basics',
      url: '/guides/getting-started'
    },
    {
      title: 'Authentication',
      description: 'How to authenticate API requests and manage API keys',
      readTime: '5 min read',
      category: 'Security',
      url: '/guides/authentication'
    },
    {
      title: 'WhatsApp Integration',
      description: 'Build WhatsApp trading bots and notification systems',
      readTime: '15 min read',
      category: 'WhatsApp',
      url: '/guides/whatsapp-integration'
    },
    {
      title: 'Market Data Streaming',
      description: 'Real-time market data integration with WebSockets',
      readTime: '12 min read',
      category: 'Real-time',
      url: '/guides/market-data-streaming'
    },
    {
      title: 'AI Trading Signals',
      description: 'Integrate AI-powered trading signals into your application',
      readTime: '20 min read',
      category: 'AI',
      url: '/guides/ai-trading-signals'
    },
    {
      title: 'Billing Integration',
      description: 'Implement subscription billing and payment processing',
      readTime: '18 min read',
      category: 'Billing',
      url: '/guides/billing-integration'
    },
    {
      title: 'Error Handling',
      description: 'Best practices for handling API errors and rate limits',
      readTime: '8 min read',
      category: 'Best Practices',
      url: '/guides/error-handling'
    },
    {
      title: 'Webhooks Setup',
      description: 'Configure webhooks for real-time event notifications',
      readTime: '10 min read',
      category: 'Webhooks',
      url: '/guides/webhooks-setup'
    }
  ];

  const categories = ['All', 'Basics', 'Security', 'WhatsApp', 'Real-time', 'AI', 'Billing', 'Best Practices', 'Webhooks'];
  const [selectedCategory, setSelectedCategory] = useState('All');

  const filteredGuides = selectedCategory === 'All' 
    ? guides 
    : guides.filter(guide => guide.category === selectedCategory);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-8"
    >
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-slate-900">Developer Guides</h2>
        <div className="text-sm text-slate-600">
          Step-by-step tutorials and best practices
        </div>
      </div>

      {/* Categories Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCategory === category
                ? 'bg-blue-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Guides Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredGuides.map((guide, index) => (
          <motion.a
            key={index}
            href={guide.url}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-300 hover:shadow-lg transition-all duration-300 group"
          >
            <div className="flex justify-between items-start mb-3">
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {guide.category}
              </span>
              <ExternalLink className="h-4 w-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
            </div>
            
            <h3 className="text-lg font-semibold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
              {guide.title}
            </h3>
            
            <p className="text-slate-600 text-sm mb-4">
              {guide.description}
            </p>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">{guide.readTime}</span>
              <span className="text-blue-600 text-sm font-medium group-hover:underline">
                Read guide →
              </span>
            </div>
          </motion.a>
        ))}
      </div>

      {/* Featured Tutorial */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold mb-2">Build a Complete Trading Bot</h3>
            <p className="text-blue-100 mb-4">
              Follow our comprehensive tutorial to build a WhatsApp trading bot with AI signals, 
              real-time data, and automated notifications.
            </p>
            <div className="flex items-center space-x-4 text-sm">
              <span className="bg-white/20 px-3 py-1 rounded-full">45 min tutorial</span>
              <span className="bg-white/20 px-3 py-1 rounded-full">Beginner friendly</span>
              <span className="bg-white/20 px-3 py-1 rounded-full">Full source code</span>
            </div>
          </div>
          <div className="hidden lg:block">
            <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
              Start Tutorial
            </button>
          </div>
        </div>
        <div className="lg:hidden mt-6">
          <button className="w-full bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
            Start Tutorial
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default DeveloperPortal;