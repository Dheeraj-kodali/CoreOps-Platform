import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  icon: LucideIcon;
  description?: string;
}

export function StatsCard({ title, value, change, isPositive = true, icon: Icon, description }: StatsCardProps) {
  return (
    <div className="p-5 rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm hover:shadow-md hover:border-[#D4AF37]/50 transition-all duration-300">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-[#FAFAFA]/70">{title}</span>
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#D4AF37]/20 to-[#FF9933]/20 flex items-center justify-center text-[#D4AF37]">
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-[#FAFAFA] font-serif">{value}</h3>
        {change && (
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${isPositive ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-400' : 'bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-400'}`}>
            {change}
          </span>
        )}
      </div>
      {description && <p className="mt-2 text-[11px] text-gray-500 dark:text-[#FAFAFA]/60">{description}</p>}
    </div>
  );
}
