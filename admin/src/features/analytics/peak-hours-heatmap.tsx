'use client';

import React from 'react';
import { Clock, Zap } from 'lucide-react';
import { PeakHourDataPoint } from '../../types/analytics';

interface PeakHoursHeatmapProps {
  data: PeakHourDataPoint[];
}

export function PeakHoursHeatmap({ data }: PeakHoursHeatmapProps) {
  if (!data || data.length === 0) {
    return <div className="h-48 flex items-center justify-center text-xs text-gray-400">No peak hour data available</div>;
  }

  const getSurgeColor = (level: string) => {
    switch (level) {
      case 'PEAK':
        return 'bg-gradient-to-br from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold shadow-md ring-2 ring-[#D4AF37]/50';
      case 'HIGH':
        return 'bg-[#FF9933]/80 text-white font-semibold';
      case 'MEDIUM':
        return 'bg-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] font-medium';
      default:
        return 'bg-gray-100 dark:bg-[#2C1A11] text-gray-500 dark:text-gray-400';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2 text-xs font-bold text-[#D4AF37] uppercase tracking-wider">
          <Clock className="w-4 h-4" />
          <span>Hourly Surge Intensity Heatmap</span>
        </div>

        <div className="flex items-center space-x-3 text-[10px]">
          <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-gray-200 dark:bg-[#2C1A11] mr-1"></span> Low</span>
          <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-[#D4AF37]/40 mr-1"></span> Med</span>
          <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-[#FF9933] mr-1"></span> High</span>
          <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-[#D4AF37] mr-1"></span> Peak</span>
        </div>
      </div>

      <div className="grid grid-cols-4 sm:grid-cols-6 lg:grid-cols-12 gap-2">
        {data.map((item, idx) => (
          <div
            key={idx}
            className={`p-2.5 rounded-xl border border-gray-200 dark:border-[#D4AF37]/20 text-center transition-all ${getSurgeColor(
              item.surge_level
            )}`}
          >
            <span className="text-[10px] block opacity-80">{item.hour_label}</span>
            <span className="text-sm font-bold block mt-0.5">{item.visitor_count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
