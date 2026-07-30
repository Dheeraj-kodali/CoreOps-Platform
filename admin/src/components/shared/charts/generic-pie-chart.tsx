'use client';

import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { GenericChartDataPoint } from '../../../types/report';

const COLORS = ['#D4AF37', '#FF9933', '#2C1A11', '#10B981', '#3B82F6', '#8B5CF6'];

interface GenericChartProps {
  data: GenericChartDataPoint[];
  innerRadius?: number;
}

export function GenericPieChart({ data, innerRadius = 0 }: GenericChartProps) {
  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={innerRadius}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
            nameKey="label"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#1C1410', borderColor: '#D4AF37', borderRadius: '12px', color: '#FAFAFA' }}
          />
          <Legend wrapperStyle={{ fontSize: '11px' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
