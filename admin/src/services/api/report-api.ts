import { apiClient } from './api-client';

export class ReportApi {
  static async list(params?: Record<string, any>): Promise<any> {
    const response = await apiClient.get('/reports/', { params });
    return response.data;
  }

  static async generate(payload: any): Promise<any> {
    const response = await apiClient.post('/reports/', payload);
    return response.data;
  }
}
