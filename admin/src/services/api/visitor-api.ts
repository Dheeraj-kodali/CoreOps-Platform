import { apiClient } from './api-client';

export class VisitorApi {
  static async list(params?: Record<string, any>): Promise<any> {
    const response = await apiClient.get('/visitors/', { params });
    return response.data;
  }

  static async getById(visitorId: string): Promise<any> {
    const response = await apiClient.get(`/visitors/${visitorId}`);
    return response.data;
  }

  static async checkDuplicate(params: { name: string; phone_number: string; visitor_date: string }): Promise<any> {
    const response = await apiClient.get('/visitors/check-duplicate', { params });
    return response.data;
  }

  static async create(payload: any): Promise<any> {
    const response = await apiClient.post('/visitors/', payload);
    return response.data;
  }

  static async update(visitorId: string, payload: any): Promise<any> {
    const response = await apiClient.put(`/visitors/${visitorId}`, payload);
    return response.data;
  }

  static async delete(visitorId: string): Promise<any> {
    const response = await apiClient.delete(`/visitors/${visitorId}`);
    return response.data;
  }
}
