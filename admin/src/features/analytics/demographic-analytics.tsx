'use client';

import React from 'react';
import { MapPin, UserCheck, Award } from 'lucide-react';
import { VillageDemographicPoint } from '../../types/analytics';

interface DemographicAnalyticsProps {
  villages: VillageDemographicPoint[];
}

export function DemographicAnalytics({ villages }: DemographicAnalyticsProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 text-xs font-bold text-[#D4AF37] uppercase tracking-wider">
        <MapPin className="w-4 h-4" />
        <span>Top Origin Villages & Regional Clusters</span>
      </div>

      <div className="space-y-2.5">
        {villages.map((v, idx) => (
          <div key={idx} className="p-3 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="w-6 h-6 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] font-bold text-xs flex items-center justify-center">
                #{idx + 1}
              </span>
              <div>
                <p className="text-xs font-bold text-gray-800 dark:text-[#FAFAFA]">{v.village_name}</p>
                <p className="text-[10px] text-gray-400">{v.district}</p>
              </div>
            </div>

            <div className="text-right">
              <p className="text-xs font-bold text-gray-800 dark:text-[#FAFAFA]">{v.visitor_count} Visitors</p>
              <p className="text-[10px] font-semibold text-[#D4AF37]">{v.percentage}% of total</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
