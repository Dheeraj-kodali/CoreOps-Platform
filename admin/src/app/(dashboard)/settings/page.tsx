'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings, Building2, Users, Clock, Bell, ShieldCheck, Layers, Database, Save, CheckCircle2, AlertCircle } from 'lucide-react';
import { SettingsRepository } from '../../../repositories/settings-repository';
import { SystemSettingsPayload } from '../../../types/settings';

const DEFAULT_SETTINGS: SystemSettingsPayload = {
  temple_profile: {
    name: 'Sri Kalki Seva Alayam',
    code: 'KALKI_001',
    tagline: 'Divine Darshan & Visitor Excellence Portal',
    address: 'Sacred Complex, Kalki Nagaram',
    city: 'Chittoor',
    state: 'Andhra Pradesh',
    country: 'India',
    pincode: '517001',
    latitude: 13.2172,
    longitude: 79.1003,
    contact_phone: '+91 98765 43210',
    contact_email: 'admin@kalkiseva.org',
    website: 'https://kalkiseva.org',
    timezone: 'Asia/Kolkata',
    default_language: 'en',
    currency: 'INR (₹)',
    opening_time: '06:00 AM',
    closing_time: '09:00 PM',
  },
  visitor_rules: {
    max_daily_capacity: 10000,
    duplicate_detection_window_days: 1,
    require_photo_capture: false,
    require_id_proof: false,
    enable_qr_tokens: true,
    default_status: 'CHECKED_IN',
    purposes: [
      { id: 'p1', name_en: 'General Darshan', name_te: 'సాధారణ దర్శనం' },
      { id: 'p2', name_en: 'Special Seva', name_te: 'ప్రత్యేక సేవ' },
      { id: 'p3', name_en: 'Annadanam', name_te: 'అన్నదానం' },
    ],
  },
  queue_rules: {
    enable_vip_queue: true,
    enable_senior_citizen_priority: true,
    enable_special_needs_priority: true,
    max_queue_length: 500,
    avg_darshan_duration_minutes: 15,
  },
  notifications: {
    enable_sms: true,
    sms_provider: 'MSG91',
    enable_whatsapp: true,
    enable_email: true,
    email_gateway: 'SMTP',
    enable_push_notifications: true,
  },
  security_policy: {
    session_timeout_minutes: 30,
    max_failed_login_attempts: 5,
    require_password_special_char: true,
    ip_whitelist: ['127.0.0.1'],
    enable_audit_logging: true,
  },
  tenant_saas: {
    tenant_id: 'tenant_kalki_001',
    tenant_name: 'Sri Kalki Seva Alayam Trust',
    subscription_plan: 'ENTERPRISE',
    storage_limit_gb: 100,
    theme_primary_color: '#D4AF37',
    license_status: 'ACTIVE',
    feature_flags: {
      qr_module: true,
      analytics_engine: true,
      reporting_engine: true,
      whatsapp_notifications: true,
      sms_notifications: true,
      offline_sync: true,
      audit_center: true,
      ai_analytics_future: false,
    },
  },
  backup_retention_days: 365,
  backup_frequency: 'DAILY',
};

type SettingTab = 'PROFILE' | 'VISITOR' | 'QUEUE' | 'NOTIFICATIONS' | 'SECURITY' | 'SAAS' | 'BACKUP';

export default function SystemSettingsPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<SettingTab>('PROFILE');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // TanStack Query for Fetching Settings
  const { data: settingsData, isLoading } = useQuery<SystemSettingsPayload>({
    queryKey: ['system-settings'],
    queryFn: async () => {
      try {
        const res = await SettingsRepository.getSettings();
        return res || DEFAULT_SETTINGS;
      } catch {
        return DEFAULT_SETTINGS;
      }
    },
  });

  const [formState, setFormState] = useState<SystemSettingsPayload>(DEFAULT_SETTINGS);

  // Update Settings Mutation
  const saveMutation = useMutation({
    mutationFn: (payload: SystemSettingsPayload) => SettingsRepository.updateSettings(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-settings'] });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    },
  });

  const handleSaveAll = (e: React.FormEvent) => {
    e.preventDefault();
    saveMutation.mutate(formState);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner & Save Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
            Centralized Configuration & SaaS Portal
          </h1>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">
            Multi-Tenant Enterprise Rules, Gate Settings, Notification Gateways & Feature Flags
          </p>
        </div>

        <button
          onClick={handleSaveAll}
          disabled={saveMutation.isPending}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md hover:brightness-110 active:scale-[0.99] disabled:opacity-50 transition-all flex items-center space-x-1.5"
        >
          <Save className="w-4 h-4" />
          <span>{saveMutation.isPending ? 'Saving Configurations...' : 'Save Configuration Changes'}</span>
        </button>
      </div>

      {/* Save Success Banner */}
      {saveSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 text-emerald-800 dark:text-emerald-300 text-xs flex items-center space-x-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          <span>System configuration successfully updated and propagated across multi-tenant cache.</span>
        </div>
      )}

      {/* Settings Category Navigation Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-gray-200 dark:border-[#D4AF37]/20 pb-3">
        <button
          onClick={() => setActiveTab('PROFILE')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all ${
            activeTab === 'PROFILE'
              ? 'bg-[#D4AF37] text-[#1C1410] font-bold shadow-sm'
              : 'bg-gray-100 dark:bg-[#2C1A11] text-gray-600 dark:text-[#FAFAFA]/70'
          }`}
        >
          <Building2 className="w-3.5 h-3.5" />
          <span>Temple Profile</span>
        </button>

        <button
          onClick={() => setActiveTab('VISITOR')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all ${
            activeTab === 'VISITOR'
              ? 'bg-[#D4AF37] text-[#1C1410] font-bold shadow-sm'
              : 'bg-gray-100 dark:bg-[#2C1A11] text-gray-600 dark:text-[#FAFAFA]/70'
          }`}
        >
          <Users className="w-3.5 h-3.5" />
          <span>Visitor & Gate Rules</span>
        </button>

        <button
          onClick={() => setActiveTab('QUEUE')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all ${
            activeTab === 'QUEUE'
              ? 'bg-[#D4AF37] text-[#1C1410] font-bold shadow-sm'
              : 'bg-gray-100 dark:bg-[#2C1A11] text-gray-600 dark:text-[#FAFAFA]/70'
          }`}
        >
          <Clock className="w-3.5 h-3.5" />
          <span>Queue Management</span>
        </button>

        <button
          onClick={() => setActiveTab('NOTIFICATIONS')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all ${
            activeTab === 'NOTIFICATIONS'
              ? 'bg-[#D4AF37] text-[#1C1410] font-bold shadow-sm'
              : 'bg-gray-100 dark:bg-[#2C1A11] text-gray-600 dark:text-[#FAFAFA]/70'
          }`}
        >
          <Bell className="w-3.5 h-3.5" />
          <span>Notifications</span>
        </button>

        <button
          onClick={() => setActiveTab('SECURITY')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all ${
            activeTab === 'SECURITY'
              ? 'bg-[#D4AF37] text-[#1C1410] font-bold shadow-sm'
              : 'bg-gray-100 dark:bg-[#2C1A11] text-gray-600 dark:text-[#FAFAFA]/70'
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Security & Audit</span>
        </button>

        <button
          onClick={() => setActiveTab('SAAS')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all ${
            activeTab === 'SAAS'
              ? 'bg-[#D4AF37] text-[#1C1410] font-bold shadow-sm'
              : 'bg-gray-100 dark:bg-[#2C1A11] text-gray-600 dark:text-[#FAFAFA]/70'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>SaaS & Feature Flags</span>
        </button>

        <button
          onClick={() => setActiveTab('BACKUP')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all ${
            activeTab === 'BACKUP'
              ? 'bg-[#D4AF37] text-[#1C1410] font-bold shadow-sm'
              : 'bg-gray-100 dark:bg-[#2C1A11] text-gray-600 dark:text-[#FAFAFA]/70'
          }`}
        >
          <Database className="w-3.5 h-3.5" />
          <span>Backup & Retention</span>
        </button>
      </div>

      {/* Tab Panels */}
      <div className="p-6 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-5">
        {activeTab === 'PROFILE' && (
          <div className="space-y-4">
            <h3 className="text-base font-bold font-serif text-[#D4AF37]">Temple Organization Profile</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="font-semibold">Temple Name</label>
                <input
                  type="text"
                  value={formState.temple_profile.name}
                  onChange={(e) =>
                    setFormState({
                      ...formState,
                      temple_profile: { ...formState.temple_profile, name: e.target.value },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
                />
              </div>

              <div>
                <label className="font-semibold">Contact Email</label>
                <input
                  type="email"
                  value={formState.temple_profile.contact_email}
                  onChange={(e) =>
                    setFormState({
                      ...formState,
                      temple_profile: { ...formState.temple_profile, contact_email: e.target.value },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
                />
              </div>

              <div>
                <label className="font-semibold">Contact Phone</label>
                <input
                  type="text"
                  value={formState.temple_profile.contact_phone}
                  onChange={(e) =>
                    setFormState({
                      ...formState,
                      temple_profile: { ...formState.temple_profile, contact_phone: e.target.value },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
                />
              </div>

              <div>
                <label className="font-semibold">City</label>
                <input
                  type="text"
                  value={formState.temple_profile.city}
                  onChange={(e) =>
                    setFormState({
                      ...formState,
                      temple_profile: { ...formState.temple_profile, city: e.target.value },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
                />
              </div>

              <div>
                <label className="font-semibold">Timezone</label>
                <input
                  type="text"
                  value={formState.temple_profile.timezone}
                  onChange={(e) =>
                    setFormState({
                      ...formState,
                      temple_profile: { ...formState.temple_profile, timezone: e.target.value },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
                />
              </div>

              <div>
                <label className="font-semibold">Default Language</label>
                <select
                  value={formState.temple_profile.default_language}
                  onChange={(e) =>
                    setFormState({
                      ...formState,
                      temple_profile: {
                        ...formState.temple_profile,
                        default_language: e.target.value as any,
                      },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
                >
                  <option value="en">English</option>
                  <option value="te">Telugu (తెలుగు)</option>
                  <option value="hi">Hindi (हिंदी)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'VISITOR' && (
          <div className="space-y-4">
            <h3 className="text-base font-bold font-serif text-[#D4AF37]">Visitor & Gate Rules</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="font-semibold">Maximum Daily Capacity</label>
                <input
                  type="number"
                  value={formState.visitor_rules.max_daily_capacity}
                  onChange={(e) =>
                    setFormState({
                      ...formState,
                      visitor_rules: {
                        ...formState.visitor_rules,
                        max_daily_capacity: Number(e.target.value),
                      },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
                />
              </div>

              <div>
                <label className="font-semibold">Duplicate Check Window (Days)</label>
                <input
                  type="number"
                  value={formState.visitor_rules.duplicate_detection_window_days}
                  onChange={(e) =>
                    setFormState({
                      ...formState,
                      visitor_rules: {
                        ...formState.visitor_rules,
                        duplicate_detection_window_days: Number(e.target.value),
                      },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
                />
              </div>

              <div className="space-y-2 pt-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formState.visitor_rules.enable_qr_tokens}
                    onChange={(e) =>
                      setFormState({
                        ...formState,
                        visitor_rules: {
                          ...formState.visitor_rules,
                          enable_qr_tokens: e.target.checked,
                        },
                      })
                    }
                    className="rounded text-[#D4AF37]"
                  />
                  <span>Enable Digital QR Token Passes</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formState.visitor_rules.require_id_proof}
                    onChange={(e) =>
                      setFormState({
                        ...formState,
                        visitor_rules: {
                          ...formState.visitor_rules,
                          require_id_proof: e.target.checked,
                        },
                      })
                    }
                    className="rounded text-[#D4AF37]"
                  />
                  <span>Require ID Proof Document for Check-in</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'SAAS' && (
          <div className="space-y-4">
            <h3 className="text-base font-bold font-serif text-[#D4AF37]">Multi-Tenant SaaS & Feature Flags</h3>
            <div className="p-4 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 space-y-4 text-xs">
              <div className="flex items-center justify-between border-b border-gray-200 dark:border-[#D4AF37]/20 pb-3">
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400">Subscription License</span>
                  <h4 className="font-bold text-sm text-[#D4AF37]">{formState.tenant_saas.subscription_plan} PLAN</h4>
                </div>
                <span className="px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold text-xs">
                  {formState.tenant_saas.license_status}
                </span>
              </div>

              {/* Feature Flags Grid */}
              <div className="space-y-2">
                <span className="font-bold text-[#D4AF37] uppercase text-[11px]">Tenant Feature Flags</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
                  {Object.entries(formState.tenant_saas.feature_flags).map(([flagKey, isEnabled]) => (
                    <label
                      key={flagKey}
                      className="p-3 rounded-xl bg-white dark:bg-[#1C1410] border border-gray-200 dark:border-[#D4AF37]/30 flex items-center justify-between cursor-pointer"
                    >
                      <span className="font-semibold text-gray-800 dark:text-[#FAFAFA] capitalize">
                        {flagKey.replace('_', ' ')}
                      </span>
                      <input
                        type="checkbox"
                        checked={isEnabled}
                        onChange={(e) =>
                          setFormState({
                            ...formState,
                            tenant_saas: {
                              ...formState.tenant_saas,
                              feature_flags: {
                                ...formState.tenant_saas.feature_flags,
                                [flagKey]: e.target.checked,
                              },
                            },
                          })
                        }
                        className="rounded text-[#D4AF37]"
                      />
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
