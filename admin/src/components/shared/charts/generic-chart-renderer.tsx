'use client';

import React from 'react';
import { GenericChartDataPoint } from '../../../types/report';
import { GenericAreaChart } from './generic-area-chart';
import { GenericBarChart } from './generic-bar-chart';
import { GenericLineChart } from './generic-line-chart';
import { GenericPieChart } from './generic-pie-chart';

interface GenericChartRendererProps {
  type: 'area' | 'bar' | 'line' | 'pie' | 'donut' | 'table';
  data: GenericChartDataPoint[];
}

export function GenericChartRenderer({ type, data }: GenericChartRendererProps) {
  if (!data || data.length === 0) {
    return <div className="h-64 flex items-center justify-center text-xs text-gray-400">No chart data available</div>;
  }

  switch (type) {
    case 'area':
      return <GenericAreaChart data={data} />;
    case 'bar':
      return <GenericBarChart data={data} />;
    case 'line':
      return <GenericLineChart data={data} />;
    case 'pie':
      return <GenericPieChart data={data} />;
    case 'donut':
      return <GenericPieChart data={data} innerRadius={55} />;
    default:
      return <GenericAreaChart data={data} />;
  }
}
