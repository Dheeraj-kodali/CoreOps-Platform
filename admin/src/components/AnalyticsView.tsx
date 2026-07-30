"use client";

import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, AreaChart, Area } from "recharts";

interface AnalyticsViewProps {
  language: "en" | "te";
}

export default function AnalyticsView() {
  const language: string = "en";
  const genderAgeData = [
    { group: "1-18 Yrs", male: 45, female: 52 },
    { group: "19-35 Yrs", male: 120, female: 110 },
    { group: "36-50 Yrs", male: 180, female: 165 },
    { group: "51+ Yrs", male: 95, female: 130 },
  ];

  const monthlyTrendData = [
    { month: "Jan", visitors: 4200 },
    { month: "Feb", visitors: 5100 },
    { month: "Mar", visitors: 6800 },
    { month: "Apr", visitors: 8200 },
    { month: "May", visitors: 7400 },
    { month: "Jun", visitors: 8900 },
    { month: "Jul", visitors: 9500 },
  ];

  return (
    <div className="space-y-6">
      <div className="temple-card p-6">
        <h3 className="heading-temple text-xl font-bold text-[#2C1A11] mb-2">
          {language === "te" ? "మాసపు వృద్ధి ట్రెండ్" : "Monthly Visitor Growth Trajectory"}
        </h3>
        <p className="text-xs text-amber-800 mb-4">Historical throughput comparison for 2026</p>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthlyTrendData}>
              <defs>
                <linearGradient id="colorVis" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#D4AF37" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#D4AF37" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="month" stroke="#888" fontSize={12} />
              <YAxis stroke="#888" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: "#2C1A11", borderRadius: "8px", color: "#FFF" }} />
              <Area type="monotone" dataKey="visitors" stroke="#997A15" fillOpacity={1} fill="url(#colorVis)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="temple-card p-6">
          <h4 className="heading-temple text-lg font-bold text-[#2C1A11] mb-2">Age & Gender Demographics</h4>
          <p className="text-xs text-amber-800 mb-4">Male vs Female distribution per age band</p>

          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={genderAgeData}>
                <XAxis dataKey="group" stroke="#888" fontSize={12} />
                <YAxis stroke="#888" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: "#2C1A11", color: "#FFF" }} />
                <Bar dataKey="male" fill="#2C1A11" radius={[4, 4, 0, 0]} />
                <Bar dataKey="female" fill="#D4AF37" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="temple-card p-6">
          <h4 className="heading-temple text-lg font-bold text-[#2C1A11] mb-2">Top Origin Villages</h4>
          <p className="text-xs text-amber-800 mb-4">Highest visitor contributions by region</p>

          <div className="space-y-3">
            {[
              { village: "Tirupati Rural", count: 2450, percentage: 32 },
              { village: "Kalki Nagaram", count: 1890, percentage: 25 },
              { village: "Madanapalle", count: 1210, percentage: 16 },
              { village: "Chittoor Town", count: 980, percentage: 13 },
            ].map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-[#2C1A11]">{item.village}</span>
                  <span className="text-amber-900 font-bold">{item.count} ({item.percentage}%)</span>
                </div>
                <div className="w-full h-2 rounded-full bg-amber-100 overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-[#D4AF37] to-[#997A15]" style={{ width: `${item.percentage}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
