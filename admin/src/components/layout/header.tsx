'use client';

import React, { useState } from 'react';
import { Search, Bell, Sun, Moon, User as UserIcon, LogOut, Globe } from 'lucide-react';
import { useAuth } from '../../providers/AuthProvider';
import { useTheme } from '../../providers/ThemeProvider';

export function Header() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [lang, setLang] = useState<'EN' | 'TE'>('EN');

  return (
    <header className="h-16 bg-white dark:bg-[#1C1410] border-b border-[#D4AF37]/25 px-6 flex items-center justify-between sticky top-0 z-30 shadow-sm transition-colors">
      {/* Quick Global Command Search */}
      <div className="relative w-72">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search visitors, phone, village..."
          className="w-full pl-9 pr-4 py-1.5 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37] transition-all"
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] bg-gray-200 dark:bg-[#3D2519] px-1.5 py-0.5 rounded text-gray-500 font-mono">
          ⌘K
        </span>
      </div>

      {/* Header Actions */}
      <div className="flex items-center space-x-3">
        {/* Language Switcher */}
        <button
          onClick={() => setLang(lang === 'EN' ? 'TE' : 'EN')}
          className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-gray-700 dark:text-[#FAFAFA] hover:bg-gray-100 dark:hover:bg-[#2C1A11] transition-colors border border-gray-200 dark:border-[#D4AF37]/30"
          title="Switch Language (English / Telugu)"
        >
          <Globe className="w-3.5 h-3.5 text-[#D4AF37]" />
          <span>{lang}</span>
        </button>

        {/* Theme Switcher Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-gray-700 dark:text-[#FAFAFA] hover:bg-gray-100 dark:hover:bg-[#2C1A11] transition-colors border border-gray-200 dark:border-[#D4AF37]/30"
          title="Toggle Dark/Light Mode"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-[#D4AF37]" /> : <Moon className="w-4 h-4 text-gray-600" />}
        </button>

        {/* Notification Bell Badge */}
        <div className="relative">
          <button className="p-2 rounded-lg text-gray-700 dark:text-[#FAFAFA] hover:bg-gray-100 dark:hover:bg-[#2C1A11] transition-colors border border-gray-200 dark:border-[#D4AF37]/30">
            <Bell className="w-4 h-4 text-gray-600 dark:text-[#D4AF37]" />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#FF9933] ring-2 ring-white dark:ring-[#1C1410]"></span>
          </button>
        </div>

        {/* User Profile Menu & Logout */}
        <div className="flex items-center space-x-2 pl-2 border-l border-gray-200 dark:border-[#D4AF37]/30">
          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-[#D4AF37] to-[#FF9933] flex items-center justify-center text-[#1C1410] font-bold text-xs shadow-sm">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'A'}
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-gray-800 dark:text-[#FAFAFA] leading-tight">{user?.full_name || 'Admin User'}</p>
            <p className="text-[10px] text-gray-500 dark:text-[#D4AF37] leading-tight">
              {user?.roles?.[0]?.name || 'SUPER_ADMIN'}
            </p>
          </div>
          <button
            onClick={logout}
            className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors ml-1"
            title="Log Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
