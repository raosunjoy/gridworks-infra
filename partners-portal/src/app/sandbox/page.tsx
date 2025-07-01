'use client'

import { useState, useEffect } from 'react'
import { useAppStore } from '@/lib/store'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Play, 
  Code, 
  Database, 
  TestTube, 
  Copy,
  ExternalLink,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Zap
} from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function SandboxPage() {
  const { user, organization, sandboxMode, toggleSandboxMode, setSandboxData } = useAppStore()
  const [activeService, setActiveService] = useState<'ai-suite' | 'anonymous' | 'trading' | 'banking'>('ai-suite')
  const [testResults, setTestResults] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Mock sandbox environments
  const sandboxServices = {
    'ai-suite': {
      name: 'AI Suite Sandbox',
      description: 'Test AI-powered customer support and chat features',
      endpoints: [
        { method: 'POST', path: '/api/ai/chat', description: 'Send chat message to AI' },
        { method: 'POST', path: '/api/ai/support', description: 'Get support response' },
        { method: 'GET', path: '/api/ai/languages', description: 'List supported languages' }
      ],
      mockData: {
        chat: { message: 'Hello, how can I help you today?', language: 'en', userId: 'test-user' },
        support: { query: 'How do I integrate your API?', category: 'technical' }
      }
    },
    'anonymous': {
      name: 'Anonymous Services Sandbox',
      description: 'Test zero-knowledge proofs and privacy features',
      endpoints: [
        { method: 'POST', path: '/api/anonymous/proof', description: 'Generate zero-knowledge proof' },
        { method: 'POST', path: '/api/anonymous/verify', description: 'Verify anonymous transaction' },
        { method: 'GET', path: '/api/anonymous/status', description: 'Check privacy compliance status' }
      ],
      mockData: {
        proof: { data: 'sensitive_data_hash', proof_type: 'zk-stark' },
        verify: { transaction_id: 'tx_anonymous_123', amount: 10000 }
      }
    },
    'trading': {
      name: 'Trading Sandbox',
      description: 'Test trading APIs with simulated market data',
      endpoints: [
        { method: 'GET', path: '/api/trading/portfolio', description: 'Get portfolio data' },
        { method: 'POST', path: '/api/trading/order', description: 'Place trading order' },
        { method: 'GET', path: '/api/trading/markets', description: 'Get market data' }
      ],
      mockData: {
        portfolio: { userId: 'test-user' },
        order: { symbol: 'RELIANCE', quantity: 10, type: 'market', side: 'buy' }
      }
    },
    'banking': {
      name: 'Banking Sandbox',
      description: 'Test banking APIs with simulated accounts',
      endpoints: [
        { method: 'GET', path: '/api/banking/accounts', description: 'List bank accounts' },
        { method: 'POST', path: '/api/banking/transfer', description: 'Transfer funds' },
        { method: 'GET', path: '/api/banking/kyc', description: 'Check KYC status' }
      ],
      mockData: {
        transfer: { from_account: 'acc_123', to_account: 'acc_456', amount: 5000, currency: 'INR' },
        kyc: { customer_id: 'cust_test_123' }
      }
    }
  }

  const runTest = async (endpoint: any) => {
    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockResponse = {
        success: true,
        data: generateMockResponse(endpoint),
        timestamp: new Date().toISOString(),
        latency: Math.floor(Math.random() * 200) + 50
      }
      
      setTestResults(prev => [...prev, {
        id: Date.now(),
        endpoint: endpoint.path,
        method: endpoint.method,
        status: 'success',
        response: mockResponse,
        timestamp: new Date().toISOString()
      }])
    } catch (error) {
      setTestResults(prev => [...prev, {
        id: Date.now(),
        endpoint: endpoint.path,
        method: endpoint.method,
        status: 'error',
        error: 'Test failed',
        timestamp: new Date().toISOString()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockResponse = (endpoint: any) => {
    const service = sandboxServices[activeService]
    
    switch (endpoint.path) {
      case '/api/ai/chat':
        return {
          reply: 'Hello! I\'m the GridWorks AI assistant. How can I help you integrate our services today?',
          confidence: 0.95,
          language: 'en',
          session_id: 'session_' + Math.random().toString(36).substr(2, 9)
        }
      
      case '/api/ai/support':
        return {
          response: 'To integrate our API, start by obtaining your API key from the dashboard, then follow our quick start guide.',
          category: 'technical',
          suggested_actions: ['Read documentation', 'Try sandbox environment', 'Contact support'],
          confidence: 0.92
        }
      
      case '/api/trading/portfolio':
        return {
          total_value: 1250000,
          positions: [
            { symbol: 'RELIANCE', quantity: 50, current_price: 2450, pnl: 15000 },
            { symbol: 'TCS', quantity: 25, current_price: 3200, pnl: -2500 }
          ],
          cash_balance: 125000,
          currency: 'INR'
        }
      
      case '/api/banking/accounts':
        return {
          accounts: [
            { id: 'acc_123', type: 'savings', balance: 250000, currency: 'INR' },
            { id: 'acc_456', type: 'current', balance: 500000, currency: 'INR' }
          ]
        }
      
      default:
        return { message: 'Test successful', data: service.mockData }
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">GridWorks Sandbox</h1>
              <Badge variant="secondary" className="animate-pulse">
                <TestTube className="h-3 w-3 mr-1" />
                Testing Environment
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline">
                {organization?.name || 'Demo Organization'}
              </Badge>
              <Button variant="outline" onClick={toggleSandboxMode}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Reset Sandbox
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Service Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Available Services</CardTitle>
              <CardDescription>Select a service to test in the sandbox</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(sandboxServices).map(([serviceId, service]) => (
                <div
                  key={serviceId}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    activeService === serviceId ? 'bg-primary/10 border-primary' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setActiveService(serviceId as any)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{service.name}</p>
                      <p className="text-sm text-muted-foreground">{service.description}</p>
                    </div>
                    <Badge variant="outline">
                      {service.endpoints.length} APIs
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* API Testing */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>{sandboxServices[activeService].name}</CardTitle>
              <CardDescription>
                Test APIs with mock data and responses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="endpoints" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="endpoints">Endpoints</TabsTrigger>
                  <TabsTrigger value="docs">Documentation</TabsTrigger>
                  <TabsTrigger value="code">Code Examples</TabsTrigger>
                </TabsList>

                <TabsContent value="endpoints" className="space-y-4">
                  <div className="space-y-4">
                    {sandboxServices[activeService].endpoints.map((endpoint, index) => (
                      <Card key={index} className="border-l-4 border-l-blue-400">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-3">
                              <Badge variant={endpoint.method === 'GET' ? 'secondary' : 'default'}>
                                {endpoint.method}
                              </Badge>
                              <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                                {endpoint.path}
                              </code>
                            </div>
                            <Button 
                              size="sm" 
                              onClick={() => runTest(endpoint)}
                              disabled={isLoading}
                            >
                              <Play className="h-3 w-3 mr-1" />
                              Test
                            </Button>
                          </div>
                          <p className="text-sm text-muted-foreground">{endpoint.description}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="docs" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">API Documentation</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium mb-2">Authentication</h4>
                          <p className="text-sm text-muted-foreground mb-2">
                            Include your API key in the Authorization header:
                          </p>
                          <code className="block bg-gray-100 p-2 rounded text-xs">
                            Authorization: Bearer gw_sandbox_your_api_key_here
                          </code>
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-2">Base URL</h4>
                          <code className="block bg-gray-100 p-2 rounded text-xs">
                            https://api-sandbox.gridworks.com
                          </code>
                        </div>

                        <div>
                          <h4 className="font-medium mb-2">Rate Limits</h4>
                          <p className="text-sm text-muted-foreground">
                            Sandbox: 1,000 requests per hour<br />
                            Production: Based on your plan tier
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="code" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Code Examples</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">JavaScript/TypeScript</h4>
                            <Button variant="outline" size="sm" onClick={() => copyToClipboard(`
import { GridWorksSDK } from '@gridworks/b2b-sdk';

const client = new GridWorksSDK({
  apiKey: 'gw_sandbox_your_key',
  environment: 'sandbox'
});

// Test AI Chat
const response = await client.aiSuite.chat({
  message: 'Hello, how can I help?',
  language: 'en'
});

console.log(response.reply);
                            `)}>
                              <Copy className="h-3 w-3 mr-1" />
                              Copy
                            </Button>
                          </div>
                          <pre className="bg-gray-900 text-green-400 p-4 rounded text-xs overflow-x-auto">
{`import { GridWorksSDK } from '@gridworks/b2b-sdk';

const client = new GridWorksSDK({
  apiKey: 'gw_sandbox_your_key',
  environment: 'sandbox'
});

// Test AI Chat
const response = await client.aiSuite.chat({
  message: 'Hello, how can I help?',
  language: 'en'
});

console.log(response.reply);`}
                          </pre>
                        </div>

                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">Python</h4>
                            <Button variant="outline" size="sm" onClick={() => copyToClipboard(`
from gridworks_sdk import GridWorksSDK

client = GridWorksSDK(
    api_key="gw_sandbox_your_key",
    environment="sandbox"
)

# Test Trading API
portfolio = client.trading.get_portfolio()
print(f"Total value: ₹{portfolio.total_value}")
                            `)}>
                              <Copy className="h-3 w-3 mr-1" />
                              Copy
                            </Button>
                          </div>
                          <pre className="bg-gray-900 text-green-400 p-4 rounded text-xs overflow-x-auto">
{`from gridworks_sdk import GridWorksSDK

client = GridWorksSDK(
    api_key="gw_sandbox_your_key",
    environment="sandbox"
)

# Test Trading API
portfolio = client.trading.get_portfolio()
print(f"Total value: ₹{portfolio.total_value}")`}
                          </pre>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Test Results */}
        {testResults.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Test Results</CardTitle>
              <CardDescription>Recent API test executions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {testResults.slice(-10).reverse().map((result) => (
                  <div key={result.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <Badge variant={result.method === 'GET' ? 'secondary' : 'default'}>
                          {result.method}
                        </Badge>
                        <code className="text-sm">{result.endpoint}</code>
                        {result.status === 'success' ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-600" />
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {new Date(result.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    
                    {result.response && (
                      <div className="mt-3">
                        <div className="flex items-center space-x-2 mb-2">
                          <Zap className="h-3 w-3 text-blue-600" />
                          <span className="text-xs text-muted-foreground">
                            {result.response.latency}ms response time
                          </span>
                        </div>
                        <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                          {JSON.stringify(result.response.data, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}