export type SystemRole =
  | 'SUPER_ADMIN'
  | 'TEMPLE_ADMIN'
  | 'MANAGER'
  | 'VOLUNTEER'
  | 'RECEPTION'
  | 'VIEWER';

export type UserStatus = 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';

export type PermissionAction =
  | 'read'
  | 'create'
  | 'update'
  | 'delete'
  | 'approve'
  | 'export'
  | 'manage';

export type PermissionModule =
  | 'visitors'
  | 'reports'
  | 'analytics'
  | 'users'
  | 'roles'
  | 'settings'
  | 'notifications'
  | 'sync'
  | 'dashboard';

export interface Permission {
  id: string;
  module: PermissionModule;
  action: PermissionAction;
  code: string; // e.g. "visitors:read"
  description: string;
}

export interface Role {
  id: string;
  name: SystemRole | string;
  code: string;
  description: string;
  permissions: (Permission | string)[];
  user_count?: number;
  is_system?: boolean;
}

export interface UserSession {
  id: string;
  token_jti: string;
  ip_address: string;
  user_agent: string;
  login_time: string;
  last_activity: string;
  is_current: boolean;
}

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  phone_number?: string;
  status: UserStatus;
  temple_id?: string;
  temple_name?: string;
  roles: Role[];
  permissions: string[];
  avatar_url?: string;
  last_login_at?: string;
  created_at: string;
  must_change_password?: boolean;
  active_sessions?: UserSession[];
}

export interface UserListResponse {
  items: User[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}
