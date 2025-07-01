import { NextAuthOptions } from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import AzureADProvider from 'next-auth/providers/azure-ad'
import { User, Organization } from './store'

// Mock database functions (replace with actual database calls)
const findOrganizationByDomain = async (domain: string): Promise<Organization | null> => {
  // Mock organization data - replace with actual database query
  const mockOrganizations: Record<string, Organization> = {
    'acme.com': {
      id: 'org_acme',
      name: 'Acme Corporation',
      domain: 'acme.com',
      plan: 'enterprise',
      apiKeys: [],
      users: [],
      settings: {
        oauth: {
          provider: 'google',
          domain: 'acme.com',
          isEnabled: true
        },
        notifications: {
          email: true,
          slack: false
        },
        security: {
          ipWhitelist: [],
          apiKeyRotation: 90,
          twoFactorRequired: true
        }
      },
      createdAt: new Date().toISOString()
    },
    'techcorp.com': {
      id: 'org_tech',
      name: 'TechCorp Ltd',
      domain: 'techcorp.com',
      plan: 'professional',
      apiKeys: [],
      users: [],
      settings: {
        oauth: {
          provider: 'microsoft',
          domain: 'techcorp.com',
          isEnabled: true
        },
        notifications: {
          email: true,
          slack: true
        },
        security: {
          ipWhitelist: ['192.168.1.0/24'],
          apiKeyRotation: 60,
          twoFactorRequired: false
        }
      },
      createdAt: new Date().toISOString()
    }
  }

  return mockOrganizations[domain] || null
}

const createOrUpdateUser = async (userData: any, organization: Organization): Promise<User> => {
  // Mock user creation - replace with actual database operations
  const user: User = {
    id: `user_${Date.now()}`,
    email: userData.email,
    name: userData.name || userData.email,
    organizationId: organization.id,
    role: userData.email.includes('admin') ? 'admin' : 'developer',
    avatar: userData.image,
    createdAt: new Date().toISOString()
  }

  return user
}

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
      authorization: {
        params: {
          prompt: 'consent',
          access_type: 'offline',
          response_type: 'code',
          hd: process.env.GOOGLE_HD || undefined // Restrict to specific domain
        }
      }
    }),
    AzureADProvider({
      clientId: process.env.AZURE_AD_CLIENT_ID || '',
      clientSecret: process.env.AZURE_AD_CLIENT_SECRET || '',
      tenantId: process.env.AZURE_AD_TENANT_ID || '',
    }),
  ],
  
  pages: {
    signIn: '/auth/signin',
    signOut: '/auth/signout',
    error: '/auth/error'
  },

  callbacks: {
    async signIn({ user, account, profile }) {
      try {
        if (!user.email) {
          console.error('No email provided')
          return false
        }

        // Extract domain from email
        const emailDomain = user.email.split('@')[1]
        
        // Check if organization exists and OAuth is enabled
        const organization = await findOrganizationByDomain(emailDomain)
        
        if (!organization) {
          console.error(`No organization found for domain: ${emailDomain}`)
          return '/auth/error?error=NoOrganization'
        }

        if (!organization.settings.oauth.isEnabled) {
          console.error(`OAuth not enabled for organization: ${organization.name}`)
          return '/auth/error?error=OAuthDisabled'
        }

        // Verify OAuth provider matches organization settings
        const providerMap: Record<string, string> = {
          'google': 'google',
          'azure-ad': 'microsoft'
        }

        const expectedProvider = organization.settings.oauth.provider
        const actualProvider = providerMap[account?.provider || '']

        if (actualProvider !== expectedProvider) {
          console.error(`Invalid OAuth provider. Expected: ${expectedProvider}, Got: ${actualProvider}`)
          return '/auth/error?error=InvalidProvider'
        }

        return true
      } catch (error) {
        console.error('Sign in error:', error)
        return false
      }
    },

    async jwt({ token, user, account }) {
      if (user && user.email) {
        const emailDomain = user.email.split('@')[1]
        const organization = await findOrganizationByDomain(emailDomain)
        
        if (organization) {
          const userData = await createOrUpdateUser(user, organization)
          
          token.user = userData
          token.organization = organization
        }
      }
      
      return token
    },

    async session({ session, token }) {
      if (token.user && token.organization) {
        session.user = token.user as User
        session.organization = token.organization as Organization
      }
      
      return session
    }
  },

  events: {
    async signIn({ user, account, profile, isNewUser }) {
      console.log(`User signed in: ${user.email} via ${account?.provider}`)
    },
    
    async signOut({ token }) {
      console.log(`User signed out: ${token?.user?.email}`)
    }
  },

  session: {
    strategy: 'jwt',
    maxAge: 24 * 60 * 60, // 24 hours
  },

  debug: process.env.NODE_ENV === 'development'
}

// OAuth Provider configurations for different corporate systems
export const oauthConfigs = {
  google: {
    name: 'Google Workspace',
    description: 'Sign in with your Google Workspace account',
    icon: '/icons/google.svg',
    domains: ['gmail.com', 'googlemail.com'] // Can be customized per organization
  },
  
  microsoft: {
    name: 'Microsoft 365',
    description: 'Sign in with your Microsoft 365 account',
    icon: '/icons/microsoft.svg',
    domains: ['outlook.com', 'hotmail.com'] // Can be customized per organization
  },
  
  okta: {
    name: 'Okta',
    description: 'Sign in with your Okta account',
    icon: '/icons/okta.svg',
    domains: [] // Custom domains configured per organization
  },
  
  saml: {
    name: 'SAML SSO',
    description: 'Sign in with your corporate SAML provider',
    icon: '/icons/saml.svg',
    domains: [] // Custom domains configured per organization
  }
}

// Helper function to get available OAuth providers for a domain
export const getAvailableProviders = async (domain?: string) => {
  if (!domain) return []
  
  const organization = await findOrganizationByDomain(domain)
  if (!organization || !organization.settings.oauth.isEnabled) {
    return []
  }

  return [organization.settings.oauth.provider]
}

// Enhanced security checks
export const validateSecurityRequirements = async (user: User, organization: Organization, clientIp?: string) => {
  const security = organization.settings.security

  // IP whitelist check
  if (security.ipWhitelist.length > 0 && clientIp) {
    const isAllowed = security.ipWhitelist.some(range => {
      // Simple IP range check - implement proper CIDR matching in production
      return clientIp.startsWith(range.split('/')[0].slice(0, -1))
    })
    
    if (!isAllowed) {
      throw new Error('Access denied: IP not in whitelist')
    }
  }

  // Two-factor authentication check
  if (security.twoFactorRequired) {
    // Implement 2FA verification logic here
    console.log('2FA required for user:', user.email)
  }

  return true
}