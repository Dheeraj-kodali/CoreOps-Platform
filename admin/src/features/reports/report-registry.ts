import { ReportTemplateConfig, ReportType } from '../../types/report';

export const REPORT_TEMPLATES: ReportTemplateConfig[] = [
  {
    id: 'DAILY_VISITORS',
    title: "Daily Visitor Footfall Report",
    description: 'Day-by-day aggregated check-in volume, group size breakdown, and peak surges.',
    chartType: 'area',
    category: 'VISITOR',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'WEEKLY_VISITORS',
    title: 'Weekly Visitor Volume Trend',
    description: 'Weekly darshan footfall aggregation and week-over-week growth percentage.',
    chartType: 'bar',
    category: 'VISITOR',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'MONTHLY_VISITORS',
    title: 'Monthly Visitor Summary',
    description: 'Monthly historical trend comparison across festival seasons.',
    chartType: 'line',
    category: 'VISITOR',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'YEARLY_VISITORS',
    title: 'Yearly Temple Growth Audit',
    description: 'Multi-year annual footfall analysis and broad demographic growth.',
    chartType: 'bar',
    category: 'VISITOR',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'PURPOSE_DISTRIBUTION',
    title: 'Visit Purpose Breakdown',
    description: 'Distribution between General Darshan, Special Seva, Volunteers, and Annadanam.',
    chartType: 'pie',
    category: 'OPERATIONS',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'VILLAGE_DISTRIBUTION',
    title: 'Village & Regional Demographics',
    description: 'Origin village analytics identifying top regional visitor clusters.',
    chartType: 'donut',
    category: 'OPERATIONS',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'VOLUNTEER_PERFORMANCE',
    title: 'Volunteer Check-in Performance',
    description: 'Registrations processed per volunteer, duty shift hours, and device logs.',
    chartType: 'bar',
    category: 'VOLUNTEER',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'VISITOR_STATUS_SUMMARY',
    title: 'Lifecycle Status Summary',
    description: 'Distribution across Registered, Checked-In, Inside Temple, and Completed.',
    chartType: 'pie',
    category: 'OPERATIONS',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'REPEAT_VISITORS',
    title: 'Repeat & Frequent Devotee Audit',
    description: 'Analysis of repeat visitor check-ins and devotee loyalty metrics.',
    chartType: 'area',
    category: 'VISITOR',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'PEAK_HOURS',
    title: 'Peak Hourly Surge Analysis',
    description: 'Hourly check-in heatmaps for darshan queue management and staffing.',
    chartType: 'area',
    category: 'OPERATIONS',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'QUEUE_STATISTICS',
    title: 'Darshan Queue Time Analytics',
    description: 'Average wait time per queue line and entry gate throughput.',
    chartType: 'line',
    category: 'SYSTEM',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
  {
    id: 'QR_SCAN_ACTIVITY',
    title: 'Gate QR Pass Scan Activity',
    description: 'Digital QR token scan verification volume per entry gate scanner.',
    chartType: 'bar',
    category: 'SYSTEM',
    supportedFormats: ['pdf', 'excel', 'csv', 'print'],
  },
];

export function getTemplateById(id: ReportType): ReportTemplateConfig {
  return REPORT_TEMPLATES.find((t) => t.id === id) || REPORT_TEMPLATES[0];
}
