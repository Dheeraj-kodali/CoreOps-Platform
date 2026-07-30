'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, Download, Printer, BarChart2, Layers, CheckCircle2 } from 'lucide-react';
import { REPORT_TEMPLATES, getTemplateById } from '../../../features/reports/report-registry';
import { ReportFilterEngine } from '../../../features/reports/report-filter-engine';
import { GenericChartRenderer } from '../../../components/shared/charts/generic-chart-renderer';
import { StatsCard } from '../../../components/shared/stats-card';
import { ExportService } from '../../../services/export-service';
import { ReportFilterState, ReportDataResponse, ReportType } from '../../../types/report';
import { ReportRepository } from '../../../repositories/report-repository';

export default function ReportingPortalPage() {
  const [selectedTemplateId, setSelectedTemplateId] = useState<ReportType>('DAILY_VISITORS');
  const [filters, setFilters] = useState<ReportFilterState>({});

  const activeTemplate = getTemplateById(selectedTemplateId);

  // TanStack Query for Report Data
  const { data: reportData, isLoading, isError } = useQuery<ReportDataResponse>({
    queryKey: ['report-engine', selectedTemplateId, filters],
    queryFn: async () => {
      // In production, fetches through ReportRepository -> ReportApi -> FastAPI ReportService
      // Mock structured report response matching FastAPI backend schema
      return {
        report_type: selectedTemplateId,
        title: activeTemplate.title,
        generated_at: new Date().toLocaleString(),
        summary_kpis: [
          { title: 'Total Volume', value: '1,420', change: '+14.2%', isPositive: true },
          { title: 'Peak Surges', value: '09:00 - 11:00 AM', isPositive: true },
          { title: 'Completion Rate', value: '94.8%', change: '+2.1%', isPositive: true },
        ],
        chart_data: [
          { label: '06:00 AM', value: 120 },
          { label: '08:00 AM', value: 340 },
          { label: '10:00 AM', value: 580 },
          { label: '12:00 PM', value: 420 },
          { label: '02:00 PM', value: 290 },
          { label: '04:00 PM', value: 450 },
          { label: '06:00 PM', value: 610 },
          { label: '08:00 PM', value: 210 },
        ],
        table_headers: ['Time Slot / Metric', 'Total Check-ins', 'Group Count', 'Status Rate'],
        table_rows: [
          ['06:00 AM - 08:00 AM', '120', '350', '98%'],
          ['08:00 AM - 10:00 AM', '340', '890', '96%'],
          ['10:00 AM - 12:00 PM', '580', '1,420', '94%'],
          ['12:00 PM - 02:00 PM', '420', '1,050', '95%'],
          ['02:00 PM - 04:00 PM', '290', '710', '93%'],
        ],
      };
    },
  });

  const handleExport = (format: 'pdf' | 'excel' | 'csv' | 'print') => {
    if (reportData) {
      ExportService.exportReport(reportData, format);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner & Export Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
            Reporting & Export Engine
          </h1>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">
            Enterprise Report Template Registry, Reusable Aggregations & Multi-Format Exporter
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => handleExport('csv')}
            className="px-3.5 py-2 rounded-xl bg-gray-100 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] text-xs font-semibold hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-all flex items-center space-x-1.5"
          >
            <Download className="w-4 h-4 text-[#D4AF37]" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => handleExport('excel')}
            className="px-3.5 py-2 rounded-xl bg-gray-100 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] text-xs font-semibold hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-all flex items-center space-x-1.5"
          >
            <Download className="w-4 h-4 text-[#D4AF37]" />
            <span>Export Excel</span>
          </button>
          <button
            onClick={() => handleExport('print')}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] text-xs font-bold shadow-md hover:brightness-110 transition-all flex items-center space-x-1.5"
          >
            <Printer className="w-4 h-4" />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Template Selector Registry */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-xs font-bold text-[#D4AF37] uppercase tracking-wider">
          <Layers className="w-4 h-4" />
          <span>Report Template Registry</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
          {REPORT_TEMPLATES.map((tmpl) => {
            const isSelected = tmpl.id === selectedTemplateId;
            return (
              <button
                key={tmpl.id}
                onClick={() => setSelectedTemplateId(tmpl.id)}
                className={`p-3 rounded-xl text-left border transition-all ${
                  isSelected
                    ? 'bg-gradient-to-r from-[#D4AF37]/20 to-[#FF9933]/20 border-[#D4AF37] shadow-sm'
                    : 'bg-gray-50 dark:bg-[#2C1A11] border-gray-200 dark:border-[#D4AF37]/20 hover:border-[#D4AF37]/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase text-[#D4AF37]">{tmpl.category}</span>
                  {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-[#D4AF37]" />}
                </div>
                <p className="text-xs font-bold mt-1 text-gray-900 dark:text-[#FAFAFA] truncate">{tmpl.title}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Universal Report Filter Engine */}
      <ReportFilterEngine filters={filters} onChange={setFilters} onReset={() => setFilters({})} />

      {/* Report KPI Metrics Summary */}
      {reportData && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {reportData.summary_kpis.map((kpi, idx) => (
            <StatsCard key={idx} title={kpi.title} value={kpi.value} change={kpi.change} isPositive={kpi.isPositive} icon={BarChart2} />
          ))}
        </div>
      )}

      {/* Reusable Chart Visualization Section */}
      {reportData && (
        <div className="p-6 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold font-serif text-gray-900 dark:text-[#D4AF37]">{reportData.title}</h3>
            <span className="text-[10px] text-gray-400 font-mono">Chart Engine: {activeTemplate.chartType.toUpperCase()}</span>
          </div>

          <GenericChartRenderer type={activeTemplate.chartType} data={reportData.chart_data} />
        </div>
      )}

      {/* Generic Report Data Table */}
      {reportData && (
        <div className="rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 dark:bg-[#2C1A11] border-b border-gray-200 dark:border-[#D4AF37]/20 text-gray-500 dark:text-[#D4AF37] uppercase font-semibold">
                  {reportData.table_headers.map((h, i) => (
                    <th key={i} className="py-3.5 px-4">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-[#D4AF37]/10">
                {reportData.table_rows.map((row, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-gray-50/50 dark:hover:bg-[#2C1A11]/40 transition-colors">
                    {row.map((cell, cellIdx) => (
                      <td key={cellIdx} className="py-3.5 px-4 text-gray-800 dark:text-[#FAFAFA]">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
