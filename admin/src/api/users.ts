import { apiClient } from './client';

export interface UserItem {
  id: string;
  username: string;
  email?: string;
  full_name: string;
  phone_number?: string;
  is_active: boolean;
  roles: Array<{ id: string; name: string }>;
  created_at: string;
}

export interface CreateUserPayload {
  username: string;
  email?: string;
  password: string;
  full_name: string;
  phone_number?: string;
  role_ids?: string[];
}

export interface RoleItem {
  id: string;
  name: string;
  description?: string;
  permissions: Array<{ id: string; code: string; module: string }>;
}

export const fetchUsers = async (): Promise<UserItem[]> => {
  const response = await apiClient.get<UserItem[]>('/users/');
  return response.data;
};

export const createUser = async (payload: CreateUserPayload): Promise<UserItem> => {
  const response = await apiClient.post<UserItem>('/users/', payload);
  return response.data;
};

export const deleteUser = async (id: string): Promise<void> => {
  await apiClient.delete(`/users/${id}`);
};

export const fetchRoles = async (): Promise<RoleItem[]> => {
  const response = await apiClient.get<RoleItem[]>('/roles/');
  return response.data;
};
