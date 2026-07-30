import { ReportApi } from '../services/api/report-api';

export class ReportRepository {
  static async getReports(params?: Record<string, any>): Promise<any[]> {
    return await ReportApi.list(params);
  }

  static async generateReport(payload: { report_type: string; title: string; format: string; parameters_json?: any }): Promise<any> {
    return await ReportApi.generate(payload);
  }
}
