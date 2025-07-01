/**
 * Service Vetting State Management Store
 * Comprehensive Zustand store for managing vetting system state
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  ServiceProposal,
  User,
  AuditLog,
  DashboardMetrics,
  ApprovalStatus,
  ServiceCategory,
  RiskLevel,
  UserRole,
} from '@/types/service-management';

interface WorkflowInstance {
  proposalId: string;
  proposal: ServiceProposal;
  stages: Array<{
    id: string;
    name: string;
    status: 'pending' | 'in_progress' | 'completed' | 'rejected' | 'escalated';
    assignee?: User;
    requiredRole: UserRole;
    startedAt?: string;
    completedAt?: string;
    timeoutHours: number;
    comments?: string;
    escalationLevel: number;
  }>;
  currentStage: number;
  overallStatus: ApprovalStatus;
  createdAt: string;
  estimatedCompletion: string;
  actualCompletion?: string;
  escalations: number;
  bottlenecks: string[];
}

interface VettingFilter {
  category?: ServiceCategory | 'all';
  status?: ApprovalStatus | 'all';
  riskLevel?: RiskLevel | 'all';
  submittedBy?: string;
  dateFrom?: string;
  dateTo?: string;
  searchTerm?: string;
}

interface AuditFilter {
  userId?: string;
  action?: string;
  resource?: string;
  outcome?: 'success' | 'failure' | 'warning' | 'all';
  sensitiveData?: boolean | 'all';
  dateFrom?: string;
  dateTo?: string;
  searchTerm?: string;
}

interface VettingState {
  // User and Authentication
  currentUser: User | null;
  isAuthenticated: boolean;
  userPermissions: string[];

  // Service Proposals
  proposals: ServiceProposal[];
  filteredProposals: ServiceProposal[];
  selectedProposal: ServiceProposal | null;
  proposalFilter: VettingFilter;
  
  // Workflows
  workflows: WorkflowInstance[];
  selectedWorkflow: WorkflowInstance | null;
  
  // Users and RBAC
  users: User[];
  selectedUser: User | null;
  
  // Audit Logs
  auditLogs: AuditLog[];
  filteredAuditLogs: AuditLog[];
  selectedAuditLog: AuditLog | null;
  auditFilter: AuditFilter;
  
  // Dashboard Metrics
  dashboardMetrics: DashboardMetrics | null;
  
  // UI State
  loading: {
    proposals: boolean;
    workflows: boolean;
    users: boolean;
    auditLogs: boolean;
    dashboard: boolean;
    global: boolean;
  };
  
  error: {
    proposals: string | null;
    workflows: string | null;
    users: string | null;
    auditLogs: string | null;
    dashboard: string | null;
    global: string | null;
  };
  
  // Modal and UI Controls
  modals: {
    createProposal: boolean;
    editProposal: boolean;
    editUser: boolean;
    confirmDelete: boolean;
    exportAuditLogs: boolean;
  };
  
  // Real-time Updates
  lastSync: string | null;
  autoRefresh: boolean;
  refreshInterval: number;
}

interface VettingActions {
  // Authentication Actions
  setCurrentUser: (user: User | null) => void;
  setAuthenticated: (authenticated: boolean) => void;
  updateUserPermissions: (permissions: string[]) => void;
  
  // Proposal Actions
  setProposals: (proposals: ServiceProposal[]) => void;
  addProposal: (proposal: ServiceProposal) => void;
  updateProposal: (id: string, updates: Partial<ServiceProposal>) => void;
  deleteProposal: (id: string) => void;
  setSelectedProposal: (proposal: ServiceProposal | null) => void;
  setProposalFilter: (filter: Partial<VettingFilter>) => void;
  applyProposalFilters: () => void;
  
  // Workflow Actions
  setWorkflows: (workflows: WorkflowInstance[]) => void;
  updateWorkflow: (id: string, updates: Partial<WorkflowInstance>) => void;
  setSelectedWorkflow: (workflow: WorkflowInstance | null) => void;
  processStageAction: (workflowId: string, stageId: string, action: string, comments?: string) => Promise<void>;
  
  // User Management Actions
  setUsers: (users: User[]) => void;
  addUser: (user: User) => void;
  updateUser: (id: string, updates: Partial<User>) => void;
  deleteUser: (id: string) => void;
  setSelectedUser: (user: User | null) => void;
  updateUserRole: (userId: string, role: UserRole) => Promise<void>;
  toggleUserStatus: (userId: string, isActive: boolean) => Promise<void>;
  
  // Audit Log Actions
  setAuditLogs: (logs: AuditLog[]) => void;
  addAuditLog: (log: AuditLog) => void;
  setSelectedAuditLog: (log: AuditLog | null) => void;
  setAuditFilter: (filter: Partial<AuditFilter>) => void;
  applyAuditFilters: () => void;
  exportAuditLogs: () => Promise<void>;
  
  // Dashboard Actions
  setDashboardMetrics: (metrics: DashboardMetrics) => void;
  refreshDashboard: () => Promise<void>;
  
  // Loading and Error Actions
  setLoading: (key: keyof VettingState['loading'], loading: boolean) => void;
  setError: (key: keyof VettingState['error'], error: string | null) => void;
  clearError: (key: keyof VettingState['error']) => void;
  clearAllErrors: () => void;
  
  // Modal Actions
  openModal: (modal: keyof VettingState['modals']) => void;
  closeModal: (modal: keyof VettingState['modals']) => void;
  closeAllModals: () => void;
  
  // Data Fetching Actions
  fetchProposals: () => Promise<void>;
  fetchWorkflows: () => Promise<void>;
  fetchUsers: () => Promise<void>;
  fetchAuditLogs: () => Promise<void>;
  fetchDashboardMetrics: () => Promise<void>;
  
  // Real-time Actions
  setAutoRefresh: (enabled: boolean) => void;
  setRefreshInterval: (interval: number) => void;
  updateLastSync: () => void;
  
  // Utility Actions
  reset: () => void;
  hasPermission: (permission: string) => boolean;
  canUserAccessProposal: (proposal: ServiceProposal) => boolean;
  canUserActOnStage: (stage: WorkflowInstance['stages'][0]) => boolean;
}

type VettingStore = VettingState & VettingActions;

const initialState: VettingState = {
  // User and Authentication
  currentUser: null,
  isAuthenticated: false,
  userPermissions: [],
  
  // Service Proposals
  proposals: [],
  filteredProposals: [],
  selectedProposal: null,
  proposalFilter: {
    category: 'all',
    status: 'all',
    riskLevel: 'all',
  },
  
  // Workflows
  workflows: [],
  selectedWorkflow: null,
  
  // Users and RBAC
  users: [],
  selectedUser: null,
  
  // Audit Logs
  auditLogs: [],
  filteredAuditLogs: [],
  selectedAuditLog: null,
  auditFilter: {
    outcome: 'all',
    sensitiveData: 'all',
    dateFrom: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    dateTo: new Date().toISOString().split('T')[0],
  },
  
  // Dashboard Metrics
  dashboardMetrics: null,
  
  // UI State
  loading: {
    proposals: false,
    workflows: false,
    users: false,
    auditLogs: false,
    dashboard: false,
    global: false,
  },
  
  error: {
    proposals: null,
    workflows: null,
    users: null,
    auditLogs: null,
    dashboard: null,
    global: null,
  },
  
  // Modal and UI Controls
  modals: {
    createProposal: false,
    editProposal: false,
    editUser: false,
    confirmDelete: false,
    exportAuditLogs: false,
  },
  
  // Real-time Updates
  lastSync: null,
  autoRefresh: false,
  refreshInterval: 30000, // 30 seconds
};

export const useVettingStore = create<VettingStore>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,
        
        // Authentication Actions
        setCurrentUser: (user) => set((state) => {
          state.currentUser = user;
          state.isAuthenticated = !!user;
          state.userPermissions = user?.permissions || [];
        }),
        
        setAuthenticated: (authenticated) => set((state) => {
          state.isAuthenticated = authenticated;
        }),
        
        updateUserPermissions: (permissions) => set((state) => {
          state.userPermissions = permissions;
        }),
        
        // Proposal Actions
        setProposals: (proposals) => set((state) => {
          state.proposals = proposals;
          get().applyProposalFilters();
        }),
        
        addProposal: (proposal) => set((state) => {
          state.proposals.push(proposal);
          get().applyProposalFilters();
        }),
        
        updateProposal: (id, updates) => set((state) => {
          const index = state.proposals.findIndex(p => p.id === id);
          if (index !== -1) {
            state.proposals[index] = { ...state.proposals[index], ...updates };
            get().applyProposalFilters();
          }
        }),
        
        deleteProposal: (id) => set((state) => {
          state.proposals = state.proposals.filter(p => p.id !== id);
          if (state.selectedProposal?.id === id) {
            state.selectedProposal = null;
          }
          get().applyProposalFilters();
        }),
        
        setSelectedProposal: (proposal) => set((state) => {
          state.selectedProposal = proposal;
        }),
        
        setProposalFilter: (filter) => set((state) => {
          state.proposalFilter = { ...state.proposalFilter, ...filter };
          get().applyProposalFilters();
        }),
        
        applyProposalFilters: () => set((state) => {
          const { proposalFilter, proposals, currentUser } = state;
          let filtered = [...proposals];
          
          // Apply category filter
          if (proposalFilter.category && proposalFilter.category !== 'all') {
            filtered = filtered.filter(p => p.category === proposalFilter.category);
          }
          
          // Apply status filter
          if (proposalFilter.status && proposalFilter.status !== 'all') {
            filtered = filtered.filter(p => p.status === proposalFilter.status);
          }
          
          // Apply risk level filter
          if (proposalFilter.riskLevel && proposalFilter.riskLevel !== 'all') {
            filtered = filtered.filter(p => p.riskLevel === proposalFilter.riskLevel);
          }
          
          // Apply search filter
          if (proposalFilter.searchTerm) {
            const searchLower = proposalFilter.searchTerm.toLowerCase();
            filtered = filtered.filter(p => 
              p.title.toLowerCase().includes(searchLower) ||
              p.description.toLowerCase().includes(searchLower) ||
              p.provider.name.toLowerCase().includes(searchLower) ||
              p.proposalNumber.toLowerCase().includes(searchLower)
            );
          }
          
          // Apply date filters
          if (proposalFilter.dateFrom) {
            const fromDate = new Date(proposalFilter.dateFrom);
            filtered = filtered.filter(p => new Date(p.submittedAt) >= fromDate);
          }
          
          if (proposalFilter.dateTo) {
            const toDate = new Date(proposalFilter.dateTo);
            toDate.setHours(23, 59, 59, 999);
            filtered = filtered.filter(p => new Date(p.submittedAt) <= toDate);
          }
          
          // Apply permission-based filtering
          if (currentUser) {
            filtered = filtered.filter(p => get().canUserAccessProposal(p));
          }
          
          state.filteredProposals = filtered;
        }),
        
        // Workflow Actions
        setWorkflows: (workflows) => set((state) => {
          state.workflows = workflows;
        }),
        
        updateWorkflow: (id, updates) => set((state) => {
          const index = state.workflows.findIndex(w => w.proposalId === id);
          if (index !== -1) {
            state.workflows[index] = { ...state.workflows[index], ...updates };
          }
        }),
        
        setSelectedWorkflow: (workflow) => set((state) => {
          state.selectedWorkflow = workflow;
        }),
        
        processStageAction: async (workflowId, stageId, action, comments) => {
          const { currentUser } = get();
          if (!currentUser) return;
          
          set((state) => {
            state.loading.workflows = true;
          });
          
          try {
            const response = await fetch(`/api/admin/workflows/${workflowId}/stages/${stageId}/action`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ action, comments, userId: currentUser.id }),
            });
            
            if (response.ok) {
              await get().fetchWorkflows();
            } else {
              throw new Error('Failed to process stage action');
            }
          } catch (error) {
            set((state) => {
              state.error.workflows = error instanceof Error ? error.message : 'Unknown error';
            });
          } finally {
            set((state) => {
              state.loading.workflows = false;
            });
          }
        },
        
        // User Management Actions
        setUsers: (users) => set((state) => {
          state.users = users;
        }),
        
        addUser: (user) => set((state) => {
          state.users.push(user);
        }),
        
        updateUser: (id, updates) => set((state) => {
          const index = state.users.findIndex(u => u.id === id);
          if (index !== -1) {
            state.users[index] = { ...state.users[index], ...updates };
          }
        }),
        
        deleteUser: (id) => set((state) => {
          state.users = state.users.filter(u => u.id !== id);
          if (state.selectedUser?.id === id) {
            state.selectedUser = null;
          }
        }),
        
        setSelectedUser: (user) => set((state) => {
          state.selectedUser = user;
        }),
        
        updateUserRole: async (userId, role) => {
          const { currentUser } = get();
          if (!currentUser) return;
          
          try {
            const response = await fetch(`/api/admin/rbac/users/${userId}/role`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ role, changedBy: currentUser.id }),
            });
            
            if (response.ok) {
              await get().fetchUsers();
            } else {
              throw new Error('Failed to update user role');
            }
          } catch (error) {
            set((state) => {
              state.error.users = error instanceof Error ? error.message : 'Unknown error';
            });
          }
        },
        
        toggleUserStatus: async (userId, isActive) => {
          const { currentUser } = get();
          if (!currentUser) return;
          
          try {
            const response = await fetch(`/api/admin/rbac/users/${userId}/toggle`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ isActive, changedBy: currentUser.id }),
            });
            
            if (response.ok) {
              await get().fetchUsers();
            } else {
              throw new Error('Failed to toggle user status');
            }
          } catch (error) {
            set((state) => {
              state.error.users = error instanceof Error ? error.message : 'Unknown error';
            });
          }
        },
        
        // Audit Log Actions
        setAuditLogs: (logs) => set((state) => {
          state.auditLogs = logs;
          get().applyAuditFilters();
        }),
        
        addAuditLog: (log) => set((state) => {
          state.auditLogs.unshift(log); // Add to beginning for chronological order
          get().applyAuditFilters();
        }),
        
        setSelectedAuditLog: (log) => set((state) => {
          state.selectedAuditLog = log;
        }),
        
        setAuditFilter: (filter) => set((state) => {
          state.auditFilter = { ...state.auditFilter, ...filter };
          get().applyAuditFilters();
        }),
        
        applyAuditFilters: () => set((state) => {
          const { auditFilter, auditLogs } = state;
          let filtered = [...auditLogs];
          
          // Apply outcome filter
          if (auditFilter.outcome && auditFilter.outcome !== 'all') {
            filtered = filtered.filter(log => log.outcome === auditFilter.outcome);
          }
          
          // Apply sensitive data filter
          if (auditFilter.sensitiveData !== 'all') {
            filtered = filtered.filter(log => log.sensitiveData === auditFilter.sensitiveData);
          }
          
          // Apply date filters
          if (auditFilter.dateFrom) {
            const fromDate = new Date(auditFilter.dateFrom);
            filtered = filtered.filter(log => new Date(log.timestamp) >= fromDate);
          }
          
          if (auditFilter.dateTo) {
            const toDate = new Date(auditFilter.dateTo);
            toDate.setHours(23, 59, 59, 999);
            filtered = filtered.filter(log => new Date(log.timestamp) <= toDate);
          }
          
          // Apply search filter
          if (auditFilter.searchTerm) {
            const searchLower = auditFilter.searchTerm.toLowerCase();
            filtered = filtered.filter(log => 
              log.action.toLowerCase().includes(searchLower) ||
              log.resource.toLowerCase().includes(searchLower) ||
              log.resourceId.toLowerCase().includes(searchLower) ||
              JSON.stringify(log.changes).toLowerCase().includes(searchLower)
            );
          }
          
          // Apply action filter
          if (auditFilter.action) {
            filtered = filtered.filter(log => 
              log.action.toLowerCase().includes(auditFilter.action!.toLowerCase())
            );
          }
          
          // Apply resource filter
          if (auditFilter.resource) {
            filtered = filtered.filter(log => 
              log.resource.toLowerCase().includes(auditFilter.resource!.toLowerCase())
            );
          }
          
          // Apply user filter
          if (auditFilter.userId) {
            filtered = filtered.filter(log => log.userId === auditFilter.userId);
          }
          
          state.filteredAuditLogs = filtered;
        }),
        
        exportAuditLogs: async () => {
          const { filteredAuditLogs, auditFilter, currentUser } = get();
          if (!currentUser) return;
          
          set((state) => {
            state.loading.auditLogs = true;
          });
          
          try {
            const exportData = {
              logs: filteredAuditLogs,
              filter: auditFilter,
              exportedBy: currentUser.id,
              exportedAt: new Date().toISOString(),
              totalRecords: filteredAuditLogs.length,
            };
            
            const response = await fetch('/api/admin/audit-logs/export', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.id}`,
              },
              body: JSON.stringify(exportData),
            });
            
            if (response.ok) {
              const blob = await response.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.style.display = 'none';
              a.href = url;
              a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.xlsx`;
              document.body.appendChild(a);
              a.click();
              window.URL.revokeObjectURL(url);
            } else {
              throw new Error('Failed to export audit logs');
            }
          } catch (error) {
            set((state) => {
              state.error.auditLogs = error instanceof Error ? error.message : 'Unknown error';
            });
          } finally {
            set((state) => {
              state.loading.auditLogs = false;
            });
          }
        },
        
        // Dashboard Actions
        setDashboardMetrics: (metrics) => set((state) => {
          state.dashboardMetrics = metrics;
        }),
        
        refreshDashboard: async () => {
          await Promise.all([
            get().fetchDashboardMetrics(),
            get().fetchProposals(),
            get().fetchWorkflows(),
          ]);
        },
        
        // Loading and Error Actions
        setLoading: (key, loading) => set((state) => {
          state.loading[key] = loading;
        }),
        
        setError: (key, error) => set((state) => {
          state.error[key] = error;
        }),
        
        clearError: (key) => set((state) => {
          state.error[key] = null;
        }),
        
        clearAllErrors: () => set((state) => {
          Object.keys(state.error).forEach(key => {
            state.error[key as keyof typeof state.error] = null;
          });
        }),
        
        // Modal Actions
        openModal: (modal) => set((state) => {
          state.modals[modal] = true;
        }),
        
        closeModal: (modal) => set((state) => {
          state.modals[modal] = false;
        }),
        
        closeAllModals: () => set((state) => {
          Object.keys(state.modals).forEach(key => {
            state.modals[key as keyof typeof state.modals] = false;
          });
        }),
        
        // Data Fetching Actions
        fetchProposals: async () => {
          const { currentUser } = get();
          if (!currentUser) return;
          
          set((state) => {
            state.loading.proposals = true;
            state.error.proposals = null;
          });
          
          try {
            const response = await fetch(`/api/admin/vetting/proposals?role=${currentUser.role}`);
            if (!response.ok) throw new Error('Failed to fetch proposals');
            
            const data = await response.json();
            get().setProposals(data);
          } catch (error) {
            set((state) => {
              state.error.proposals = error instanceof Error ? error.message : 'Unknown error';
            });
          } finally {
            set((state) => {
              state.loading.proposals = false;
            });
          }
        },
        
        fetchWorkflows: async () => {
          const { currentUser } = get();
          if (!currentUser) return;
          
          set((state) => {
            state.loading.workflows = true;
            state.error.workflows = null;
          });
          
          try {
            const response = await fetch(`/api/admin/workflows?userId=${currentUser.id}`);
            if (!response.ok) throw new Error('Failed to fetch workflows');
            
            const data = await response.json();
            get().setWorkflows(data);
          } catch (error) {
            set((state) => {
              state.error.workflows = error instanceof Error ? error.message : 'Unknown error';
            });
          } finally {
            set((state) => {
              state.loading.workflows = false;
            });
          }
        },
        
        fetchUsers: async () => {
          set((state) => {
            state.loading.users = true;
            state.error.users = null;
          });
          
          try {
            const response = await fetch('/api/admin/rbac/users');
            if (!response.ok) throw new Error('Failed to fetch users');
            
            const data = await response.json();
            get().setUsers(data);
          } catch (error) {
            set((state) => {
              state.error.users = error instanceof Error ? error.message : 'Unknown error';
            });
          } finally {
            set((state) => {
              state.loading.users = false;
            });
          }
        },
        
        fetchAuditLogs: async () => {
          const { currentUser } = get();
          if (!currentUser) return;
          
          set((state) => {
            state.loading.auditLogs = true;
            state.error.auditLogs = null;
          });
          
          try {
            const response = await fetch('/api/admin/audit-logs', {
              headers: {
                'Authorization': `Bearer ${currentUser.id}`,
              },
            });
            if (!response.ok) throw new Error('Failed to fetch audit logs');
            
            const data = await response.json();
            get().setAuditLogs(data);
          } catch (error) {
            set((state) => {
              state.error.auditLogs = error instanceof Error ? error.message : 'Unknown error';
            });
          } finally {
            set((state) => {
              state.loading.auditLogs = false;
            });
          }
        },
        
        fetchDashboardMetrics: async () => {
          set((state) => {
            state.loading.dashboard = true;
            state.error.dashboard = null;
          });
          
          try {
            const response = await fetch('/api/admin/vetting/metrics');
            if (!response.ok) throw new Error('Failed to fetch dashboard metrics');
            
            const data = await response.json();
            get().setDashboardMetrics(data);
          } catch (error) {
            set((state) => {
              state.error.dashboard = error instanceof Error ? error.message : 'Unknown error';
            });
          } finally {
            set((state) => {
              state.loading.dashboard = false;
            });
          }
        },
        
        // Real-time Actions
        setAutoRefresh: (enabled) => set((state) => {
          state.autoRefresh = enabled;
        }),
        
        setRefreshInterval: (interval) => set((state) => {
          state.refreshInterval = interval;
        }),
        
        updateLastSync: () => set((state) => {
          state.lastSync = new Date().toISOString();
        }),
        
        // Utility Actions
        reset: () => set(() => ({ ...initialState })),
        
        hasPermission: (permission) => {
          const { userPermissions } = get();
          return userPermissions.includes(permission);
        },
        
        canUserAccessProposal: (proposal) => {
          const { currentUser } = get();
          if (!currentUser) return false;
          
          // CEO can see everything
          if (currentUser.role === UserRole.CEO) return true;
          
          // Role-based visibility rules
          switch (proposal.category) {
            case ServiceCategory.PRE_IPO_FUNDS:
            case ServiceCategory.HEDGE_FUNDS:
            case ServiceCategory.PRIVATE_EQUITY:
              return [UserRole.CRO, UserRole.INVESTMENT_HEAD, UserRole.SENIOR_INVESTMENT_ANALYST].includes(currentUser.role);
            
            case ServiceCategory.MEDICAL_EVACUATION:
            case ServiceCategory.SECURITY_SERVICES:
              return [UserRole.CRO, UserRole.SECURITY_HEAD, UserRole.SENIOR_SECURITY_ANALYST].includes(currentUser.role);
            
            case ServiceCategory.LEGAL_SERVICES:
              return [UserRole.CCO, UserRole.CRO, UserRole.SENIOR_COMPLIANCE_ANALYST].includes(currentUser.role);
            
            default:
              return [UserRole.CRO, UserRole.CCO].includes(currentUser.role);
          }
        },
        
        canUserActOnStage: (stage) => {
          const { currentUser } = get();
          if (!currentUser) return false;
          return stage.requiredRole === currentUser.role || currentUser.role === UserRole.CEO;
        },
      })),
      {
        name: 'vetting-store',
        partialize: (state) => ({
          currentUser: state.currentUser,
          isAuthenticated: state.isAuthenticated,
          userPermissions: state.userPermissions,
          proposalFilter: state.proposalFilter,
          auditFilter: state.auditFilter,
          autoRefresh: state.autoRefresh,
          refreshInterval: state.refreshInterval,
        }),
      }
    ),
    {
      name: 'vetting-store',
    }
  )
);

// Selectors for computed values
export const vettingSelectors = {
  // Proposal Selectors
  getProposalsByStatus: (status: ApprovalStatus) => (state: VettingStore) =>
    state.proposals.filter(p => p.status === status),
  
  getProposalsByCategory: (category: ServiceCategory) => (state: VettingStore) =>
    state.proposals.filter(p => p.category === category),
  
  getProposalsByRisk: (riskLevel: RiskLevel) => (state: VettingStore) =>
    state.proposals.filter(p => p.riskLevel === riskLevel),
  
  // Workflow Selectors
  getActiveWorkflows: (state: VettingStore) =>
    state.workflows.filter(w => 
      ![ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED].includes(w.overallStatus)
    ),
  
  getOverdueWorkflows: (state: VettingStore) =>
    state.workflows.filter(w => {
      const currentStage = w.stages[w.currentStage];
      if (!currentStage?.startedAt) return false;
      
      const startTime = new Date(currentStage.startedAt);
      const timeoutTime = new Date(startTime.getTime() + currentStage.timeoutHours * 60 * 60 * 1000);
      return new Date() > timeoutTime;
    }),
  
  // User Selectors
  getUsersByRole: (role: UserRole) => (state: VettingStore) =>
    state.users.filter(u => u.role === role),
  
  getActiveUsers: (state: VettingStore) =>
    state.users.filter(u => u.isActive),
  
  // Audit Selectors
  getSensitiveAuditLogs: (state: VettingStore) =>
    state.auditLogs.filter(log => log.sensitiveData),
  
  getFailedAuditLogs: (state: VettingStore) =>
    state.auditLogs.filter(log => log.outcome === 'failure'),
  
  // Dashboard Selectors
  getTotalProposalsInReview: (state: VettingStore) =>
    state.proposals.filter(p => 
      [ApprovalStatus.UNDER_REVIEW, ApprovalStatus.SECURITY_REVIEW, ApprovalStatus.COMPLIANCE_REVIEW].includes(p.status)
    ).length,
  
  getPendingApprovals: (state: VettingStore) =>
    state.proposals.filter(p => p.status === ApprovalStatus.PENDING_APPROVAL).length,
};