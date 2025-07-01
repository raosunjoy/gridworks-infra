'use client'

import { useState, useEffect, useRef } from 'react'
import { useAppStore } from '@/lib/store'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  MessageCircle, 
  X, 
  Send, 
  Bot, 
  User, 
  Minimize2, 
  Maximize2,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  BookOpen,
  Code,
  HelpCircle
} from 'lucide-react'

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
  type?: 'text' | 'code' | 'link' | 'suggestion'
  suggestions?: string[]
  links?: { title: string; url: string }[]
}

export default function AiChatWidget() {
  const { 
    chatOpen, 
    chatMessages, 
    toggleChat, 
    addChatMessage, 
    clearChat,
    user,
    organization 
  } = useAppStore()
  
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (chatOpen && messages.length === 0) {
      // Welcome message
      const welcomeMessage: Message = {
        id: 'welcome-' + Date.now(),
        content: `Hi ${user?.name || 'there'}! I'm the GridWorks AI Assistant. I'm here to help you with:\n\n• API integration questions\n• Service documentation\n• Troubleshooting issues\n• Billing and account questions\n\nWhat can I help you with today?`,
        isUser: false,
        timestamp: new Date(),
        type: 'text',
        suggestions: [
          'How do I integrate the AI Suite API?',
          'What are the rate limits?',
          'Show me code examples',
          'Help with API authentication'
        ]
      }
      setMessages([welcomeMessage])
    }
  }, [chatOpen, user?.name, messages.length])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: 'user-' + Date.now(),
      content: input,
      isUser: true,
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = generateAiResponse(input)
      setMessages(prev => [...prev, aiResponse])
      setIsTyping(false)
    }, 1000 + Math.random() * 2000)
  }

  const generateAiResponse = (userInput: string): Message => {
    const input = userInput.toLowerCase()
    
    // API Integration
    if (input.includes('api') || input.includes('integrate')) {
      return {
        id: 'ai-' + Date.now(),
        content: `I'd be happy to help you with API integration! Here's a quick overview:\n\n**Getting Started:**\n1. Create an API key in the API Keys section\n2. Choose your environment (sandbox/production)\n3. Install our SDK\n\nWhich service are you looking to integrate?`,
        isUser: false,
        timestamp: new Date(),
        type: 'text',
        suggestions: [
          'AI Suite integration',
          'Trading API setup',
          'Banking services',
          'Show me code examples'
        ],
        links: [
          { title: 'API Documentation', url: '/docs' },
          { title: 'Create API Key', url: '/api-keys' },
          { title: 'Sandbox Environment', url: '/sandbox' }
        ]
      }
    }

    // Authentication
    if (input.includes('auth') || input.includes('key')) {
      return {
        id: 'ai-' + Date.now(),
        content: `**API Authentication Guide:**\n\nFor all API requests, include your API key in the Authorization header:\n\n\`\`\`\nAuthorization: Bearer gw_your_api_key_here\n\`\`\`\n\n**Important:**\n• Use sandbox keys for testing\n• Keep production keys secure\n• Rotate keys regularly`,
        isUser: false,
        timestamp: new Date(),
        type: 'code',
        suggestions: [
          'Create new API key',
          'Sandbox vs Production',
          'Key security best practices'
        ]
      }
    }

    // Rate Limits
    if (input.includes('rate') || input.includes('limit')) {
      return {
        id: 'ai-' + Date.now(),
        content: `**Rate Limits by Plan:**\n\n• **Professional:** 10,000 requests/month\n• **Enterprise:** Unlimited requests\n• **UHNW:** Unlimited + priority\n\n**Sandbox:** 1,000 requests/hour\n\nYour current plan: ${organization?.plan || 'Professional'}`,
        isUser: false,
        timestamp: new Date(),
        type: 'text',
        suggestions: [
          'Upgrade my plan',
          'Monitor usage',
          'View pricing'
        ]
      }
    }

    // Code Examples
    if (input.includes('code') || input.includes('example')) {
      return {
        id: 'ai-' + Date.now(),
        content: `**Quick Code Example:**\n\n\`\`\`javascript\nimport { GridWorksSDK } from '@gridworks/b2b-sdk';\n\nconst client = new GridWorksSDK({\n  apiKey: 'your-api-key',\n  environment: 'sandbox'\n});\n\n// AI Chat Example\nconst response = await client.aiSuite.chat({\n  message: 'Hello',\n  language: 'en'\n});\n\nconsole.log(response.reply);\n\`\`\``,
        isUser: false,
        timestamp: new Date(),
        type: 'code',
        suggestions: [
          'Python examples',
          'More API examples',
          'Try in sandbox'
        ]
      }
    }

    // Billing
    if (input.includes('billing') || input.includes('price')) {
      return {
        id: 'ai-' + Date.now(),
        content: `**Billing Information:**\n\nYour current plan: **${organization?.plan || 'Professional'}**\n\n• Billing is monthly\n• Usage-based pricing\n• No setup fees\n\nWould you like to see pricing details or upgrade options?`,
        isUser: false,
        timestamp: new Date(),
        type: 'text',
        suggestions: [
          'View detailed pricing',
          'Upgrade plan',
          'Usage analytics',
          'Contact billing support'
        ]
      }
    }

    // Default response
    return {
      id: 'ai-' + Date.now(),
      content: `I understand you're asking about "${userInput}". Let me help you with that!\n\nFor specific technical questions, I recommend:\n\n• Checking our documentation\n• Trying the sandbox environment\n• Contacting our support team for complex issues\n\nWhat specific aspect would you like me to explain?`,
      isUser: false,
      timestamp: new Date(),
      type: 'text',
      suggestions: [
        'API documentation',
        'Contact support',
        'Try sandbox',
        'View tutorials'
      ]
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion)
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  if (!chatOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={toggleChat}
          className="rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all duration-300 bg-primary hover:bg-primary/90"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      </div>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Card className={`w-96 shadow-2xl transition-all duration-300 ${
        isMinimized ? 'h-16' : 'h-[600px]'
      }`}>
        <CardHeader className="flex flex-row items-center justify-between p-4 bg-primary text-primary-foreground rounded-t-lg">
          <div className="flex items-center space-x-2">
            <Bot className="h-5 w-5" />
            <div>
              <CardTitle className="text-sm font-medium">GridWorks AI Assistant</CardTitle>
              <div className="flex items-center space-x-1 text-xs opacity-90">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>Online</span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-primary-foreground hover:bg-primary-foreground/20"
              onClick={() => setIsMinimized(!isMinimized)}
            >
              {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-primary-foreground hover:bg-primary-foreground/20"
              onClick={toggleChat}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        {!isMinimized && (
          <CardContent className="flex flex-col h-[536px] p-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3 ${
                      message.isUser
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {!message.isUser && <Bot className="h-4 w-4 mt-1 text-primary" />}
                      {message.isUser && <User className="h-4 w-4 mt-1" />}
                      <div className="flex-1">
                        <div className="text-sm whitespace-pre-wrap">
                          {message.content}
                        </div>
                        
                        {message.links && (
                          <div className="mt-2 space-y-1">
                            {message.links.map((link, index) => (
                              <Button
                                key={index}
                                variant="outline"
                                size="sm"
                                className="h-6 text-xs mr-1"
                                onClick={() => window.open(link.url, '_blank')}
                              >
                                <BookOpen className="h-3 w-3 mr-1" />
                                {link.title}
                              </Button>
                            ))}
                          </div>
                        )}

                        {!message.isUser && (
                          <div className="flex items-center justify-between mt-2">
                            <div className="text-xs opacity-70">
                              {message.timestamp.toLocaleTimeString()}
                            </div>
                            <div className="flex items-center space-x-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={() => copyMessage(message.content)}
                              >
                                <Copy className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                              >
                                <ThumbsUp className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                              >
                                <ThumbsDown className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Suggestions */}
              {messages.length > 0 && messages[messages.length - 1].suggestions && !messages[messages.length - 1].isUser && (
                <div className="flex flex-wrap gap-2">
                  {messages[messages.length - 1].suggestions?.map((suggestion, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="h-7 text-xs"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      {suggestion}
                    </Button>
                  ))}
                </div>
              )}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3 max-w-[85%]">
                    <div className="flex items-center space-x-2">
                      <Bot className="h-4 w-4 text-primary" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your question..."
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  className="flex-1"
                />
                <Button onClick={sendMessage} disabled={!input.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center justify-between mt-2">
                <div className="text-xs text-muted-foreground">
                  Powered by GridWorks AI
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 text-xs"
                    onClick={clearChat}
                  >
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Clear
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 text-xs"
                    onClick={() => window.open('/support', '_blank')}
                  >
                    <HelpCircle className="h-3 w-3 mr-1" />
                    Support
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  )
}