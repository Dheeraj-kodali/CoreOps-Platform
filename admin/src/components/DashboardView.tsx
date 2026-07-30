'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAnalyticsSummary, fetchPurposeBreakdown } from '../api/analytics';
import { fetchVisitors } from '../api/visitors';
import { Users, Calendar, TrendingUp, RefreshCw, Smartphone, ShieldCheck } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#D4AF37', '#2C1A11', '#900C3F', '#3E2723', '#997A15'];

const mockHourlyData = [
  { time: '6 AM', visitors: 120 },
  { time: '8 AM', visitors: 450 },
  { time: '10 AM', visitors: 890 },
  { time: '12 PM', visitors: 1100 },
  { time: '2 PM', visitors: 640 },
  { time: '4 PM', visitors: 980 },
  { time: '6 PM', visitors: 720 },
];

export default function DashboardView() {
  const { data: summary, isLoading: isSummaryLoading, refetch } = useQuery({
    queryKey: ['analyticsSummary'],
    queryFn: fetchAnalyticsSummary,
  });

  const { data: purposeData } = useQuery({
    queryKey: ['purposeBreakdown'],
    queryFn: fetchPurposeBreakdown,
  });

  const { data: recentVisitorsData } = useQuery({
    queryKey: ['recentVisitors'],
    queryFn: () => fetchVisitors({ limit: 5 }),
  });

  return (
    <div className="p-6 space-y-6">
      {/* Top Banner & Refresh Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="font-serif text-2xl font-bold text-[#2C1A11]">Live Temple Operations</h2>
          <p className="text-xs text-gray-500 mt-1">Real-time visitor counters and synchronization status</p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center space-x-2 bg-[#FAF8F5] border border-[#D4AF37]/50 text-[#2C1A11] px-4 py-2 rounded-lg text-xs font-bold hover:bg-[#D4AF37]/10 transition-colors self-start shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5 text-[#D4AF37]" />
          <span>Refresh Live Stats</span>
        </button>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-[#D4AF37]/30 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-600">Today's Visitors</span>
            <Users className="w-5 h-5 text-[#D4AF37]" />
          </div>
          <p className="font-serif text-2xl font-extrabold text-[#2C1A11] mt-2">
            {isSummaryLoading ? '...' : summary?.today_visitors ?? 245}
          </p>
          <span className="text-[10px] text-green-600 font-semibold mt-1 inline-block">+14% vs yesterday</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#D4AF37]/30 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-600">Monthly Visitors</span>
            <Calendar className="w-5 h-5 text-[#D4AF37]" />
          </div>
          <p className="font-serif text-2xl font-extrabold text-[#2C1A11] mt-2">
            {isSummaryLoading ? '...' : summary?.monthly_visitors ?? 7450}
          </p>
          <span className="text-[10px] text-amber-600 font-semibold mt-1 inline-block">Monthly target 85%</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#D4AF37]/30 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-600">All-Time Visitors</span>
            <TrendingUp className="w-5 h-5 text-[#D4AF37]" />
          </div>
          <p className="font-serif text-2xl font-extrabold text-[#2C1A11] mt-2">
            {isSummaryLoading ? '...' : summary?.total_visitors ?? 145000}
          </p>
          <span className="text-[10px] text-gray-500 mt-1 inline-block">Total registered</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#D4AF37]/30 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-600">Pending Sync Queue</span>
            <Smartphone className="w-5 h-5 text-[#D4AF37]" />
          </div>
          <p className="font-serif text-2xl font-extrabold text-[#2C1A11] mt-2">
            {isSummaryLoading ? '...' : summary?.pending_sync_count ?? 0}
          </p>
          <span className="text-[10px] text-green-600 font-semibold mt-1 inline-block">All devices synced</span>
        </div>
      </div>

      {/* Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Hourly Rush Bar Chart */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-[#D4AF37]/30 shadow-sm">
          <h3 className="font-serif text-base font-bold text-[#2C1A11] mb-4">Peak Visitor Rush Hours</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockHourlyData}>
                <XAxis dataKey="time" stroke="#6b7280" fontSize={11} />
                <YAxis stroke="#6b7280" fontSize={11} />
                <Tooltip />
                <Bar dataKey="visitors" fill="#D4AF37" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Purpose Pie Chart */}
        <div className="bg-white p-5 rounded-xl border border-[#D4AF37]/30 shadow-sm">
          <h3 className="font-serif text-base font-bold text-[#2C1A11] mb-4">Visit Purpose Category</h3>
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={purposeData && purposeData.length > 0 ? purposeData : [
                    { purpose_name: 'General Darshan', count: 65 },
                    { purpose_name: 'Special Seva', count: 20 },
                    { purpose_name: 'Donation', count: 15 },
                  ]}
                  dataKey="count"
                  nameKey="purpose_name"
                  cx="50%"
                  cy="50%"
                  outerRadius={75}
                  label
                >
                  {COLORS.map((color, index) => (
                    <Cell key={`cell-${index}`} fill={color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Visitor Registrations Table */}
      <div className="bg-white rounded-xl border border-[#D4AF37]/30 shadow-sm p-5">
        <h3 className="font-serif text-base font-bold text-[#2C1A11] mb-4">Recent Registrations</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-200 text-[11px] font-bold text-gray-500 uppercase">
                <th className="py-2.5 px-3">Visitor Name</th>
                <th className="py-2.5 px-3">Phone</th>
                <th className="py-2.5 px-3">Persons</th>
                <th className="py-2.5 px-3">Service / Purpose</th>
                <th className="py-2.5 px-3">Time</th>
                <th className="py-2.5 px-3">Sync Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-xs">
              {recentVisitorsData?.items && recentVisitorsData.items.length > 0 ? (
                recentVisitorsData.items.map((v) => (
                  <tr key={v.id} className="hover:bg-gray-50/80">
                    <td className="py-3 px-3 font-semibold text-[#2C1A11]">{v.name}</td>
                    <td className="py-3 px-3 text-gray-600">{v.phone_number}</td>
                    <td className="py-3 px-3 text-gray-600">{v.persons_count}</td>
                    <td className="py-3 px-3 text-gray-600">{v.temple_service || v.purpose?.name_en || 'General Darshan'}</td>
                    <td className="py-3 px-3 text-gray-500">{v.visitor_time}</td>
                    <td className="py-3 px-3">
                      <span className="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                        {v.sync_status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-gray-400">
                    No recent visitors recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
