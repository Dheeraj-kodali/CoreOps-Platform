import { apiClient } from './api-client';

export class SettingApi {
  static async getSettings(): Promise<any> {
    const response = await apiClient.get('/settings/');
    return response.data;
  }

  static async updateSettings(payload: any): Promise<any> {
    const response = await apiClient.put('/settings/', payload);
    return response.data;
  }
}
