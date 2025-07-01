'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  Users, 
  DollarSign, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  XCircle,
  Clock,
  Globe,
  Smartphone,
  MessageSquare,
  CreditCard,
  Activity,
  Filter,
  Download,
  RefreshCw,
  Eye,
  Settings,
  Shield,
  Zap
} from 'lucide-react';

const AdminDashboard: React.FC = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('revenue');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data for demonstration
  const [dashboardData, setDashboardData] = useState({
    overview: {
      totalRevenue: 1250000,
      totalUsers: 47200,
      activeSubscriptions: 42850,
      apiCalls: 8932451,
      revenueGrowth: 12.5,
      userGrowth: 8.3,
      subscriptionGrowth: 15.2,
      apiGrowth: 22.1
    },
    recentActivity: [
      { id: 1, type: 'subscription', user: 'demo_bank', action: 'Upgraded to BLACK tier', time: '2 minutes ago', status: 'success' },
      { id: 2, type: 'payment', user: 'retail_user_123', action: 'Payment completed - ₹499', time: '5 minutes ago', status: 'success' },
      { id: 3, type: 'api', user: 'fintech_partner', action: 'API quota exceeded', time: '8 minutes ago', status: 'warning' },
      { id: 4, type: 'user', user: 'new_trader_456', action: 'Account registered', time: '12 minutes ago', status: 'info' },
      { id: 5, type: 'whatsapp', user: 'premium_user', action: 'WhatsApp message sent', time: '15 minutes ago', status: 'success' }
    ],
    systemHealth: {
      api: { status: 'healthy', uptime: 99.98, responseTime: 145 },
      database: { status: 'healthy', uptime: 99.95, responseTime: 12 },
      whatsapp: { status: 'degraded', uptime: 98.2, responseTime: 892 },
      billing: { status: 'healthy', uptime: 99.99, responseTime: 67 },
      ai: { status: 'healthy', uptime: 99.87, responseTime: 234 }
    },
    tierDistribution: [
      { tier: 'LITE', users: 35400, revenue: 708000, color: 'bg-blue-500' },
      { tier: 'PRO', users: 8250, revenue: 2062500, color: 'bg-green-500' },
      { tier: 'ELITE', users: 3425, revenue: 1541250, color: 'bg-purple-500' },
      { tier: 'BLACK', users: 125, revenue: 937500, color: 'bg-black' }
    ]
  });

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    setTimeout(() => {
      setIsRefreshing(false);
    }, 2000);
  };

  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 }
  };

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <motion.header 
        className="bg-white border-b border-slate-200 sticky top-0 z-50"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-8 w-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-slate-900">Admin Dashboard</h1>
              </div>
              <div className="flex items-center space-x-2 ml-8">
                <select 
                  value={selectedTimeRange}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                  className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="1d">Last 24 hours</option>
                  <option value="7d">Last 7 days</option>
                  <option value="30d">Last 30 days</option>
                  <option value="90d">Last 90 days</option>
                </select>
                <button 
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                  className="flex items-center space-x-2 px-3 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                  <span className="text-sm">Refresh</span>
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="text-slate-600 hover:text-slate-900 transition-colors">
                <Download className="h-5 w-5" />
              </button>
              <button className="text-slate-600 hover:text-slate-900 transition-colors">
                <Settings className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Navigation Tabs */}
      <motion.div 
        className="bg-white border-b border-slate-200"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'users', label: 'Users', icon: Users },
              { id: 'revenue', label: 'Revenue', icon: DollarSign },
              { id: 'system', label: 'System Health', icon: Activity },
              { id: 'api', label: 'API Usage', icon: Globe },
              { id: 'support', label: 'Support', icon: MessageSquare }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </motion.div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <motion.div {...fadeInUp} transition={{ duration: 0.6 }} className="space-y-8">
            {/* Key Metrics */}
            <motion.div 
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
              variants={staggerChildren}
              initial="initial"
              animate="animate"
            >
              {[
                {
                  title: 'Total Revenue',
                  value: `₹${(dashboardData.overview.totalRevenue / 100000).toFixed(1)}L`,
                  change: `+${dashboardData.overview.revenueGrowth}%`,
                  icon: DollarSign,
                  color: 'text-green-600',
                  bgColor: 'bg-green-100'
                },
                {
                  title: 'Total Users',
                  value: `${(dashboardData.overview.totalUsers / 1000).toFixed(1)}K`,
                  change: `+${dashboardData.overview.userGrowth}%`,
                  icon: Users,
                  color: 'text-blue-600',
                  bgColor: 'bg-blue-100'
                },
                {
                  title: 'Active Subscriptions',
                  value: `${(dashboardData.overview.activeSubscriptions / 1000).toFixed(1)}K`,
                  change: `+${dashboardData.overview.subscriptionGrowth}%`,
                  icon: CreditCard,
                  color: 'text-purple-600',
                  bgColor: 'bg-purple-100'
                },
                {
                  title: 'API Calls',
                  value: `${(dashboardData.overview.apiCalls / 1000000).toFixed(1)}M`,
                  change: `+${dashboardData.overview.apiGrowth}%`,
                  icon: Globe,
                  color: 'text-orange-600',
                  bgColor: 'bg-orange-100'
                }
              ].map((metric, index) => (
                <motion.div
                  key={index}
                  variants={fadeInUp}
                  transition={{ duration: 0.6 }}
                  className="bg-white p-6 rounded-xl border border-slate-200 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-600">{metric.title}</p>
                      <p className="text-3xl font-bold text-slate-900 mt-2">{metric.value}</p>
                      <div className="flex items-center mt-2">
                        <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                        <span className="text-sm text-green-600">{metric.change}</span>
                        <span className="text-sm text-slate-500 ml-1">vs last period</span>
                      </div>
                    </div>
                    <div className={`p-3 rounded-lg ${metric.bgColor}`}>
                      <metric.icon className={`h-6 w-6 ${metric.color}`} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Charts Section */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Revenue Chart */}
              <motion.div 
                className="bg-white p-6 rounded-xl border border-slate-200"
                variants={fadeInUp}
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-slate-900">Revenue Overview</h3>
                  <select className="px-3 py-2 border border-slate-300 rounded-lg text-sm">
                    <option>Revenue</option>
                    <option>Users</option>
                    <option>Subscriptions</option>
                  </select>
                </div>
                
                {/* Mock Chart */}
                <div className="h-64 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg flex items-end justify-center p-4">
                  <div className="flex items-end space-x-2 h-full w-full">
                    {[40, 65, 45, 80, 60, 90, 75].map((height, index) => (
                      <div
                        key={index}
                        className="bg-blue-500 rounded-t flex-1 transition-all duration-500 hover:bg-blue-600"
                        style={{ height: `${height}%` }}
                      />
                    ))}
                  </div>
                </div>
                
                <div className="mt-4 flex justify-center space-x-6 text-sm">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                    <span className="text-slate-600">Revenue</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                    <span className="text-slate-600">Target</span>
                  </div>
                </div>
              </motion.div>

              {/* Tier Distribution */}
              <motion.div 
                className="bg-white p-6 rounded-xl border border-slate-200"
                variants={fadeInUp}
              >
                <h3 className="text-lg font-semibold text-slate-900 mb-6">User Tier Distribution</h3>
                
                <div className="space-y-4">
                  {dashboardData.tierDistribution.map((tier, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded ${tier.color}`}></div>
                        <span className="font-medium text-slate-900">{tier.tier}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-slate-900">
                          {tier.users.toLocaleString()} users
                        </div>
                        <div className="text-xs text-slate-600">
                          ₹{(tier.revenue / 100000).toFixed(1)}L revenue
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 pt-4 border-t border-slate-200">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Total Users:</span>
                    <span className="font-medium">
                      {dashboardData.tierDistribution.reduce((sum, tier) => sum + tier.users, 0).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm mt-1">
                    <span className="text-slate-600">Total Revenue:</span>
                    <span className="font-medium">
                      ₹{(dashboardData.tierDistribution.reduce((sum, tier) => sum + tier.revenue, 0) / 100000).toFixed(1)}L
                    </span>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Recent Activity & System Health */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Recent Activity */}
              <motion.div 
                className="bg-white p-6 rounded-xl border border-slate-200"
                variants={fadeInUp}
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-slate-900">Recent Activity</h3>
                  <button className="text-blue-600 hover:text-blue-800 text-sm">View all</button>
                </div>
                
                <div className="space-y-4">
                  {dashboardData.recentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className={`p-2 rounded-lg ${
                        activity.status === 'success' ? 'bg-green-100' :
                        activity.status === 'warning' ? 'bg-yellow-100' :
                        activity.status === 'error' ? 'bg-red-100' :
                        'bg-blue-100'
                      }`}>
                        {activity.status === 'success' && <CheckCircle className="h-4 w-4 text-green-600" />}
                        {activity.status === 'warning' && <AlertTriangle className="h-4 w-4 text-yellow-600" />}
                        {activity.status === 'error' && <XCircle className="h-4 w-4 text-red-600" />}
                        {activity.status === 'info' && <Users className="h-4 w-4 text-blue-600" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900">{activity.user}</p>
                        <p className="text-sm text-slate-600">{activity.action}</p>
                        <p className="text-xs text-slate-500 mt-1">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* System Health */}
              <motion.div 
                className="bg-white p-6 rounded-xl border border-slate-200"
                variants={fadeInUp}
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-slate-900">System Health</h3>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-slate-600">All systems operational</span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  {Object.entries(dashboardData.systemHealth).map(([service, health]) => (
                    <div key={service} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${
                          health.status === 'healthy' ? 'bg-green-500' :
                          health.status === 'degraded' ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}></div>
                        <span className="font-medium text-slate-900 capitalize">{service}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-slate-900">
                          {health.uptime}% uptime
                        </div>
                        <div className="text-xs text-slate-600">
                          {health.responseTime}ms avg
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 pt-4 border-t border-slate-200">
                  <button className="w-full text-blue-600 hover:text-blue-800 text-sm font-medium">
                    View detailed system status →
                  </button>
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}

        {activeTab === 'users' && (
          <UserManagement />
        )}

        {activeTab === 'revenue' && (
          <RevenueAnalytics />
        )}

        {activeTab === 'system' && (
          <SystemHealth />
        )}

        {activeTab === 'api' && (
          <APIUsage />
        )}

        {activeTab === 'support' && (
          <SupportDashboard />
        )}
      </div>
    </div>
  );
};

// User Management Component
const UserManagement: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTier, setSelectedTier] = useState('all');

  const users = [
    { id: 1, name: 'Demo Bank', email: 'admin@demobank.com', tier: 'BLACK', status: 'active', revenue: 125000, joinDate: '2025-01-15' },
    { id: 2, name: 'John Trader', email: 'john@example.com', tier: 'PRO', status: 'active', revenue: 2499, joinDate: '2025-02-20' },
    { id: 3, name: 'Fintech Startup', email: 'dev@fintech.com', tier: 'ELITE', status: 'active', revenue: 12500, joinDate: '2025-03-10' },
    { id: 4, name: 'Retail Investor', email: 'retail@gmail.com', tier: 'LITE', status: 'suspended', revenue: 199, joinDate: '2025-04-05' }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Filters */}
      <div className="bg-white p-6 rounded-xl border border-slate-200">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <select 
            value={selectedTier}
            onChange={(e) => setSelectedTier(e.target.value)}
            className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Tiers</option>
            <option value="LITE">LITE</option>
            <option value="PRO">PRO</option>
            <option value="ELITE">ELITE</option>
            <option value="BLACK">BLACK</option>
          </select>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Export
          </button>
        </div>
      </div>

      {/* User Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Tier</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Revenue</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Join Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-slate-900">{user.name}</div>
                      <div className="text-sm text-slate-500">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.tier === 'BLACK' ? 'bg-black text-white' :
                      user.tier === 'ELITE' ? 'bg-purple-100 text-purple-800' :
                      user.tier === 'PRO' ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {user.tier}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    ₹{user.revenue.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    {user.joinDate}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button className="text-blue-600 hover:text-blue-900">
                      <Eye className="h-4 w-4" />
                    </button>
                    <button className="text-slate-600 hover:text-slate-900">
                      <Settings className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
};

// Revenue Analytics Component
const RevenueAnalytics: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      <div className="text-center py-20">
        <DollarSign className="h-16 w-16 text-slate-400 mx-auto mb-4" />
        <h3 className="text-xl font-medium text-slate-600">Revenue Analytics</h3>
        <p className="text-slate-500 mt-2">Detailed revenue analytics coming soon...</p>
      </div>
    </motion.div>
  );
};

// System Health Component
const SystemHealth: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      <div className="text-center py-20">
        <Activity className="h-16 w-16 text-slate-400 mx-auto mb-4" />
        <h3 className="text-xl font-medium text-slate-600">System Health Monitoring</h3>
        <p className="text-slate-500 mt-2">Advanced system monitoring dashboard coming soon...</p>
      </div>
    </motion.div>
  );
};

// API Usage Component
const APIUsage: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      <div className="text-center py-20">
        <Globe className="h-16 w-16 text-slate-400 mx-auto mb-4" />
        <h3 className="text-xl font-medium text-slate-600">API Usage Analytics</h3>
        <p className="text-slate-500 mt-2">Comprehensive API usage dashboard coming soon...</p>
      </div>
    </motion.div>
  );
};

// Support Dashboard Component
const SupportDashboard: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      <div className="text-center py-20">
        <MessageSquare className="h-16 w-16 text-slate-400 mx-auto mb-4" />
        <h3 className="text-xl font-medium text-slate-600">Support Dashboard</h3>
        <p className="text-slate-500 mt-2">Support ticket management coming soon...</p>
      </div>
    </motion.div>
  );
};

export default AdminDashboard;