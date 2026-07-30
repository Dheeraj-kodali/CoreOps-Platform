'use client';

import React from 'react';
import { Bell, Globe, User, LogOut } from 'lucide-react';
import { logoutAdmin } from '../api/auth';

interface HeaderProps {
  user?: { full_name?: string; username?: string } | null;
  onLogout?: () => void;
}

export default function Header({ user, onLogout }: HeaderProps) {
  const handleLogoutClick = async () => {
    await logoutAdmin();
    if (onLogout) onLogout();
  };

  return (
    <header className="h-16 bg-white border-b border-[#D4AF37]/30 px-6 flex items-center justify-between shadow-sm sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <h1 className="font-serif text-lg font-bold text-[#2C1A11]">
          Sri Kalki Seva Alayam
        </h1>
        <span className="bg-[#D4AF37]/20 text-[#2C1A11] text-[10px] font-bold px-2 py-0.5 rounded-full border border-[#D4AF37]/40">
          Admin Console
        </span>
      </div>

      <div className="flex items-center space-x-4">
        {/* Language selector */}
        <button className="flex items-center space-x-1 text-xs font-semibold text-gray-600 hover:text-[#2C1A11] bg-gray-50 border border-gray-200 px-2.5 py-1.5 rounded-lg transition-colors">
          <Globe className="w-3.5 h-3.5 text-[#D4AF37]" />
          <span>English</span>
        </button>

        {/* Notifications badge */}
        <button className="p-1.5 text-gray-500 hover:text-[#2C1A11] relative rounded-lg hover:bg-gray-50 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
        </button>

        {/* User profile */}
        <div className="flex items-center space-x-3 pl-3 border-l border-gray-200">
          <div className="w-8 h-8 rounded-full bg-[#2C1A11] text-[#D4AF37] flex items-center justify-center font-bold text-xs shadow-sm">
            {user?.full_name ? user.full_name.charAt(0) : 'A'}
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-bold text-[#2C1A11] leading-none">
              {user?.full_name || 'Super Administrator'}
            </p>
            <p className="text-[10px] text-gray-500 mt-0.5">
              @{user?.username || 'admin'}
            </p>
          </div>

          <button
            onClick={handleLogoutClick}
            title="Sign Out"
            className="p-1.5 text-gray-400 hover:text-red-600 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
