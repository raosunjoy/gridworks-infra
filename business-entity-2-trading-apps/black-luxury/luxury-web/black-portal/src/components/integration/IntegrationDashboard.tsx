/**
 * Three-Way Integration Dashboard
 * Real-time monitoring and management of the unified ecosystem
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  Users, 
  DollarSign, 
  Shield, 
  Zap, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  ArrowRight,
  Server,
  Database,
  Cloud,
  Lock,
  Globe,
  TrendingUp,
  BarChart3,
  Network
} from 'lucide-react';
import { threeWayIntegration } from '@/services/ThreeWayIntegration';

interface ServiceHealth {
  service: string;
  status: 'healthy' | 'degraded' | 'down';
  latency: number;
  lastCheck: string;
  metrics: {
    requestsPerMinute: number;
    errorRate: number;
    avgResponseTime: number;
  };
}

interface DataFlow {
  from: string;
  to: string;
  messagesPerMinute: number;
  avgLatency: number;
  errorRate: number;
  lastSync: string;
}

interface IntegrationMetrics {
  activeUsers: number;
  syncQueueSize: number;
  healthStatus: 'healthy' | 'degraded' | 'critical';
  dataFlows: {
    portalToPlatform: DataFlow;
    platformToSupport: DataFlow;
    supportToPortal: DataFlow;
  };
  tierDistribution: {
    onyx: number;
    obsidian: number;
    void: number;
  };
  revenueSync: {
    synced: boolean;
    lastSync: string;
  };
}

export const IntegrationDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<IntegrationMetrics | null>(null);
  const [healthChecks, setHealthChecks] = useState<Map<string, ServiceHealth>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        
        // Get integration metrics
        const metricsData = await threeWayIntegration.getIntegrationMetrics();
        setMetrics(metricsData);
        
        // Get health checks
        const healthData = await threeWayIntegration.performHealthCheck();
        setHealthChecks(healthData);
        
      } catch (error) {
        console.error('Failed to load integration data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();

    // Setup auto-refresh
    const interval = autoRefresh ? setInterval(loadData, 10000) : null;

    // Listen for health updates
    const handleHealthUpdate = (health: Map<string, ServiceHealth>) => {
      setHealthChecks(health);
    };

    threeWayIntegration.on('health:updated', handleHealthUpdate);

    return () => {
      if (interval) clearInterval(interval);
      threeWayIntegration.off('health:updated', handleHealthUpdate);
    };
  }, [autoRefresh]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'down':
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getServiceIcon = (service: string) => {
    switch (service) {
      case 'black_portal':
        return <Globe className="w-6 h-6" />;
      case 'trading_platform':
        return <BarChart3 className="w-6 h-6" />;
      case 'support_portal':
        return <Shield className="w-6 h-6" />;
      default:
        return <Server className="w-6 h-6" />;
    }
  };

  const formatLatency = (latency: number) => {
    if (latency < 0) return 'N/A';
    if (latency < 1000) return `${latency}ms`;
    return `${(latency / 1000).toFixed(2)}s`;
  };

  const formatErrorRate = (rate: number) => {
    return `${(rate * 100).toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <RefreshCw className="w-8 h-8 text-purple-500" />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
            Three-Way Integration Dashboard
          </h1>
          <p className="text-gray-400 mt-2">
            Unified ecosystem monitoring for Black Portal ↔ Platform ↔ Support
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
              autoRefresh 
                ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
                : 'bg-gray-800 text-gray-400 border border-gray-700'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto Refresh
          </button>
          
          <div className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
            metrics?.healthStatus === 'healthy' 
              ? 'bg-green-500/20 text-green-400' 
              : metrics?.healthStatus === 'degraded'
              ? 'bg-yellow-500/20 text-yellow-400'
              : 'bg-red-500/20 text-red-400'
          }`}>
            {getStatusIcon(metrics?.healthStatus || 'unknown')}
            <span className="font-medium">
              System {metrics?.healthStatus || 'Unknown'}
            </span>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-900 border border-gray-800 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <Users className="w-8 h-8 text-blue-500" />
            <TrendingUp className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-3xl font-bold">{metrics?.activeUsers.toLocaleString() || 0}</div>
          <div className="text-gray-400 text-sm mt-1">Active Users</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gray-900 border border-gray-800 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <Database className="w-8 h-8 text-purple-500" />
            <div className={`text-sm px-2 py-1 rounded ${
              metrics?.syncQueueSize === 0 
                ? 'bg-green-500/20 text-green-400' 
                : 'bg-yellow-500/20 text-yellow-400'
            }`}>
              {metrics?.syncQueueSize || 0} pending
            </div>
          </div>
          <div className="text-3xl font-bold">Real-time</div>
          <div className="text-gray-400 text-sm mt-1">Data Synchronization</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-900 border border-gray-800 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <DollarSign className="w-8 h-8 text-green-500" />
            {metrics?.revenueSync.synced ? (
              <CheckCircle className="w-5 h-5 text-green-400" />
            ) : (
              <RefreshCw className="w-5 h-5 text-yellow-400 animate-spin" />
            )}
          </div>
          <div className="text-3xl font-bold">₹15,250 Cr</div>
          <div className="text-gray-400 text-sm mt-1">Annual Revenue Target</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gray-900 border border-gray-800 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <Lock className="w-8 h-8 text-yellow-500" />
            <Shield className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-3xl font-bold">100%</div>
          <div className="text-gray-400 text-sm mt-1">ZK Privacy Active</div>
        </motion.div>
      </div>

      {/* Service Health */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-purple-400" />
          Service Health Status
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.from(healthChecks.entries()).map(([key, health]) => (
            <motion.div
              key={key}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gray-900 border border-gray-800 rounded-xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getServiceIcon(health.service)}
                  <div>
                    <div className="font-semibold capitalize">
                      {health.service.replace('_', ' ')}
                    </div>
                    <div className="text-sm text-gray-400">
                      Last check: {new Date(health.lastCheck).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
                {getStatusIcon(health.status)}
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Latency</span>
                  <span className={health.latency < 100 ? 'text-green-400' : 'text-yellow-400'}>
                    {formatLatency(health.latency)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Requests/min</span>
                  <span>{health.metrics.requestsPerMinute}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Error Rate</span>
                  <span className={health.metrics.errorRate < 0.01 ? 'text-green-400' : 'text-red-400'}>
                    {formatErrorRate(health.metrics.errorRate)}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Data Flow Visualization */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Network className="w-5 h-5 text-purple-400" />
          Real-time Data Flow
        </h2>
        
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Portal to Platform */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-center"
            >
              <div className="mb-4">
                <Globe className="w-12 h-12 mx-auto text-purple-500 mb-2" />
                <div className="font-semibold">Black Portal</div>
              </div>
              
              <motion.div
                animate={{ x: [0, 10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="flex items-center justify-center my-4"
              >
                <ArrowRight className="w-6 h-6 text-green-400" />
              </motion.div>
              
              <div className="text-sm space-y-1">
                <div>{metrics?.dataFlows.portalToPlatform.messagesPerMinute || 0} msg/min</div>
                <div className="text-gray-400">
                  {formatLatency(metrics?.dataFlows.portalToPlatform.avgLatency || 0)}
                </div>
              </div>
            </motion.div>

            {/* Platform to Support */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-center"
            >
              <div className="mb-4">
                <BarChart3 className="w-12 h-12 mx-auto text-blue-500 mb-2" />
                <div className="font-semibold">Trading Platform</div>
              </div>
              
              <motion.div
                animate={{ x: [0, 10, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                className="flex items-center justify-center my-4"
              >
                <ArrowRight className="w-6 h-6 text-green-400" />
              </motion.div>
              
              <div className="text-sm space-y-1">
                <div>{metrics?.dataFlows.platformToSupport.messagesPerMinute || 0} msg/min</div>
                <div className="text-gray-400">
                  {formatLatency(metrics?.dataFlows.platformToSupport.avgLatency || 0)}
                </div>
              </div>
            </motion.div>

            {/* Support to Portal */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="text-center"
            >
              <div className="mb-4">
                <Shield className="w-12 h-12 mx-auto text-green-500 mb-2" />
                <div className="font-semibold">Support Portal</div>
              </div>
              
              <motion.div
                animate={{ y: [0, -10, 0], x: [-40, -40, -40], rotate: [0, 0, -90] }}
                transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                className="flex items-center justify-center my-4"
              >
                <ArrowRight className="w-6 h-6 text-green-400" />
              </motion.div>
              
              <div className="text-sm space-y-1">
                <div>{metrics?.dataFlows.supportToPortal.messagesPerMinute || 0} msg/min</div>
                <div className="text-gray-400">
                  {formatLatency(metrics?.dataFlows.supportToPortal.avgLatency || 0)}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Tier Distribution */}
      <div>
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-purple-400" />
          User Tier Distribution
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-2xl font-bold">Onyx</div>
              <div className="text-gray-400">Silver Stream Society</div>
            </div>
            <div className="text-4xl font-bold text-gray-300">
              {metrics?.tierDistribution.onyx || 0}
            </div>
            <div className="text-sm text-gray-500 mt-2">₹100+ Cr portfolio</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-700/50 rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-2xl font-bold text-purple-300">Obsidian</div>
              <div className="text-purple-400">Crystal Empire Network</div>
            </div>
            <div className="text-4xl font-bold text-purple-300">
              {metrics?.tierDistribution.obsidian || 0}
            </div>
            <div className="text-sm text-purple-400 mt-2">₹1,000+ Cr portfolio</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/20 border border-yellow-700/50 rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-2xl font-bold text-yellow-300">Void</div>
              <div className="text-yellow-400">Quantum Consciousness</div>
            </div>
            <div className="text-4xl font-bold text-yellow-300">
              {metrics?.tierDistribution.void || 0}
            </div>
            <div className="text-sm text-yellow-400 mt-2">₹8,000+ Cr portfolio</div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};