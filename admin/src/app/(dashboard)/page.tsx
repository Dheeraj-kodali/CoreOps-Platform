'use client';

import React from 'react';
import { Users, UserCheck, ShieldCheck, Activity, ArrowUpRight } from 'lucide-react';
import { StatsCard } from '../../components/shared/stats-card';

export default function ExecutiveDashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header Overview Banner */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#1C1410] via-[#2C1A11] to-[#1C1410] border border-[#D4AF37]/40 text-[#FAFAFA] shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="px-3 py-1 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] text-xs font-semibold uppercase tracking-wider border border-[#D4AF37]/30">
            Enterprise SaaS Edition
          </span>
          <h1 className="text-2xl md:text-3xl font-bold mt-2 font-serif text-[#D4AF37]">
            Sri Kalki Seva Alayam
          </h1>
          <p className="text-xs text-[#FAFAFA]/70 mt-1 max-w-xl">
            Real-time Visitor Footfall, Volunteer Tracking & Analytics Command Center.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-semibold text-xs shadow-md hover:brightness-110 transition-all flex items-center">
            <span>Register Visitor</span>
            <ArrowUpRight className="w-4 h-4 ml-1.5" />
          </button>
        </div>
      </div>

      {/* Key Executive Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Today's Footfall"
          value="1,248"
          change="+18.5%"
          isPositive={true}
          icon={Users}
          description="Total visitors checked in today"
        />
        <StatsCard
          title="Active Volunteers"
          value="14"
          change="Gate 1 & 2"
          isPositive={true}
          icon={UserCheck}
          description="Volunteers actively registering visitors"
        />
        <StatsCard
          title="Sync Status"
          value="100%"
          change="0 Pending"
          isPositive={true}
          icon={Activity}
          description="All mobile offline devices synced"
        />
        <StatsCard
          title="System Health"
          value="Optimal"
          change="Postgres RLS Active"
          isPositive={true}
          icon={ShieldCheck}
          description="Multi-tenant security isolation active"
        />
      </div>
    </div>
  );
}
