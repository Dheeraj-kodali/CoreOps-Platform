'use client';

import React from 'react';
import { Calendar, Filter, RefreshCw, Search } from 'lucide-react';
import { ReportFilterState } from '../../types/report';

interface ReportFilterEngineProps {
  filters: ReportFilterState;
  onChange: (filters: ReportFilterState) => void;
  onReset: () => void;
}

export function ReportFilterEngine({ filters, onChange, onReset }: ReportFilterEngineProps) {
  return (
    <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-3">
      <div className="flex items-center space-x-2 text-xs font-bold text-[#D4AF37] uppercase tracking-wider mb-2">
        <Filter className="w-4 h-4" />
        <span>Universal Report Filter System</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Date From */}
        <div className="relative">
          <Calendar className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="date"
            value={filters.date_from || ''}
            onChange={(e) => onChange({ ...filters, date_from: e.target.value })}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
          />
        </div>

        {/* Date To */}
        <div className="relative">
          <Calendar className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="date"
            value={filters.date_to || ''}
            onChange={(e) => onChange({ ...filters, date_to: e.target.value })}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
          />
        </div>

        {/* Visitor Status Filter */}
        <div>
          <select
            value={filters.status || ''}
            onChange={(e) => onChange({ ...filters, status: e.target.value || undefined })}
            className="w-full px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
          >
            <option value="">All Statuses</option>
            <option value="REGISTERED">Registered</option>
            <option value="CHECKED_IN">Checked In</option>
            <option value="INSIDE_TEMPLE">Inside Temple</option>
            <option value="COMPLETED">Completed</option>
          </select>
        </div>

        {/* Reset Action */}
        <button
          onClick={onReset}
          className="py-2 px-3 rounded-xl bg-gray-100 dark:bg-[#2C1A11] text-xs font-semibold text-gray-600 dark:text-[#FAFAFA]/70 hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-colors flex items-center justify-center space-x-1"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Filters</span>
        </button>
      </div>
    </div>
  );
}
