export interface Permission {
  id: string;
  code: string;
  module: string;
  description?: string;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions: Permission[];
}

export interface User {
  id: string;
  username: string;
  email?: string;
  full_name: string;
  phone_number?: string;
  is_active: boolean;
  roles: Role[];
  temple_id?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
