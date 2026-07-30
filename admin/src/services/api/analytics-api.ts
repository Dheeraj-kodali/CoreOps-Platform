import { apiClient } from './api-client';

export class AnalyticsApi {
  static async getSummary(params?: Record<string, any>): Promise<any> {
    const response = await apiClient.get('/analytics/summary', { params });
    return response.data;
  }

  static async getPeakHours(params?: Record<string, any>): Promise<any> {
    const response = await apiClient.get('/analytics/peak-hours', { params });
    return response.data;
  }

  static async getVillages(params?: Record<string, any>): Promise<any> {
    const response = await apiClient.get('/analytics/villages', { params });
    return response.data;
  }
}
