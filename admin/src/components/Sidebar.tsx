'use client';

import React from 'react';
import {
  LayoutDashboard,
  Users,
  BarChart3,
  FileText,
  UserCheck,
  Bell,
  Settings,
  ShieldCheck,
  Building,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Live Dashboard', icon: LayoutDashboard },
    { id: 'visitors', label: 'Visitor Registry', icon: Users },
    { id: 'analytics', label: 'Demographics & Trends', icon: BarChart3 },
    { id: 'reports', label: 'Reports & Export', icon: FileText },
    { id: 'users', label: 'User & Role Control', icon: UserCheck },
    { id: 'notifications', label: 'Messaging & SMS', icon: Bell },
    { id: 'audit', label: 'Audit Logs', icon: ShieldCheck },
    { id: 'settings', label: 'System Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#2C1A11] text-white flex flex-col min-h-screen shadow-xl border-r border-[#D4AF37]/20">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#D4AF37]/20 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#D4AF37] to-[#997A15] flex items-center justify-center shadow-md">
          <Building className="w-5 h-5 text-[#2C1A11]" />
        </div>
        <div>
          <h2 className="font-serif text-sm font-bold text-[#D4AF37] leading-tight">
            Sri Kalki Seva
          </h2>
          <p className="text-[10px] text-amber-200/70">Visitor Management System</p>
        </div>
      </div>

      {/* Menu Options */}
      <nav className="flex-1 p-3 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-[#D4AF37] text-[#2C1A11] shadow-md font-bold'
                  : 'text-amber-100/80 hover:bg-white/10 hover:text-white'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-[#2C1A11]' : 'text-[#D4AF37]'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-[#D4AF37]/20 text-[10px] text-amber-200/50 text-center">
        Enterprise Build v1.2.0
      </div>
    </aside>
  );
}
