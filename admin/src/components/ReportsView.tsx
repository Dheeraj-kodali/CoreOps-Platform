"use client";

import React, { useState } from "react";
import { FileText, FileSpreadsheet, FileCode, Download, Calendar } from "lucide-react";

interface ReportsViewProps {
  language: "en" | "te";
}

export default function ReportsView() {
  const language: string = "en";
  const [reportType, setReportType] = useState("DAILY");
  const [format, setFormat] = useState("pdf");

  const reportsList = [
    { title: "Daily Visitor Summary", desc: "Detailed breakdown of entries, purposes, and rush hours for today", type: "DAILY" },
    { title: "Weekly Demographic Audit", desc: "Village-level visitor counts and gender distribution for the week", type: "WEEKLY" },
    { title: "Monthly Seva Performance", desc: "Seva revenue, volunteer throughput, and purpose totals for July 2026", type: "MONTHLY" },
    { title: "Volunteer Activity Log", desc: "Registration logs grouped by active volunteers and device IDs", type: "VOLUNTEER" },
  ];

  return (
    <div className="space-y-6">
      <div className="temple-card p-6">
        <h3 className="heading-temple text-xl font-bold text-[#2C1A11] mb-2">
          {language === "te" ? "కస్టమ్ రిపోర్ట్ ఎగుమతి" : "Custom Report Export Engine"}
        </h3>
        <p className="text-xs text-amber-800 mb-6">Select report criteria and export format for single-click download.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-xs font-bold uppercase text-amber-900 mb-2">Date Range</label>
            <div className="flex items-center gap-2">
              <input type="date" className="w-full p-2 text-sm border border-[#D4AF37]/40 rounded-lg bg-white" defaultValue="2026-07-01" />
              <span className="text-xs text-gray-500">to</span>
              <input type="date" className="w-full p-2 text-sm border border-[#D4AF37]/40 rounded-lg bg-white" defaultValue="2026-07-26" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-amber-900 mb-2">Report Type</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full p-2 text-sm border border-[#D4AF37]/40 rounded-lg bg-white text-[#2C1A11]"
            >
              <option value="DAILY">Daily Visitor Report</option>
              <option value="WEEKLY">Weekly Overview Report</option>
              <option value="MONTHLY">Monthly Audit Report</option>
              <option value="VOLUNTEER">Volunteer Activity Report</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-amber-900 mb-2">Export Format</label>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setFormat("pdf")}
                className={`flex-1 py-2 px-3 rounded-lg border text-xs font-bold flex items-center justify-center gap-1 ${
                  format === "pdf" ? "bg-[#900C3F] text-white border-[#900C3F]" : "border-gray-300 bg-white"
                }`}
              >
                <FileText className="w-4 h-4" /> PDF
              </button>
              <button
                onClick={() => setFormat("excel")}
                className={`flex-1 py-2 px-3 rounded-lg border text-xs font-bold flex items-center justify-center gap-1 ${
                  format === "excel" ? "bg-green-700 text-white border-green-700" : "border-gray-300 bg-white"
                }`}
              >
                <FileSpreadsheet className="w-4 h-4" /> Excel
              </button>
              <button
                onClick={() => setFormat("csv")}
                className={`flex-1 py-2 px-3 rounded-lg border text-xs font-bold flex items-center justify-center gap-1 ${
                  format === "csv" ? "bg-[#2C1A11] text-[#D4AF37] border-[#2C1A11]" : "border-gray-300 bg-white"
                }`}
              >
                <FileCode className="w-4 h-4" /> CSV
              </button>
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-[#D4AF37] to-[#997A15] text-[#2C1A11] font-bold text-sm rounded-lg shadow-lg hover:opacity-95 transition-all">
            <Download className="w-4 h-4" /> Generate & Download Report
          </button>
        </div>
      </div>

      {/* Available Report Catalog */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reportsList.map((rep, idx) => (
          <div key={idx} className="temple-card p-6 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-[#D4AF37]/30">
                {rep.type}
              </span>
              <h4 className="heading-temple text-base font-bold text-[#2C1A11] mt-2">{rep.title}</h4>
              <p className="text-xs text-gray-600 mt-1">{rep.desc}</p>
            </div>
            <div className="mt-4 pt-4 border-t border-amber-100 flex items-center justify-between">
              <span className="text-xs text-gray-400">Ready for instant stream</span>
              <button className="text-xs font-bold text-[#2C1A11] hover:text-[#D4AF37] flex items-center gap-1">
                <Download className="w-3.5 h-3.5" /> Download
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
