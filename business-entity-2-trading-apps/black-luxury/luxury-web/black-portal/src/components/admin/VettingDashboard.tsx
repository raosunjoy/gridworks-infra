/**
 * Service Vetting Dashboard
 * Main admin interface for managing service proposals and vetting workflow
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  DashboardMetrics,
  ServiceProposal,
  ApprovalStatus,
  ServiceCategory,
  RiskLevel,
  UserRole,
  User,
} from '@/types/service-management';

interface VettingDashboardProps {
  currentUser: User;
}

export const VettingDashboard: React.FC<VettingDashboardProps> = ({
  currentUser,
}) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [proposals, setProposals] = useState<ServiceProposal[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<ServiceCategory | 'all'>('all');
  const [selectedStatus, setSelectedStatus] = useState<ApprovalStatus | 'all'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard metrics
      const metricsResponse = await fetch('/api/admin/vetting/metrics');
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

      // Fetch proposals based on user role permissions
      const proposalsResponse = await fetch(`/api/admin/vetting/proposals?role=${currentUser.role}`);
      const proposalsData = await proposalsResponse.json();
      setProposals(proposalsData);
      
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: ApprovalStatus): string => {
    switch (status) {
      case ApprovalStatus.APPROVED: return 'bg-green-100 text-green-800 border-green-200';
      case ApprovalStatus.REJECTED: return 'bg-red-100 text-red-800 border-red-200';
      case ApprovalStatus.PENDING_APPROVAL: return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case ApprovalStatus.UNDER_REVIEW: return 'bg-blue-100 text-blue-800 border-blue-200';
      case ApprovalStatus.SECURITY_REVIEW: return 'bg-purple-100 text-purple-800 border-purple-200';
      case ApprovalStatus.COMPLIANCE_REVIEW: return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case ApprovalStatus.SUSPENDED: return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRiskColor = (risk: RiskLevel): string => {
    switch (risk) {
      case RiskLevel.LOW: return 'text-green-600';
      case RiskLevel.MEDIUM: return 'text-yellow-600';
      case RiskLevel.HIGH: return 'text-orange-600';
      case RiskLevel.CRITICAL: return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const canUserViewProposal = (proposal: ServiceProposal): boolean => {
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
  };

  const filteredProposals = proposals.filter(proposal => {
    const categoryMatch = selectedCategory === 'all' || proposal.category === selectedCategory;
    const statusMatch = selectedStatus === 'all' || proposal.status === selectedStatus;
    const permissionMatch = canUserViewProposal(proposal);
    
    return categoryMatch && statusMatch && permissionMatch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-yellow-400 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">Service Vetting Dashboard</h1>
          <p className="text-gray-400">
            Secure and unbiased service approval for Black tier ultra-premium services
          </p>
        </motion.div>

        {/* Metrics Overview */}
        {metrics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          >
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Pending Reviews</p>
                  <p className="text-3xl font-bold text-white">{metrics.proposalsInReview}</p>
                </div>
                <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-yellow-400 rounded"></div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Pending Approvals</p>
                  <p className="text-3xl font-bold text-white">{metrics.pendingApprovals}</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-blue-400 rounded"></div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Approved This Month</p>
                  <p className="text-3xl font-bold text-green-400">{metrics.approvedThisMonth}</p>
                </div>
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-green-400 rounded"></div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Rejected This Month</p>
                  <p className="text-3xl font-bold text-red-400">{metrics.rejectedThisMonth}</p>
                </div>
                <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-red-400 rounded"></div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Performance Metrics */}
        {metrics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700 mb-8"
          >
            <h3 className="text-xl font-semibold text-white mb-4">Performance Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-gray-400 text-sm">Avg Approval Time</p>
                <p className="text-2xl font-bold text-white">{metrics.performanceMetrics.avgApprovalTime}h</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Compliance Rate</p>
                <p className="text-2xl font-bold text-green-400">
                  {(metrics.performanceMetrics.complianceRate * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Escalation Rate</p>
                <p className="text-2xl font-bold text-yellow-400">
                  {(metrics.performanceMetrics.escalationRate * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700 mb-8"
        >
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value as ServiceCategory | 'all')}
                className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
              >
                <option value="all">All Categories</option>
                {Object.values(ServiceCategory).map(category => (
                  <option key={category} value={category}>
                    {category.replace(/_/g, ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as ApprovalStatus | 'all')}
                className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
              >
                <option value="all">All Statuses</option>
                {Object.values(ApprovalStatus).map(status => (
                  <option key={status} value={status}>
                    {status.replace(/_/g, ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </motion.div>

        {/* Proposals Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700 overflow-hidden"
        >
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-xl font-semibold text-white">Service Proposals</h3>
            <p className="text-gray-400 text-sm">
              {filteredProposals.length} proposals match your filters
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Proposal
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Risk Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Submitted
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                <AnimatePresence>
                  {filteredProposals.map((proposal) => (
                    <motion.tr
                      key={proposal.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="hover:bg-gray-700/50 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-white">{proposal.title}</div>
                          <div className="text-sm text-gray-400">{proposal.proposalNumber}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-300">
                          {proposal.category.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${getRiskColor(proposal.riskLevel)}`}>
                          {proposal.riskLevel.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getStatusColor(proposal.status)}`}>
                          {proposal.status.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {new Date(proposal.submittedAt).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button className="text-yellow-400 hover:text-yellow-300 transition-colors">
                            View
                          </button>
                          <button className="text-blue-400 hover:text-blue-300 transition-colors">
                            Review
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
};