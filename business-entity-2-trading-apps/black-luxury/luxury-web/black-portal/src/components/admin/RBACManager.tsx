/**
 * RBAC (Role-Based Access Control) Manager
 * Comprehensive interface for managing user roles and permissions
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  UserRole,
  Permission,
  ROLE_PERMISSIONS,
} from '@/types/service-management';

interface RolePermissionMatrix {
  role: UserRole;
  permissions: Permission[];
  userCount: number;
  description: string;
}

interface UserWithActions extends User {
  actions?: {
    canEdit: boolean;
    canDelete: boolean;
    canPromote: boolean;
    canDemote: boolean;
  };
}

interface RBACManagerProps {
  currentUser: User;
}

export const RBACManager: React.FC<RBACManagerProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<UserWithActions[]>([]);
  const [roleMatrix, setRoleMatrix] = useState<RolePermissionMatrix[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserWithActions | null>(null);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'users' | 'roles' | 'permissions'>('users');

  useEffect(() => {
    fetchRBACData();
  }, []);

  const fetchRBACData = async () => {
    try {
      setLoading(true);
      
      // Fetch users with role information
      const usersResponse = await fetch('/api/admin/rbac/users');
      const usersData = await usersResponse.json();
      
      // Add action permissions based on current user role
      const usersWithActions = usersData.map((user: User) => ({
        ...user,
        actions: getUserActions(user),
      }));
      
      setUsers(usersWithActions);

      // Generate role permission matrix
      const matrix = Object.entries(ROLE_PERMISSIONS).map(([role, permissions]) => ({
        role: role as UserRole,
        permissions,
        userCount: usersData.filter((u: User) => u.role === role).length,
        description: getRoleDescription(role as UserRole),
      }));
      
      setRoleMatrix(matrix);
      
    } catch (error) {
      console.error('Failed to fetch RBAC data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUserActions = (user: User) => {
    const isSelfEdit = user.id === currentUser.id;
    const isHigherRole = getRoleHierarchy(user.role) >= getRoleHierarchy(currentUser.role);
    
    return {
      canEdit: currentUser.role === UserRole.CEO || currentUser.role === UserRole.ADMIN || isSelfEdit,
      canDelete: currentUser.role === UserRole.CEO && !isSelfEdit && !isHigherRole,
      canPromote: (currentUser.role === UserRole.CEO || currentUser.role === UserRole.ADMIN) && !isHigherRole,
      canDemote: (currentUser.role === UserRole.CEO || currentUser.role === UserRole.ADMIN) && !isHigherRole,
    };
  };

  const getRoleHierarchy = (role: UserRole): number => {
    const hierarchy = {
      [UserRole.CEO]: 10,
      [UserRole.CRO]: 9,
      [UserRole.CCO]: 9,
      [UserRole.INVESTMENT_HEAD]: 8,
      [UserRole.CONCIERGE_HEAD]: 8,
      [UserRole.SECURITY_HEAD]: 8,
      [UserRole.SENIOR_INVESTMENT_ANALYST]: 7,
      [UserRole.SENIOR_COMPLIANCE_ANALYST]: 7,
      [UserRole.SENIOR_SECURITY_ANALYST]: 7,
      [UserRole.INVESTMENT_ANALYST]: 6,
      [UserRole.COMPLIANCE_ANALYST]: 6,
      [UserRole.SECURITY_ANALYST]: 6,
      [UserRole.SERVICE_COORDINATOR]: 5,
      [UserRole.ADMIN]: 4,
      [UserRole.READONLY]: 1,
    };
    return hierarchy[role] || 0;
  };

  const getRoleDescription = (role: UserRole): string => {
    const descriptions = {
      [UserRole.CEO]: 'Chief Executive Officer - Full system access and ultimate approval authority',
      [UserRole.CRO]: 'Chief Risk Officer - Risk management and assessment oversight',
      [UserRole.CCO]: 'Chief Compliance Officer - Regulatory compliance and legal oversight',
      [UserRole.INVESTMENT_HEAD]: 'Investment Department Head - Investment strategy and fund management',
      [UserRole.CONCIERGE_HEAD]: 'Concierge Services Head - Luxury service coordination and vendor management',
      [UserRole.SECURITY_HEAD]: 'Security Department Head - Security protocols and threat assessment',
      [UserRole.SENIOR_INVESTMENT_ANALYST]: 'Senior Investment Analyst - Advanced investment analysis and research',
      [UserRole.SENIOR_COMPLIANCE_ANALYST]: 'Senior Compliance Analyst - Advanced compliance monitoring',
      [UserRole.SENIOR_SECURITY_ANALYST]: 'Senior Security Analyst - Advanced security assessments',
      [UserRole.INVESTMENT_ANALYST]: 'Investment Analyst - Investment research and analysis',
      [UserRole.COMPLIANCE_ANALYST]: 'Compliance Analyst - Regulatory compliance monitoring',
      [UserRole.SECURITY_ANALYST]: 'Security Analyst - Security monitoring and assessment',
      [UserRole.SERVICE_COORDINATOR]: 'Service Coordinator - Service proposal coordination',
      [UserRole.ADMIN]: 'Administrator - User and system administration',
      [UserRole.READONLY]: 'Read-Only User - Limited viewing access',
    };
    return descriptions[role] || 'Role description not available';
  };

  const handleRoleChange = async (userId: string, newRole: UserRole) => {
    try {
      await fetch(`/api/admin/rbac/users/${userId}/role`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole, changedBy: currentUser.id }),
      });
      
      await fetchRBACData();
    } catch (error) {
      console.error('Failed to update user role:', error);
    }
  };

  const handleUserToggle = async (userId: string, isActive: boolean) => {
    try {
      await fetch(`/api/admin/rbac/users/${userId}/toggle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ isActive, changedBy: currentUser.id }),
      });
      
      await fetchRBACData();
    } catch (error) {
      console.error('Failed to toggle user status:', error);
    }
  };

  const getRoleColor = (role: UserRole): string => {
    const colors = {
      [UserRole.CEO]: 'bg-purple-100 text-purple-800 border-purple-200',
      [UserRole.CRO]: 'bg-red-100 text-red-800 border-red-200',
      [UserRole.CCO]: 'bg-blue-100 text-blue-800 border-blue-200',
      [UserRole.INVESTMENT_HEAD]: 'bg-green-100 text-green-800 border-green-200',
      [UserRole.CONCIERGE_HEAD]: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      [UserRole.SECURITY_HEAD]: 'bg-orange-100 text-orange-800 border-orange-200',
      [UserRole.SENIOR_INVESTMENT_ANALYST]: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      [UserRole.SENIOR_COMPLIANCE_ANALYST]: 'bg-cyan-100 text-cyan-800 border-cyan-200',
      [UserRole.SENIOR_SECURITY_ANALYST]: 'bg-amber-100 text-amber-800 border-amber-200',
      [UserRole.INVESTMENT_ANALYST]: 'bg-lime-100 text-lime-800 border-lime-200',
      [UserRole.COMPLIANCE_ANALYST]: 'bg-teal-100 text-teal-800 border-teal-200',
      [UserRole.SECURITY_ANALYST]: 'bg-rose-100 text-rose-800 border-rose-200',
      [UserRole.SERVICE_COORDINATOR]: 'bg-violet-100 text-violet-800 border-violet-200',
      [UserRole.ADMIN]: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      [UserRole.READONLY]: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[role] || 'bg-gray-100 text-gray-800 border-gray-200';
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
          <h1 className="text-4xl font-bold text-white mb-2">RBAC Management</h1>
          <p className="text-gray-400">
            Secure role-based access control for service vetting system
          </p>
        </motion.div>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex space-x-1 bg-gray-800 p-1 rounded-lg">
            {[
              { id: 'users', label: 'Users', icon: '👥' },
              { id: 'roles', label: 'Roles', icon: '🎭' },
              { id: 'permissions', label: 'Permissions', icon: '🔐' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-yellow-400 text-black font-medium'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          {activeTab === 'users' && (
            <motion.div
              key="users"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Users Management */}
              <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700">
                <div className="p-6 border-b border-gray-700 flex justify-between items-center">
                  <div>
                    <h3 className="text-xl font-semibold text-white">User Management</h3>
                    <p className="text-gray-400 text-sm">{users.length} users in the system</p>
                  </div>
                  <button
                    onClick={() => setShowCreateUser(true)}
                    className="px-4 py-2 text-black bg-yellow-400 rounded-lg hover:bg-yellow-300 transition-colors font-medium"
                  >
                    Add User
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-900">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Role
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Department
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Last Login
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {users.map((user) => (
                        <tr key={user.id} className="hover:bg-gray-700/50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-full flex items-center justify-center text-black font-bold">
                                {user.name.charAt(0).toUpperCase()}
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-white">{user.name}</div>
                                <div className="text-sm text-gray-400">{user.email}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getRoleColor(user.role)}`}>
                              {user.role.replace(/_/g, ' ').toUpperCase()}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {user.department}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className={`w-2 h-2 rounded-full mr-2 ${user.isActive ? 'bg-green-400' : 'bg-red-400'}`} />
                              <span className={`text-sm ${user.isActive ? 'text-green-400' : 'text-red-400'}`}>
                                {user.isActive ? 'Active' : 'Inactive'}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                            {new Date(user.lastLogin).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex space-x-2">
                              {user.actions?.canEdit && (
                                <button
                                  onClick={() => setSelectedUser(user)}
                                  className="text-yellow-400 hover:text-yellow-300 transition-colors"
                                >
                                  Edit
                                </button>
                              )}
                              {user.actions?.canPromote && (
                                <button className="text-green-400 hover:text-green-300 transition-colors">
                                  Promote
                                </button>
                              )}
                              {user.actions?.canDemote && (
                                <button className="text-orange-400 hover:text-orange-300 transition-colors">
                                  Demote
                                </button>
                              )}
                              {user.actions?.canDelete && (
                                <button className="text-red-400 hover:text-red-300 transition-colors">
                                  Delete
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'roles' && (
            <motion.div
              key="roles"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Role Matrix */}
              <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700">
                <div className="p-6 border-b border-gray-700">
                  <h3 className="text-xl font-semibold text-white">Role Hierarchy</h3>
                  <p className="text-gray-400 text-sm">Overview of all roles and their permission counts</p>
                </div>

                <div className="p-6 space-y-4">
                  {roleMatrix
                    .sort((a, b) => getRoleHierarchy(b.role) - getRoleHierarchy(a.role))
                    .map((roleData) => (
                      <div
                        key={roleData.role}
                        className="bg-gray-700 p-4 rounded-lg border-l-4 border-yellow-400"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full border ${getRoleColor(roleData.role)}`}>
                                {roleData.role.replace(/_/g, ' ').toUpperCase()}
                              </span>
                              <span className="text-sm text-gray-400">
                                {roleData.userCount} user{roleData.userCount !== 1 ? 's' : ''}
                              </span>
                            </div>
                            <p className="text-sm text-gray-300 mb-3">{roleData.description}</p>
                            <div className="flex flex-wrap gap-1">
                              {roleData.permissions.slice(0, 5).map((permission) => (
                                <span
                                  key={permission}
                                  className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded"
                                >
                                  {permission.replace(/_/g, ' ')}
                                </span>
                              ))}
                              {roleData.permissions.length > 5 && (
                                <span className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded">
                                  +{roleData.permissions.length - 5} more
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-white">
                              {roleData.permissions.length}
                            </div>
                            <div className="text-xs text-gray-400">permissions</div>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'permissions' && (
            <motion.div
              key="permissions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Permission Matrix */}
              <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-gray-700">
                <div className="p-6 border-b border-gray-700">
                  <h3 className="text-xl font-semibold text-white">Permission Matrix</h3>
                  <p className="text-gray-400 text-sm">Comprehensive view of all permissions by role</p>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-900">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Permission
                        </th>
                        {Object.keys(ROLE_PERMISSIONS).map((role) => (
                          <th key={role} className="px-3 py-3 text-center text-xs font-medium text-gray-300 uppercase tracking-wider">
                            {role.replace(/_/g, ' ')}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {Object.values(Permission).map((permission) => (
                        <tr key={permission} className="hover:bg-gray-700/50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-white">
                              {permission.replace(/_/g, ' ').toUpperCase()}
                            </div>
                          </td>
                          {Object.entries(ROLE_PERMISSIONS).map(([role, permissions]) => (
                            <td key={role} className="px-3 py-4 text-center">
                              {permissions.includes(permission) ? (
                                <span className="text-green-400 text-lg">✓</span>
                              ) : (
                                <span className="text-gray-600 text-lg">✗</span>
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* User Edit Modal */}
        <AnimatePresence>
          {selectedUser && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
              onClick={() => setSelectedUser(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-gray-800 p-6 rounded-lg border border-gray-700 max-w-md w-full m-4"
                onClick={(e) => e.stopPropagation()}
              >
                <h3 className="text-xl font-semibold text-white mb-4">Edit User</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Role
                    </label>
                    <select
                      value={selectedUser.role}
                      onChange={(e) => handleRoleChange(selectedUser.id, e.target.value as UserRole)}
                      className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    >
                      {Object.values(UserRole).map((role) => (
                        <option key={role} value={role}>
                          {role.replace(/_/g, ' ').toUpperCase()}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="isActive"
                      checked={selectedUser.isActive}
                      onChange={(e) => handleUserToggle(selectedUser.id, e.target.checked)}
                      className="w-4 h-4 text-yellow-600 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500"
                    />
                    <label htmlFor="isActive" className="ml-2 text-sm text-gray-300">
                      Active User
                    </label>
                  </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    onClick={() => setSelectedUser(null)}
                    className="px-4 py-2 text-gray-300 border border-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => setSelectedUser(null)}
                    className="px-4 py-2 text-black bg-yellow-400 rounded-lg hover:bg-yellow-300 transition-colors font-medium"
                  >
                    Save Changes
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};