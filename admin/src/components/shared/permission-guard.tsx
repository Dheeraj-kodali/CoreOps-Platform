'use client';

import React from 'react';
import { useAuth } from '../../providers/AuthProvider';
import { PermissionResolver } from '../../resolvers/permission-resolver';

interface PermissionGuardProps {
  permission: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function PermissionGuard({ permission, children, fallback = null }: PermissionGuardProps) {
  const { user } = useAuth();

  if (!user) return <>{fallback}</>;

  const hasAccess = PermissionResolver.hasPermission(user, permission);

  if (!hasAccess) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
