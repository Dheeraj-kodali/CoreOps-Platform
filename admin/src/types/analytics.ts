export interface SummaryStatsResponse {
  total_visitors: number;
  today_visitors: number;
  total_volunteers: number;
  active_volunteers: number;
  total_purposes: number;
  total_villages: number;
  growth_rate_percentage?: number;
  repeat_visitor_percentage?: number;
  avg_queue_time_minutes?: number;
}

export interface PeakHourDataPoint {
  hour_label: string; // e.g. "09:00 AM"
  hour_24: number;
  visitor_count: number;
  surge_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'PEAK';
}

export interface VillageDemographicPoint {
  village_name: string;
  district: string;
  visitor_count: number;
  percentage: number;
}

export interface AnalyticsFilterState {
  date_from?: string;
  date_to?: string;
  temple_id?: string;
  volunteer_id?: string;
  village_id?: string;
  purpose_id?: string;
  status?: string;
}
