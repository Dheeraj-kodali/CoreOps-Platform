export type VisitorStatus =
  | 'REGISTERED'
  | 'CHECKED_IN'
  | 'WAITING'
  | 'INSIDE_TEMPLE'
  | 'COMPLETED'
  | 'CANCELLED';

export interface Purpose {
  id: string;
  name_en: string;
  name_te: string;
  code: string;
}

export interface Village {
  id: string;
  name_en: string;
  name_te: string;
  district?: string;
  state?: string;
}

export interface TimelineEvent {
  id: string;
  status: VisitorStatus;
  label: string;
  timestamp: string;
  actor: string;
  notes?: string;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  entity: string;
  old_value?: any;
  new_value?: any;
}

export interface Visitor {
  id: string;
  visitor_uuid: string;
  name: string;
  phone_number: string;
  gender: 'MALE' | 'FEMALE' | 'OTHER';
  age: number;
  persons_count: number;
  status: VisitorStatus;
  temple_id?: string;
  village_id?: string;
  village_name_custom?: string;
  purpose_id: string;
  temple_service?: string;
  visitor_date: string;
  visitor_time: string;
  volunteer_id: string;
  notes?: string;
  photo_url?: string;
  sync_status: 'PENDING' | 'SYNCED' | 'CONFLICT' | 'FAILED';
  total_visits_count?: number;
  is_repeat_visitor?: boolean;
  purpose?: Purpose;
  village?: Village;
  timeline?: TimelineEvent[];
  audit_logs?: AuditEvent[];
}

export interface VisitorListResponse {
  items: Visitor[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}
