import { apiClient } from './api-client';

export class AuthApi {
  static async login(credentials: { username: string; password: string }): Promise<any> {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  }

  static async logout(): Promise<any> {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  }

  static async getMe(): Promise<any> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  }

  static async forgotPassword(data: { username_or_email: string }): Promise<any> {
    const response = await apiClient.post('/auth/forgot-password', data);
    return response.data;
  }

  static async resetPassword(data: { reset_token: string; new_password: string }): Promise<any> {
    const response = await apiClient.post('/auth/reset-password', data);
    return response.data;
  }
}
