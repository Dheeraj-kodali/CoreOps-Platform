import { AnalyticsApi } from '../services/api/analytics-api';

export class AnalyticsRepository {
  static async getSummaryStats(params?: Record<string, any>): Promise<any> {
    return await AnalyticsApi.getSummary(params);
  }

  static async getPeakHours(params?: Record<string, any>): Promise<any> {
    return await AnalyticsApi.getPeakHours(params);
  }

  static async getVillageDemographics(params?: Record<string, any>): Promise<any> {
    return await AnalyticsApi.getVillages(params);
  }
}
