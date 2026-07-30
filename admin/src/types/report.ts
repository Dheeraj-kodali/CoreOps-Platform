export type ReportType =
  | 'DAILY_VISITORS'
  | 'WEEKLY_VISITORS'
  | 'MONTHLY_VISITORS'
  | 'YEARLY_VISITORS'
  | 'PURPOSE_DISTRIBUTION'
  | 'VILLAGE_DISTRIBUTION'
  | 'VOLUNTEER_PERFORMANCE'
  | 'VISITOR_STATUS_SUMMARY'
  | 'REPEAT_VISITORS'
  | 'PEAK_HOURS'
  | 'QUEUE_STATISTICS'
  | 'QR_SCAN_ACTIVITY';

export type ExportFormat = 'pdf' | 'excel' | 'csv' | 'print';

export interface ReportFilterState {
  date_from?: string;
  date_to?: string;
  temple_id?: string;
  volunteer_id?: string;
  village_id?: string;
  purpose_id?: string;
  status?: string;
  is_repeat?: boolean;
  search?: string;
}

export interface ReportTemplateConfig {
  id: ReportType;
  title: string;
  description: string;
  chartType: 'area' | 'bar' | 'line' | 'pie' | 'donut' | 'table';
  category: 'VISITOR' | 'OPERATIONS' | 'VOLUNTEER' | 'SYSTEM';
  supportedFormats: ExportFormat[];
}

export interface GenericChartDataPoint {
  label: string;
  value: number;
  secondaryValue?: number;
  category?: string;
  color?: string;
}

export interface ReportDataResponse {
  report_type: ReportType;
  title: string;
  generated_at: string;
  summary_kpis: {
    title: string;
    value: string | number;
    change?: string;
    isPositive?: boolean;
  }[];
  chart_data: GenericChartDataPoint[];
  table_headers: string[];
  table_rows: any[][];
}
