'use client';

import React from 'react';
import { PermissionAction, PermissionModule } from '../../types/user';

interface PermissionMatrixProps {
  selectedPermissions: string[];
  onChange: (permissions: string[]) => void;
  disabled?: boolean;
}

const MODULES: { id: PermissionModule; label: string }[] = [
  { id: 'visitors', label: 'Visitor Management' },
  { id: 'reports', label: 'Reporting & Export Engine' },
  { id: 'analytics', label: 'Analytics Command Portal' },
  { id: 'users', label: 'User IAM Management' },
  { id: 'roles', label: 'Role & Policy Matrix' },
  { id: 'settings', label: 'Temple System Settings' },
  { id: 'notifications', label: 'Notification Center' },
  { id: 'sync', label: 'Offline Sync Pipeline' },
];

const ACTIONS: PermissionAction[] = ['read', 'create', 'update', 'delete', 'approve', 'export', 'manage'];

export function PermissionMatrix({ selectedPermissions, onChange, disabled = false }: PermissionMatrixProps) {
  const togglePermission = (code: string) => {
    if (disabled) return;
    if (selectedPermissions.includes(code)) {
      onChange(selectedPermissions.filter((p) => p !== code));
    } else {
      onChange([...selectedPermissions, code]);
    }
  };

  const toggleModuleAll = (module: PermissionModule) => {
    if (disabled) return;
    const moduleCodes = ACTIONS.map((a) => `${module}:${a}`);
    const allSelected = moduleCodes.every((code) => selectedPermissions.includes(code));

    if (allSelected) {
      onChange(selectedPermissions.filter((p) => !moduleCodes.includes(p)));
    } else {
      const merged = Array.from(new Set([...selectedPermissions, ...moduleCodes]));
      onChange(merged);
    }
  };

  return (
    <div className="rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/30 shadow-sm overflow-hidden text-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 dark:bg-[#2C1A11] border-b border-gray-200 dark:border-[#D4AF37]/20 text-gray-500 dark:text-[#D4AF37] uppercase font-semibold text-[11px]">
              <th className="py-3 px-4 min-w-[160px]">Module / Entity</th>
              {ACTIONS.map((action) => (
                <th key={action} className="py-3 px-2 text-center capitalize min-w-[70px]">
                  {action}
                </th>
              ))}
              <th className="py-3 px-3 text-center">Toggle All</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-[#D4AF37]/10">
            {MODULES.map((mod) => {
              const moduleCodes = ACTIONS.map((a) => `${mod.id}:${a}`);
              const allChecked = moduleCodes.every((code) => selectedPermissions.includes(code));

              return (
                <tr key={mod.id} className="hover:bg-gray-50/50 dark:hover:bg-[#2C1A11]/40 transition-colors">
                  <td className="py-3 px-4 font-semibold text-gray-800 dark:text-[#FAFAFA]">{mod.label}</td>
                  {ACTIONS.map((action) => {
                    const code = `${mod.id}:${action}`;
                    const isChecked = selectedPermissions.includes(code);

                    return (
                      <td key={action} className="py-3 px-2 text-center">
                        <input
                          type="checkbox"
                          disabled={disabled}
                          checked={isChecked}
                          onChange={() => togglePermission(code)}
                          className="rounded border-[#D4AF37]/40 bg-gray-50 dark:bg-[#1C1410] text-[#D4AF37] focus:ring-[#D4AF37]"
                        />
                      </td>
                    );
                  })}
                  <td className="py-3 px-3 text-center">
                    <button
                      type="button"
                      disabled={disabled}
                      onClick={() => toggleModuleAll(mod.id)}
                      className="text-[10px] text-[#D4AF37] hover:underline font-semibold"
                    >
                      {allChecked ? 'Deselect' : 'Select All'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
