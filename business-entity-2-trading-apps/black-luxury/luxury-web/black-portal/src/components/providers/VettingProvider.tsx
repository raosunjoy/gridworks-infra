/**
 * Vetting System Provider
 * Context provider for the service vetting system with real-time updates
 */

import React, { createContext, useContext, useEffect, useRef } from 'react';
import { useVettingStore, vettingSelectors } from '@/stores/vettingStore';
import { User } from '@/types/service-management';

interface VettingProviderProps {
  children: React.ReactNode;
  initialUser?: User;
}

interface VettingContextType {
  // Store instance
  store: typeof useVettingStore;
  
  // Selectors
  selectors: typeof vettingSelectors;
  
  // Real-time functionality
  startRealTimeUpdates: () => void;
  stopRealTimeUpdates: () => void;
}

const VettingContext = createContext<VettingContextType | undefined>(undefined);

export const VettingProvider: React.FC<VettingProviderProps> = ({
  children,
  initialUser,
}) => {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  
  const {
    setCurrentUser,
    autoRefresh,
    refreshInterval,
    updateLastSync,
    fetchProposals,
    fetchWorkflows,
    fetchAuditLogs,
    fetchDashboardMetrics,
    addAuditLog,
    updateWorkflow,
    updateProposal,
  } = useVettingStore();

  // Initialize user on mount
  useEffect(() => {
    if (initialUser) {
      setCurrentUser(initialUser);
    }
  }, [initialUser, setCurrentUser]);

  // Real-time polling updates
  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      startRealTimeUpdates();
    } else {
      stopRealTimeUpdates();
    }

    return () => {
      stopRealTimeUpdates();
    };
  }, [autoRefresh, refreshInterval]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (initialUser) {
      connectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [initialUser]);

  const startRealTimeUpdates = () => {
    stopRealTimeUpdates(); // Clear existing interval
    
    intervalRef.current = setInterval(async () => {
      try {
        await Promise.all([
          fetchProposals(),
          fetchWorkflows(),
          fetchDashboardMetrics(),
        ]);
        updateLastSync();
      } catch (error) {
        console.error('Failed to refresh data:', error);
      }
    }, refreshInterval);
  };

  const stopRealTimeUpdates = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const connectWebSocket = () => {
    if (!initialUser) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:3001'}/ws/vetting`;
    wsRef.current = new WebSocket(`${wsUrl}?userId=${initialUser.id}&role=${initialUser.role}`);

    wsRef.current.onopen = () => {
      console.log('WebSocket connected for real-time vetting updates');
    };

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        if (initialUser) {
          connectWebSocket();
        }
      }, 5000);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'PROPOSAL_CREATED':
      case 'PROPOSAL_UPDATED':
        updateProposal(data.proposalId, data.proposal);
        break;
        
      case 'WORKFLOW_UPDATED':
        updateWorkflow(data.workflowId, data.workflow);
        break;
        
      case 'AUDIT_LOG_CREATED':
        addAuditLog(data.auditLog);
        break;
        
      case 'STAGE_ACTION_PROCESSED':
        // Refresh workflows to get latest stage information
        fetchWorkflows();
        break;
        
      case 'USER_ROLE_UPDATED':
        if (data.userId === initialUser?.id) {
          // Current user's role was updated, need to refresh permissions
          setCurrentUser({ ...initialUser, role: data.newRole });
        }
        break;
        
      case 'EMERGENCY_ALERT':
        // Handle emergency notifications
        showEmergencyNotification(data.alert);
        break;
        
      case 'SYSTEM_MAINTENANCE':
        // Handle system maintenance notifications
        showMaintenanceNotification(data.maintenance);
        break;
        
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const showEmergencyNotification = (alert: any) => {
    // Create a custom notification for emergency alerts
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('🚨 Emergency Alert', {
        body: alert.message,
        icon: '/icons/emergency.png',
        tag: 'emergency',
        requireInteraction: true,
      });
    }
    
    // Also show in-app notification
    console.warn('Emergency Alert:', alert);
  };

  const showMaintenanceNotification = (maintenance: any) => {
    // Show maintenance notification
    console.info('System Maintenance:', maintenance);
  };

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const contextValue: VettingContextType = {
    store: useVettingStore,
    selectors: vettingSelectors,
    startRealTimeUpdates,
    stopRealTimeUpdates,
  };

  return (
    <VettingContext.Provider value={contextValue}>
      {children}
    </VettingContext.Provider>
  );
};

export const useVettingContext = () => {
  const context = useContext(VettingContext);
  if (context === undefined) {
    throw new Error('useVettingContext must be used within a VettingProvider');
  }
  return context;
};

// Custom hooks for common operations
export const useVettingData = () => {
  const {
    proposals,
    filteredProposals,
    workflows,
    users,
    auditLogs,
    filteredAuditLogs,
    dashboardMetrics,
    loading,
    error,
  } = useVettingStore();

  return {
    proposals,
    filteredProposals,
    workflows,
    users,
    auditLogs,
    filteredAuditLogs,
    dashboardMetrics,
    loading,
    error,
  };
};

export const useVettingActions = () => {
  const {
    fetchProposals,
    fetchWorkflows,
    fetchUsers,
    fetchAuditLogs,
    fetchDashboardMetrics,
    setSelectedProposal,
    setSelectedWorkflow,
    setSelectedUser,
    setSelectedAuditLog,
    setProposalFilter,
    setAuditFilter,
    processStageAction,
    updateUserRole,
    toggleUserStatus,
    exportAuditLogs,
    openModal,
    closeModal,
    refreshDashboard,
  } = useVettingStore();

  return {
    fetchProposals,
    fetchWorkflows,
    fetchUsers,
    fetchAuditLogs,
    fetchDashboardMetrics,
    setSelectedProposal,
    setSelectedWorkflow,
    setSelectedUser,
    setSelectedAuditLog,
    setProposalFilter,
    setAuditFilter,
    processStageAction,
    updateUserRole,
    toggleUserStatus,
    exportAuditLogs,
    openModal,
    closeModal,
    refreshDashboard,
  };
};

export const useVettingFilters = () => {
  const {
    proposalFilter,
    auditFilter,
    setProposalFilter,
    setAuditFilter,
    applyProposalFilters,
    applyAuditFilters,
  } = useVettingStore();

  return {
    proposalFilter,
    auditFilter,
    setProposalFilter,
    setAuditFilter,
    applyProposalFilters,
    applyAuditFilters,
  };
};

export const useVettingPermissions = () => {
  const {
    currentUser,
    hasPermission,
    canUserAccessProposal,
    canUserActOnStage,
  } = useVettingStore();

  return {
    currentUser,
    hasPermission,
    canUserAccessProposal,
    canUserActOnStage,
  };
};

export const useVettingSelectors = () => {
  const store = useVettingStore();
  
  return {
    proposalsByStatus: (status: any) => vettingSelectors.getProposalsByStatus(status)(store),
    proposalsByCategory: (category: any) => vettingSelectors.getProposalsByCategory(category)(store),
    proposalsByRisk: (riskLevel: any) => vettingSelectors.getProposalsByRisk(riskLevel)(store),
    activeWorkflows: vettingSelectors.getActiveWorkflows(store),
    overdueWorkflows: vettingSelectors.getOverdueWorkflows(store),
    usersByRole: (role: any) => vettingSelectors.getUsersByRole(role)(store),
    activeUsers: vettingSelectors.getActiveUsers(store),
    sensitiveAuditLogs: vettingSelectors.getSensitiveAuditLogs(store),
    failedAuditLogs: vettingSelectors.getFailedAuditLogs(store),
    totalProposalsInReview: vettingSelectors.getTotalProposalsInReview(store),
    pendingApprovals: vettingSelectors.getPendingApprovals(store),
  };
};