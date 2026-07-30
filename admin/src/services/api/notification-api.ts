import { apiClient } from './api-client';

export class NotificationApi {
  static async listLogs(params?: Record<string, any>): Promise<any> {
    const response = await apiClient.get('/notifications/logs', { params });
    return response.data;
  }

  static async getTemplates(): Promise<any> {
    const response = await apiClient.get('/notifications/templates');
    return response.data;
  }

  static async send(payload: any): Promise<any> {
    const response = await apiClient.post('/notifications/broadcast', payload);
    return response.data;
  }

  static async retry(id: string): Promise<any> {
    const response = await apiClient.post(`/notifications/retry/${id}`);
    return response.data;
  }
}
