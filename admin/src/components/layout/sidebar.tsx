'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  UserCheck,
  Building2,
  FileText,
  BarChart3,
  Bell,
  ShieldCheck,
  Settings,
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '../../providers/AuthProvider';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const { hasPermission, hasRole } = useAuth();

  const navigationItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, permission: null },
    { name: 'Visitors', href: '/visitors', icon: Users, permission: null },
    { name: 'Volunteers', href: '/volunteers', icon: UserCheck, permission: 'volunteers:read' },
    { name: 'Analytics', href: '/analytics', icon: BarChart3, permission: 'analytics:read' },
    { name: 'Reports', href: '/reports', icon: FileText, permission: 'reports:read' },
    { name: 'Users', href: '/users', icon: UserCheck, permission: 'users:read' },
    { name: 'Roles & Perms', href: '/roles', icon: ShieldCheck, permission: 'roles:read' },
    { name: 'Temple Config', href: '/temples', icon: Building2, permission: 'temple:read' },
    { name: 'Settings', href: '/settings', icon: Settings, permission: null },
    { name: 'Audit Logs', href: '/audit', icon: ShieldAlert, permission: 'audit:read' },
    { name: 'Notifications', href: '/notifications', icon: Bell, permission: null },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 z-40 h-screen transition-all duration-300 bg-[#1C1410] text-[#FAFAFA] border-r border-[#D4AF37]/30 flex flex-col ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Sidebar Header / Brand */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-[#D4AF37]/20">
        {!collapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#FF9933] flex items-center justify-center font-bold text-[#1C1410] text-xl shadow-md">
              🛕
            </div>
            <div>
              <h1 className="font-bold text-sm text-[#D4AF37] tracking-wider uppercase font-serif">Sri Kalki</h1>
              <p className="text-[10px] text-[#FAFAFA]/70 tracking-tight">Visitor Console</p>
            </div>
          </div>
        )}

        {collapsed && (
          <div className="mx-auto w-10 h-10 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#FF9933] flex items-center justify-center font-bold text-[#1C1410] text-xl shadow-md">
            🛕
          </div>
        )}

        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg text-[#D4AF37] hover:bg-[#2C1A11] transition-colors focus:outline-none"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>

      {/* Navigation Menu */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {navigationItems.map((item) => {
          // Check permission if specified
          if (item.permission && !hasPermission(item.permission) && !hasRole('SUPER_ADMIN')) {
            return null;
          }

          const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                isActive
                  ? 'bg-gradient-to-r from-[#D4AF37] to-[#B38F24] text-[#1C1410] font-semibold shadow-md'
                  : 'text-[#FAFAFA]/80 hover:bg-[#2C1A11] hover:text-[#D4AF37]'
              } ${collapsed ? 'justify-center' : ''}`}
            >
              <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-[#1C1410]' : 'text-[#D4AF37]'}`} />
              {!collapsed && <span className="ml-3 text-sm tracking-wide">{item.name}</span>}
            </Link>
          );
        })}
      </div>

      {/* Sidebar Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-[#D4AF37]/20 text-center text-xs text-[#FAFAFA]/50">
          <p className="text-[#D4AF37]">TVMS Enterprise SaaS</p>
          <p className="text-[10px] mt-0.5">v1.0.0 Architecture Freeze</p>
        </div>
      )}
    </aside>
  );
}
