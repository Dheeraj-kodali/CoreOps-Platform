'use client';

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { GenericChartDataPoint } from '../../../types/report';

interface GenericChartProps {
  data: GenericChartDataPoint[];
  color?: string;
}

export function GenericBarChart({ data, color = '#FF9933' }: GenericChartProps) {
  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#D4AF37" strokeOpacity={0.15} />
          <XAxis dataKey="label" stroke="#888888" fontSize={11} tickLine={false} />
          <YAxis stroke="#888888" fontSize={11} tickLine={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1C1410', borderColor: '#D4AF37', borderRadius: '12px', color: '#FAFAFA' }}
          />
          <Bar dataKey="value" fill={color} radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
