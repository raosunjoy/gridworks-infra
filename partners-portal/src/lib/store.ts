import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Types
export interface User {
  id: string
  email: string
  name: string
  organizationId: string
  role: 'admin' | 'developer' | 'viewer'
  avatar?: string
  createdAt: string
}

export interface Organization {
  id: string
  name: string
  domain: string
  plan: 'professional' | 'enterprise' | 'uhnw'
  subscriptionId?: string
  apiKeys: ApiKey[]
  users: User[]
  settings: OrganizationSettings
  createdAt: string
}

export interface ApiKey {
  id: string
  name: string
  key: string
  services: ServiceType[]
  environment: 'sandbox' | 'production'
  isActive: boolean
  usage: {
    requests: number
    limit: number
    resetDate: string
  }
  createdAt: string
  lastUsed?: string
}

export interface OrganizationSettings {
  oauth: {
    provider: 'google' | 'microsoft' | 'okta' | 'saml'
    domain: string
    isEnabled: boolean
  }
  notifications: {
    email: boolean
    slack: boolean
    webhook?: string
  }
  security: {
    ipWhitelist: string[]
    apiKeyRotation: number // days
    twoFactorRequired: boolean
  }
}

export type ServiceType = 'ai-suite' | 'anonymous' | 'trading' | 'banking'

export interface ServiceConfig {
  id: ServiceType
  name: string
  description: string
  basePrice: number
  features: string[]
  isSelected: boolean
}

export interface PricingCalculation {
  services: ServiceConfig[]
  baseTotal: number
  discounts: number
  finalTotal: number
  plan: 'professional' | 'enterprise' | 'uhnw'
}

export interface ChatMessage {
  id: string
  message: string
  isUser: boolean
  timestamp: string
  context?: string
}

export interface SupportTicket {
  id: string
  title: string
  description: string
  status: 'open' | 'in-progress' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignedTo?: string
  createdBy: string
  createdAt: string
  updatedAt: string
  messages: ChatMessage[]
}

// Store State Interface
interface AppState {
  // Authentication
  user: User | null
  organization: Organization | null
  isAuthenticated: boolean
  
  // UI State
  isLoading: boolean
  sidebarOpen: boolean
  activeTab: string
  
  // Admin State
  isAdminMode: boolean
  allOrganizations: Organization[]
  selectedOrgId: string | null
  
  // Pricing & Services
  selectedServices: ServiceType[]
  pricingCalculation: PricingCalculation | null
  
  // AI Chat
  chatOpen: boolean
  chatMessages: ChatMessage[]
  
  // Support
  supportTickets: SupportTicket[]
  
  // Sandbox
  sandboxMode: boolean
  sandboxData: any
  
  // Actions
  setUser: (user: User | null) => void
  setOrganization: (org: Organization | null) => void
  login: (user: User, organization: Organization) => void
  logout: () => void
  
  // UI Actions
  setLoading: (loading: boolean) => void
  setSidebarOpen: (open: boolean) => void
  setActiveTab: (tab: string) => void
  
  // Admin Actions
  toggleAdminMode: () => void
  setAllOrganizations: (orgs: Organization[]) => void
  selectOrganization: (orgId: string) => void
  
  // Service Selection
  toggleService: (service: ServiceType) => void
  calculatePricing: () => void
  
  // API Key Management
  generateApiKey: (name: string, services: ServiceType[], environment: 'sandbox' | 'production') => Promise<ApiKey>
  revokeApiKey: (keyId: string) => void
  
  // Chat Actions
  toggleChat: () => void
  addChatMessage: (message: string, isUser: boolean) => void
  clearChat: () => void
  
  // Support Actions
  createTicket: (title: string, description: string, priority: 'low' | 'medium' | 'high' | 'critical') => void
  updateTicketStatus: (ticketId: string, status: 'open' | 'in-progress' | 'resolved' | 'closed') => void
  
  // Sandbox Actions
  toggleSandboxMode: () => void
  setSandboxData: (data: any) => void
}

// Service Configurations
const serviceConfigs: ServiceConfig[] = [
  {
    id: 'ai-suite',
    name: 'AI Suite Services',
    description: 'Multi-language AI support, chat, and automation',
    basePrice: 15000,
    features: ['11 Language Support', 'OpenAI & Claude Integration', '24/7 AI Chat', 'Sentiment Analysis'],
    isSelected: false
  },
  {
    id: 'anonymous',
    name: 'Anonymous Services',
    description: 'Zero-knowledge proofs and privacy solutions',
    basePrice: 20000,
    features: ['Zero-Knowledge Proofs', 'Anonymous Transactions', 'Privacy Compliance', 'Quantum-Resistant Encryption'],
    isSelected: false
  },
  {
    id: 'trading',
    name: 'Trading-as-a-Service',
    description: 'Global exchange connectivity and trading infrastructure',
    basePrice: 25000,
    features: ['NSE/BSE Integration', 'Global Exchanges', 'Real-time Data', 'Risk Management'],
    isSelected: false
  },
  {
    id: 'banking',
    name: 'Banking-as-a-Service',
    description: 'Complete banking infrastructure and compliance',
    basePrice: 30000,
    features: ['Multi-currency Support', 'KYC/AML Automation', 'Payment Processing', 'Regulatory Compliance'],
    isSelected: false
  }
]

// Zustand Store
export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial State
      user: null,
      organization: null,
      isAuthenticated: false,
      isLoading: false,
      sidebarOpen: true,
      activeTab: 'dashboard',
      isAdminMode: false,
      allOrganizations: [],
      selectedOrgId: null,
      selectedServices: [],
      pricingCalculation: null,
      chatOpen: false,
      chatMessages: [],
      supportTickets: [],
      sandboxMode: false,
      sandboxData: null,

      // Authentication Actions
      setUser: (user) => set({ user }),
      setOrganization: (organization) => set({ organization }),
      
      login: (user, organization) => set({ 
        user, 
        organization, 
        isAuthenticated: true,
        isLoading: false 
      }),
      
      logout: () => set({ 
        user: null, 
        organization: null, 
        isAuthenticated: false,
        isAdminMode: false,
        selectedServices: [],
        chatMessages: [],
        activeTab: 'dashboard'
      }),

      // UI Actions
      setLoading: (isLoading) => set({ isLoading }),
      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      setActiveTab: (activeTab) => set({ activeTab }),

      // Admin Actions
      toggleAdminMode: () => {
        const { user } = get()
        if (user?.role === 'admin') {
          set((state) => ({ isAdminMode: !state.isAdminMode }))
        }
      },
      
      setAllOrganizations: (allOrganizations) => set({ allOrganizations }),
      selectOrganization: (selectedOrgId) => set({ selectedOrgId }),

      // Service Selection & Pricing
      toggleService: (service) => {
        set((state) => {
          const isSelected = state.selectedServices.includes(service)
          const newServices = isSelected 
            ? state.selectedServices.filter(s => s !== service)
            : [...state.selectedServices, service]
          
          return { selectedServices: newServices }
        })
        get().calculatePricing()
      },

      calculatePricing: () => {
        const { selectedServices, organization } = get()
        
        if (!organization || selectedServices.length === 0) {
          set({ pricingCalculation: null })
          return
        }

        const services = serviceConfigs.map(service => ({
          ...service,
          isSelected: selectedServices.includes(service.id)
        })).filter(service => service.isSelected)

        let baseTotal = services.reduce((total, service) => total + service.basePrice, 0)
        let discounts = 0

        // Plan-based discounts
        if (organization.plan === 'enterprise') {
          discounts = baseTotal * 0.15 // 15% enterprise discount
        } else if (organization.plan === 'uhnw') {
          discounts = baseTotal * 0.25 // 25% UHNW discount
        }

        // Volume discounts
        if (services.length >= 3) {
          discounts += baseTotal * 0.1 // 10% for 3+ services
        }

        const finalTotal = baseTotal - discounts

        set({
          pricingCalculation: {
            services,
            baseTotal,
            discounts,
            finalTotal,
            plan: organization.plan
          }
        })
      },

      // API Key Management
      generateApiKey: async (name, services, environment) => {
        const { organization } = get()
        if (!organization) throw new Error('No organization found')

        const newKey: ApiKey = {
          id: `key_${Date.now()}`,
          name,
          key: `gw_${environment}_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`,
          services,
          environment,
          isActive: true,
          usage: {
            requests: 0,
            limit: environment === 'sandbox' ? 1000 : 10000,
            resetDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
          },
          createdAt: new Date().toISOString()
        }

        set((state) => ({
          organization: state.organization ? {
            ...state.organization,
            apiKeys: [...state.organization.apiKeys, newKey]
          } : null
        }))

        return newKey
      },

      revokeApiKey: (keyId) => {
        set((state) => ({
          organization: state.organization ? {
            ...state.organization,
            apiKeys: state.organization.apiKeys.map(key =>
              key.id === keyId ? { ...key, isActive: false } : key
            )
          } : null
        }))
      },

      // Chat Actions
      toggleChat: () => set((state) => ({ chatOpen: !state.chatOpen })),
      
      addChatMessage: (message, isUser) => {
        const newMessage: ChatMessage = {
          id: `msg_${Date.now()}`,
          message,
          isUser,
          timestamp: new Date().toISOString()
        }
        
        set((state) => ({
          chatMessages: [...state.chatMessages, newMessage]
        }))
      },
      
      clearChat: () => set({ chatMessages: [] }),

      // Support Actions
      createTicket: (title, description, priority) => {
        const { user } = get()
        if (!user) return

        const newTicket: SupportTicket = {
          id: `ticket_${Date.now()}`,
          title,
          description,
          status: 'open',
          priority,
          createdBy: user.id,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages: []
        }

        set((state) => ({
          supportTickets: [...state.supportTickets, newTicket]
        }))
      },

      updateTicketStatus: (ticketId, status) => {
        set((state) => ({
          supportTickets: state.supportTickets.map(ticket =>
            ticket.id === ticketId 
              ? { ...ticket, status, updatedAt: new Date().toISOString() }
              : ticket
          )
        }))
      },

      // Sandbox Actions
      toggleSandboxMode: () => set((state) => ({ sandboxMode: !state.sandboxMode })),
      setSandboxData: (sandboxData) => set({ sandboxData })
    }),
    {
      name: 'gridworks-portal-storage',
      partialize: (state) => ({
        user: state.user,
        organization: state.organization,
        isAuthenticated: state.isAuthenticated,
        selectedServices: state.selectedServices,
        chatMessages: state.chatMessages,
        supportTickets: state.supportTickets,
        sandboxMode: state.sandboxMode
      })
    }
  )
)