'use client'

import { useAppStore } from '@/lib/store'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  BarChart3,
  Key,
  Zap,
  CreditCard,
  Users,
  Activity,
  TrendingUp,
  ArrowRight,
  Bot,
  TestTube,
  Settings,
  Eye
} from 'lucide-react'
import Link from 'next/link'

export default function DashboardPage() {
  const { user, organization, selectedServices } = useAppStore()

  const quickStats = [
    { label: 'API Requests Today', value: '12,543', icon: <BarChart3 className="h-5 w-5" />, color: 'text-blue-600' },
    { label: 'Active API Keys', value: '3', icon: <Key className="h-5 w-5" />, color: 'text-green-600' },
    { label: 'Uptime', value: '99.97%', icon: <Activity className="h-5 w-5" />, color: 'text-emerald-600' },
    { label: 'This Month Cost', value: '₹75,000', icon: <CreditCard className="h-5 w-5" />, color: 'text-purple-600' }
  ]

  const quickActions = [
    { title: 'Create API Key', description: 'Generate new API keys for your services', href: '/api-keys', icon: <Key className="h-5 w-5" /> },
    { title: 'Test in Sandbox', description: 'Try APIs with mock data', href: '/sandbox', icon: <TestTube className="h-5 w-5" /> },
    { title: 'View Documentation', description: 'API guides and examples', href: '/docs', icon: <Eye className="h-5 w-5" /> },
    { title: 'Manage Billing', description: 'View usage and invoices', href: '/billing', icon: <CreditCard className="h-5 w-5" /> },
    { title: 'Monitor Systems', description: 'Real-time system health', href: '/monitoring', icon: <Activity className="h-5 w-5" /> },
    { title: 'Admin Portal', description: 'Manage organizations', href: '/admin', icon: <Settings className="h-5 w-5" /> }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Welcome back, {user?.name || 'Developer'}!</h1>
              <p className="text-muted-foreground">
                {organization?.name || 'Your Organization'} • {organization?.plan || 'Professional'} Plan
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="text-green-600 border-green-600">
                <Activity className="h-3 w-3 mr-1" />
                All Systems Operational
              </Badge>
              <Link href="/pricing">
                <Button>
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Upgrade Plan
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Quick Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          {quickStats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                  </div>
                  <div className={stat.color}>
                    {stat.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and shortcuts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {quickActions.map((action, index) => (
                  <Link key={index} href={action.href}>
                    <Card className="cursor-pointer hover:shadow-lg transition-all">
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-primary/10 rounded-lg text-primary">
                            {action.icon}
                          </div>
                          <div>
                            <h4 className="font-medium">{action.title}</h4>
                            <p className="text-sm text-muted-foreground">{action.description}</p>
                          </div>
                          <ArrowRight className="h-4 w-4 text-muted-foreground ml-auto" />
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Service Status */}
          <Card>
            <CardHeader>
              <CardTitle>Service Status</CardTitle>
              <CardDescription>Current health of all services</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: 'AI Suite', status: 'operational', latency: '125ms' },
                  { name: 'Anonymous Services', status: 'operational', latency: '98ms' },
                  { name: 'Trading API', status: 'operational', latency: '156ms' },
                  { name: 'Banking API', status: 'operational', latency: '89ms' }
                ].map((service, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm font-medium">{service.name}</span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {service.latency}
                    </div>
                  </div>
                ))}
              </div>
              <Link href="/monitoring" className="block mt-4">
                <Button variant="outline" className="w-full">
                  View Detailed Monitoring
                  <ArrowRight className="h-3 w-3 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest actions and system events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { time: '2 minutes ago', event: 'API key "Production Key" used for Trading API', type: 'api' },
                { time: '15 minutes ago', event: 'New AI ticket created for memory usage monitoring', type: 'ai' },
                { time: '1 hour ago', event: 'Sandbox test completed for Banking API', type: 'test' },
                { time: '3 hours ago', event: 'Invoice #INV-001 paid successfully', type: 'billing' },
                { time: '1 day ago', event: 'API key "Development Key" created', type: 'api' }
              ].map((activity, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                  <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                    {activity.type === 'api' && <Key className="h-4 w-4 text-primary" />}
                    {activity.type === 'ai' && <Bot className="h-4 w-4 text-primary" />}
                    {activity.type === 'test' && <TestTube className="h-4 w-4 text-primary" />}
                    {activity.type === 'billing' && <CreditCard className="h-4 w-4 text-primary" />}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.event}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}