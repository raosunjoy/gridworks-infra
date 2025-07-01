'use client'

import { useState, useEffect } from 'react'
import { useAppStore } from '@/lib/store'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { 
  Plus, 
  Key, 
  Copy, 
  Eye, 
  EyeOff, 
  Trash2, 
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  BarChart3,
  Settings,
  Calendar
} from 'lucide-react'
import { Switch } from '@/components/ui/switch'

export default function ApiKeysPage() {
  const { 
    user, 
    organization, 
    generateApiKey, 
    revokeApiKey 
  } = useAppStore()
  
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [keyName, setKeyName] = useState('')
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [environment, setEnvironment] = useState<'sandbox' | 'production'>('sandbox')
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set())
  const [newKey, setNewKey] = useState<string | null>(null)

  const services = [
    { id: 'ai-suite', name: 'AI Suite Services', icon: '🤖' },
    { id: 'anonymous', name: 'Anonymous Services', icon: '🔒' },
    { id: 'trading', name: 'Trading-as-a-Service', icon: '📈' },
    { id: 'banking', name: 'Banking-as-a-Service', icon: '🏦' }
  ]

  const apiKeys = organization?.apiKeys || []

  const handleCreateKey = async () => {
    if (!keyName.trim() || selectedServices.length === 0) return

    try {
      const key = await generateApiKey(
        keyName, 
        selectedServices as any[], 
        environment
      )
      setNewKey(key.key)
      setIsDialogOpen(false)
      setKeyName('')
      setSelectedServices([])
    } catch (error) {
      console.error('Failed to create API key:', error)
    }
  }

  const toggleKeyVisibility = (keyId: string) => {
    const newVisible = new Set(visibleKeys)
    if (newVisible.has(keyId)) {
      newVisible.delete(keyId)
    } else {
      newVisible.add(keyId)
    }
    setVisibleKeys(newVisible)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const formatKey = (key: string, isVisible: boolean) => {
    if (isVisible) return key
    return key.substring(0, 12) + '...' + key.substring(key.length - 4)
  }

  const getUsagePercentage = (used: number, limit: number) => {
    return Math.round((used / limit) * 100)
  }

  const getUsageColor = (percentage: number) => {
    if (percentage < 50) return 'text-green-600'
    if (percentage < 80) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">API Key Management</h1>
              <Badge variant="outline">
                {organization?.name || 'Your Organization'}
              </Badge>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create API Key
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create New API Key</DialogTitle>
                  <DialogDescription>
                    Generate a new API key for accessing GridWorks services
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="keyName">Key Name</Label>
                    <Input
                      id="keyName"
                      placeholder="e.g., Production API, Development Key"
                      value={keyName}
                      onChange={(e) => setKeyName(e.target.value)}
                    />
                  </div>

                  <div>
                    <Label>Environment</Label>
                    <div className="flex items-center space-x-4 mt-2">
                      <div className="flex items-center space-x-2">
                        <input
                          type="radio"
                          id="sandbox"
                          name="environment"
                          checked={environment === 'sandbox'}
                          onChange={() => setEnvironment('sandbox')}
                        />
                        <Label htmlFor="sandbox">Sandbox</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="radio"
                          id="production"
                          name="environment"
                          checked={environment === 'production'}
                          onChange={() => setEnvironment('production')}
                        />
                        <Label htmlFor="production">Production</Label>
                      </div>
                    </div>
                  </div>

                  <div>
                    <Label>Services</Label>
                    <div className="space-y-2 mt-2">
                      {services.map((service) => (
                        <div key={service.id} className="flex items-center space-x-2">
                          <Switch
                            checked={selectedServices.includes(service.id)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedServices([...selectedServices, service.id])
                              } else {
                                setSelectedServices(selectedServices.filter(s => s !== service.id))
                              }
                            }}
                          />
                          <span className="text-sm">{service.icon} {service.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button 
                      onClick={handleCreateKey}
                      disabled={!keyName.trim() || selectedServices.length === 0}
                    >
                      Create Key
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* New Key Alert */}
        {newKey && (
          <Card className="mb-8 border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-green-800 flex items-center">
                <CheckCircle className="h-5 w-5 mr-2" />
                API Key Created Successfully
              </CardTitle>
              <CardDescription className="text-green-700">
                Save this key securely. You won't be able to see it again.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 bg-white p-3 rounded border">
                <code className="flex-1 text-sm font-mono">{newKey}</code>
                <Button size="sm" variant="outline" onClick={() => copyToClipboard(newKey)}>
                  <Copy className="h-3 w-3" />
                </Button>
              </div>
              <Button 
                size="sm" 
                variant="ghost" 
                className="mt-2"
                onClick={() => setNewKey(null)}
              >
                Dismiss
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Overview Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Keys</p>
                  <p className="text-3xl font-bold">{apiKeys.length}</p>
                </div>
                <Key className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active Keys</p>
                  <p className="text-3xl font-bold text-green-600">
                    {apiKeys.filter(key => key.isActive).length}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Production Keys</p>
                  <p className="text-3xl font-bold text-red-600">
                    {apiKeys.filter(key => key.environment === 'production').length}
                  </p>
                </div>
                <Settings className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Requests</p>
                  <p className="text-3xl font-bold">
                    {apiKeys.reduce((sum, key) => sum + key.usage.requests, 0).toLocaleString()}
                  </p>
                </div>
                <BarChart3 className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* API Keys List */}
        <div className="space-y-6">
          {apiKeys.length > 0 ? (
            apiKeys.map((key) => (
              <Card key={key.id} className={`${!key.isActive ? 'opacity-60' : ''}`}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Key className="h-5 w-5 text-primary" />
                      <div>
                        <CardTitle className="text-lg">{key.name}</CardTitle>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant={key.environment === 'production' ? 'destructive' : 'secondary'}>
                            {key.environment}
                          </Badge>
                          {key.isActive ? (
                            <Badge variant="outline" className="text-green-600 border-green-600">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Active
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-red-600 border-red-600">
                              <XCircle className="h-3 w-3 mr-1" />
                              Revoked
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => toggleKeyVisibility(key.id)}
                      >
                        {visibleKeys.has(key.id) ? (
                          <EyeOff className="h-3 w-3" />
                        ) : (
                          <Eye className="h-3 w-3" />
                        )}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => copyToClipboard(key.key)}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                      {key.isActive && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => revokeApiKey(key.id)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* API Key */}
                    <div>
                      <Label className="text-xs">API Key</Label>
                      <div className="flex items-center space-x-2 bg-gray-50 p-2 rounded mt-1">
                        <code className="flex-1 text-sm font-mono">
                          {formatKey(key.key, visibleKeys.has(key.id))}
                        </code>
                      </div>
                    </div>

                    {/* Services */}
                    <div>
                      <Label className="text-xs">Enabled Services</Label>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {key.services.map((serviceId) => {
                          const service = services.find(s => s.id === serviceId)
                          return service ? (
                            <Badge key={serviceId} variant="outline">
                              {service.icon} {service.name}
                            </Badge>
                          ) : null
                        })}
                      </div>
                    </div>

                    {/* Usage Stats */}
                    <div className="grid md:grid-cols-3 gap-4">
                      <div>
                        <Label className="text-xs">Usage This Month</Label>
                        <div className="mt-1">
                          <div className="flex items-center justify-between text-sm">
                            <span>{key.usage.requests.toLocaleString()} requests</span>
                            <span className={getUsageColor(getUsagePercentage(key.usage.requests, key.usage.limit))}>
                              {getUsagePercentage(key.usage.requests, key.usage.limit)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                            <div 
                              className={`h-2 rounded-full ${
                                getUsagePercentage(key.usage.requests, key.usage.limit) < 50 ? 'bg-green-600' :
                                getUsagePercentage(key.usage.requests, key.usage.limit) < 80 ? 'bg-yellow-600' :
                                'bg-red-600'
                              }`}
                              style={{ width: `${Math.min(getUsagePercentage(key.usage.requests, key.usage.limit), 100)}%` }}
                            ></div>
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Limit: {key.usage.limit.toLocaleString()} requests
                          </div>
                        </div>
                      </div>

                      <div>
                        <Label className="text-xs">Created</Label>
                        <div className="flex items-center text-sm mt-1">
                          <Calendar className="h-3 w-3 mr-1 text-muted-foreground" />
                          {new Date(key.createdAt).toLocaleDateString()}
                        </div>
                      </div>

                      <div>
                        <Label className="text-xs">Last Used</Label>
                        <div className="text-sm mt-1">
                          {key.lastUsed ? (
                            new Date(key.lastUsed).toLocaleDateString()
                          ) : (
                            <span className="text-muted-foreground">Never</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <Key className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No API Keys</h3>
                <p className="text-muted-foreground mb-4">
                  Create your first API key to start using GridWorks services
                </p>
                <Button onClick={() => setIsDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create API Key
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}