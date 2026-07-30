'use client';

import React, { useEffect } from 'react';
import { ShieldAlert, RefreshCw, Home } from 'lucide-react';
import Link from 'next/link';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('[Global Error Boundary Caught Exception]:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#FAF8F5] dark:bg-[#140E0B] flex items-center justify-center p-6 text-[#1C1410] dark:text-[#FAFAFA]">
      <div className="max-w-md w-full p-8 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/30 shadow-2xl text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-950/50 text-red-600 dark:text-red-400 flex items-center justify-center mx-auto shadow-inner">
          <ShieldAlert className="w-8 h-8" />
        </div>

        <div>
          <h1 className="text-2xl font-bold font-serif text-[#D4AF37]">Application Error</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            An unexpected error occurred in the system runtime. Our security boundaries prevented data exposure.
          </p>
          {error.message && (
            <div className="mt-3 p-3 rounded-xl bg-gray-100 dark:bg-[#2C1A11] text-[11px] font-mono text-red-600 dark:text-red-400 text-left overflow-x-auto">
              {error.message}
            </div>
          )}
        </div>

        <div className="flex items-center justify-center space-x-3 pt-2">
          <button
            onClick={() => reset()}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-semibold text-xs shadow-md hover:brightness-110 transition-all flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-1.5" />
            <span>Try Again</span>
          </button>
          <Link
            href="/dashboard"
            className="px-5 py-2.5 rounded-xl bg-gray-100 dark:bg-[#2C1A11] text-gray-700 dark:text-[#FAFAFA] font-medium text-xs hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-colors flex items-center"
          >
            <Home className="w-4 h-4 mr-1.5 text-[#D4AF37]" />
            <span>Dashboard</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
