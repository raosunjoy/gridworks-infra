'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  Shield, 
  TrendingUp, 
  CreditCard, 
  Settings, 
  CheckCircle,
  Clock,
  Users,
  Globe,
  Zap
} from 'lucide-react';

interface ServiceTier {
  name: string;
  price: number;
  currency: string;
  billingPeriod: 'monthly' | 'annually';
  features: string[];
  limits: {
    requests: number;
    users: number;
    storage: string;
  };
  sla: {
    uptime: string;
    support: string;
    responseTime: string;
  };
}

interface ServiceConfig {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: 'ai-suite' | 'anonymous' | 'trading' | 'banking';
  status: 'available' | 'coming-soon' | 'beta';
  pricing: ServiceTier[];
  features: {
    name: string;
    description: string;
    included: boolean;
  }[];
  integrations: string[];
  compliance: string[];
  regions: string[];
}

const services: ServiceConfig[] = [
  {
    id: 'ai-suite',
    name: 'AI Suite Services',
    description: 'Multi-language AI support, market intelligence, and content moderation',
    icon: <Brain className="h-8 w-8" />,
    category: 'ai-suite',
    status: 'available',
    pricing: [
      {
        name: 'Professional',
        price: 25000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          '10,000 AI requests/month',
          '5 languages supported',
          'Basic market intelligence',
          'Email support'
        ],
        limits: {
          requests: 10000,
          users: 50,
          storage: '10GB'
        },
        sla: {
          uptime: '99.5%',
          support: '24/5',
          responseTime: '< 4 hours'
        }
      },
      {
        name: 'Enterprise',
        price: 100000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          'Unlimited AI requests',
          '11 languages supported',
          'Advanced market intelligence',
          'WhatsApp Business integration',
          'Priority support'
        ],
        limits: {
          requests: -1,
          users: 500,
          storage: '1TB'
        },
        sla: {
          uptime: '99.99%',
          support: '24/7',
          responseTime: '< 1 hour'
        }
      }
    ],
    features: [
      {
        name: 'Multi-language Support',
        description: 'AI support in 11 Indian and global languages',
        included: true
      },
      {
        name: 'Morning Pulse Intelligence',
        description: 'Pre-market analysis delivered at 7:30 AM IST',
        included: true
      },
      {
        name: 'Content Moderation',
        description: 'AI-powered spam and compliance checking',
        included: true
      },
      {
        name: 'WhatsApp Business Integration',
        description: 'Direct customer support via WhatsApp',
        included: false
      }
    ],
    integrations: ['WhatsApp Business', 'Telegram', 'Slack', 'Microsoft Teams'],
    compliance: ['GDPR', 'CCPA', 'Indian IT Act'],
    regions: ['India', 'US', 'EU', 'APAC']
  },
  {
    id: 'anonymous-services',
    name: 'Anonymous Services',
    description: 'World\'s first anonymous portfolio management with zero-knowledge proofs',
    icon: <Shield className="h-8 w-8" />,
    category: 'anonymous',
    status: 'available',
    pricing: [
      {
        name: 'Onyx Tier',
        price: 200000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          'Portfolio verification up to ₹2Cr',
          'Basic ZK proof generation',
          'Anonymous communication',
          'Butler AI (Sterling personality)'
        ],
        limits: {
          requests: 1000,
          users: 10,
          storage: '100GB'
        },
        sla: {
          uptime: '99.9%',
          support: '24/7',
          responseTime: '< 2 hours'
        }
      },
      {
        name: 'Obsidian Tier',
        price: 500000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          'Portfolio verification up to ₹5Cr',
          'Advanced ZK proof generation',
          'Anonymous deal flow sharing',
          'Butler AI (Prism personality)',
          'Emergency identity protocols'
        ],
        limits: {
          requests: 5000,
          users: 50,
          storage: '1TB'
        },
        sla: {
          uptime: '99.99%',
          support: '24/7',
          responseTime: '< 30 minutes'
        }
      },
      {
        name: 'Void Tier',
        price: 1500000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          'Unlimited portfolio verification',
          'Quantum-resistant encryption',
          'Elite anonymous networks',
          'Butler AI (Nexus personality)',
          'White-glove concierge service'
        ],
        limits: {
          requests: -1,
          users: 500,
          storage: '10TB'
        },
        sla: {
          uptime: '99.999%',
          support: '24/7',
          responseTime: '< 15 minutes'
        }
      }
    ],
    features: [
      {
        name: 'Zero-Knowledge Proofs',
        description: 'Cryptographic verification without revealing private data',
        included: true
      },
      {
        name: 'Anonymous Portfolio Management',
        description: 'Verify wealth without disclosing identity or holdings',
        included: true
      },
      {
        name: 'Butler AI Mediation',
        description: 'AI-powered anonymous investment assistance',
        included: true
      },
      {
        name: 'Emergency Identity Reveal',
        description: 'Progressive identity disclosure for compliance',
        included: false
      }
    ],
    integrations: ['Crypto Wallets', 'Banking APIs', 'Trading Platforms'],
    compliance: ['AML', 'KYC Progressive', 'FATCA', 'CRS'],
    regions: ['Global (Offshore)', 'Switzerland', 'Singapore', 'Dubai']
  },
  {
    id: 'trading-services',
    name: 'Trading-as-a-Service',
    description: 'Multi-exchange trading with advanced risk management',
    icon: <TrendingUp className="h-8 w-8" />,
    category: 'trading',
    status: 'available',
    pricing: [
      {
        name: 'Professional',
        price: 50000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          '10,000 trades/month',
          'NSE & BSE connectivity',
          'Basic risk management',
          'Real-time market data'
        ],
        limits: {
          requests: 10000,
          users: 100,
          storage: '50GB'
        },
        sla: {
          uptime: '99.9%',
          support: '24/5',
          responseTime: '< 2 hours'
        }
      },
      {
        name: 'Enterprise',
        price: 200000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          'Unlimited trades',
          'Global exchange connectivity',
          'Advanced risk engine',
          'Algorithmic trading support',
          'Dedicated account manager'
        ],
        limits: {
          requests: -1,
          users: 1000,
          storage: '5TB'
        },
        sla: {
          uptime: '99.99%',
          support: '24/7',
          responseTime: '< 30 minutes'
        }
      }
    ],
    features: [
      {
        name: 'Multi-Exchange Connectivity',
        description: 'Connect to NSE, BSE, MCX, and global exchanges',
        included: true
      },
      {
        name: 'Risk Management Engine',
        description: 'Real-time risk assessment and position monitoring',
        included: true
      },
      {
        name: 'Algorithmic Trading',
        description: 'Deploy custom trading algorithms with API access',
        included: false
      },
      {
        name: 'Regulatory Reporting',
        description: 'Automated compliance reporting to regulators',
        included: true
      }
    ],
    integrations: ['NSE', 'BSE', 'MCX', 'NASDAQ', 'NYSE', 'LSE'],
    compliance: ['SEBI', 'RBI', 'MiFID II', 'Dodd-Frank'],
    regions: ['India', 'US', 'EU', 'APAC']
  },
  {
    id: 'banking-services',
    name: 'Banking-as-a-Service',
    description: 'Complete digital banking infrastructure without banking license',
    icon: <CreditCard className="h-8 w-8" />,
    category: 'banking',
    status: 'available',
    pricing: [
      {
        name: 'Professional',
        price: 75000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          '10,000 transactions/month',
          'Multi-currency support',
          'Basic compliance tools',
          'API access'
        ],
        limits: {
          requests: 10000,
          users: 200,
          storage: '100GB'
        },
        sla: {
          uptime: '99.9%',
          support: '24/5',
          responseTime: '< 4 hours'
        }
      },
      {
        name: 'Enterprise',
        price: 300000,
        currency: 'INR',
        billingPeriod: 'monthly',
        features: [
          'Unlimited transactions',
          'Global payment networks',
          'Advanced KYC/AML',
          'Escrow services',
          'White-label solutions'
        ],
        limits: {
          requests: -1,
          users: 2000,
          storage: '10TB'
        },
        sla: {
          uptime: '99.99%',
          support: '24/7',
          responseTime: '< 1 hour'
        }
      }
    ],
    features: [
      {
        name: 'Payment Processing',
        description: 'Multi-currency payment processing with instant settlement',
        included: true
      },
      {
        name: 'Virtual Accounts',
        description: 'Create virtual accounts without banking license',
        included: true
      },
      {
        name: 'KYC/AML Automation',
        description: 'Automated compliance verification and reporting',
        included: true
      },
      {
        name: 'Escrow Services',
        description: 'Secure escrow for high-value transactions',
        included: false
      }
    ],
    integrations: ['SWIFT', 'ACH', 'UPI', 'RTGS', 'NEFT', 'Wire Transfer'],
    compliance: ['PCI DSS', 'RBI', 'AML', 'KYC', 'FEMA'],
    regions: ['India', 'US', 'EU', 'APAC']
  }
];

export default function ServiceCatalog() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedService, setSelectedService] = useState<ServiceConfig | null>(null);
  const [enabledServices, setEnabledServices] = useState<Set<string>>(new Set());

  const categories = [
    { id: 'all', name: 'All Services', icon: <Globe className="h-4 w-4" /> },
    { id: 'ai-suite', name: 'AI Suite', icon: <Brain className="h-4 w-4" /> },
    { id: 'anonymous', name: 'Anonymous', icon: <Shield className="h-4 w-4" /> },
    { id: 'trading', name: 'Trading', icon: <TrendingUp className="h-4 w-4" /> },
    { id: 'banking', name: 'Banking', icon: <CreditCard className="h-4 w-4" /> }
  ];

  const filteredServices = selectedCategory === 'all' 
    ? services 
    : services.filter(service => service.category === selectedCategory);

  const handleServiceToggle = (serviceId: string, enabled: boolean) => {
    const newEnabledServices = new Set(enabledServices);
    if (enabled) {
      newEnabledServices.add(serviceId);
    } else {
      newEnabledServices.delete(serviceId);
    }
    setEnabledServices(newEnabledServices);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      available: { label: 'Available', color: 'bg-green-100 text-green-800' },
      beta: { label: 'Beta', color: 'bg-blue-100 text-blue-800' },
      'coming-soon': { label: 'Coming Soon', color: 'bg-gray-100 text-gray-800' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig];
    return (
      <Badge className={config.color}>
        {config.label}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Service Catalog</h1>
          <p className="text-gray-600 mt-2">
            Discover and configure GridWorks B2B infrastructure services
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="outline" className="px-3 py-1">
            <Zap className="h-4 w-4 mr-2" />
            {enabledServices.size} Services Active
          </Badge>
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Bulk Configure
          </Button>
        </div>
      </div>

      {/* Category Filters */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
        <TabsList className="grid w-full grid-cols-5">
          {categories.map((category) => (
            <TabsTrigger 
              key={category.id} 
              value={category.id}
              className="flex items-center space-x-2"
            >
              {category.icon}
              <span>{category.name}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value={selectedCategory} className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredServices.map((service) => (
              <Card 
                key={service.id} 
                className="relative transition-all hover:shadow-lg cursor-pointer"
                onClick={() => setSelectedService(service)}
              >
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        {service.icon}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{service.name}</CardTitle>
                        {getStatusBadge(service.status)}
                      </div>
                    </div>
                    <Switch
                      checked={enabledServices.has(service.id)}
                      onCheckedChange={(checked) => handleServiceToggle(service.id, checked)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                  <CardDescription className="text-sm text-gray-600 mt-2">
                    {service.description}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Pricing Preview */}
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-sm text-gray-600">Starting from</div>
                    <div className="text-2xl font-bold text-gray-900">
                      ₹{service.pricing[0].price.toLocaleString()}
                      <span className="text-sm font-normal text-gray-600">
                        /{service.pricing[0].billingPeriod === 'monthly' ? 'month' : 'year'}
                      </span>
                    </div>
                  </div>

                  {/* Key Features */}
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-900">Key Features</div>
                    <div className="space-y-1">
                      {service.features.slice(0, 3).map((feature, index) => (
                        <div key={index} className="flex items-center space-x-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-gray-600">{feature.name}</span>
                        </div>
                      ))}
                      {service.features.length > 3 && (
                        <div className="text-sm text-blue-600">
                          +{service.features.length - 3} more features
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Regions */}
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Globe className="h-4 w-4" />
                    <span>{service.regions.length} regions available</span>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2 pt-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle demo request
                      }}
                    >
                      <Clock className="h-4 w-4 mr-2" />
                      Schedule Demo
                    </Button>
                    <Button 
                      size="sm" 
                      className="flex-1"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle service activation
                      }}
                    >
                      Configure
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Service Detail Modal would go here */}
      {selectedService && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto p-6">
            {/* Modal content for detailed service view */}
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-blue-100 rounded-lg">
                  {selectedService.icon}
                </div>
                <div>
                  <h2 className="text-2xl font-bold">{selectedService.name}</h2>
                  <p className="text-gray-600">{selectedService.description}</p>
                </div>
              </div>
              <Button 
                variant="ghost" 
                onClick={() => setSelectedService(null)}
              >
                ×
              </Button>
            </div>

            {/* Detailed service information would go here */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {selectedService.pricing.map((tier, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle>{tier.name}</CardTitle>
                    <div className="text-3xl font-bold">
                      ₹{tier.price.toLocaleString()}
                      <span className="text-sm font-normal text-gray-600">
                        /{tier.billingPeriod === 'monthly' ? 'month' : 'year'}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {tier.features.map((feature, i) => (
                        <li key={i} className="flex items-center space-x-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button className="w-full mt-4">
                      Select {tier.name}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}