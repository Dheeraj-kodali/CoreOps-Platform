export type NotificationChannel = 'SMS' | 'WHATSAPP' | 'EMAIL' | 'PUSH' | 'IN_APP';

export type NotificationStatus = 'PENDING' | 'SENT' | 'FAILED' | 'DELIVERED' | 'READ';

export interface NotificationLog {
  id: string;
  recipient_name: string;
  recipient_contact: string;
  channel: NotificationChannel;
  title?: string;
  message: string;
  status: NotificationStatus;
  sent_at: string;
  retry_count: number;
  error_detail?: string;
}

export interface NotificationTemplate {
  id: string;
  title: string;
  code: string;
  channel: NotificationChannel;
  template_body: string;
  variables: string[]; // e.g. ["visitor_name", "date", "token_pass"]
  is_active: boolean;
}

export interface BroadcastNotificationPayload {
  channel: NotificationChannel;
  target_audience: 'ALL_VOLUNTEERS' | 'ALL_STAFF' | 'TODAY_VISITORS' | 'CUSTOM';
  recipient_phone_or_email?: string;
  title?: string;
  message: string;
}
