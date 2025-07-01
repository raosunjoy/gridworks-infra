import { loadStripe } from '@stripe/stripe-js'
import Stripe from 'stripe'

// Client-side Stripe
export const getStripe = () => {
  return loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)
}

// Server-side Stripe
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-06-20',
})

// Subscription Plans Configuration
export const subscriptionPlans = {
  professional: {
    id: 'professional',
    name: 'Professional',
    description: 'Perfect for growing companies',
    basePrice: 25000, // ₹25,000 in paisa (₹250.00)
    stripePriceId: process.env.STRIPE_PROFESSIONAL_PRICE_ID || 'price_professional',
    features: [
      '10,000 API requests/month',
      'Basic AI support (5 languages)',
      'NSE & BSE trading connectivity',
      'Multi-currency payments',
      'Email support',
      '99.5% uptime SLA'
    ]
  },
  enterprise: {
    id: 'enterprise',
    name: 'Enterprise',
    description: 'For large organizations',
    basePrice: 50000, // ₹50,000 in paisa (₹500.00) 
    stripePriceId: process.env.STRIPE_ENTERPRISE_PRICE_ID || 'price_enterprise',
    features: [
      'Unlimited API requests',
      'Advanced AI support (11 languages)',
      'Global exchange connectivity',
      'Advanced KYC/AML automation',
      '24/7 priority support',
      '99.99% uptime SLA',
      'Dedicated account manager'
    ]
  },
  uhnw: {
    id: 'uhnw',
    name: 'UHNW',
    description: 'Ultra High Net Worth services',
    basePrice: 100000, // ₹100,000 in paisa (₹1,000.00)
    stripePriceId: process.env.STRIPE_UHNW_PRICE_ID || 'price_uhnw',
    features: [
      'Anonymous portfolio management',
      'Zero-knowledge proof verification',
      'Butler AI assistance',
      'Quantum-resistant encryption',
      'White-glove concierge service',
      '99.999% uptime SLA',
      'On-site support available'
    ]
  }
}

// Service Add-ons Configuration
export const serviceAddons = {
  'ai-suite': {
    id: 'ai-suite',
    name: 'AI Suite Services',
    price: 15000, // ₹15,000 in paisa
    stripePriceId: process.env.STRIPE_AI_SUITE_PRICE_ID || 'price_ai_suite',
    description: 'Multi-language AI support, chat, and automation'
  },
  'anonymous': {
    id: 'anonymous',
    name: 'Anonymous Services',
    price: 20000, // ₹20,000 in paisa
    stripePriceId: process.env.STRIPE_ANONYMOUS_PRICE_ID || 'price_anonymous',
    description: 'Zero-knowledge proofs and privacy solutions'
  },
  'trading': {
    id: 'trading',
    name: 'Trading-as-a-Service',
    price: 25000, // ₹25,000 in paisa
    stripePriceId: process.env.STRIPE_TRADING_PRICE_ID || 'price_trading',
    description: 'Global exchange connectivity and trading infrastructure'
  },
  'banking': {
    id: 'banking',
    name: 'Banking-as-a-Service',
    price: 30000, // ₹30,000 in paisa
    stripePriceId: process.env.STRIPE_BANKING_PRICE_ID || 'price_banking',
    description: 'Complete banking infrastructure and compliance'
  }
}

// Helper Functions
export const formatCurrency = (amountInPaisa: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amountInPaisa / 100)
}

export const calculateSubscriptionPrice = (
  planId: keyof typeof subscriptionPlans,
  selectedServices: string[] = []
) => {
  const plan = subscriptionPlans[planId]
  if (!plan) return { basePrice: 0, servicePrice: 0, total: 0 }

  const servicePrice = selectedServices.reduce((total, serviceId) => {
    const service = serviceAddons[serviceId as keyof typeof serviceAddons]
    return total + (service?.price || 0)
  }, 0)

  const basePrice = plan.basePrice
  const total = basePrice + servicePrice

  // Apply discounts based on plan
  let discount = 0
  if (planId === 'enterprise') {
    discount = total * 0.15 // 15% discount
  } else if (planId === 'uhnw') {
    discount = total * 0.25 // 25% discount
  }

  // Volume discount for 3+ services
  if (selectedServices.length >= 3) {
    discount += total * 0.1 // Additional 10% for volume
  }

  return {
    basePrice,
    servicePrice,
    subtotal: total,
    discount: Math.round(discount),
    total: Math.round(total - discount)
  }
}

// Stripe Webhook Event Types
export type StripeWebhookEvent = 
  | 'customer.subscription.created'
  | 'customer.subscription.updated'
  | 'customer.subscription.deleted'
  | 'invoice.payment_succeeded'
  | 'invoice.payment_failed'
  | 'customer.created'
  | 'customer.updated'

// Subscription Status Types
export type SubscriptionStatus = 
  | 'incomplete'
  | 'incomplete_expired'
  | 'trialing'
  | 'active'
  | 'past_due'
  | 'canceled'
  | 'unpaid'

export interface SubscriptionData {
  id: string
  customerId: string
  status: SubscriptionStatus
  planId: string
  services: string[]
  currentPeriodStart: Date
  currentPeriodEnd: Date
  cancelAtPeriodEnd: boolean
  metadata?: Record<string, string>
}

// API Helper Functions
export const createStripeCustomer = async (
  email: string,
  name: string,
  organizationId: string
) => {
  return await stripe.customers.create({
    email,
    name,
    metadata: {
      organizationId
    }
  })
}

export const createSubscription = async (
  customerId: string,
  planId: keyof typeof subscriptionPlans,
  selectedServices: string[] = [],
  metadata: Record<string, string> = {}
) => {
  const plan = subscriptionPlans[planId]
  if (!plan) throw new Error('Invalid plan ID')

  // Build line items
  const lineItems: Stripe.SubscriptionCreateParams.Item[] = [
    {
      price: plan.stripePriceId,
      quantity: 1
    }
  ]

  // Add service add-ons
  selectedServices.forEach(serviceId => {
    const service = serviceAddons[serviceId as keyof typeof serviceAddons]
    if (service) {
      lineItems.push({
        price: service.stripePriceId,
        quantity: 1
      })
    }
  })

  return await stripe.subscriptions.create({
    customer: customerId,
    items: lineItems,
    metadata: {
      ...metadata,
      planId,
      services: selectedServices.join(',')
    },
    payment_behavior: 'default_incomplete',
    payment_settings: { save_default_payment_method: 'on_subscription' },
    expand: ['latest_invoice.payment_intent']
  })
}

export const updateSubscription = async (
  subscriptionId: string,
  planId: keyof typeof subscriptionPlans,
  selectedServices: string[] = []
) => {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId)
  const plan = subscriptionPlans[planId]
  
  if (!plan) throw new Error('Invalid plan ID')

  // Clear existing items and add new ones
  const items: Stripe.SubscriptionUpdateParams.Item[] = subscription.items.data.map(item => ({
    id: item.id,
    deleted: true
  }))

  // Add new plan
  items.push({
    price: plan.stripePriceId,
    quantity: 1
  })

  // Add new services
  selectedServices.forEach(serviceId => {
    const service = serviceAddons[serviceId as keyof typeof serviceAddons]
    if (service) {
      items.push({
        price: service.stripePriceId,
        quantity: 1
      })
    }
  })

  return await stripe.subscriptions.update(subscriptionId, {
    items,
    metadata: {
      planId,
      services: selectedServices.join(',')
    },
    proration_behavior: 'create_prorations'
  })
}

export const cancelSubscription = async (subscriptionId: string, cancelAtPeriodEnd = true) => {
  if (cancelAtPeriodEnd) {
    return await stripe.subscriptions.update(subscriptionId, {
      cancel_at_period_end: true
    })
  } else {
    return await stripe.subscriptions.cancel(subscriptionId)
  }
}

export const getSubscriptionUsage = async (subscriptionId: string) => {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId, {
    expand: ['items.data.price']
  })
  
  const usage = await Promise.all(
    subscription.items.data.map(async (item) => {
      const usageRecords = await stripe.subscriptionItems.listUsageRecords(item.id)
      return {
        itemId: item.id,
        priceId: item.price.id,
        usage: usageRecords.data
      }
    })
  )

  return usage
}