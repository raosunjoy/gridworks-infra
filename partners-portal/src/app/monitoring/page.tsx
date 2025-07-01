'use client'

import { useState, useEffect } from 'react'
import { useAppStore } from '@/lib/store'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Zap,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Clock,
  Server,
  Database,
  Cpu,
  HardDrive,
  Network,
  Bot,
  Ticket,
  Bell,
  Eye,
  Settings
} from 'lucide-react'

interface SystemMetric {
  name: string
  value: number
  unit: string
  status: 'healthy' | 'warning' | 'critical'
  trend: 'up' | 'down' | 'stable'
  icon: React.ReactNode
}

interface Incident {
  id: string
  title: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: 'investigating' | 'identified' | 'monitoring' | 'resolved'
  createdAt: Date
  resolvedAt?: Date
  affectedServices: string[]
  autoResolved: boolean
}

interface AiTicket {
  id: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  category: 'performance' | 'availability' | 'security' | 'billing' | 'integration'
  aiAnalysis: string
  suggestedActions: string[]
  createdAt: Date
  assignedTo?: string
}

export default function MonitoringPage() {
  const { user, organization } = useAppStore()
  const [currentTab, setCurrentTab] = useState('overview')
  const [refreshing, setRefreshing] = useState(false)

  // Mock system metrics
  const systemMetrics: SystemMetric[] = [
    {
      name: 'API Response Time',
      value: 125,
      unit: 'ms',
      status: 'healthy',
      trend: 'stable',
      icon: <Zap className="h-4 w-4" />
    },
    {
      name: 'Uptime',
      value: 99.97,
      unit: '%',
      status: 'healthy',
      trend: 'up',
      icon: <Activity className="h-4 w-4" />
    },
    {
      name: 'Error Rate',
      value: 0.03,
      unit: '%',
      status: 'healthy',
      trend: 'down',
      icon: <AlertTriangle className="h-4 w-4" />
    },
    {
      name: 'CPU Usage',
      value: 45,
      unit: '%',
      status: 'healthy',
      trend: 'stable',
      icon: <Cpu className="h-4 w-4" />
    },
    {
      name: 'Memory Usage',
      value: 68,
      unit: '%',
      status: 'warning',
      trend: 'up',
      icon: <HardDrive className="h-4 w-4" />
    },
    {
      name: 'Network I/O',
      value: 2.4,
      unit: 'GB/s',
      status: 'healthy',
      trend: 'stable',
      icon: <Network className="h-4 w-4" />
    }
  ]

  // Mock recent incidents
  const incidents: Incident[] = [
    {
      id: 'inc_001',
      title: 'API Rate Limit Exceeded',
      description: 'High traffic caused rate limiting on AI Suite APIs',
      severity: 'medium',
      status: 'resolved',
      createdAt: new Date('2024-07-15T10:30:00'),
      resolvedAt: new Date('2024-07-15T11:15:00'),
      affectedServices: ['AI Suite'],
      autoResolved: true
    },
    {
      id: 'inc_002',
      title: 'Database Connection Pool Exhausted',
      description: 'Trading service experiencing connection timeouts',
      severity: 'high',
      status: 'monitoring',
      createdAt: new Date('2024-07-14T15:45:00'),
      resolvedAt: new Date('2024-07-14T16:30:00'),
      affectedServices: ['Trading API'],
      autoResolved: true
    },
    {
      id: 'inc_003',
      title: 'Increased Response Times',
      description: 'Banking API showing elevated response times',
      severity: 'low',
      status: 'resolved',
      createdAt: new Date('2024-07-13T09:20:00'),
      resolvedAt: new Date('2024-07-13T09:45:00'),
      affectedServices: ['Banking API'],
      autoResolved: false
    }
  ]

  // Mock AI-generated tickets
  const aiTickets: AiTicket[] = [
    {
      id: 'ticket_001',
      title: 'Memory Usage Trending Upward',
      description: 'System memory usage has increased by 15% over the past 24 hours',
      priority: 'medium',
      status: 'in_progress',
      category: 'performance',
      aiAnalysis: 'Analysis indicates potential memory leak in the AI Suite service. Pattern suggests gradual accumulation over time, likely related to chat session management.',
      suggestedActions: [
        'Review chat session cleanup routines',
        'Implement memory profiling',
        'Consider increasing memory allocation temporarily',
        'Schedule service restart during low-traffic window'
      ],
      createdAt: new Date('2024-07-15T08:30:00'),
      assignedTo: 'AI System'
    },
    {
      id: 'ticket_002',
      title: 'Unusual API Usage Pattern Detected',
      description: 'Anonymous Services API showing 300% increase in usage from specific IP range',
      priority: 'high',
      status: 'open',
      category: 'security',
      aiAnalysis: 'Detected suspicious traffic pattern suggesting potential automated testing or reconnaissance. Traffic originates from cloud provider IP ranges.',
      suggestedActions: [
        'Review authentication logs',
        'Implement rate limiting for IP range',
        'Monitor for data exfiltration attempts',
        'Contact security team for further analysis'
      ],
      createdAt: new Date('2024-07-15T12:15:00')
    },
    {
      id: 'ticket_003',
      title: 'Billing Discrepancy Identified',
      description: 'Usage tracking shows mismatch between recorded and billed API calls',
      priority: 'medium',
      status: 'resolved',
      category: 'billing',
      aiAnalysis: 'Identified timing issue in usage aggregation causing double-counting during daily rollover period. Affects approximately 0.1% of total requests.',
      suggestedActions: [
        'Adjust aggregation timing window',
        'Implement idempotency checks',
        'Review billing calculation logic',
        'Process corrective billing adjustments'
      ],
      createdAt: new Date('2024-07-14T16:20:00'),
      assignedTo: 'Billing Team'
    }
  ]

  const refreshMetrics = async () => {
    setRefreshing(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    setRefreshing(false)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-50 border-green-200'
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'critical': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'critical': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getIncidentStatusIcon = (status: string) => {
    switch (status) {
      case 'resolved': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'monitoring': return <Eye className="h-4 w-4 text-blue-600" />
      case 'investigating': return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      default: return <XCircle className="h-4 w-4 text-red-600" />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">System Monitoring</h1>
              <Badge variant="outline" className="text-green-600 border-green-600">
                <Activity className="h-3 w-3 mr-1" />
                All Systems Operational
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline">
                {organization?.name || 'Your Organization'}
              </Badge>
              <Button variant="outline" onClick={refreshMetrics} disabled={refreshing}>
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="incidents">Incidents</TabsTrigger>
            <TabsTrigger value="ai-tickets">AI Tickets</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* System Health Metrics */}
            <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4">
              {systemMetrics.map((metric, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {metric.icon}
                        <span className="text-xs font-medium text-muted-foreground">{metric.name}</span>
                      </div>
                      <div className="flex items-center">
                        {metric.trend === 'up' && <TrendingUp className="h-3 w-3 text-green-600" />}
                        {metric.trend === 'down' && <TrendingDown className="h-3 w-3 text-red-600" />}
                        {metric.trend === 'stable' && <div className="w-3 h-3 bg-gray-400 rounded-full" />}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <p className="text-lg font-bold">
                        {metric.value}{metric.unit}
                      </p>
                      <Badge variant="outline" className={getStatusColor(metric.status)}>
                        {metric.status}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Service Status */}
            <Card>
              <CardHeader>
                <CardTitle>Service Status</CardTitle>
                <CardDescription>Real-time status of all GridWorks services</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  {[
                    { name: 'AI Suite Services', status: 'operational', uptime: 99.98 },
                    { name: 'Anonymous Services', status: 'operational', uptime: 99.95 },
                    { name: 'Trading-as-a-Service', status: 'operational', uptime: 99.97 },
                    { name: 'Banking-as-a-Service', status: 'operational', uptime: 99.99 }
                  ].map((service, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <div>
                          <p className="font-medium">{service.name}</p>
                          <p className="text-sm text-muted-foreground">{service.uptime}% uptime</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-green-600 border-green-600">
                        {service.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest system events and automated responses</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { time: '2 minutes ago', event: 'Auto-scaled AI Suite instances', type: 'scale', icon: <TrendingUp className="h-4 w-4 text-blue-600" /> },
                    { time: '15 minutes ago', event: 'Memory cleanup completed', type: 'maintenance', icon: <RefreshCw className="h-4 w-4 text-green-600" /> },
                    { time: '1 hour ago', event: 'Generated AI ticket for usage anomaly', type: 'ai', icon: <Bot className="h-4 w-4 text-purple-600" /> },
                    { time: '3 hours ago', event: 'Resolved database connection issue', type: 'resolve', icon: <CheckCircle className="h-4 w-4 text-green-600" /> }
                  ].map((activity, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                      {activity.icon}
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.event}</p>
                        <p className="text-xs text-muted-foreground">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="incidents" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Incident History</CardTitle>
                <CardDescription>Recent incidents and their resolution status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {incidents.map((incident) => (
                    <div key={incident.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          {getIncidentStatusIcon(incident.status)}
                          <div>
                            <h4 className="font-medium">{incident.title}</h4>
                            <p className="text-sm text-muted-foreground">{incident.description}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className={getSeverityColor(incident.severity)}>
                            {incident.severity}
                          </Badge>
                          {incident.autoResolved && (
                            <Badge variant="outline" className="text-purple-600 border-purple-600">
                              <Bot className="h-3 w-3 mr-1" />
                              Auto-resolved
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      <div className="grid md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Started</p>
                          <p className="font-medium">{incident.createdAt.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Duration</p>
                          <p className="font-medium">
                            {incident.resolvedAt 
                              ? `${Math.round((incident.resolvedAt.getTime() - incident.createdAt.getTime()) / 60000)} minutes`
                              : 'Ongoing'
                            }
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Affected Services</p>
                          <p className="font-medium">{incident.affectedServices.join(', ')}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai-tickets" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>AI-Generated Support Tickets</CardTitle>
                <CardDescription>Automated issue detection and resolution suggestions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {aiTickets.map((ticket) => (
                    <div key={ticket.id} className="p-6 border rounded-lg">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <Bot className="h-5 w-5 text-purple-600" />
                          <div>
                            <h4 className="font-medium">{ticket.title}</h4>
                            <p className="text-sm text-muted-foreground">{ticket.description}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className={getSeverityColor(ticket.priority)}>
                            {ticket.priority}
                          </Badge>
                          <Badge variant="outline">
                            {ticket.status}
                          </Badge>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <h5 className="font-medium mb-2">AI Analysis</h5>
                          <p className="text-sm text-muted-foreground bg-gray-50 p-3 rounded">
                            {ticket.aiAnalysis}
                          </p>
                        </div>

                        <div>
                          <h5 className="font-medium mb-2">Suggested Actions</h5>
                          <ul className="space-y-2">
                            {ticket.suggestedActions.map((action, index) => (
                              <li key={index} className="flex items-center space-x-2 text-sm">
                                <CheckCircle className="h-3 w-3 text-green-600" />
                                <span>{action}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="flex items-center justify-between pt-3 border-t">
                          <div className="text-sm text-muted-foreground">
                            Created {ticket.createdAt.toLocaleString()}
                            {ticket.assignedTo && ` • Assigned to ${ticket.assignedTo}`}
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button variant="outline" size="sm">
                              <Eye className="h-3 w-3 mr-1" />
                              View Details
                            </Button>
                            <Button size="sm">
                              <Ticket className="h-3 w-3 mr-1" />
                              Create Ticket
                            </Button>
                          </div>
                        </div>
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
                <CardTitle>Monitoring Settings</CardTitle>
                <CardDescription>Configure alerts and monitoring preferences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Email Alerts</h4>
                      <p className="text-sm text-muted-foreground">Receive email notifications for critical incidents</p>
                    </div>
                    <Button variant="outline">
                      <Bell className="h-4 w-4 mr-2" />
                      Configure
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">AI Ticket Generation</h4>
                      <p className="text-sm text-muted-foreground">Automatically create tickets for detected anomalies</p>
                    </div>
                    <Button variant="outline">
                      <Bot className="h-4 w-4 mr-2" />
                      Configure
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Auto-healing</h4>
                      <p className="text-sm text-muted-foreground">Enable automatic resolution of common issues</p>
                    </div>
                    <Button variant="outline">
                      <Settings className="h-4 w-4 mr-2" />
                      Configure
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}