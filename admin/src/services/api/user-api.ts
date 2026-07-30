import { apiClient } from './api-client';

export class UserApi {
  static async list(params?: Record<string, any>): Promise<any> {
    const response = await apiClient.get('/users/', { params });
    return response.data;
  }

  static async getById(userId: string): Promise<any> {
    const response = await apiClient.get(`/users/${userId}`);
    return response.data;
  }

  static async create(payload: any): Promise<any> {
    const response = await apiClient.post('/users/', payload);
    return response.data;
  }

  static async update(userId: string, payload: any): Promise<any> {
    const response = await apiClient.put(`/users/${userId}`, payload);
    return response.data;
  }

  static async getRoles(): Promise<any> {
    const response = await apiClient.get('/roles/');
    return response.data;
  }

  static async getPermissions(): Promise<any> {
    const response = await apiClient.get('/permissions/');
    return response.data;
  }
}
