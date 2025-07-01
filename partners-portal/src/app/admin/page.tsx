'use client'

import { useEffect } from 'react'
import { useAppStore } from '@/lib/store'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Users, 
  Building2, 
  CreditCard, 
  Key, 
  BarChart3, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Settings,
  Shield,
  Activity
} from 'lucide-react'

export default function AdminPage() {
  const {
    user,
    organization,
    isAdminMode,
    allOrganizations,
    selectedOrgId,
    toggleAdminMode,
    setAllOrganizations,
    selectOrganization
  } = useAppStore()

  // Mock data - replace with actual API calls
  useEffect(() => {
    if (user?.role === 'admin') {
      setAllOrganizations([
        {
          id: 'org_acme',
          name: 'Acme Corporation',
          domain: 'acme.com',
          plan: 'enterprise',
          apiKeys: [
            {
              id: 'key_1',
              name: 'Production API',
              key: 'gw_prod_...',
              services: ['ai-suite', 'trading'],
              environment: 'production',
              isActive: true,
              usage: { requests: 15420, limit: 50000, resetDate: '2024-08-01' },
              createdAt: '2024-07-01'
            }
          ],
          users: [
            {
              id: 'user_1',
              email: 'admin@acme.com',
              name: 'John Admin',
              organizationId: 'org_acme',
              role: 'admin',
              createdAt: '2024-06-01'
            }
          ],
          settings: {
            oauth: { provider: 'google', domain: 'acme.com', isEnabled: true },
            notifications: { email: true, slack: false },
            security: { ipWhitelist: [], apiKeyRotation: 90, twoFactorRequired: true }
          },
          createdAt: '2024-06-01'
        },
        {
          id: 'org_tech',
          name: 'TechCorp Ltd',
          domain: 'techcorp.com',
          plan: 'professional',
          apiKeys: [],
          users: [],
          settings: {
            oauth: { provider: 'microsoft', domain: 'techcorp.com', isEnabled: true },
            notifications: { email: true, slack: true },
            security: { ipWhitelist: [], apiKeyRotation: 60, twoFactorRequired: false }
          },
          createdAt: '2024-06-15'
        }
      ])
    }
  }, [user, setAllOrganizations])

  if (!user || user.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center text-red-600">Access Denied</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center text-muted-foreground">
              You need administrator privileges to access this page.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const selectedOrg = allOrganizations.find(org => org.id === selectedOrgId) || allOrganizations[0]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Admin Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">GridWorks Admin Portal</h1>
              <Badge variant="destructive" className="animate-pulse">
                <Shield className="h-3 w-3 mr-1" />
                Admin Mode
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline">
                {allOrganizations.length} Organizations
              </Badge>
              <Button variant="outline" onClick={toggleAdminMode}>
                Exit Admin Mode
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Overview Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Organizations</p>
                  <p className="text-3xl font-bold">{allOrganizations.length}</p>
                </div>
                <Building2 className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active Users</p>
                  <p className="text-3xl font-bold">
                    {allOrganizations.reduce((sum, org) => sum + org.users.length, 0)}
                  </p>
                </div>
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">API Keys</p>
                  <p className="text-3xl font-bold">
                    {allOrganizations.reduce((sum, org) => sum + org.apiKeys.length, 0)}
                  </p>
                </div>
                <Key className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">System Health</p>
                  <div className="flex items-center space-x-1 mt-1">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-600">Operational</span>
                  </div>
                </div>
                <Activity className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Organization Management */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Organization List */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Organizations</CardTitle>
              <CardDescription>Manage all GridWorks organizations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {allOrganizations.map((org) => (
                <div
                  key={org.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedOrgId === org.id ? 'bg-primary/10 border-primary' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => selectOrganization(org.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{org.name}</p>
                      <p className="text-sm text-muted-foreground">{org.domain}</p>
                    </div>
                    <Badge variant={org.plan === 'enterprise' ? 'default' : 'secondary'}>
                      {org.plan}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                    <span>{org.users.length} users</span>
                    <span>{org.apiKeys.length} keys</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Organization Details */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>{selectedOrg.name}</CardTitle>
              <CardDescription>Organization management and settings</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="overview" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="users">Users</TabsTrigger>
                  <TabsTrigger value="keys">API Keys</TabsTrigger>
                  <TabsTrigger value="settings">Settings</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Domain</p>
                      <p className="text-muted-foreground">{selectedOrg.domain}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Plan</p>
                      <Badge variant={selectedOrg.plan === 'enterprise' ? 'default' : 'secondary'}>
                        {selectedOrg.plan}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Created</p>
                      <p className="text-muted-foreground">
                        {new Date(selectedOrg.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">OAuth Provider</p>
                      <p className="text-muted-foreground capitalize">
                        {selectedOrg.settings.oauth.provider}
                      </p>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="users" className="space-y-4">
                  {selectedOrg.users.length > 0 ? (
                    <div className="space-y-3">
                      {selectedOrg.users.map((user) => (
                        <div key={user.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <p className="font-medium">{user.name}</p>
                            <p className="text-sm text-muted-foreground">{user.email}</p>
                          </div>
                          <Badge variant={user.role === 'admin' ? 'destructive' : 'outline'}>
                            {user.role}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      No users found for this organization
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="keys" className="space-y-4">
                  {selectedOrg.apiKeys.length > 0 ? (
                    <div className="space-y-3">
                      {selectedOrg.apiKeys.map((key) => (
                        <div key={key.id} className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <p className="font-medium">{key.name}</p>
                            <div className="flex items-center space-x-2">
                              <Badge variant={key.environment === 'production' ? 'destructive' : 'secondary'}>
                                {key.environment}
                              </Badge>
                              {key.isActive ? (
                                <CheckCircle className="h-4 w-4 text-green-600" />
                              ) : (
                                <XCircle className="h-4 w-4 text-red-600" />
                              )}
                            </div>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">
                            Services: {key.services.join(', ')}
                          </p>
                          <div className="text-xs text-muted-foreground">
                            Usage: {key.usage.requests.toLocaleString()} / {key.usage.limit.toLocaleString()} requests
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      No API keys found for this organization
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="settings" className="space-y-4">
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium mb-3">OAuth Configuration</h4>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Provider</span>
                          <Badge variant="outline">{selectedOrg.settings.oauth.provider}</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Domain</span>
                          <span className="text-sm text-muted-foreground">{selectedOrg.settings.oauth.domain}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Enabled</span>
                          {selectedOrg.settings.oauth.isEnabled ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-600" />
                          )}
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-3">Security Settings</h4>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Two-Factor Required</span>
                          {selectedOrg.settings.security.twoFactorRequired ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-600" />
                          )}
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">API Key Rotation</span>
                          <span className="text-sm text-muted-foreground">
                            {selectedOrg.settings.security.apiKeyRotation} days
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}