'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, UserPlus, Shield, KeyRound, Laptop, Eye, Trash2, CheckCircle2, XCircle, RefreshCw, Mail, Phone, Calendar } from 'lucide-react';
import { UserRepository } from '../../../repositories/user-repository';
import { useDebounce } from '../../../hooks/use-debounce';
import { TableSkeleton } from '../../../components/shared/loading-skeleton';
import { PermissionGuard } from '../../../components/shared/permission-guard';
import { SessionManagementPanel } from '../../../features/iam/session-management-panel';
import { PasswordManagementModal } from '../../../features/iam/password-management-modal';
import { User, UserStatus } from '../../../types/user';

export default function UserManagementPage() {
  const queryClient = useQueryClient();

  // Search & Filter States
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 400);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [page, setPage] = useState(1);
  const [limit] = useState(20);

  // Selected States & Modals
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Form States for Create User
  const [newUsername, setNewUsername] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newFullName, setNewFullName] = useState('');
  const [newRole, setNewRole] = useState('TEMPLE_ADMIN');

  // TanStack Query for User List
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['users', debouncedSearch, statusFilter, page, limit],
    queryFn: () =>
      UserRepository.getUsers({
        search: debouncedSearch || undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        page,
        limit,
      }),
  });

  // Toggle User Active Status Mutation
  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: UserStatus }) => UserRepository.updateUser(id, { status } as any),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const handleToggleStatus = (user: User) => {
    const nextStatus: UserStatus = user.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    if (confirm(`Are you sure you want to change user status for '${user.username}' to ${nextStatus}?`)) {
      statusMutation.mutate({ id: user.id, status: nextStatus });
    }
  };

  const handleCreateUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername || !newEmail || !newFullName) return;

    try {
      await UserRepository.createUser({
        username: newUsername,
        email: newEmail,
        full_name: newFullName,
        roles: [newRole],
      } as any);

      setNewUsername('');
      setNewEmail('');
      setNewFullName('');
      setIsCreateModalOpen(false);
      refetch();
    } catch (err: any) {
      alert(err?.message || 'Failed to create user.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
            Identity & Access Management (IAM)
          </h1>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">
            Enterprise User Accounts, Multi-Tenant Roles & Security Session Governance
          </p>
        </div>

        <PermissionGuard permission="users:create">
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] text-xs font-bold shadow-md hover:brightness-110 transition-all flex items-center space-x-1.5"
          >
            <UserPlus className="w-4 h-4" />
            <span>Create User Account</span>
          </button>
        </PermissionGuard>
      </div>

      {/* Advanced Search & Filter Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search username, email, full name..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            >
              <option value="ALL">All Account Statuses</option>
              <option value="ACTIVE">Active Users</option>
              <option value="INACTIVE">Inactive Users</option>
              <option value="SUSPENDED">Suspended Users</option>
            </select>
          </div>

          <button
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('ALL');
              setPage(1);
            }}
            className="py-2 px-3 rounded-xl bg-gray-100 dark:bg-[#2C1A11] text-xs font-semibold text-gray-600 dark:text-[#FAFAFA]/70 hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-colors flex items-center justify-center space-x-1"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset Filters</span>
          </button>
        </div>
      </div>

      {/* User Accounts Data Table */}
      <div className="rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6">
            <TableSkeleton rows={6} />
          </div>
        ) : isError ? (
          <div className="p-8 text-center text-red-500 text-xs">
            Failed to load user account directory.
          </div>
        ) : !data || data.length === 0 ? (
          <div className="p-12 text-center text-gray-500 dark:text-gray-400 text-xs space-y-2">
            <p className="font-semibold text-sm text-gray-700 dark:text-[#FAFAFA]">No User Accounts Found</p>
            <p>Try adjusting your search terms or status filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 dark:bg-[#2C1A11] border-b border-gray-200 dark:border-[#D4AF37]/20 text-gray-500 dark:text-[#D4AF37] uppercase font-semibold">
                  <th className="py-3.5 px-4">User Account</th>
                  <th className="py-3.5 px-4">Email Address</th>
                  <th className="py-3.5 px-4">Assigned Roles</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Assigned Temple</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-[#D4AF37]/10">
                {data.map((usr) => (
                  <tr key={usr.id} className="hover:bg-gray-50/50 dark:hover:bg-[#2C1A11]/40 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-gray-900 dark:text-[#FAFAFA]">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold flex items-center justify-center text-xs">
                          {usr.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p>{usr.full_name || usr.username}</p>
                          <p className="text-[10px] text-gray-400 font-mono">@{usr.username}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-gray-600 dark:text-gray-300 font-mono">{usr.email}</td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {usr.roles.map((r, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/30 text-[10px] font-bold"
                          >
                            {typeof r === 'string' ? r : r.name}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <button
                        onClick={() => handleToggleStatus(usr)}
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold flex items-center space-x-1 ${
                          usr.status === 'ACTIVE'
                            ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300'
                            : 'bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-300'
                        }`}
                      >
                        {usr.status === 'ACTIVE' ? <CheckCircle2 className="w-3 h-3 text-emerald-500" /> : <XCircle className="w-3 h-3 text-red-500" />}
                        <span>{usr.status}</span>
                      </button>
                    </td>
                    <td className="py-3.5 px-4 text-gray-600 dark:text-gray-300">
                      {usr.temple_name || 'Sri Kalki Seva Alayam'}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => {
                            setSelectedUser(usr);
                            setIsPasswordModalOpen(true);
                          }}
                          className="p-1.5 rounded-lg text-[#D4AF37] hover:bg-gray-100 dark:hover:bg-[#2C1A11] transition-colors"
                          title="Reset User Password"
                        >
                          <KeyRound className="w-4 h-4" />
                        </button>

                        <button
                          onClick={() => {
                            setSelectedUser(usr);
                            setIsDrawerOpen(true);
                          }}
                          className="p-1.5 rounded-lg text-[#D4AF37] hover:bg-gray-100 dark:hover:bg-[#2C1A11] transition-colors"
                          title="View Profile & Active Sessions"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* User Profile & Sessions Drawer */}
      {isDrawerOpen && selectedUser && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end animate-fadeIn">
          <div className="w-full max-w-lg bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] h-full shadow-2xl border-l border-[#D4AF37]/30 flex flex-col justify-between overflow-y-auto p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-gray-200 dark:border-[#D4AF37]/20 pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xl flex items-center justify-center">
                  {selectedUser.username.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h3 className="font-bold font-serif text-lg text-[#D4AF37]">{selectedUser.full_name || selectedUser.username}</h3>
                  <p className="text-xs text-gray-500 font-mono">@{selectedUser.username}</p>
                </div>
              </div>
              <button onClick={() => setIsDrawerOpen(false)} className="text-gray-400 hover:text-[#FAFAFA]">
                ✕
              </button>
            </div>

            {/* User Session Management Panel */}
            <SessionManagementPanel
              sessions={selectedUser.active_sessions || [
                { id: 's1', token_jti: 'jti_1', ip_address: '127.0.0.1', user_agent: 'Chrome 124 / Windows', login_time: 'Today 09:30 AM', last_activity: '2 mins ago', is_current: true }
              ]}
              onRevokeSession={(jti) => alert(`Revoked session token JTI: ${jti}`)}
              onRevokeAllSessions={() => alert(`All active sessions revoked for ${selectedUser.username}`)}
            />
          </div>
        </div>
      )}

      {/* Password Management Modal */}
      {selectedUser && (
        <PasswordManagementModal
          userId={selectedUser.id}
          username={selectedUser.username}
          isOpen={isPasswordModalOpen}
          onClose={() => setIsPasswordModalOpen(false)}
        />
      )}

      {/* Create User Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
          <div className="max-w-md w-full bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] rounded-3xl shadow-2xl border border-[#D4AF37]/40 p-6 space-y-4 relative">
            <button onClick={() => setIsCreateModalOpen(false)} className="absolute top-4 right-4 text-gray-400 hover:text-[#FAFAFA]">
              ✕
            </button>

            <div>
              <h3 className="text-lg font-bold font-serif text-[#D4AF37]">Create New User Account</h3>
              <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-1">Provision a new executive user or volunteer account.</p>
            </div>

            <form onSubmit={handleCreateUserSubmit} className="space-y-3">
              <div>
                <label className="text-xs font-semibold">Username *</label>
                <input
                  type="text"
                  required
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="e.g. j.doe"
                  className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold">Email Address *</label>
                <input
                  type="email"
                  required
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="jdoe@kalkiseva.org"
                  className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold">Full Name *</label>
                <input
                  type="text"
                  required
                  value={newFullName}
                  onChange={(e) => setNewFullName(e.target.value)}
                  placeholder="e.g. John Doe"
                  className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold">Assign System Role</label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
                >
                  <option value="SUPER_ADMIN">Super Admin</option>
                  <option value="TEMPLE_ADMIN">Temple Admin</option>
                  <option value="MANAGER">Manager</option>
                  <option value="VOLUNTEER">Volunteer</option>
                  <option value="RECEPTION">Reception</option>
                  <option value="VIEWER">Viewer</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 mt-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md hover:brightness-110 transition-all"
              >
                Provision User Account
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
