import React from 'react';
import Link from 'next/link';
import { ShieldX, Home } from 'lucide-react';

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen bg-[#FAF8F5] dark:bg-[#140E0B] flex items-center justify-center p-6 text-[#1C1410] dark:text-[#FAFAFA]">
      <div className="max-w-md w-full p-8 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/30 shadow-2xl text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-950/50 text-red-600 dark:text-red-400 flex items-center justify-center mx-auto shadow-inner">
          <ShieldX className="w-8 h-8" />
        </div>

        <div>
          <h1 className="text-2xl font-bold font-serif text-[#D4AF37]">403 - Permission Denied</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Your user account does not possess sufficient privileges to access this enterprise module.
          </p>
        </div>

        <div className="flex items-center justify-center space-x-3 pt-2">
          <Link
            href="/dashboard"
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-semibold text-xs shadow-md hover:brightness-110 transition-all flex items-center"
          >
            <Home className="w-4 h-4 mr-1.5" />
            <span>Return to Dashboard</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
