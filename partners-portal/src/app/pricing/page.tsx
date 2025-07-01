'use client'

import { useState, useEffect } from 'react'
import { useAppStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { CheckCircle, ArrowRight, Minus, Plus } from 'lucide-react'
import Link from 'next/link'

export default function PricingPage() {
  const { selectedServices, toggleService, pricingCalculation, calculatePricing } = useAppStore()
  const [selectedPlan, setSelectedPlan] = useState<'professional' | 'enterprise' | 'uhnw'>('professional')

  useEffect(() => {
    calculatePricing()
  }, [selectedServices, calculatePricing])

  const serviceConfigs = [
    {
      id: 'ai-suite' as const,
      name: 'AI Suite Services',
      description: 'Multi-language AI support, chat, and automation',
      basePrice: 15000,
      features: ['11 Language Support', 'OpenAI & Claude Integration', '24/7 AI Chat', 'Sentiment Analysis'],
      icon: '🤖'
    },
    {
      id: 'anonymous' as const,
      name: 'Anonymous Services',
      description: 'Zero-knowledge proofs and privacy solutions',
      basePrice: 20000,
      features: ['Zero-Knowledge Proofs', 'Anonymous Transactions', 'Privacy Compliance', 'Quantum-Resistant Encryption'],
      icon: '🔒'
    },
    {
      id: 'trading' as const,
      name: 'Trading-as-a-Service',
      description: 'Global exchange connectivity and trading infrastructure',
      basePrice: 25000,
      features: ['NSE/BSE Integration', 'Global Exchanges', 'Real-time Data', 'Risk Management'],
      icon: '📈'
    },
    {
      id: 'banking' as const,
      name: 'Banking-as-a-Service',
      description: 'Complete banking infrastructure and compliance',
      basePrice: 30000,
      features: ['Multi-currency Support', 'KYC/AML Automation', 'Payment Processing', 'Regulatory Compliance'],
      icon: '🏦'
    }
  ]

  const pricingTiers = [
    {
      name: "Professional",
      id: "professional" as const,
      basePrice: 25000,
      description: "Perfect for growing companies",
      popular: false,
      discount: 0,
      features: [
        "10,000 API requests/month",
        "Basic AI support (5 languages)",
        "NSE & BSE trading connectivity",
        "Multi-currency payments",
        "Email support",
        "99.5% uptime SLA"
      ]
    },
    {
      name: "Enterprise",
      id: "enterprise" as const,
      basePrice: 50000,
      description: "For large organizations",
      popular: true,
      discount: 0.15,
      features: [
        "Unlimited API requests",
        "Advanced AI support (11 languages)",
        "Global exchange connectivity",
        "Advanced KYC/AML automation",
        "24/7 priority support",
        "99.99% uptime SLA",
        "Dedicated account manager"
      ]
    },
    {
      name: "UHNW",
      id: "uhnw" as const,
      basePrice: 100000,
      description: "Ultra High Net Worth services",
      popular: false,
      discount: 0.25,
      features: [
        "Anonymous portfolio management",
        "Zero-knowledge proof verification",
        "Butler AI assistance",
        "Quantum-resistant encryption",
        "White-glove concierge service",
        "99.999% uptime SLA",
        "On-site support available"
      ]
    }
  ]

  const calculatePrice = (plan: typeof pricingTiers[0]) => {
    const selectedServicePrices = serviceConfigs
      .filter(service => selectedServices.includes(service.id))
      .reduce((sum, service) => sum + service.basePrice, 0)
    
    const totalBase = plan.basePrice + selectedServicePrices
    const discount = totalBase * plan.discount
    const volumeDiscount = selectedServices.length >= 3 ? totalBase * 0.1 : 0
    
    return {
      base: totalBase,
      discount: discount + volumeDiscount,
      final: totalBase - discount - volumeDiscount
    }
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <Link href="/">
                <h1 className="text-2xl font-bold cursor-pointer">GridWorks</h1>
              </Link>
              <div className="hidden md:flex items-center space-x-6">
                <Link href="/services" className="text-sm font-medium hover:text-primary">Services</Link>
                <Link href="/pricing" className="text-sm font-medium text-primary border-b-2 border-primary">Pricing</Link>
                <Link href="/docs" className="text-sm font-medium hover:text-primary">Documentation</Link>
                <Link href="/support" className="text-sm font-medium hover:text-primary">Support</Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth/signin">
                <Button variant="outline">Sign In</Button>
              </Link>
              <Link href="/auth/signup">
                <Button>Get Started</Button>
              </Link>
            </div>
          </nav>
        </div>
      </header>

      {/* Pricing Content */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold mb-6">Flexible, Service-Based Pricing</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Build your perfect plan by selecting only the services you need. Pay for what you use.
            </p>
          </div>

          {/* Service Selection */}
          <div className="mb-16">
            <h2 className="text-2xl font-bold text-center mb-8">Choose Your Services</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
              {serviceConfigs.map((service) => (
                <Card key={service.id} className={`cursor-pointer transition-all ${
                  selectedServices.includes(service.id) 
                    ? 'ring-2 ring-primary bg-primary/5' 
                    : 'hover:shadow-lg'
                }`} onClick={() => toggleService(service.id)}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="text-2xl">{service.icon}</div>
                      <Switch checked={selectedServices.includes(service.id)} />
                    </div>
                    <CardTitle className="text-lg">{service.name}</CardTitle>
                    <div className="text-xl font-bold text-primary">
                      ₹{service.basePrice.toLocaleString()}/month
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="mb-3">{service.description}</CardDescription>
                    <ul className="space-y-1">
                      {service.features.slice(0, 3).map((feature, i) => (
                        <li key={i} className="text-xs text-muted-foreground flex items-center">
                          <CheckCircle className="h-3 w-3 mr-1 text-green-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Plan Selection */}
          <div className="mb-16">
            <h2 className="text-2xl font-bold text-center mb-8">Select Your Plan Tier</h2>
            <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {pricingTiers.map((tier) => {
                const pricing = calculatePrice(tier)
                return (
                  <Card key={tier.id} className={`relative cursor-pointer transition-all ${
                    tier.popular ? 'ring-2 ring-primary' : ''
                  } ${selectedPlan === tier.id ? 'bg-primary/5' : ''}`} 
                  onClick={() => setSelectedPlan(tier.id)}>
                    {tier.popular && (
                      <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary text-primary-foreground">
                        Most Popular
                      </Badge>
                    )}
                    <CardHeader className="text-center">
                      <CardTitle className="text-2xl">{tier.name}</CardTitle>
                      <div className="space-y-1">
                        <div className="text-lg text-muted-foreground">Base Plan</div>
                        <div className="text-2xl font-bold">₹{tier.basePrice.toLocaleString()}/month</div>
                        {tier.discount > 0 && (
                          <Badge variant="outline" className="text-green-600">
                            {Math.round(tier.discount * 100)}% discount
                          </Badge>
                        )}
                      </div>
                      <CardDescription>{tier.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <ul className="space-y-2">
                        {tier.features.map((feature, i) => (
                          <li key={i} className="flex items-center space-x-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>

          {/* Pricing Calculator */}
          <div className="max-w-4xl mx-auto">
            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">Your Custom Quote</CardTitle>
                <CardDescription>Based on your selected services and plan tier</CardDescription>
              </CardHeader>
              <CardContent>
                {selectedServices.length > 0 ? (
                  <div className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium mb-3">Selected Services</h4>
                        <div className="space-y-2">
                          {serviceConfigs
                            .filter(service => selectedServices.includes(service.id))
                            .map(service => (
                              <div key={service.id} className="flex justify-between items-center">
                                <span className="text-sm">{service.name}</span>
                                <span className="font-medium">₹{service.basePrice.toLocaleString()}</span>
                              </div>
                            ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-3">Plan Benefits</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-sm">Base Plan ({pricingTiers.find(p => p.id === selectedPlan)?.name})</span>
                            <span className="font-medium">₹{pricingTiers.find(p => p.id === selectedPlan)?.basePrice.toLocaleString()}</span>
                          </div>
                          {pricingTiers.find(p => p.id === selectedPlan)?.discount > 0 && (
                            <div className="flex justify-between items-center text-green-600">
                              <span className="text-sm">Plan Discount</span>
                              <span className="font-medium">-₹{(calculatePrice(pricingTiers.find(p => p.id === selectedPlan)!).discount).toLocaleString()}</span>
                            </div>
                          )}
                          {selectedServices.length >= 3 && (
                            <div className="flex justify-between items-center text-green-600">
                              <span className="text-sm">Volume Discount (3+ services)</span>
                              <span className="font-medium">-10%</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="border-t pt-4">
                      <div className="flex justify-between items-center text-lg font-bold">
                        <span>Total Monthly Cost</span>
                        <span className="text-2xl text-primary">
                          ₹{calculatePrice(pricingTiers.find(p => p.id === selectedPlan)!).final.toLocaleString()}
                        </span>
                      </div>
                      {calculatePrice(pricingTiers.find(p => p.id === selectedPlan)!).discount > 0 && (
                        <div className="text-center mt-2">
                          <span className="text-sm text-muted-foreground line-through">
                            ₹{calculatePrice(pricingTiers.find(p => p.id === selectedPlan)!).base.toLocaleString()}
                          </span>
                          <span className="text-sm text-green-600 ml-2 font-medium">
                            Save ₹{calculatePrice(pricingTiers.find(p => p.id === selectedPlan)!).discount.toLocaleString()}/month
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="text-center">
                      <Link href="/auth/signup">
                        <Button size="lg" className="w-full md:w-auto">
                          Get Started with This Plan
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground mb-4">Select services above to see your custom pricing</p>
                    <div className="text-2xl font-bold text-primary">₹0/month</div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Additional Information */}
          <div className="mt-20 text-center">
            <h3 className="text-2xl font-bold mb-8">All plans include:</h3>
            <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">99.9%+</div>
                <div className="text-sm text-muted-foreground">Uptime SLA</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">48hrs</div>
                <div className="text-sm text-muted-foreground">Deployment Time</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">11</div>
                <div className="text-sm text-muted-foreground">Languages Supported</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary">100%</div>
                <div className="text-sm text-muted-foreground">Test Coverage</div>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="mt-20">
            <Card className="max-w-4xl mx-auto">
              <CardHeader className="text-center">
                <CardTitle className="text-3xl">Need a custom solution?</CardTitle>
                <CardDescription className="text-lg">
                  Contact our sales team for enterprise pricing and custom implementations
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <div className="flex justify-center gap-4">
                  <Link href="/support">
                    <Button size="lg">Contact Sales</Button>
                  </Link>
                  <Link href="/services">
                    <Button size="lg" variant="outline">View Services</Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  )
}