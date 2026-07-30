export interface TempleProfileConfig {
  name: string;
  code: string;
  tagline?: string;
  logo_url?: string;
  address: string;
  city: string;
  state: string;
  country: string;
  pincode: string;
  latitude?: number;
  longitude?: number;
  contact_phone: string;
  contact_email: string;
  website?: string;
  timezone: string;
  default_language: 'en' | 'te' | 'hi';
  currency: string;
  opening_time: string;
  closing_time: string;
}

export interface VisitorRulesConfig {
  max_daily_capacity: number;
  duplicate_detection_window_days: number;
  require_photo_capture: boolean;
  require_id_proof: boolean;
  enable_qr_tokens: boolean;
  default_status: string;
  purposes: { id: string; name_en: string; name_te: string }[];
}

export interface QueueRulesConfig {
  enable_vip_queue: boolean;
  enable_senior_citizen_priority: boolean;
  enable_special_needs_priority: boolean;
  max_queue_length: number;
  avg_darshan_duration_minutes: number;
}

export interface NotificationRulesConfig {
  enable_sms: boolean;
  sms_provider: 'TWILIO' | 'MSG91' | 'FAST2SMS';
  enable_whatsapp: boolean;
  whatsapp_business_id?: string;
  enable_email: boolean;
  email_gateway: 'SMTP' | 'SES' | 'SENDGRID';
  enable_push_notifications: boolean;
}

export interface SecurityPolicyConfig {
  session_timeout_minutes: number;
  max_failed_login_attempts: number;
  require_password_special_char: boolean;
  ip_whitelist: string[];
  enable_audit_logging: boolean;
}

export interface FeatureFlagsConfig {
  qr_module: boolean;
  analytics_engine: boolean;
  reporting_engine: boolean;
  whatsapp_notifications: boolean;
  sms_notifications: boolean;
  offline_sync: boolean;
  audit_center: boolean;
  ai_analytics_future: boolean;
}

export interface TenantSaaSConfig {
  tenant_id: string;
  tenant_name: string;
  subscription_plan: 'STARTER' | 'PROFESSIONAL' | 'ENTERPRISE';
  storage_limit_gb: number;
  theme_primary_color: string;
  license_status: 'ACTIVE' | 'EXPIRED' | 'TRIAL';
  feature_flags: FeatureFlagsConfig;
}

export interface SystemSettingsPayload {
  temple_profile: TempleProfileConfig;
  visitor_rules: VisitorRulesConfig;
  queue_rules: QueueRulesConfig;
  notifications: NotificationRulesConfig;
  security_policy: SecurityPolicyConfig;
  tenant_saas: TenantSaaSConfig;
  backup_retention_days: number;
  backup_frequency: 'HOURLY' | 'DAILY' | 'WEEKLY';
}
