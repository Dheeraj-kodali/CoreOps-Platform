import React from 'react';
import Link from 'next/link';
import { Home, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#FAF8F5] dark:bg-[#140E0B] flex items-center justify-center p-6 text-[#1C1410] dark:text-[#FAFAFA]">
      <div className="max-w-md w-full p-8 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/30 shadow-2xl text-center space-y-6">
        <div className="text-6xl font-bold font-serif text-[#D4AF37] tracking-wider">404</div>
        <div>
          <h1 className="text-xl font-bold text-gray-800 dark:text-[#FAFAFA]">Page Not Found</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            The resource or path you requested does not exist or has been relocated.
          </p>
        </div>

        <div className="flex items-center justify-center space-x-3 pt-2">
          <Link
            href="/dashboard"
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-semibold text-xs shadow-md hover:brightness-110 transition-all flex items-center"
          >
            <Home className="w-4 h-4 mr-1.5" />
            <span>Back to Dashboard</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
