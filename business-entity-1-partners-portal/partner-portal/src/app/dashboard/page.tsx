'use client';

import React from 'react';
import { useSession } from 'next-auth/react';
import { motion } from 'framer-motion';
import { redirect } from 'next/navigation';
import { 
  BarChart3, 
  Users, 
  DollarSign, 
  TrendingUp, 
  Activity,
  Bell,
  Settings,
  LogOut,
  Shield,
  Zap
} from 'lucide-react';
import Link from 'next/link';

const DashboardPage: React.FC = () => {
  const { data: session, status } = useSession();

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (status === 'unauthenticated') {
    redirect('/auth/signin');
  }

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
                <h1 className="text-2xl font-bold text-slate-900">TradeMate Portal</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-slate-900">{session?.user?.name}</p>
                <p className="text-xs text-slate-600">{session?.user?.email}</p>
              </div>
              <div className="flex items-center space-x-2">
                <button className="p-2 text-slate-600 hover:text-slate-900 transition-colors">
                  <Bell className="h-5 w-5" />
                </button>
                <button className="p-2 text-slate-600 hover:text-slate-900 transition-colors">
                  <Settings className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <motion.div 
          className="mb-8"
          {...fadeInUp}
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-2">
            Welcome back, {session?.user?.name?.split(' ')[0]}
          </h2>
          <p className="text-slate-600">
            Manage your TradeMate integration and monitor your API usage.
          </p>
        </motion.div>

        {/* Quick Stats */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          variants={staggerChildren}
          initial="initial"
          animate="animate"
        >
          {[
            {
              title: 'API Calls',
              value: '12.4K',
              change: '+8.2%',
              icon: Activity,
              color: 'text-blue-600',
              bgColor: 'bg-blue-100'
            },
            {
              title: 'Active Users',
              value: '1,284',
              change: '+12.5%',
              icon: Users,
              color: 'text-green-600',
              bgColor: 'bg-green-100'
            },
            {
              title: 'Revenue',
              value: '₹85.2K',
              change: '+15.3%',
              icon: DollarSign,
              color: 'text-purple-600',
              bgColor: 'bg-purple-100'
            },
            {
              title: 'Uptime',
              value: '99.9%',
              change: '+0.1%',
              icon: Zap,
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
                    <span className="text-sm text-slate-500 ml-1">vs last month</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${metric.bgColor}`}>
                  <metric.icon className={`h-6 w-6 ${metric.color}`} />
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Quick Actions */}
        <motion.div 
          className="grid lg:grid-cols-2 gap-6 mb-8"
          variants={staggerChildren}
          initial="initial"
          animate="animate"
        >
          {/* API Management */}
          <motion.div 
            className="bg-white p-6 rounded-xl border border-slate-200"
            variants={fadeInUp}
          >
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
              <Activity className="h-5 w-5 mr-2 text-blue-600" />
              API Management
            </h3>
            <p className="text-slate-600 mb-6">
              Monitor your API usage, manage keys, and view integration status.
            </p>
            <div className="space-y-3">
              <Link 
                href="/demo"
                className="w-full text-left px-4 py-3 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors flex items-center justify-between"
              >
                <span className="font-medium text-green-900">🚀 Try Interactive Demo</span>
                <span className="text-green-600">→</span>
              </Link>
              <Link 
                href="/developer"
                className="w-full text-left px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors flex items-center justify-between"
              >
                <span className="font-medium text-blue-900">View API Documentation</span>
                <span className="text-blue-600">→</span>
              </Link>
              <button className="w-full text-left px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors flex items-center justify-between">
                <span className="font-medium text-slate-900">Manage API Keys</span>
                <span className="text-slate-600">→</span>
              </button>
              <button className="w-full text-left px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors flex items-center justify-between">
                <span className="font-medium text-slate-900">Usage Analytics</span>
                <span className="text-slate-600">→</span>
              </button>
            </div>
          </motion.div>

          {/* System Health */}
          <motion.div 
            className="bg-white p-6 rounded-xl border border-slate-200"
            variants={fadeInUp}
          >
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
              <Shield className="h-5 w-5 mr-2 text-green-600" />
              System Health
            </h3>
            <p className="text-slate-600 mb-6">
              Monitor system health and view self-healing status.
            </p>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="font-medium text-slate-900">API Service</span>
                </div>
                <span className="text-sm text-slate-600">Healthy</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="font-medium text-slate-900">Database</span>
                </div>
                <span className="text-sm text-slate-600">Healthy</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span className="font-medium text-slate-900">Cache</span>
                </div>
                <span className="text-sm text-slate-600">Degraded</span>
              </div>
              <Link 
                href="/dashboard/health"
                className="w-full inline-block text-center px-4 py-2 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors font-medium text-green-900 mt-4"
              >
                View Self-Healing Dashboard
              </Link>
            </div>
          </motion.div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div 
          className="bg-white p-6 rounded-xl border border-slate-200"
          {...fadeInUp}
        >
          <h3 className="text-lg font-semibold text-slate-900 mb-6">
            Recent Activity
          </h3>
          <div className="space-y-4">
            {[
              {
                action: 'API key generated',
                time: '2 minutes ago',
                status: 'success'
              },
              {
                action: 'WhatsApp integration tested',
                time: '15 minutes ago',
                status: 'success'
              },
              {
                action: 'Rate limit warning',
                time: '1 hour ago',
                status: 'warning'
              },
              {
                action: 'User authentication successful',
                time: '2 hours ago',
                status: 'info'
              }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-3 border-b border-slate-100 last:border-0">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-green-500' :
                    activity.status === 'warning' ? 'bg-yellow-500' :
                    activity.status === 'error' ? 'bg-red-500' :
                    'bg-blue-500'
                  }`}></div>
                  <span className="font-medium text-slate-900">{activity.action}</span>
                </div>
                <span className="text-sm text-slate-500">{activity.time}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardPage;