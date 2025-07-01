'use client';

import { useState } from 'react';
import Link from 'next/link';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid';
import { 
  CurrencyRupeeIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  BoltIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';

const plans = [
  {
    name: 'Starter',
    tier: 'starter',
    price: 'Free',
    period: 'forever',
    description: 'Perfect for startups and small businesses getting started with AI support.',
    features: [
      'Up to 1,000 API calls/month',
      'WhatsApp Business API',
      'Basic AI chat support',
      '2 Indian languages',
      'Email support',
      'Basic analytics',
      'Standard rate limits'
    ],
    notIncluded: [
      'Advanced AI features',
      'Priority support',
      'Custom integrations',
      'Dedicated account manager'
    ],
    cta: 'Get Started Free',
    popular: false,
    color: 'gray'
  },
  {
    name: 'Professional',
    tier: 'professional',
    price: '₹4,999',
    period: 'per month',
    description: 'Ideal for growing fintech companies with moderate API usage.',
    features: [
      'Up to 50,000 API calls/month',
      'WhatsApp Business API',
      'Advanced AI chat with context',
      'All 11 Indian languages',
      'Priority email support',
      'Advanced analytics & insights',
      'Higher rate limits',
      'Custom webhooks',
      'Basic compliance tools'
    ],
    notIncluded: [
      'Dedicated infrastructure',
      'Custom AI training',
      'White-label solutions'
    ],
    cta: 'Start Free Trial',
    popular: true,
    color: 'blue'
  },
  {
    name: 'Enterprise',
    tier: 'enterprise',
    price: '₹19,999',
    period: 'per month',
    description: 'For large fintech companies requiring enterprise-grade solutions.',
    features: [
      'Unlimited API calls',
      'WhatsApp Business API',
      'Premium AI with custom training',
      'All 11 Indian languages + custom',
      '24/7 phone & chat support',
      'Enterprise analytics & BI',
      'No rate limits',
      'Custom integrations',
      'Advanced compliance & audit',
      'Dedicated account manager',
      'SLA guarantees (99.9% uptime)',
      'White-label options'
    ],
    notIncluded: [],
    cta: 'Contact Sales',
    popular: false,
    color: 'purple'
  }
];

const features = [
  {
    name: 'Multi-language Support',
    icon: GlobeAltIcon,
    description: 'Native support for 11 Indian languages with cultural context understanding.'
  },
  {
    name: 'Zero-Knowledge Privacy',
    icon: ShieldCheckIcon,
    description: 'Enterprise-grade security with end-to-end encryption and zero data retention.'
  },
  {
    name: 'AI-Powered Support',
    icon: ChatBubbleLeftRightIcon,
    description: 'Advanced conversational AI trained specifically for Indian fintech scenarios.'
  },
  {
    name: 'Lightning Fast',
    icon: BoltIcon,
    description: 'Sub-second response times with 99.9% uptime SLA for enterprise customers.'
  },
  {
    name: 'Scalable Infrastructure',
    icon: UserGroupIcon,
    description: 'Auto-scaling infrastructure that grows with your business needs.'
  },
  {
    name: 'Cost Effective',
    icon: CurrencyRupeeIcon,
    description: 'Transparent pricing with no hidden costs. Pay only for what you use.'
  }
];

const faqs = [
  {
    question: 'What is included in the free plan?',
    answer: 'The free plan includes 1,000 API calls per month, basic WhatsApp integration, AI chat support in 2 Indian languages, and email support. Perfect for testing and small-scale implementations.'
  },
  {
    question: 'Can I upgrade or downgrade my plan anytime?',
    answer: 'Yes, you can change your plan at any time. Upgrades take effect immediately, while downgrades take effect at the next billing cycle. You\'ll only pay for the time you use.'
  },
  {
    question: 'Do you offer custom enterprise solutions?',
    answer: 'Absolutely! Our Enterprise plan includes custom integrations, dedicated infrastructure, and white-label solutions. Contact our sales team to discuss your specific requirements.'
  },
  {
    question: 'What languages are supported?',
    answer: 'We support all 11 major Indian languages: Hindi, English, Bengali, Telugu, Marathi, Tamil, Gujarati, Urdu, Kannada, Odia, and Punjabi. Enterprise customers can request additional language support.'
  },
  {
    question: 'Is there a free trial for paid plans?',
    answer: 'Yes! We offer a 14-day free trial for all paid plans. No credit card required. You can explore all features and see how TradeMate fits your needs.'
  },
  {
    question: 'What kind of support do you provide?',
    answer: 'Support varies by plan: Starter gets email support, Professional gets priority email support, and Enterprise gets 24/7 phone and chat support with a dedicated account manager.'
  }
];

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">TM</span>
              </div>
              <span className="text-xl font-semibold text-gray-900">TradeMate</span>
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
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Choose the perfect plan for your fintech business. Start free and scale as you grow. 
            No hidden fees, no long-term contracts.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center mb-12">
            <span className={`mr-3 ${billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`ml-3 ${billingCycle === 'yearly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Yearly
            </span>
            {billingCycle === 'yearly' && (
              <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                Save 20%
              </span>
            )}
          </div>
        </div>

        {/* Pricing Plans */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          {plans.map((plan) => (
            <div
              key={plan.tier}
              className={`relative bg-white rounded-2xl shadow-sm border-2 ${
                plan.popular 
                  ? 'border-blue-500 ring-2 ring-blue-500 ring-opacity-50' 
                  : 'border-gray-200'
              } p-8`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                  {plan.period !== 'forever' && (
                    <span className="text-gray-500 ml-1">/{plan.period}</span>
                  )}
                </div>
                <p className="text-gray-600">{plan.description}</p>
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <CheckIcon className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
                {plan.notIncluded.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <XMarkIcon className="h-5 w-5 text-gray-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-400">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                  plan.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>

        {/* Features Section */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything you need to scale your fintech business
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built specifically for Indian fintech companies with enterprise-grade security, 
              multi-language support, and AI-powered customer engagement.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div key={feature.name} className="bg-white p-6 rounded-lg border border-gray-200">
                <feature.icon className="h-8 w-8 text-blue-600 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.name}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about our pricing and plans.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            {faqs.map((faq, index) => (
              <div key={index} className="border-b border-gray-200 py-6">
                <button
                  onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                  className="flex items-center justify-between w-full text-left"
                >
                  <span className="text-lg font-medium text-gray-900">{faq.question}</span>
                  <span className="ml-6 flex-shrink-0">
                    {expandedFaq === index ? (
                      <XMarkIcon className="h-6 w-6 text-gray-400" />
                    ) : (
                      <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                    )}
                  </span>
                </button>
                {expandedFaq === index && (
                  <div className="mt-4">
                    <p className="text-gray-600">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-blue-600 rounded-2xl p-8 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of fintech companies already using TradeMate to power their customer engagement.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/signup"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Start Free Trial
            </Link>
            <Link
              href="/contact"
              className="bg-blue-700 text-white border border-blue-400 px-8 py-3 rounded-lg font-medium hover:bg-blue-800 transition-colors"
            >
              Contact Sales
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}