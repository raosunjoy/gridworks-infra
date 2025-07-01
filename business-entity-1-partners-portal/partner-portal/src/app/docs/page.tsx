'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  BookOpenIcon, 
  CodeBracketIcon, 
  CogIcon, 
  KeyIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';

const sections = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: BookOpenIcon,
    items: [
      { title: 'Quick Start Guide', href: '/docs/quickstart' },
      { title: 'Authentication', href: '/docs/auth' },
      { title: 'API Overview', href: '/docs/api' },
      { title: 'SDK Installation', href: '/docs/sdk' },
    ]
  },
  {
    id: 'api-reference',
    title: 'API Reference',
    icon: CodeBracketIcon,
    items: [
      { title: 'REST API', href: '/docs/rest-api' },
      { title: 'WhatsApp API', href: '/docs/whatsapp' },
      { title: 'AI Chat API', href: '/docs/ai-chat' },
      { title: 'Webhooks', href: '/docs/webhooks' },
    ]
  },
  {
    id: 'integration',
    title: 'Integration Guides',
    icon: CogIcon,
    items: [
      { title: 'Web Integration', href: '/docs/web-integration' },
      { title: 'Mobile Integration', href: '/docs/mobile-integration' },
      { title: 'Backend Integration', href: '/docs/backend-integration' },
      { title: 'Testing', href: '/docs/testing' },
    ]
  },
  {
    id: 'security',
    title: 'Security',
    icon: ShieldCheckIcon,
    items: [
      { title: 'Zero-Knowledge Privacy', href: '/docs/privacy' },
      { title: 'API Security', href: '/docs/security' },
      { title: 'Compliance', href: '/docs/compliance' },
      { title: 'Data Protection', href: '/docs/data-protection' },
    ]
  }
];

const quickLinks = [
  {
    title: 'API Playground',
    description: 'Test API endpoints in real-time',
    href: '/developer',
    icon: CodeBracketIcon,
    external: false
  },
  {
    title: 'Sample Code',
    description: 'Ready-to-use code examples',
    href: 'https://github.com/trademate/examples',
    icon: DocumentTextIcon,
    external: true
  },
  {
    title: 'Support Forum',
    description: 'Get help from community',
    href: '/contact',
    icon: ChatBubbleLeftRightIcon,
    external: false
  },
  {
    title: 'API Keys',
    description: 'Manage your API credentials',
    href: '/dashboard/api-keys',
    icon: KeyIcon,
    external: false
  }
];

export default function DocsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <span className="text-xl font-semibold text-gray-900">TradeMate</span>
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                Docs
              </span>
            </Link>
            <Link 
              href="/dashboard"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Developer Documentation
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Everything you need to integrate TradeMate's AI-powered fintech solutions. 
            Get started with our APIs, SDKs, and comprehensive guides.
          </p>
          
          {/* Search */}
          <div className="max-w-md mx-auto">
            <div className="relative">
              <input
                type="text"
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-3 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Start</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickLinks.map((link) => (
              <Link
                key={link.title}
                href={link.href}
                className="bg-white p-6 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all group"
                {...(link.external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
              >
                <div className="flex items-center justify-between mb-3">
                  <link.icon className="h-6 w-6 text-blue-600" />
                  {link.external && (
                    <ArrowTopRightOnSquareIcon className="h-4 w-4 text-gray-400 group-hover:text-blue-600" />
                  )}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{link.title}</h3>
                <p className="text-sm text-gray-600">{link.description}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* Documentation Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {sections.map((section) => (
            <div key={section.id} className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center mb-4">
                <section.icon className="h-6 w-6 text-blue-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">{section.title}</h3>
              </div>
              <div className="space-y-3">
                {section.items.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="block p-3 rounded-lg hover:bg-gray-50 transition-colors group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-gray-700 group-hover:text-blue-600">{item.title}</span>
                      <ArrowTopRightOnSquareIcon className="h-4 w-4 text-gray-400 group-hover:text-blue-600" />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Popular Topics */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Popular Topics</h2>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Authentication</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link href="/docs/auth/oauth" className="text-blue-600 hover:text-blue-800">OAuth 2.0 Setup</Link></li>
                  <li><Link href="/docs/auth/api-keys" className="text-blue-600 hover:text-blue-800">API Key Management</Link></li>
                  <li><Link href="/docs/auth/jwt" className="text-blue-600 hover:text-blue-800">JWT Tokens</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">WhatsApp Integration</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link href="/docs/whatsapp/setup" className="text-blue-600 hover:text-blue-800">Initial Setup</Link></li>
                  <li><Link href="/docs/whatsapp/messages" className="text-blue-600 hover:text-blue-800">Sending Messages</Link></li>
                  <li><Link href="/docs/whatsapp/templates" className="text-blue-600 hover:text-blue-800">Message Templates</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">AI Features</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link href="/docs/ai/chat" className="text-blue-600 hover:text-blue-800">AI Chat Integration</Link></li>
                  <li><Link href="/docs/ai/languages" className="text-blue-600 hover:text-blue-800">Multi-language Support</Link></li>
                  <li><Link href="/docs/ai/customization" className="text-blue-600 hover:text-blue-800">AI Customization</Link></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Support Section */}
        <div className="mt-16 bg-blue-50 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Need Help?</h2>
          <p className="text-gray-600 mb-6">
            Can't find what you're looking for? Our support team is here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/contact"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Contact Support
            </Link>
            <Link 
              href="https://github.com/trademate/examples"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white text-blue-600 border border-blue-600 px-6 py-3 rounded-lg hover:bg-blue-50 transition-colors"
            >
              View Examples
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}