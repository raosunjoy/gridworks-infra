/**
 * Comprehensive Test Suite for Service Vetting System
 * Tests all components, state management, and workflows
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { useVettingStore } from '@/stores/vettingStore';
import { VettingProvider } from '@/components/providers/VettingProvider';
import { VettingDashboard } from '@/components/admin/VettingDashboard';
import { ServiceProposalForm } from '@/components/admin/ServiceProposalForm';
import { ApprovalWorkflowDashboard } from '@/components/admin/ApprovalWorkflowDashboard';
import { RBACManager } from '@/components/admin/RBACManager';
import { AuditLogViewer } from '@/components/admin/AuditLogViewer';
import {
  ServiceProposal,
  User,
  UserRole,
  ApprovalStatus,
  ServiceCategory,
  RiskLevel,
} from '@/types/service-management';

// Mock fetch globally
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Mock WebSocket
global.WebSocket = jest.fn(() => ({
  close: jest.fn(),
  send: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  onopen: null,
  onclose: null,
  onmessage: null,
  onerror: null,
})) as any;

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    form: ({ children, ...props }: any) => <form {...props}>{children}</form>,
    table: ({ children, ...props }: any) => <table {...props}>{children}</table>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Test data
const mockUser: User = {
  id: 'user-1',
  email: 'ceo@gridworks.ai',
  name: 'John CEO',
  role: UserRole.CEO,
  permissions: [],
  department: 'Executive',
  mfaEnabled: true,
  lastLogin: '2025-06-29T10:00:00Z',
  isActive: true,
  approvalLimits: {
    investmentAmount: Number.MAX_SAFE_INTEGER,
    riskLevel: RiskLevel.CRITICAL,
    requiresCoApproval: false,
  },
};

const mockProposal: ServiceProposal = {
  id: 'proposal-1',
  proposalNumber: 'SP-2025-001',
  title: 'SpaceX Pre-IPO Investment Fund',
  description: 'Exclusive access to SpaceX pre-IPO shares',
  category: ServiceCategory.PRE_IPO_FUNDS,
  tierAccess: 'void_exclusive' as any,
  riskLevel: RiskLevel.HIGH,
  provider: {
    id: 'provider-1',
    name: 'Elite Ventures',
    legalName: 'Elite Ventures Private Limited',
    registrationNumber: 'U65100MH2020PTC123456',
    jurisdiction: 'India',
    website: 'https://eliteventures.com',
    primaryContact: {
      name: 'Jane Doe',
      email: 'jane@eliteventures.com',
      phone: '+91-98765-43210',
      title: 'Managing Director',
    },
    businessLicense: 'LICENSE-123',
    insuranceCoverage: {
      provider: 'HDFC ERGO',
      policyNumber: 'POL-123456',
      coverage: 100000000,
      expiryDate: '2026-06-29T00:00:00Z',
    },
    financialHealth: {
      creditRating: 'AAA',
      auditedFinancials: true,
      lastAuditDate: '2024-12-31T00:00:00Z',
      netWorth: 500000000,
    },
  },
  serviceDetails: {
    minimumInvestment: 100000000,
    maximumInvestment: 1000000000,
    expectedReturns: '25-35% annually',
    investmentPeriod: '3-5 years',
    liquidityTerms: 'Limited liquidity during holding period',
    fees: {
      managementFee: 2.0,
      performanceFee: 20.0,
      entryFee: 1.0,
      exitFee: 0.5,
    },
  },
  complianceDocuments: [],
  riskAssessment: {
    overallRisk: RiskLevel.HIGH,
    marketRisk: RiskLevel.HIGH,
    liquidityRisk: RiskLevel.CRITICAL,
    operationalRisk: RiskLevel.MEDIUM,
    regulatoryRisk: RiskLevel.HIGH,
    riskMitigationMeasures: ['Diversified portfolio', 'Professional management'],
  },
  dueDiligence: {
    backgroundCheckCompleted: true,
    financialAuditCompleted: true,
    legalReviewCompleted: true,
    regulatoryApprovalObtained: false,
    referencesVerified: true,
  },
  anonymityFeatures: {
    zkProofCompatible: true,
    anonymousTransactions: true,
    identityShielding: true,
    communicationProtocol: 'Butler AI mediated',
  },
  status: ApprovalStatus.UNDER_REVIEW,
  submittedBy: 'user-2',
  submittedAt: '2025-06-29T09:00:00Z',
  reviewStages: [],
  approvals: [],
  onboardingTimeline: '2-3 weeks',
  integrationRequirements: ['API integration', 'Compliance setup'],
  supportRequirements: 'Dedicated relationship manager',
  expectedVolume: {
    monthly: 500000000,
    annual: 6000000000,
  },
  successMetrics: [
    { metric: 'Client Satisfaction', target: 95, measurement: 'percentage' },
    { metric: 'Return Performance', target: 30, measurement: 'percentage_annual' },
  ],
};

const mockDashboardMetrics = {
  proposalsInReview: 15,
  pendingApprovals: 8,
  approvedThisMonth: 12,
  rejectedThisMonth: 3,
  byCategory: {},
  byRiskLevel: {},
  performanceMetrics: {
    avgApprovalTime: 72,
    bottleneckStage: 'Compliance Review',
    complianceRate: 0.95,
    escalationRate: 0.08,
  },
};

// Test utilities
const renderWithProvider = (component: React.ReactElement, user = mockUser) => {
  return render(
    <VettingProvider initialUser={user}>
      {component}
    </VettingProvider>
  );
};

const setupMockResponses = () => {
  mockFetch.mockImplementation((url: string) => {
    if (url.includes('/api/admin/vetting/metrics')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockDashboardMetrics),
      } as Response);
    }
    
    if (url.includes('/api/admin/vetting/proposals')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([mockProposal]),
      } as Response);
    }
    
    if (url.includes('/api/admin/workflows')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);
    }
    
    if (url.includes('/api/admin/rbac/users')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([mockUser]),
      } as Response);
    }
    
    if (url.includes('/api/admin/audit-logs')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);
    }
    
    return Promise.resolve({
      ok: false,
      json: () => Promise.resolve({}),
    } as Response);
  });
};

describe('Service Vetting System', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    setupMockResponses();
    // Reset store state
    useVettingStore.getState().reset();
  });

  describe('Zustand Store', () => {
    it('should initialize with correct default state', () => {
      const store = useVettingStore.getState();
      
      expect(store.currentUser).toBeNull();
      expect(store.isAuthenticated).toBe(false);
      expect(store.proposals).toEqual([]);
      expect(store.workflows).toEqual([]);
      expect(store.users).toEqual([]);
      expect(store.auditLogs).toEqual([]);
      expect(store.loading.global).toBe(false);
      expect(store.modals.createProposal).toBe(false);
    });

    it('should set current user and update authentication state', () => {
      const { setCurrentUser } = useVettingStore.getState();
      
      act(() => {
        setCurrentUser(mockUser);
      });
      
      const store = useVettingStore.getState();
      expect(store.currentUser).toEqual(mockUser);
      expect(store.isAuthenticated).toBe(true);
      expect(store.userPermissions).toEqual(mockUser.permissions);
    });

    it('should manage proposals correctly', () => {
      const { setProposals, addProposal, updateProposal, deleteProposal } = useVettingStore.getState();
      
      // Set initial proposals
      act(() => {
        setProposals([mockProposal]);
      });
      
      expect(useVettingStore.getState().proposals).toHaveLength(1);
      
      // Add new proposal
      const newProposal = { ...mockProposal, id: 'proposal-2', title: 'New Proposal' };
      act(() => {
        addProposal(newProposal);
      });
      
      expect(useVettingStore.getState().proposals).toHaveLength(2);
      
      // Update proposal
      act(() => {
        updateProposal('proposal-1', { status: ApprovalStatus.APPROVED });
      });
      
      const updatedProposal = useVettingStore.getState().proposals.find(p => p.id === 'proposal-1');
      expect(updatedProposal?.status).toBe(ApprovalStatus.APPROVED);
      
      // Delete proposal
      act(() => {
        deleteProposal('proposal-1');
      });
      
      expect(useVettingStore.getState().proposals).toHaveLength(1);
      expect(useVettingStore.getState().proposals[0].id).toBe('proposal-2');
    });

    it('should apply proposal filters correctly', () => {
      const { setProposals, setProposalFilter, setCurrentUser } = useVettingStore.getState();
      
      // Set up test data
      act(() => {
        setCurrentUser(mockUser);
        setProposals([
          mockProposal,
          { ...mockProposal, id: 'proposal-2', category: ServiceCategory.REAL_ESTATE_FUNDS },
          { ...mockProposal, id: 'proposal-3', status: ApprovalStatus.APPROVED },
        ]);
      });
      
      // Filter by category
      act(() => {
        setProposalFilter({ category: ServiceCategory.PRE_IPO_FUNDS });
      });
      
      expect(useVettingStore.getState().filteredProposals).toHaveLength(2);
      
      // Filter by status
      act(() => {
        setProposalFilter({ category: 'all', status: ApprovalStatus.APPROVED });
      });
      
      expect(useVettingStore.getState().filteredProposals).toHaveLength(1);
      
      // Search filter
      act(() => {
        setProposalFilter({ category: 'all', status: 'all', searchTerm: 'SpaceX' });
      });
      
      expect(useVettingStore.getState().filteredProposals).toHaveLength(2);
    });

    it('should manage modal state correctly', () => {
      const { openModal, closeModal, closeAllModals } = useVettingStore.getState();
      
      // Open modal
      act(() => {
        openModal('createProposal');
      });
      
      expect(useVettingStore.getState().modals.createProposal).toBe(true);
      
      // Close specific modal
      act(() => {
        closeModal('createProposal');
      });
      
      expect(useVettingStore.getState().modals.createProposal).toBe(false);
      
      // Open multiple modals and close all
      act(() => {
        openModal('createProposal');
        openModal('editUser');
      });
      
      expect(useVettingStore.getState().modals.createProposal).toBe(true);
      expect(useVettingStore.getState().modals.editUser).toBe(true);
      
      act(() => {
        closeAllModals();
      });
      
      expect(useVettingStore.getState().modals.createProposal).toBe(false);
      expect(useVettingStore.getState().modals.editUser).toBe(false);
    });
  });

  describe('VettingDashboard Component', () => {
    it('should render dashboard with metrics', async () => {
      renderWithProvider(<VettingDashboard currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('Service Vetting Dashboard')).toBeInTheDocument();
      });
      
      // Check if metrics are displayed
      await waitFor(() => {
        expect(screen.getByText('15')).toBeInTheDocument(); // Pending Reviews
        expect(screen.getByText('8')).toBeInTheDocument(); // Pending Approvals
      });
    });

    it('should filter proposals correctly', async () => {
      renderWithProvider(<VettingDashboard currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('Service Vetting Dashboard')).toBeInTheDocument();
      });
      
      // Test category filter
      const categorySelect = screen.getByDisplayValue('All Categories');
      fireEvent.change(categorySelect, { target: { value: ServiceCategory.PRE_IPO_FUNDS } });
      
      // Should trigger filter application
      expect(categorySelect).toHaveValue(ServiceCategory.PRE_IPO_FUNDS);
    });

    it('should display proposals table', async () => {
      renderWithProvider(<VettingDashboard currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('Service Proposals')).toBeInTheDocument();
      });
      
      // Check table headers
      expect(screen.getByText('Proposal')).toBeInTheDocument();
      expect(screen.getByText('Category')).toBeInTheDocument();
      expect(screen.getByText('Risk Level')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
    });
  });

  describe('ServiceProposalForm Component', () => {
    const mockOnSubmit = jest.fn();
    const mockOnCancel = jest.fn();

    beforeEach(() => {
      mockOnSubmit.mockClear();
      mockOnCancel.mockClear();
    });

    it('should render form with all steps', () => {
      renderWithProvider(
        <ServiceProposalForm
          currentUser={mockUser}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );
      
      expect(screen.getByText('Create Service Proposal')).toBeInTheDocument();
      expect(screen.getByText('Step 1 of 6')).toBeInTheDocument();
      expect(screen.getByText('Basic Information')).toBeInTheDocument();
    });

    it('should validate required fields', async () => {
      const user = userEvent.setup();
      
      renderWithProvider(
        <ServiceProposalForm
          currentUser={mockUser}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );
      
      // Try to go to next step without filling required fields
      const nextButton = screen.getByText('Next');
      await user.click(nextButton);
      
      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText('Title is required')).toBeInTheDocument();
      });
    });

    it('should navigate through form steps', async () => {
      const user = userEvent.setup();
      
      renderWithProvider(
        <ServiceProposalForm
          currentUser={mockUser}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );
      
      // Fill required fields in step 1
      await user.type(screen.getByPlaceholderText('e.g., SpaceX Pre-IPO Investment Fund'), mockProposal.title);
      await user.type(screen.getByPlaceholderText('Detailed description of the service offering...'), mockProposal.description);
      await user.type(screen.getByPlaceholderText('Company name'), mockProposal.provider.name);
      await user.type(screen.getByPlaceholderText('Legal company name as registered'), mockProposal.provider.legalName);
      
      // Go to next step
      const nextButton = screen.getByText('Next');
      await user.click(nextButton);
      
      // Should be on step 2
      await waitFor(() => {
        expect(screen.getByText('Step 2 of 6')).toBeInTheDocument();
        expect(screen.getByText('Provider Details')).toBeInTheDocument();
      });
    });

    it('should handle form cancellation', async () => {
      const user = userEvent.setup();
      
      renderWithProvider(
        <ServiceProposalForm
          currentUser={mockUser}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );
      
      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);
      
      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });
  });

  describe('ApprovalWorkflowDashboard Component', () => {
    it('should render workflow dashboard', async () => {
      renderWithProvider(<ApprovalWorkflowDashboard currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('Approval Workflow Dashboard')).toBeInTheDocument();
      });
      
      expect(screen.getByText('Real-time visualization and management of service proposal approval workflows')).toBeInTheDocument();
    });

    it('should display workflow filters', async () => {
      renderWithProvider(<ApprovalWorkflowDashboard currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('Status Filter')).toBeInTheDocument();
        expect(screen.getByText('Category Filter')).toBeInTheDocument();
      });
      
      // Check filter options
      expect(screen.getByDisplayValue('All Statuses')).toBeInTheDocument();
      expect(screen.getByDisplayValue('All Categories')).toBeInTheDocument();
    });
  });

  describe('RBACManager Component', () => {
    it('should render RBAC management interface', async () => {
      renderWithProvider(<RBACManager currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('RBAC Management')).toBeInTheDocument();
      });
      
      // Check tabs
      expect(screen.getByText('Users')).toBeInTheDocument();
      expect(screen.getByText('Roles')).toBeInTheDocument();
      expect(screen.getByText('Permissions')).toBeInTheDocument();
    });

    it('should display users table', async () => {
      renderWithProvider(<RBACManager currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('User Management')).toBeInTheDocument();
      });
      
      // Should display table headers
      expect(screen.getByText('User')).toBeInTheDocument();
      expect(screen.getByText('Role')).toBeInTheDocument();
      expect(screen.getByText('Department')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
    });

    it('should switch between tabs', async () => {
      const user = userEvent.setup();
      
      renderWithProvider(<RBACManager currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('RBAC Management')).toBeInTheDocument();
      });
      
      // Click on Roles tab
      const rolesTab = screen.getByText('Roles');
      await user.click(rolesTab);
      
      await waitFor(() => {
        expect(screen.getByText('Role Hierarchy')).toBeInTheDocument();
      });
      
      // Click on Permissions tab
      const permissionsTab = screen.getByText('Permissions');
      await user.click(permissionsTab);
      
      await waitFor(() => {
        expect(screen.getByText('Permission Matrix')).toBeInTheDocument();
      });
    });
  });

  describe('AuditLogViewer Component', () => {
    it('should render audit log viewer', async () => {
      renderWithProvider(<AuditLogViewer currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('Audit Log Viewer')).toBeInTheDocument();
      });
      
      expect(screen.getByText('Comprehensive compliance tracking and security monitoring')).toBeInTheDocument();
    });

    it('should display audit log filters', async () => {
      renderWithProvider(<AuditLogViewer currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search logs...')).toBeInTheDocument();
      });
      
      // Check filter controls
      expect(screen.getByDisplayValue('All Outcomes')).toBeInTheDocument();
      expect(screen.getByText('Export Logs')).toBeInTheDocument();
    });

    it('should handle audit log export', async () => {
      const user = userEvent.setup();
      
      // Mock successful export
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          blob: () => Promise.resolve(new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })),
        } as Response)
      );
      
      renderWithProvider(<AuditLogViewer currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('Export Logs')).toBeInTheDocument();
      });
      
      const exportButton = screen.getByText('Export Logs');
      await user.click(exportButton);
      
      // Should call export API
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/admin/audit-logs/export',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
            }),
          })
        );
      });
    });
  });

  describe('Real-time Updates', () => {
    it('should handle WebSocket connection', () => {
      renderWithProvider(<VettingDashboard currentUser={mockUser} />);
      
      // Verify WebSocket was created
      expect(global.WebSocket).toHaveBeenCalled();
    });

    it('should handle auto-refresh when enabled', () => {
      jest.useFakeTimers();
      
      // Enable auto-refresh
      act(() => {
        useVettingStore.getState().setAutoRefresh(true);
        useVettingStore.getState().setRefreshInterval(5000);
      });
      
      renderWithProvider(<VettingDashboard currentUser={mockUser} />);
      
      // Fast-forward time
      act(() => {
        jest.advanceTimersByTime(6000);
      });
      
      // Should have made additional API calls for refresh
      expect(mockFetch).toHaveBeenCalledTimes(4); // Initial load + one refresh cycle
      
      jest.useRealTimers();
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      // Mock API failure
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ error: 'API Error' }),
        } as Response)
      );
      
      renderWithProvider(<VettingDashboard currentUser={mockUser} />);
      
      await waitFor(() => {
        expect(screen.getByText('Service Vetting Dashboard')).toBeInTheDocument();
      });
      
      // Error should be stored in state
      await waitFor(() => {
        const store = useVettingStore.getState();
        expect(store.error.proposals).toBeTruthy();
      });
    });

    it('should handle network timeouts', async () => {
      // Mock network timeout
      mockFetch.mockImplementationOnce(() =>
        Promise.reject(new Error('Network timeout'))
      );
      
      renderWithProvider(<VettingDashboard currentUser={mockUser} />);
      
      await waitFor(() => {
        const store = useVettingStore.getState();
        expect(store.error.proposals).toBeTruthy();
      });
    });
  });

  describe('Permission-based Access Control', () => {
    it('should restrict proposal access based on user role', () => {
      const analystUser: User = {
        ...mockUser,
        role: UserRole.INVESTMENT_ANALYST,
      };
      
      act(() => {
        useVettingStore.getState().setCurrentUser(analystUser);
      });
      
      const store = useVettingStore.getState();
      
      // Investment analyst should access investment-related proposals
      const investmentProposal = { ...mockProposal, category: ServiceCategory.PRE_IPO_FUNDS };
      expect(store.canUserAccessProposal(investmentProposal)).toBe(true);
      
      // But not medical evacuation proposals
      const medicalProposal = { ...mockProposal, category: ServiceCategory.MEDICAL_EVACUATION };
      expect(store.canUserAccessProposal(medicalProposal)).toBe(false);
    });

    it('should allow CEO to access all proposals', () => {
      act(() => {
        useVettingStore.getState().setCurrentUser(mockUser); // CEO
      });
      
      const store = useVettingStore.getState();
      
      // CEO should access any category
      const proposals = [
        { ...mockProposal, category: ServiceCategory.PRE_IPO_FUNDS },
        { ...mockProposal, category: ServiceCategory.MEDICAL_EVACUATION },
        { ...mockProposal, category: ServiceCategory.LEGAL_SERVICES },
      ];
      
      proposals.forEach(proposal => {
        expect(store.canUserAccessProposal(proposal)).toBe(true);
      });
    });
  });
});

describe('Store Persistence', () => {
  it('should persist user session and filters', () => {
    // Set some state
    act(() => {
      useVettingStore.getState().setCurrentUser(mockUser);
      useVettingStore.getState().setProposalFilter({ category: ServiceCategory.PRE_IPO_FUNDS });
      useVettingStore.getState().setAutoRefresh(true);
    });
    
    const state = useVettingStore.getState();
    
    // These should be persisted according to the partialize function
    expect(state.currentUser).toEqual(mockUser);
    expect(state.proposalFilter.category).toBe(ServiceCategory.PRE_IPO_FUNDS);
    expect(state.autoRefresh).toBe(true);
  });
});