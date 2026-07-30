'use client';

import React, { useState } from 'react';
import { ShieldCheck, Plus, Edit2, Trash2, Users, Lock } from 'lucide-react';
import { PermissionMatrix } from '../../../features/iam/permission-matrix';
import { Role } from '../../../types/user';
import { PermissionGuard } from '../../../components/shared/permission-guard';

const DEFAULT_ROLES: Role[] = [
  {
    id: 'r1',
    name: 'SUPER_ADMIN',
    code: 'super_admin',
    description: 'Full multi-tenant system governance, multi-temple administration, and security audit control.',
    permissions: ['visitors:manage', 'reports:manage', 'analytics:manage', 'users:manage', 'roles:manage', 'settings:manage'],
    user_count: 2,
    is_system: true,
  },
  {
    id: 'r2',
    name: 'TEMPLE_ADMIN',
    code: 'temple_admin',
    description: 'Executive administrator for temple operations, reports, user assignments, and volunteer governance.',
    permissions: ['visitors:manage', 'reports:manage', 'analytics:read', 'users:manage', 'roles:read'],
    user_count: 5,
    is_system: true,
  },
  {
    id: 'r3',
    name: 'MANAGER',
    code: 'manager',
    description: 'Temple operations supervisor managing visitor queues, reports, and gate throughput.',
    permissions: ['visitors:update', 'visitors:read', 'reports:read', 'analytics:read'],
    user_count: 8,
    is_system: true,
  },
  {
    id: 'r4',
    name: 'VOLUNTEER',
    code: 'volunteer',
    description: 'Gate check-in operator, mobile check-in app user, and QR scanner staff.',
    permissions: ['visitors:create', 'visitors:read'],
    user_count: 45,
    is_system: true,
  },
  {
    id: 'r5',
    name: 'RECEPTION',
    code: 'reception',
    description: 'Front desk registration and visitor check-in counter staff.',
    permissions: ['visitors:create', 'visitors:read', 'visitors:update'],
    user_count: 12,
    is_system: true,
  },
  {
    id: 'r6',
    name: 'VIEWER',
    code: 'viewer',
    description: 'Read-only access for temple trust board members and external auditors.',
    permissions: ['visitors:read', 'reports:read', 'analytics:read'],
    user_count: 15,
    is_system: true,
  },
];

export default function RoleManagementPage() {
  const [roles, setRoles] = useState<Role[]>(DEFAULT_ROLES);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [roleName, setRoleName] = useState('');
  const [roleDesc, setRoleDesc] = useState('');
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  const handleOpenCreate = () => {
    setSelectedRole(null);
    setRoleName('');
    setRoleDesc('');
    setSelectedPermissions([]);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (role: Role) => {
    setSelectedRole(role);
    setRoleName(role.name);
    setRoleDesc(role.description);
    const permissionCodes = (role.permissions || []).map((p) => (typeof p === 'string' ? p : p.code));
    setSelectedPermissions(permissionCodes);
    setIsModalOpen(true);
  };

  const handleSaveRole = (e: React.FormEvent) => {
    e.preventDefault();
    if (!roleName) return;

    if (selectedRole) {
      setRoles(
        roles.map((r) =>
          r.id === selectedRole.id ? { ...r, name: roleName, description: roleDesc, permissions: selectedPermissions } : r
        )
      );
    } else {
      const newRole: Role = {
        id: `r_${Date.now()}`,
        name: roleName,
        code: roleName.toLowerCase().replace(/\s+/g, '_'),
        description: roleDesc,
        permissions: selectedPermissions,
        user_count: 0,
        is_system: false,
      };
      setRoles([...roles, newRole]);
    }
    setIsModalOpen(false);
  };

  const handleDeleteRole = (id: string, name: string) => {
    if (confirm(`Are you sure you want to delete role '${name}'?`)) {
      setRoles(roles.filter((r) => r.id !== id));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner & Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
            Role Management & Policy Matrix
          </h1>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">
            RBAC System Roles, Custom Security Policies & Fine-Grained Module Matrix
          </p>
        </div>

        <PermissionGuard permission="roles:create">
          <button
            onClick={handleOpenCreate}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] text-xs font-bold shadow-md hover:brightness-110 transition-all flex items-center space-x-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Create Custom Role</span>
          </button>
        </PermissionGuard>
      </div>

      {/* Role Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {roles.map((role) => (
          <div
            key={role.id}
            className="p-5 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/30 shadow-sm space-y-4 flex flex-col justify-between"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-5 h-5 text-[#D4AF37]" />
                  <h3 className="font-bold font-serif text-base text-gray-900 dark:text-[#D4AF37]">{role.name}</h3>
                </div>
                {role.is_system && (
                  <span className="px-2 py-0.5 rounded-full bg-[#D4AF37]/20 border border-[#D4AF37]/40 text-[#D4AF37] font-bold text-[9px] uppercase tracking-wider">
                    System Default
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 leading-relaxed">{role.description}</p>
            </div>

            <div className="pt-3 border-t border-gray-100 dark:border-[#D4AF37]/20 flex items-center justify-between text-xs">
              <span className="flex items-center text-gray-500">
                <Users className="w-3.5 h-3.5 mr-1 text-[#D4AF37]" />
                {role.user_count || 0} Assigned User(s)
              </span>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleOpenEdit(role)}
                  className="p-1.5 rounded-lg text-[#D4AF37] hover:bg-gray-100 dark:hover:bg-[#2C1A11] transition-colors"
                  title="Edit Role & Permissions"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                {!role.is_system && (
                  <button
                    onClick={() => handleDeleteRole(role.id, role.name)}
                    className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                    title="Delete Role"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Role & Permission Matrix Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
          <div className="max-w-4xl w-full bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] rounded-3xl shadow-2xl border border-[#D4AF37]/40 p-6 space-y-5 relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-[#FAFAFA]"
            >
              ✕
            </button>

            <div>
              <h3 className="text-lg font-bold font-serif text-[#D4AF37]">
                {selectedRole ? `Edit Role: ${selectedRole.name}` : 'Create Custom Role'}
              </h3>
              <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-0.5">
                Define role title, description, and assign module-level access permissions.
              </p>
            </div>

            <form onSubmit={handleSaveRole} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold">Role Name *</label>
                  <input
                    type="text"
                    required
                    value={roleName}
                    onChange={(e) => setRoleName(e.target.value)}
                    placeholder="e.g. SEVA_COORDINATOR"
                    className="w-full mt-1 px-3.5 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold">Description</label>
                  <input
                    type="text"
                    value={roleDesc}
                    onChange={(e) => setRoleDesc(e.target.value)}
                    placeholder="Role responsibilities and scope"
                    className="w-full mt-1 px-3.5 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
                  />
                </div>
              </div>

              {/* Module Permission Matrix */}
              <div className="space-y-2 pt-2">
                <label className="text-xs font-semibold text-[#D4AF37] uppercase tracking-wider">
                  Module Permission Policy Matrix
                </label>
                <PermissionMatrix
                  selectedPermissions={selectedPermissions}
                  onChange={setSelectedPermissions}
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md hover:brightness-110 transition-all"
              >
                Save Role & Policy Matrix
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
