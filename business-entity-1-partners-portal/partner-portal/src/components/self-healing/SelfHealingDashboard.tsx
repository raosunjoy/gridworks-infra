'use client';

import React, { useEffect } from 'react';
import { useSelfHealingStore } from '@/store/self-healing';
import { HealthStatus } from '@/types';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp, 
  Clock,
  Zap,
  Shield,
  RefreshCw
} from 'lucide-react';

interface StatusCardProps {
  title: string;
  status: HealthStatus;
  color: string;
  icon?: React.ReactNode;
}

const StatusCard: React.FC<StatusCardProps> = ({ title, status, color, icon }) => {
  const getStatusIcon = () => {
    switch (status) {
      case HealthStatus.HEALTHY:
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case HealthStatus.DEGRADED:
        return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
      case HealthStatus.CRITICAL:
        return <AlertTriangle className="w-6 h-6 text-red-500" />;
      default:
        return <Activity className="w-6 h-6 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case HealthStatus.HEALTHY:
        return 'border-green-200 bg-green-50';
      case HealthStatus.DEGRADED:
        return 'border-yellow-200 bg-yellow-50';
      case HealthStatus.CRITICAL:
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className={`p-6 rounded-lg border-2 ${getStatusColor()} transition-all duration-200`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 capitalize mt-1">{status}</p>
        </div>
        <div className="flex-shrink-0">
          {icon || getStatusIcon()}
        </div>
      </div>
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: 'up' | 'down' | 'stable';
  period?: string;
  icon?: React.ReactNode;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, trend, period, icon }) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />;
      default:
        return null;
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h4 className="text-sm font-medium text-gray-500">{title}</h4>
          <div className="flex items-center mt-2">
            <span className="text-2xl font-bold text-gray-900">{value}</span>
            {getTrendIcon()}
          </div>
          {period && (
            <p className="text-xs text-gray-400 mt-1">{period}</p>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0 ml-4">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};

interface ServiceHealthCardProps {
  service: any;
  onManualIntervention: (serviceName: string) => void;
}

const ServiceHealthCard: React.FC<ServiceHealthCardProps> = ({ service, onManualIntervention }) => {
  const getHealthColor = () => {
    switch (service.status) {
      case HealthStatus.HEALTHY:
        return 'text-green-600 bg-green-100';
      case HealthStatus.DEGRADED:
        return 'text-yellow-600 bg-yellow-100';
      case HealthStatus.CRITICAL:
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h5 className="font-medium text-gray-900 capitalize">{service.name}</h5>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getHealthColor()}`}>
          {service.status}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Response Time:</span>
          <span className="ml-2 font-medium">{service.responseTime}ms</span>
        </div>
        <div>
          <span className="text-gray-500">Error Rate:</span>
          <span className="ml-2 font-medium">{(service.errorRate * 100).toFixed(2)}%</span>
        </div>
        <div>
          <span className="text-gray-500">Uptime:</span>
          <span className="ml-2 font-medium">{(service.uptime * 100).toFixed(2)}%</span>
        </div>
        <div>
          <span className="text-gray-500">Last Check:</span>
          <span className="ml-2 font-medium">
            {new Date(service.lastCheck).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {service.status !== HealthStatus.HEALTHY && (
        <button
          onClick={() => onManualIntervention(service.name)}
          className="mt-3 w-full px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
        >
          Trigger Manual Recovery
        </button>
      )}
    </div>
  );
};

interface HealingTimelineProps {
  incidents: any[];
}

const HealingTimeline: React.FC<HealingTimelineProps> = ({ incidents }) => {
  const getIncidentIcon = (type: string) => {
    switch (type) {
      case 'auto_recovery':
        return <RefreshCw className="w-4 h-4 text-blue-500" />;
      case 'preventive_action':
        return <Shield className="w-4 h-4 text-green-500" />;
      case 'manual_intervention':
        return <Zap className="w-4 h-4 text-orange-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved':
        return 'text-green-600';
      case 'in_progress':
        return 'text-blue-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-4">
      {incidents.slice(0, 10).map((incident, index) => (
        <div key={incident.id} className="flex items-start space-x-3">
          <div className="flex-shrink-0 mt-1">
            {getIncidentIcon(incident.type)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900">
                {incident.service} - {incident.description}
              </p>
              <span className={`text-xs font-medium ${getStatusColor(incident.status)}`}>
                {incident.status}
              </span>
            </div>
            <div className="flex items-center space-x-4 mt-1">
              <span className="text-xs text-gray-500">
                {new Date(incident.timestamp).toLocaleString()}
              </span>
              {incident.duration && (
                <span className="text-xs text-gray-500">
                  Duration: {incident.duration}ms
                </span>
              )}
            </div>
            {incident.actions && incident.actions.length > 0 && (
              <div className="mt-2">
                <p className="text-xs text-gray-600">Actions taken:</p>
                <ul className="text-xs text-gray-500 list-disc list-inside">
                  {incident.actions.map((action: string, actionIndex: number) => (
                    <li key={actionIndex}>{action}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

interface PredictiveInsightsProps {
  predictions: any[];
}

const PredictiveInsights: React.FC<PredictiveInsightsProps> = ({ predictions }) => {
  const getInsightColor = (type: string) => {
    switch (type) {
      case 'critical':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'info':
        return 'border-blue-200 bg-blue-50 text-blue-800';
      default:
        return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  return (
    <div className="space-y-3">
      {predictions.map((prediction, index) => (
        <div key={index} className={`p-4 rounded-lg border ${getInsightColor(prediction.type)}`}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium">{prediction.message}</p>
              <div className="flex items-center space-x-4 mt-2">
                <span className="text-xs">
                  Probability: {(prediction.probability * 100).toFixed(1)}%
                </span>
                <span className="text-xs">
                  Timeframe: {prediction.timeframe}
                </span>
              </div>
              {prediction.suggestedAction && (
                <p className="text-xs mt-2">
                  <strong>Suggested Action:</strong> {prediction.suggestedAction}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
      {predictions.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No predictive insights available at the moment.</p>
        </div>
      )}
    </div>
  );
};

const SelfHealingDashboard: React.FC = () => {
  const store = useSelfHealingStore();
  const { 
    healingStatus, 
    metrics, 
    startHealthMonitoring, 
    stopHealthMonitoring,
    triggerManualRecovery 
  } = store;
  const incidents = (store as any).incidents || [];

  useEffect(() => {
    // Start monitoring when component mounts
    startHealthMonitoring();
    
    // Cleanup on unmount
    return () => {
      stopHealthMonitoring();
    };
  }, [startHealthMonitoring, stopHealthMonitoring]);

  const handleManualIntervention = async (serviceName: string) => {
    try {
      await triggerManualRecovery(serviceName);
    } catch (error) {
      console.error('Manual recovery failed:', error);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Self-Healing Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Real-time system health monitoring and autonomous recovery
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Clock className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-500">
            Last updated: {healingStatus.lastUpdate.toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatusCard
          title="System Health"
          status={healingStatus.overall}
          color={healingStatus.overall === HealthStatus.HEALTHY ? 'green' : 'red'}
          icon={<Activity className="w-6 h-6" />}
        />
        <MetricCard
          title="Auto-Recovery Rate"
          value={`${metrics.autoRecoveryRate}%`}
          trend={metrics.recoveryTrend}
          icon={<RefreshCw className="w-6 h-6 text-blue-500" />}
        />
        <MetricCard
          title="Incidents Prevented"
          value={metrics.incidentsPrevented}
          period="Last 24h"
          icon={<Shield className="w-6 h-6 text-green-500" />}
        />
        <MetricCard
          title="Active Services"
          value={healingStatus.services.length}
          icon={<Zap className="w-6 h-6 text-purple-500" />}
        />
      </div>

      {/* Service Health Grid */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Service Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {healingStatus.services.map((service) => (
            <ServiceHealthCard
              key={service.name}
              service={service}
              onManualIntervention={handleManualIntervention}
            />
          ))}
        </div>
      </div>

      {/* Healing Timeline and Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Healing Activities
          </h3>
          <HealingTimeline incidents={incidents} />
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Predictive Insights
          </h3>
          <PredictiveInsights predictions={metrics.predictions} />
        </div>
      </div>
    </div>
  );
};

export default SelfHealingDashboard;