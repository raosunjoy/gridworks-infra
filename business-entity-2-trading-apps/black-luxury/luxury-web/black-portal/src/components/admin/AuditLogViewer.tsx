/**
 * Audit Log Viewer
 * Comprehensive compliance tracking and audit trail visualization
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AuditLog,
  User,
  UserRole,
  Permission,
} from '@/types/service-management';

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

interface AuditLogViewerProps {
  currentUser: User;
}

interface AuditLogWithUser extends AuditLog {
  user?: {
    name: string;
    email: string;
    role: UserRole;
    department: string;
  };
}

export const AuditLogViewer: React.FC<AuditLogViewerProps> = ({ currentUser }) => {
  const [auditLogs, setAuditLogs] = useState<AuditLogWithUser[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<AuditLogWithUser[]>([]);
  const [selectedLog, setSelectedLog] = useState<AuditLogWithUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<AuditFilter>({
    outcome: 'all',
    sensitiveData: 'all',
    dateFrom: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
    dateTo: new Date().toISOString().split('T')[0], // today
  });
  const [exportLoading, setExportLoading] = useState(false);

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [auditLogs, filter]);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/audit-logs', {
        headers: {
          'Authorization': `Bearer ${currentUser.id}`,
        },
      });
      const data = await response.json();
      setAuditLogs(data);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...auditLogs];

    // User filter
    if (filter.userId) {
      filtered = filtered.filter(log => log.userId === filter.userId);
    }

    // Action filter
    if (filter.action) {
      filtered = filtered.filter(log => 
        log.action.toLowerCase().includes(filter.action!.toLowerCase())
      );
    }

    // Resource filter
    if (filter.resource) {
      filtered = filtered.filter(log => 
        log.resource.toLowerCase().includes(filter.resource!.toLowerCase())
      );
    }

    // Outcome filter
    if (filter.outcome && filter.outcome !== 'all') {
      filtered = filtered.filter(log => log.outcome === filter.outcome);
    }

    // Sensitive data filter
    if (filter.sensitiveData !== 'all') {
      filtered = filtered.filter(log => log.sensitiveData === filter.sensitiveData);
    }

    // Date range filter
    if (filter.dateFrom) {
      const fromDate = new Date(filter.dateFrom);
      filtered = filtered.filter(log => new Date(log.timestamp) >= fromDate);
    }

    if (filter.dateTo) {
      const toDate = new Date(filter.dateTo);
      toDate.setHours(23, 59, 59, 999); // Include the full day
      filtered = filtered.filter(log => new Date(log.timestamp) <= toDate);
    }

    // Search term filter
    if (filter.searchTerm) {
      const searchLower = filter.searchTerm.toLowerCase();
      filtered = filtered.filter(log => 
        log.action.toLowerCase().includes(searchLower) ||
        log.resource.toLowerCase().includes(searchLower) ||
        log.resourceId.toLowerCase().includes(searchLower) ||
        JSON.stringify(log.changes).toLowerCase().includes(searchLower) ||
        log.user?.name.toLowerCase().includes(searchLower) ||
        log.user?.email.toLowerCase().includes(searchLower)
      );
    }

    // Sort by timestamp (newest first)
    filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    setFilteredLogs(filtered);
  };

  const exportAuditLogs = async () => {
    try {
      setExportLoading(true);
      
      const exportData = {
        logs: filteredLogs,
        filter,
        exportedBy: currentUser.id,
        exportedAt: new Date().toISOString(),
        totalRecords: filteredLogs.length,
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
      }
    } catch (error) {
      console.error('Failed to export audit logs:', error);
    } finally {
      setExportLoading(false);
    }
  };

  const getOutcomeIcon = (outcome: AuditLog['outcome']) => {
    switch (outcome) {
      case 'success': return '✅';
      case 'failure': return '❌';
      case 'warning': return '⚠️';
      default: return '❓';
    }
  };

  const getOutcomeColor = (outcome: AuditLog['outcome']) => {
    switch (outcome) {
      case 'success': return 'text-green-400';
      case 'failure': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getActionCategory = (action: string): { category: string; color: string } => {
    if (action.includes('LOGIN') || action.includes('LOGOUT')) {
      return { category: 'Authentication', color: 'bg-blue-100 text-blue-800' };
    }
    if (action.includes('CREATE') || action.includes('SUBMIT')) {
      return { category: 'Creation', color: 'bg-green-100 text-green-800' };
    }
    if (action.includes('UPDATE') || action.includes('EDIT') || action.includes('MODIFY')) {
      return { category: 'Modification', color: 'bg-yellow-100 text-yellow-800' };
    }
    if (action.includes('DELETE') || action.includes('REMOVE')) {
      return { category: 'Deletion', color: 'bg-red-100 text-red-800' };
    }
    if (action.includes('APPROVE') || action.includes('REJECT')) {
      return { category: 'Approval', color: 'bg-purple-100 text-purple-800' };
    }
    if (action.includes('EMERGENCY')) {
      return { category: 'Emergency', color: 'bg-orange-100 text-orange-800' };
    }
    return { category: 'Other', color: 'bg-gray-100 text-gray-800' };
  };

  const canAccessSensitiveData = (): boolean => {
    return [UserRole.CEO, UserRole.CCO, UserRole.ADMIN].includes(currentUser.role);
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString(),
      relative: getRelativeTime(date),
    };
  };

  const getRelativeTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
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
          <h1 className="text-4xl font-bold text-white mb-2">Audit Log Viewer</h1>
          <p className="text-gray-400">
            Comprehensive compliance tracking and security monitoring
          </p>
        </motion.div>

        {/* Stats Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Events</p>
                <p className="text-3xl font-bold text-white">{filteredLogs.length}</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Success Rate</p>
                <p className="text-3xl font-bold text-green-400">
                  {filteredLogs.length > 0 
                    ? Math.round((filteredLogs.filter(log => log.outcome === 'success').length / filteredLogs.length) * 100)
                    : 0}%
                </p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <span className="text-2xl">✅</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Sensitive Data</p>
                <p className="text-3xl font-bold text-yellow-400">
                  {filteredLogs.filter(log => log.sensitiveData).length}
                </p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🔒</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Failed Events</p>
                <p className="text-3xl font-bold text-red-400">
                  {filteredLogs.filter(log => log.outcome === 'failure').length}
                </p>
              </div>
              <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                <span className="text-2xl">❌</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700 mb-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Search</label>
              <input
                type="text"
                value={filter.searchTerm || ''}
                onChange={(e) => setFilter(prev => ({ ...prev, searchTerm: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="Search logs..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Outcome</label>
              <select
                value={filter.outcome}
                onChange={(e) => setFilter(prev => ({ ...prev, outcome: e.target.value as any }))}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
              >
                <option value="all">All Outcomes</option>
                <option value="success">Success</option>
                <option value="failure">Failure</option>
                <option value="warning">Warning</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">From Date</label>
              <input
                type="date"
                value={filter.dateFrom || ''}
                onChange={(e) => setFilter(prev => ({ ...prev, dateFrom: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">To Date</label>
              <input
                type="date"
                value={filter.dateTo || ''}
                onChange={(e) => setFilter(prev => ({ ...prev, dateTo: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Action</label>
              <input
                type="text"
                value={filter.action || ''}
                onChange={(e) => setFilter(prev => ({ ...prev, action: e.target.value }))}
                className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="Filter by action"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Resource</label>
              <input
                type="text"
                value={filter.resource || ''}
                onChange={(e) => setFilter(prev => ({ ...prev, resource: e.target.value }))}
                className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                placeholder="Filter by resource"
              />
            </div>

            {canAccessSensitiveData() && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Sensitive Data</label>
                <select
                  value={filter.sensitiveData?.toString() || 'all'}
                  onChange={(e) => setFilter(prev => ({ 
                    ...prev, 
                    sensitiveData: e.target.value === 'all' ? 'all' : e.target.value === 'true'
                  }))}
                  className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                >
                  <option value="all">All</option>
                  <option value="true">Sensitive Only</option>
                  <option value="false">Non-Sensitive Only</option>
                </select>
              </div>
            )}

            <button
              onClick={exportAuditLogs}
              disabled={exportLoading}
              className="px-4 py-2 text-black bg-yellow-400 rounded-lg hover:bg-yellow-300 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {exportLoading && (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-4 h-4 border-2 border-black border-t-transparent rounded-full"
                />
              )}
              Export Logs
            </button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Audit Logs List */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700"
            >
              <div className="p-6 border-b border-gray-700">
                <h3 className="text-xl font-semibold text-white">Audit Events</h3>
                <p className="text-gray-400 text-sm">
                  {filteredLogs.length} events found
                </p>
              </div>

              <div className="max-h-[700px] overflow-y-auto">
                <AnimatePresence>
                  {filteredLogs.map((log) => {
                    const timestamp = formatTimestamp(log.timestamp);
                    const actionCategory = getActionCategory(log.action);
                    
                    return (
                      <motion.div
                        key={log.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className={`p-4 border-b border-gray-700 cursor-pointer transition-colors hover:bg-gray-700/30 ${
                          selectedLog?.id === log.id ? 'bg-gray-700/50' : ''
                        }`}
                        onClick={() => setSelectedLog(log)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <span className="text-lg">{getOutcomeIcon(log.outcome)}</span>
                            <div>
                              <div className="flex items-center space-x-2">
                                <span className="text-sm font-medium text-white">{log.action}</span>
                                <span className={`px-2 py-1 text-xs rounded-full ${actionCategory.color}`}>
                                  {actionCategory.category}
                                </span>
                                {log.sensitiveData && canAccessSensitiveData() && (
                                  <span className="px-2 py-1 text-xs bg-yellow-900 text-yellow-300 rounded-full">
                                    🔒 Sensitive
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-gray-400 mt-1">
                                {log.resource} • {log.resourceId}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-gray-400">{timestamp.relative}</p>
                            <p className="text-xs text-gray-500">{timestamp.time}</p>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-400">
                              {log.user?.name || 'Unknown User'}
                            </span>
                            <span className="text-xs text-gray-500">•</span>
                            <span className="text-xs text-gray-500">{log.ipAddress}</span>
                          </div>
                          <span className={`text-xs font-medium ${getOutcomeColor(log.outcome)}`}>
                            {log.outcome.toUpperCase()}
                          </span>
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            </motion.div>
          </div>

          {/* Log Details */}
          <div>
            <AnimatePresence mode="wait">
              {selectedLog ? (
                <motion.div
                  key={selectedLog.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700"
                >
                  <div className="p-6 border-b border-gray-700">
                    <h3 className="text-xl font-semibold text-white mb-2">Event Details</h3>
                    <p className="text-gray-400 text-sm">{selectedLog.action}</p>
                  </div>

                  <div className="p-6 space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-300 mb-2">Basic Information</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Event ID:</span>
                          <span className="text-white font-mono">{selectedLog.id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Timestamp:</span>
                          <span className="text-white">{formatTimestamp(selectedLog.timestamp).date} {formatTimestamp(selectedLog.timestamp).time}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Outcome:</span>
                          <span className={`font-medium ${getOutcomeColor(selectedLog.outcome)}`}>
                            {getOutcomeIcon(selectedLog.outcome)} {selectedLog.outcome.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Resource:</span>
                          <span className="text-white">{selectedLog.resource}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Resource ID:</span>
                          <span className="text-white font-mono">{selectedLog.resourceId}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-300 mb-2">User Information</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">User:</span>
                          <span className="text-white">{selectedLog.user?.name || 'Unknown'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Email:</span>
                          <span className="text-white">{selectedLog.user?.email || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Role:</span>
                          <span className="text-white">{selectedLog.user?.role?.replace(/_/g, ' ').toUpperCase() || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">IP Address:</span>
                          <span className="text-white font-mono">{selectedLog.ipAddress}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">User Agent:</span>
                          <span className="text-white text-xs break-all">{selectedLog.userAgent}</span>
                        </div>
                      </div>
                    </div>

                    {selectedLog.changes && Object.keys(selectedLog.changes).length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2">Changes</h4>
                        <div className="bg-gray-700 p-3 rounded text-xs">
                          <pre className="text-gray-300 whitespace-pre-wrap">
                            {JSON.stringify(selectedLog.changes, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}

                    {selectedLog.sensitiveData && (
                      <div className="bg-yellow-900/20 border border-yellow-600 p-3 rounded">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-yellow-300">🔒</span>
                          <span className="text-yellow-300 text-sm font-medium">Sensitive Data</span>
                        </div>
                        <p className="text-yellow-200 text-xs">
                          This event involved sensitive data processing. Access is restricted to authorized personnel only.
                        </p>
                      </div>
                    )}
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
                  <h3 className="text-lg font-medium text-white mb-2">Select an Event</h3>
                  <p className="text-gray-400 text-sm">
                    Click on an audit event from the list to view detailed information.
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