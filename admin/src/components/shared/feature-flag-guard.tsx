'use client';

import React from 'react';
import { FeatureFlagsConfig } from '../../types/settings';

interface FeatureFlagGuardProps {
  flag: keyof FeatureFlagsConfig;
  activeFlags?: FeatureFlagsConfig;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

const DEFAULT_FLAGS: FeatureFlagsConfig = {
  qr_module: true,
  analytics_engine: true,
  reporting_engine: true,
  whatsapp_notifications: true,
  sms_notifications: true,
  offline_sync: true,
  audit_center: true,
  ai_analytics_future: false,
};

export function FeatureFlagGuard({ flag, activeFlags = DEFAULT_FLAGS, children, fallback = null }: FeatureFlagGuardProps) {
  const isEnabled = activeFlags ? activeFlags[flag] : DEFAULT_FLAGS[flag];

  if (!isEnabled) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
