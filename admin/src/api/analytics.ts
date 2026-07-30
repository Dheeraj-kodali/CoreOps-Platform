import { apiClient } from './client';

export interface AnalyticsSummary {
  today_visitors: number;
  weekly_visitors: number;
  monthly_visitors: number;
  yearly_visitors: number;
  total_visitors: number;
  pending_sync_count: number;
  active_volunteers: number;
  online_devices: number;
}

export interface PurposeBreakdownItem {
  purpose_name: string;
  count: number;
  percentage: number;
}

export const fetchAnalyticsSummary = async (): Promise<AnalyticsSummary> => {
  const response = await apiClient.get<AnalyticsSummary>('/analytics/summary');
  return response.data;
};

export const fetchPurposeBreakdown = async (): Promise<PurposeBreakdownItem[]> => {
  const response = await apiClient.get<PurposeBreakdownItem[]>('/analytics/purpose-breakdown');
  return response.data;
};
