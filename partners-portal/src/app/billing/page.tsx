'use client'

import { useState, useEffect } from 'react'
import { useAppStore } from '@/lib/store'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  CreditCard, 
  Download, 
  Calendar, 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw,
  ExternalLink,
  Receipt,
  Wallet,
  BarChart3
} from 'lucide-react'
import { formatCurrency, calculateSubscriptionPrice, subscriptionPlans } from '@/lib/stripe'

export default function BillingPage() {
  const { user, organization, selectedServices } = useAppStore()
  const [currentTab, setCurrentTab] = useState('overview')
  const [isLoading, setIsLoading] = useState(false)

  // Mock subscription data - replace with actual Stripe integration
  const subscriptionData = {
    id: 'sub_1234567890',
    status: 'active' as const,
    planId: 'enterprise' as const,
    services: ['ai-suite', 'trading'],
    currentPeriodStart: new Date('2024-07-01'),
    currentPeriodEnd: new Date('2024-08-01'),
    cancelAtPeriodEnd: false,
    nextInvoiceAmount: 75000, // ₹750.00
    customerId: 'cust_1234567890'
  }

  // Mock invoice data
  const invoices = [
    {
      id: 'inv_001',
      date: new Date('2024-07-01'),
      amount: 75000,
      status: 'paid' as const,
      description: 'Enterprise Plan + AI Suite + Trading Services',
      downloadUrl: '#'
    },
    {
      id: 'inv_002',
      date: new Date('2024-06-01'),
      amount: 75000,
      status: 'paid' as const,
      description: 'Enterprise Plan + AI Suite + Trading Services',
      downloadUrl: '#'
    },
    {
      id: 'inv_003',
      date: new Date('2024-05-01'),
      amount: 50000,
      status: 'paid' as const,
      description: 'Enterprise Plan',
      downloadUrl: '#'
    }
  ]

  // Mock usage data
  const usageData = [
    { service: 'AI Suite', requests: 45230, limit: 50000, cost: 15000 },
    { service: 'Trading API', requests: 12450, limit: 15000, cost: 25000 },
    { service: 'Platform Base', requests: 8920, limit: 10000, cost: 50000 }
  ]

  const currentPlan = subscriptionPlans[subscriptionData.planId]
  const pricing = calculateSubscriptionPrice(subscriptionData.planId, subscriptionData.services)

  const handleManagePaymentMethod = () => {
    // Redirect to Stripe customer portal
    setIsLoading(true)
    // In real implementation, call API to create portal session
    setTimeout(() => {
      setIsLoading(false)
      // window.open(portalUrl, '_blank')
    }, 1000)
  }

  const handleCancelSubscription = () => {
    // Handle subscription cancellation
    console.log('Cancel subscription')
  }

  const handleUpgradePlan = () => {
    // Redirect to pricing page with upgrade flow
    window.location.href = '/pricing'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50 border-green-200'
      case 'past_due': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'canceled': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getUsagePercentage = (used: number, limit: number) => {
    return Math.round((used / limit) * 100)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">Billing & Subscription</h1>
              <Badge variant="outline">
                {organization?.name || 'Your Organization'}
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={handleManagePaymentMethod} disabled={isLoading}>
                <CreditCard className="h-4 w-4 mr-2" />
                {isLoading ? 'Loading...' : 'Manage Payment'}
              </Button>
              <Button onClick={handleUpgradePlan}>
                <TrendingUp className="h-4 w-4 mr-2" />
                Upgrade Plan
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Current Subscription Overview */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Current Plan</p>
                  <p className="text-2xl font-bold">{currentPlan.name}</p>
                </div>
                <Wallet className="h-8 w-8 text-primary" />
              </div>
              <Badge className={getStatusColor(subscriptionData.status)}>
                {subscriptionData.status === 'active' && <CheckCircle className="h-3 w-3 mr-1" />}
                {subscriptionData.status}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Monthly Cost</p>
                  <p className="text-2xl font-bold">{formatCurrency(pricing.total)}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-green-600" />
              </div>
              <p className="text-sm text-muted-foreground">
                {pricing.discount > 0 && (
                  <span>Saving {formatCurrency(pricing.discount)}/month</span>
                )}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Next Invoice</p>
                  <p className="text-2xl font-bold">
                    {subscriptionData.currentPeriodEnd.toLocaleDateString()}
                  </p>
                </div>
                <Calendar className="h-8 w-8 text-blue-600" />
              </div>
              <p className="text-sm text-muted-foreground">
                {formatCurrency(subscriptionData.nextInvoiceAmount)}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Billing Details */}
        <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="usage">Usage</TabsTrigger>
            <TabsTrigger value="invoices">Invoices</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Current Subscription Details */}
            <Card>
              <CardHeader>
                <CardTitle>Subscription Details</CardTitle>
                <CardDescription>Your current plan and services</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-3">Current Plan</h4>
                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{currentPlan.name}</span>
                          <span className="text-lg font-bold">{formatCurrency(currentPlan.basePrice)}</span>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{currentPlan.description}</p>
                        <div className="space-y-1">
                          {currentPlan.features.slice(0, 3).map((feature, index) => (
                            <div key={index} className="flex items-center text-sm">
                              <CheckCircle className="h-3 w-3 mr-2 text-green-600" />
                              {feature}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-3">Active Services</h4>
                      <div className="space-y-2">
                        {subscriptionData.services.map((serviceId) => (
                          <div key={serviceId} className="flex items-center justify-between p-3 border rounded-lg">
                            <span className="text-sm font-medium">
                              {serviceId === 'ai-suite' && '🤖 AI Suite Services'}
                              {serviceId === 'trading' && '📈 Trading-as-a-Service'}
                              {serviceId === 'banking' && '🏦 Banking-as-a-Service'}
                              {serviceId === 'anonymous' && '🔒 Anonymous Services'}
                            </span>
                            <span className="text-sm font-bold">
                              {formatCurrency(serviceId === 'ai-suite' ? 15000 : serviceId === 'trading' ? 25000 : 20000)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between text-lg font-bold">
                      <span>Total Monthly Cost</span>
                      <span>{formatCurrency(pricing.total)}</span>
                    </div>
                    {pricing.discount > 0 && (
                      <div className="text-sm text-green-600 text-right">
                        You're saving {formatCurrency(pricing.discount)} per month!
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Billing Cycle */}
            <Card>
              <CardHeader>
                <CardTitle>Billing Cycle</CardTitle>
                <CardDescription>Your subscription renewal information</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">Current Period</p>
                    <p className="text-lg font-medium">
                      {subscriptionData.currentPeriodStart.toLocaleDateString()} - {subscriptionData.currentPeriodEnd.toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">Next Renewal</p>
                    <p className="text-lg font-medium">
                      {subscriptionData.currentPeriodEnd.toLocaleDateString()}
                    </p>
                  </div>
                </div>
                {subscriptionData.cancelAtPeriodEnd && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-center">
                      <AlertCircle className="h-4 w-4 text-yellow-600 mr-2" />
                      <span className="text-sm text-yellow-700">
                        Your subscription will be canceled at the end of the current period.
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="usage" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Usage Analytics</CardTitle>
                <CardDescription>Track your API usage and costs this month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {usageData.map((usage, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">{usage.service}</h4>
                        <div className="text-right">
                          <p className="font-medium">{formatCurrency(usage.cost)}</p>
                          <p className="text-sm text-muted-foreground">
                            {usage.requests.toLocaleString()} / {usage.limit.toLocaleString()} requests
                          </p>
                        </div>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            getUsagePercentage(usage.requests, usage.limit) < 70 ? 'bg-green-600' :
                            getUsagePercentage(usage.requests, usage.limit) < 90 ? 'bg-yellow-600' :
                            'bg-red-600'
                          }`}
                          style={{ width: `${Math.min(getUsagePercentage(usage.requests, usage.limit), 100)}%` }}
                        />
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {getUsagePercentage(usage.requests, usage.limit)}% of monthly limit used
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="invoices" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Invoice History</CardTitle>
                <CardDescription>Download and view your past invoices</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {invoices.map((invoice) => (
                    <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <Receipt className="h-8 w-8 text-primary" />
                        <div>
                          <p className="font-medium">{invoice.description}</p>
                          <p className="text-sm text-muted-foreground">
                            {invoice.date.toLocaleDateString()} • {invoice.id.toUpperCase()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <p className="font-bold">{formatCurrency(invoice.amount)}</p>
                          <Badge 
                            variant="outline" 
                            className={invoice.status === 'paid' ? 'text-green-600 border-green-600' : 'text-red-600 border-red-600'}
                          >
                            {invoice.status === 'paid' ? <CheckCircle className="h-3 w-3 mr-1" /> : <XCircle className="h-3 w-3 mr-1" />}
                            {invoice.status}
                          </Badge>
                        </div>
                        <Button variant="outline" size="sm">
                          <Download className="h-3 w-3 mr-1" />
                          Download
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Subscription Settings</CardTitle>
                <CardDescription>Manage your subscription and billing preferences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Payment Method</h4>
                      <p className="text-sm text-muted-foreground">Manage your payment methods and billing information</p>
                    </div>
                    <Button variant="outline" onClick={handleManagePaymentMethod} disabled={isLoading}>
                      <CreditCard className="h-4 w-4 mr-2" />
                      Manage
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Upgrade Plan</h4>
                      <p className="text-sm text-muted-foreground">Change your subscription plan or add services</p>
                    </div>
                    <Button onClick={handleUpgradePlan}>
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Upgrade
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Cancel Subscription</h4>
                      <p className="text-sm text-muted-foreground">Cancel your subscription at the end of the billing period</p>
                    </div>
                    <Button variant="outline" onClick={handleCancelSubscription}>
                      Cancel
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Billing Information</CardTitle>
                <CardDescription>Update your billing details and tax information</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Organization</p>
                      <p className="font-medium">{organization?.name}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Email</p>
                      <p className="font-medium">{user?.email}</p>
                    </div>
                  </div>
                  <Button variant="outline">
                    Update Billing Information
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}