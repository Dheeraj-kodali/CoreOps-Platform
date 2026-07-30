'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../providers/AuthProvider';
import { PermissionResolver } from '../../resolvers/permission-resolver';
import { LoadingSkeleton } from './loading-skeleton';

interface AuthGuardProps {
  requiredPermission?: string;
  children: React.ReactNode;
}

export function AuthGuard({ requiredPermission, children }: AuthGuardProps) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF8F5] dark:bg-[#140E0B]">
        <div className="text-center space-y-4">
          <LoadingSkeleton className="w-16 h-16 rounded-full mx-auto" />
          <p className="text-xs font-semibold text-[#D4AF37] uppercase tracking-wider">Verifying Session Security...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (requiredPermission && !PermissionResolver.hasPermission(user, requiredPermission)) {
    return (
      <div className="p-8 rounded-2xl bg-white dark:bg-[#1C1410] border border-red-200 dark:border-red-900/50 text-center space-y-3">
        <h2 className="text-lg font-bold text-red-600 dark:text-red-400">Access Denied</h2>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          Your account does not possess the required permission (<span className="font-mono">{requiredPermission}</span>) to view this page.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
