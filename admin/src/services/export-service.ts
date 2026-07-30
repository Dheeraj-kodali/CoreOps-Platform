import { ExportFormat, ReportDataResponse } from '../types/report';

export class ExportService {
  /**
   * Universal Export Execution Handler.
   */
  static exportReport(data: ReportDataResponse, format: ExportFormat): void {
    switch (format) {
      case 'csv':
      case 'excel':
        this.exportCSV(data);
        break;
      case 'pdf':
      case 'print':
        this.printReport(data);
        break;
      default:
        this.exportCSV(data);
    }
  }

  private static exportCSV(data: ReportDataResponse): void {
    if (!data.table_headers || !data.table_rows) return;

    const headersStr = data.table_headers.map((h) => `"${h}"`).join(',') + '\n';
    const rowsStr = data.table_rows
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n');

    const csvContent = headersStr + rowsStr;
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${data.report_type.toLowerCase()}_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  private static printReport(data: ReportDataResponse): void {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const kpiHTML = data.summary_kpis
      .map(
        (kpi) => `
        <div style="border: 1px solid #D4AF37; padding: 12px; border-radius: 8px; flex: 1; text-align: center;">
          <div style="font-size: 10px; text-transform: uppercase; color: #666;">${kpi.title}</div>
          <div style="font-size: 18px; font-weight: bold; color: #2C1A11;">${kpi.value}</div>
        </div>
      `
      )
      .join('');

    const tableHeadersHTML = data.table_headers.map((h) => `<th style="padding: 8px; border-bottom: 2px solid #D4AF37; text-align: left;">${h}</th>`).join('');
    const tableRowsHTML = data.table_rows
      .map(
        (row) => `<tr>${row.map((cell) => `<td style="padding: 8px; border-bottom: 1px solid #eee;">${cell}</td>`).join('')}</tr>`
      )
      .join('');

    const content = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>${data.title} - Sri Kalki Seva Alayam</title>
          <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; color: #1C1410; }
            .header { text-align: center; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; margin-bottom: 20px; }
            .kpis { display: flex; gap: 15px; margin-bottom: 25px; }
            table { width: 100%; border-collapse: collapse; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1 style="color: #D4AF37; margin: 0;">Sri Kalki Seva Alayam</h1>
            <h3 style="margin: 5px 0;">${data.title}</h3>
            <p style="font-size: 11px; color: #666;">Generated on: ${data.generated_at}</p>
          </div>
          <div class="kpis">${kpiHTML}</div>
          <table>
            <thead><tr>${tableHeadersHTML}</tr></thead>
            <tbody>${tableRowsHTML}</tbody>
          </table>
          <script>
            window.onload = function() { window.print(); }
          </script>
        </body>
      </html>
    `;

    printWindow.document.write(content);
    printWindow.document.close();
  }
}
