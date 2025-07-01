/**
 * Approval Workflow Visualization Dashboard
 * Real-time visualization of service proposal approval workflows
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ServiceProposal,
  ApprovalStatus,
  UserRole,
  User,
  ServiceCategory,
  RiskLevel,
} from '@/types/service-management';
import { ServiceVettingEngine } from '@/services/ServiceVettingEngine';

interface WorkflowStage {
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
}

interface WorkflowInstance {
  proposalId: string;
  proposal: ServiceProposal;
  stages: WorkflowStage[];
  currentStage: number;
  overallStatus: ApprovalStatus;
  createdAt: string;
  estimatedCompletion: string;
  actualCompletion?: string;
  escalations: number;
  bottlenecks: string[];
}

interface ApprovalWorkflowDashboardProps {
  currentUser: User;
}

export const ApprovalWorkflowDashboard: React.FC<ApprovalWorkflowDashboardProps> = ({
  currentUser,
}) => {
  const [workflows, setWorkflows] = useState<WorkflowInstance[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowInstance | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<ApprovalStatus | 'all'>('all');
  const [filterCategory, setFilterCategory] = useState<ServiceCategory | 'all'>('all');

  useEffect(() => {
    fetchWorkflows();
    const interval = setInterval(fetchWorkflows, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/admin/workflows?userId=${currentUser.id}`);
      const data = await response.json();
      setWorkflows(data);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStageIcon = (status: WorkflowStage['status']) => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      case 'rejected': return '❌';
      case 'escalated': return '⚡';
      default: return '⏳';
    }
  };

  const getStageColor = (status: WorkflowStage['status']) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'in_progress': return 'bg-blue-500';
      case 'rejected': return 'bg-red-500';
      case 'escalated': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskColor = (risk: RiskLevel) => {
    switch (risk) {
      case RiskLevel.LOW: return 'text-green-400';
      case RiskLevel.MEDIUM: return 'text-yellow-400';
      case RiskLevel.HIGH: return 'text-orange-400';
      case RiskLevel.CRITICAL: return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getTimeRemaining = (stage: WorkflowStage) => {
    if (!stage.startedAt || stage.status === 'completed') return null;
    
    const startTime = new Date(stage.startedAt);
    const timeoutTime = new Date(startTime.getTime() + stage.timeoutHours * 60 * 60 * 1000);
    const now = new Date();
    const remaining = timeoutTime.getTime() - now.getTime();
    
    if (remaining <= 0) return 'Overdue';
    
    const hours = Math.floor(remaining / (1000 * 60 * 60));
    const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m remaining`;
  };

  const handleStageAction = async (workflowId: string, stageId: string, action: 'approve' | 'reject' | 'escalate', comments?: string) => {
    try {
      await fetch(`/api/admin/workflows/${workflowId}/stages/${stageId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, comments, userId: currentUser.id }),
      });
      
      await fetchWorkflows();
    } catch (error) {
      console.error('Failed to process stage action:', error);
    }
  };

  const filteredWorkflows = workflows.filter(workflow => {
    const statusMatch = filterStatus === 'all' || workflow.overallStatus === filterStatus;
    const categoryMatch = filterCategory === 'all' || workflow.proposal.category === filterCategory;
    return statusMatch && categoryMatch;
  });

  const canUserActOnStage = (stage: WorkflowStage): boolean => {
    return stage.requiredRole === currentUser.role || currentUser.role === UserRole.CEO;
  };

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
          <h1 className="text-4xl font-bold text-white mb-2">Approval Workflow Dashboard</h1>
          <p className="text-gray-400">
            Real-time visualization and management of service proposal approval workflows
          </p>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700 mb-8"
        >
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Status Filter</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as ApprovalStatus | 'all')}
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

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Category Filter</label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value as ServiceCategory | 'all')}
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

            <div className="flex items-end">
              <button
                onClick={fetchWorkflows}
                className="px-4 py-2 text-black bg-yellow-400 rounded-lg hover:bg-yellow-300 transition-colors font-medium"
              >
                Refresh
              </button>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Workflow List */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700"
            >
              <div className="p-6 border-b border-gray-700">
                <h3 className="text-xl font-semibold text-white">Active Workflows</h3>
                <p className="text-gray-400 text-sm">
                  {filteredWorkflows.length} workflows match your filters
                </p>
              </div>

              <div className="max-h-[600px] overflow-y-auto">
                <AnimatePresence>
                  {filteredWorkflows.map((workflow) => (
                    <motion.div
                      key={workflow.proposalId}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className={`p-6 border-b border-gray-700 cursor-pointer transition-colors ${
                        selectedWorkflow?.proposalId === workflow.proposalId
                          ? 'bg-gray-700/50'
                          : 'hover:bg-gray-700/30'
                      }`}
                      onClick={() => setSelectedWorkflow(workflow)}
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="text-lg font-medium text-white mb-1">
                            {workflow.proposal.title}
                          </h4>
                          <p className="text-sm text-gray-400">
                            {workflow.proposal.proposalNumber} • {workflow.proposal.provider.name}
                          </p>
                        </div>
                        <div className="text-right">
                          <span className={`text-sm font-medium ${getRiskColor(workflow.proposal.riskLevel)}`}>
                            {workflow.proposal.riskLevel.toUpperCase()} RISK
                          </span>
                          <p className="text-xs text-gray-400 mt-1">
                            Stage {workflow.currentStage + 1} of {workflow.stages.length}
                          </p>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="mb-4">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                          <span>Progress</span>
                          <span>{Math.round(((workflow.currentStage + 1) / workflow.stages.length) * 100)}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-yellow-500 to-yellow-400 h-2 rounded-full transition-all"
                            style={{ width: `${((workflow.currentStage + 1) / workflow.stages.length) * 100}%` }}
                          />
                        </div>
                      </div>

                      {/* Current Stage */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{getStageIcon(workflow.stages[workflow.currentStage]?.status)}</span>
                          <span className="text-sm text-gray-300">
                            {workflow.stages[workflow.currentStage]?.name}
                          </span>
                        </div>

                        <div className="flex items-center space-x-4">
                          {workflow.escalations > 0 && (
                            <span className="px-2 py-1 text-xs bg-yellow-900 text-yellow-300 rounded-full">
                              {workflow.escalations} escalation{workflow.escalations > 1 ? 's' : ''}
                            </span>
                          )}
                          
                          {workflow.bottlenecks.length > 0 && (
                            <span className="px-2 py-1 text-xs bg-red-900 text-red-300 rounded-full">
                              Bottleneck
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Time Remaining */}
                      {workflow.stages[workflow.currentStage] && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-400">
                            {getTimeRemaining(workflow.stages[workflow.currentStage]) || 'No time limit'}
                          </p>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </motion.div>
          </div>

          {/* Workflow Details */}
          <div>
            <AnimatePresence mode="wait">
              {selectedWorkflow ? (
                <motion.div
                  key={selectedWorkflow.proposalId}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700"
                >
                  <div className="p-6 border-b border-gray-700">
                    <h3 className="text-xl font-semibold text-white mb-2">Workflow Details</h3>
                    <p className="text-gray-400 text-sm">{selectedWorkflow.proposal.title}</p>
                  </div>

                  <div className="p-6">
                    {/* Workflow Stages */}
                    <div className="space-y-4">
                      {selectedWorkflow.stages.map((stage, index) => (
                        <div
                          key={stage.id}
                          className={`relative ${index < selectedWorkflow.stages.length - 1 ? 'pb-8' : ''}`}
                        >
                          {/* Connector Line */}
                          {index < selectedWorkflow.stages.length - 1 && (
                            <div className="absolute left-4 top-8 w-0.5 h-6 bg-gray-600" />
                          )}

                          <div className="flex items-start space-x-3">
                            {/* Stage Icon */}
                            <div className={`w-8 h-8 rounded-full ${getStageColor(stage.status)} flex items-center justify-center text-white text-sm font-bold relative z-10`}>
                              {index + 1}
                            </div>

                            {/* Stage Details */}
                            <div className="flex-1 min-w-0">
                              <div className="flex justify-between items-start mb-1">
                                <h4 className="text-sm font-medium text-white">{stage.name}</h4>
                                <span className="text-xs text-gray-400">{getStageIcon(stage.status)}</span>
                              </div>

                              <p className="text-xs text-gray-400 mb-2">
                                Required: {stage.requiredRole.replace(/_/g, ' ').toUpperCase()}
                              </p>

                              {stage.assignee && (
                                <p className="text-xs text-gray-400 mb-2">
                                  Assigned: {stage.assignee.name}
                                </p>
                              )}

                              {stage.status === 'in_progress' && (
                                <div className="mb-2">
                                  <p className="text-xs text-yellow-400">
                                    {getTimeRemaining(stage)}
                                  </p>
                                </div>
                              )}

                              {stage.comments && (
                                <div className="bg-gray-700 p-2 rounded text-xs text-gray-300 mb-2">
                                  {stage.comments}
                                </div>
                              )}

                              {/* Stage Actions */}
                              {stage.status === 'in_progress' && canUserActOnStage(stage) && (
                                <div className="flex space-x-2 mt-2">
                                  <button
                                    onClick={() => handleStageAction(selectedWorkflow.proposalId, stage.id, 'approve')}
                                    className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-500 transition-colors"
                                  >
                                    Approve
                                  </button>
                                  <button
                                    onClick={() => handleStageAction(selectedWorkflow.proposalId, stage.id, 'reject')}
                                    className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-500 transition-colors"
                                  >
                                    Reject
                                  </button>
                                  <button
                                    onClick={() => handleStageAction(selectedWorkflow.proposalId, stage.id, 'escalate')}
                                    className="px-3 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-500 transition-colors"
                                  >
                                    Escalate
                                  </button>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Workflow Summary */}
                    <div className="mt-6 pt-6 border-t border-gray-700">
                      <h4 className="text-sm font-medium text-white mb-3">Workflow Summary</h4>
                      
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Created:</span>
                          <span className="text-white">
                            {new Date(selectedWorkflow.createdAt).toLocaleDateString()}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-400">Est. Completion:</span>
                          <span className="text-white">
                            {new Date(selectedWorkflow.estimatedCompletion).toLocaleDateString()}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-400">Category:</span>
                          <span className="text-white">
                            {selectedWorkflow.proposal.category.replace(/_/g, ' ').toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-400">Risk Level:</span>
                          <span className={getRiskColor(selectedWorkflow.proposal.riskLevel)}>
                            {selectedWorkflow.proposal.riskLevel.toUpperCase()}
                          </span>
                        </div>
                      </div>

                      {selectedWorkflow.bottlenecks.length > 0 && (
                        <div className="mt-4 p-3 bg-red-900/20 border border-red-600 rounded">
                          <h5 className="text-xs font-medium text-red-300 mb-1">Bottlenecks Detected</h5>
                          <ul className="text-xs text-red-200 space-y-1">
                            {selectedWorkflow.bottlenecks.map((bottleneck, index) => (
                              <li key={index}>• {bottleneck}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700 p-8 text-center"
                >
                  <div className="text-gray-400 mb-4">
                    <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Select a Workflow</h3>
                  <p className="text-gray-400 text-sm">
                    Click on a workflow from the list to view its details and manage approval stages.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};