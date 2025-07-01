'use client'

import { useState, useEffect } from 'react'
import { signIn, getProviders } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Building2, Mail, Shield, ArrowRight, AlertCircle } from 'lucide-react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { oauthConfigs, getAvailableProviders } from '@/lib/auth'

export default function SignInPage() {
  const [email, setEmail] = useState('')
  const [domain, setDomain] = useState('')
  const [availableProviders, setAvailableProviders] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [step, setStep] = useState<'email' | 'provider'>('email')
  
  const searchParams = useSearchParams()
  const callbackUrl = searchParams?.get('callbackUrl') || '/dashboard'
  const errorParam = searchParams?.get('error')

  useEffect(() => {
    if (errorParam) {
      const errorMessages: Record<string, string> = {
        'NoOrganization': 'Your organization is not registered with GridWorks. Please contact your administrator.',
        'OAuthDisabled': 'Single Sign-On is not enabled for your organization.',
        'InvalidProvider': 'Please use the correct authentication provider for your organization.',
        'AccessDenied': 'Access denied. Please check your permissions.',
        'CredentialsSignin': 'Invalid credentials. Please try again.'
      }
      setError(errorMessages[errorParam] || 'An authentication error occurred.')
    }
  }, [errorParam])

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setIsLoading(true)
    setError('')

    try {
      const emailDomain = email.split('@')[1]
      setDomain(emailDomain)
      
      const providers = await getAvailableProviders(emailDomain)
      
      if (providers.length === 0) {
        setError('Your organization is not configured for single sign-on. Please contact your administrator.')
        setIsLoading(false)
        return
      }
      
      setAvailableProviders(providers)
      setStep('provider')
    } catch (err) {
      setError('Failed to verify organization. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleProviderSignIn = async (provider: string) => {
    setIsLoading(true)
    try {
      await signIn(provider, { callbackUrl })
    } catch (err) {
      setError('Authentication failed. Please try again.')
      setIsLoading(false)
    }
  }

  if (step === 'provider') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center">
            <Link href="/">
              <h1 className="text-3xl font-bold cursor-pointer">GridWorks</h1>
            </Link>
            <p className="text-muted-foreground mt-2">Enterprise Portal</p>
          </div>

          <Card>
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center space-x-2">
                <Building2 className="h-5 w-5" />
                <span>Sign in to {domain}</span>
              </CardTitle>
              <CardDescription>
                Choose your organization's authentication method
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              <div className="space-y-3">
                {availableProviders.map((provider) => {
                  const config = oauthConfigs[provider as keyof typeof oauthConfigs]
                  if (!config) return null

                  return (
                    <Button
                      key={provider}
                      variant="outline"
                      className="w-full h-12 justify-start"
                      onClick={() => handleProviderSignIn(provider)}
                      disabled={isLoading}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-6 h-6 bg-gray-200 rounded flex items-center justify-center">
                          {provider === 'google' && <span className="text-xs font-bold">G</span>}
                          {provider === 'microsoft' && <span className="text-xs font-bold">M</span>}
                          {provider === 'okta' && <span className="text-xs font-bold">O</span>}
                          {provider === 'saml' && <span className="text-xs font-bold">S</span>}
                        </div>
                        <div className="text-left">
                          <div className="font-medium">{config.name}</div>
                          <div className="text-xs text-muted-foreground">{config.description}</div>
                        </div>
                      </div>
                      <ArrowRight className="h-4 w-4 ml-auto" />
                    </Button>
                  )
                })}
              </div>

              <div className="pt-4 border-t">
                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => setStep('email')}
                >
                  ← Use different email
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Don't have access?{' '}
              <Link href="/support" className="text-primary hover:underline">
                Contact Support
              </Link>
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <Link href="/">
            <h1 className="text-3xl font-bold cursor-pointer">GridWorks</h1>
          </Link>
          <p className="text-muted-foreground mt-2">Enterprise Portal</p>
        </div>

        <Card>
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2">
              <Shield className="h-5 w-5" />
              <span>Secure Sign In</span>
            </CardTitle>
            <CardDescription>
              Enter your corporate email to continue with single sign-on
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleEmailSubmit} className="space-y-4">
              {error && (
                <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Corporate Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your.name@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Use your organization's email address
                </p>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Verifying...' : 'Continue'}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </form>

            <div className="mt-6 space-y-4">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    Enterprise Features
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center space-x-1">
                  <Badge variant="outline" className="h-4 w-4 p-0 flex items-center justify-center">
                    ✓
                  </Badge>
                  <span>Single Sign-On</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Badge variant="outline" className="h-4 w-4 p-0 flex items-center justify-center">
                    ✓
                  </Badge>
                  <span>Multi-Factor Auth</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Badge variant="outline" className="h-4 w-4 p-0 flex items-center justify-center">
                    ✓
                  </Badge>
                  <span>IP Restrictions</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Badge variant="outline" className="h-4 w-4 p-0 flex items-center justify-center">
                    ✓
                  </Badge>
                  <span>Audit Logging</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            New to GridWorks?{' '}
            <Link href="/support" className="text-primary hover:underline">
              Contact Sales
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}