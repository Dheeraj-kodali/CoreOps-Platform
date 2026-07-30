'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, TrendingUp, Users, Clock, MapPin, RefreshCw, Calendar } from 'lucide-react';
import { AnalyticsRepository } from '../../../repositories/analytics-repository';
import { StatsCard } from '../../../components/shared/stats-card';
import { GenericChartRenderer } from '../../../components/shared/charts/generic-chart-renderer';
import { PeakHoursHeatmap } from '../../../features/analytics/peak-hours-heatmap';
import { DemographicAnalytics } from '../../../features/analytics/demographic-analytics';
import { PeakHourDataPoint, VillageDemographicPoint } from '../../../types/analytics';

export default function AnalyticsPortalPage() {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  // TanStack Query for Analytics Summary Stats
  const { data: summaryData } = useQuery({
    queryKey: ['analytics-summary', dateFrom, dateTo],
    queryFn: () => AnalyticsRepository.getSummaryStats({ date_from: dateFrom, date_to: dateTo }),
  });

  // TanStack Query for Peak Hours
  const { data: peakHoursData } = useQuery<PeakHourDataPoint[]>({
    queryKey: ['analytics-peak-hours', dateFrom, dateTo],
    queryFn: async () => {
      // In production calls AnalyticsRepository.getPeakHours()
      return [
        { hour_label: '06 AM', hour_24: 6, visitor_count: 120, surge_level: 'LOW' },
        { hour_label: '07 AM', hour_24: 7, visitor_count: 240, surge_level: 'MEDIUM' },
        { hour_label: '08 AM', hour_24: 8, visitor_count: 450, surge_level: 'HIGH' },
        { hour_label: '09 AM', hour_24: 9, visitor_count: 680, surge_level: 'PEAK' },
        { hour_label: '10 AM', hour_24: 10, visitor_count: 720, surge_level: 'PEAK' },
        { hour_label: '11 AM', hour_24: 11, visitor_count: 510, surge_level: 'HIGH' },
        { hour_label: '12 PM', hour_24: 12, visitor_count: 380, surge_level: 'MEDIUM' },
        { hour_label: '01 PM', hour_24: 13, visitor_count: 290, surge_level: 'LOW' },
        { hour_label: '02 PM', hour_24: 14, visitor_count: 310, surge_level: 'MEDIUM' },
        { hour_label: '03 PM', hour_24: 15, visitor_count: 490, surge_level: 'HIGH' },
        { hour_label: '04 PM', hour_24: 16, visitor_count: 630, surge_level: 'PEAK' },
        { hour_label: '05 PM', hour_24: 17, visitor_count: 550, surge_level: 'HIGH' },
      ];
    },
  });

  // Mock Time Series Data for Area Chart
  const timeSeriesData = [
    { label: 'Mon', value: 1240 },
    { label: 'Tue', value: 1450 },
    { label: 'Wed', value: 1120 },
    { label: 'Thu', value: 1680 },
    { label: 'Fri', value: 2100 },
    { label: 'Sat', value: 3450 },
    { label: 'Sun', value: 3890 },
  ];

  // Mock Village Demographics
  const mockVillages: VillageDemographicPoint[] = [
    { village_name: 'Kalki Nagaram', district: 'Chittoor', visitor_count: 1420, percentage: 38.5 },
    { village_name: 'Tirupati Rural', district: 'Tirupati', visitor_count: 980, percentage: 26.6 },
    { village_name: 'Madanapalle', district: 'Annamayya', visitor_count: 650, percentage: 17.6 },
    { village_name: 'Chittoor Urban', district: 'Chittoor', visitor_count: 420, percentage: 11.4 },
  ];

  // Mock Purpose Distribution
  const mockPurposes = [
    { label: 'General Darshan', value: 2450, color: '#D4AF37' },
    { label: 'Special Seva', value: 890, color: '#FF9933' },
    { label: 'Voluntary Service', value: 320, color: '#10B981' },
    { label: 'Annadanam', value: 230, color: '#3B82F6' },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner & Date Filter */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
            Analytics Command Portal
          </h1>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">
            Real-time Footfall Time Series, Peak Surge Heatmaps, Village Demographics & Queue Time Analytics
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <div className="relative">
            <Calendar className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="pl-9 pr-3 py-2 text-xs rounded-xl bg-white dark:bg-[#1C1410] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>
          <div className="relative">
            <Calendar className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="pl-9 pr-3 py-2 text-xs rounded-xl bg-white dark:bg-[#1C1410] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>
        </div>
      </div>

      {/* Summary KPI Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Weekly Visitor Growth"
          value="+24.8%"
          change="+3.2% vs Last Wk"
          isPositive={true}
          icon={TrendingUp}
          description="Aggregated weekly footfall momentum"
        />
        <StatsCard
          title="Repeat Devotee Rate"
          value="34.2%"
          change="1,240 Devotees"
          isPositive={true}
          icon={Users}
          description="Devotees checking in 2+ times"
        />
        <StatsCard
          title="Avg Queue Wait Time"
          value="14.5 Mins"
          change="-2.1 Mins"
          isPositive={true}
          icon={Clock}
          description="Average wait time at shrine entrance"
        />
        <StatsCard
          title="Top Regional Origin"
          value="Kalki Nagaram"
          change="38.5% Share"
          isPositive={true}
          icon={MapPin}
          description="Highest density visitor village"
        />
      </div>

      {/* Time Series Area Chart & Purpose Donut Chart Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
              7-Day Visitor Check-in Trend
            </h3>
            <span className="text-[10px] text-gray-400 font-mono">Time Series Metric</span>
          </div>
          <GenericChartRenderer type="area" data={timeSeriesData} />
        </div>

        <div className="p-6 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-4">
          <h3 className="text-base font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
            Visit Purpose Distribution
          </h3>
          <GenericChartRenderer type="donut" data={mockPurposes} />
        </div>
      </div>

      {/* Hourly Surge Intensity Heatmap */}
      <div className="p-6 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm">
        {peakHoursData && <PeakHoursHeatmap data={peakHoursData} />}
      </div>

      {/* Village Origin Demographic Analysis */}
      <div className="p-6 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm">
        <DemographicAnalytics villages={mockVillages} />
      </div>
    </div>
  );
}
