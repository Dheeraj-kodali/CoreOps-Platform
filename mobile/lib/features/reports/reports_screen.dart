import 'dart:io';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:share_plus/share_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:excel/excel.dart' as excel_pkg;
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/widgets/shared/temple_app_bar.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({Key? key}) : super(key: key);

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  final _repository = VisitorRepository();
  bool _isLoading = false;
  String _selectedFilter = 'TODAY'; // TODAY, WEEKLY, MONTHLY, CUSTOM
  List<VisitorModel> _visitors = [];

  @override
  void initState() {
    super.initState();
    _loadReportData();
  }

  Future<void> _loadReportData() async {
    setState(() => _isLoading = true);
    final data = await _repository.getFilteredVisitors(filterType: _selectedFilter);
    if (mounted) {
      setState(() {
        _visitors = data;
        _isLoading = false;
      });
    }
  }

  // Generate Professional PDF Document
  Future<pw.Document> _buildPdfDocument(String title) async {
    final pdf = pw.Document();
    final nowStr = DateTime.now().toString().split('.').first;

    final totalCount = _visitors.length;
    final totalMembers = _visitors.fold<int>(0, (sum, v) => sum + v.personsCount);
    final insideCount = _visitors.where((v) => v.status == 'CHECKED_IN' || v.status == 'INSIDE').fold<int>(0, (sum, v) => sum + v.personsCount);
    final leftCount = _visitors.where((v) => v.status == 'CHECKED_OUT').fold<int>(0, (sum, v) => sum + v.personsCount);

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        header: (pw.Context context) => pw.Column(
          crossAxisAlignment: pw.CrossAxisAlignment.start,
          children: [
            pw.Row(
              mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
              children: [
                pw.Text('SRI KALKI SEVA ALAYAM', style: pw.TextStyle(fontSize: 18, fontWeight: pw.FontWeight.bold, color: PdfColors.brown900)),
                pw.Text('Report: $title', style: pw.TextStyle(fontSize: 12, fontWeight: pw.FontWeight.bold)),
              ],
            ),
            pw.Text('Sacred Visitor Management & Analytics System', style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700)),
            pw.Divider(thickness: 1, color: PdfColors.amber800),
            pw.SizedBox(height: 10),
          ],
        ),
        footer: (pw.Context context) => pw.Row(
          mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
          children: [
            pw.Text('Generated: $nowStr | Filter: $_selectedFilter', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey600)),
            pw.Text('Page ${context.pageNumber} of ${context.pagesCount}', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey600)),
          ],
        ),
        build: (pw.Context context) => [
          // Statistics Summary Cards
          pw.Container(
            padding: const pw.EdgeInsets.all(12),
            decoration: pw.BoxDecoration(
              color: PdfColors.amber50,
              borderRadius: const pw.BorderRadius.all(pw.Radius.circular(6)),
              border: pw.Border.all(color: PdfColors.amber300),
            ),
            child: pw.Row(
              mainAxisAlignment: pw.MainAxisAlignment.spaceAround,
              children: [
                pw.Column(children: [
                  pw.Text('Total Visits', style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700)),
                  pw.Text('$totalCount', style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold)),
                ]),
                pw.Column(children: [
                  pw.Text('Total Devotees', style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700)),
                  pw.Text('$totalMembers', style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold, color: PdfColors.brown900)),
                ]),
                pw.Column(children: [
                  pw.Text('Inside Temple', style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700)),
                  pw.Text('$insideCount', style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold, color: PdfColors.green800)),
                ]),
                pw.Column(children: [
                  pw.Text('Completed Visits', style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700)),
                  pw.Text('$leftCount', style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold, color: PdfColors.blueGrey800)),
                ]),
              ],
            ),
          ),
          pw.SizedBox(height: 16),

          // Visitor Table
          pw.Table.fromTextArray(
            headers: ['#', 'Visitor ID', 'Name', 'Phone', 'Village', 'Purpose', 'Psn', 'In', 'Out', 'Duration', 'Status'],
            data: List<List<String>>.generate(
              _visitors.length,
              (i) {
                final v = _visitors[i];
                return [
                  '${i + 1}',
                  v.id,
                  v.name,
                  v.phoneNumber,
                  v.village,
                  v.purpose,
                  '${v.personsCount}',
                  v.timeIn,
                  v.timeOut ?? '—',
                  v.formattedDuration,
                  v.displayStatus,
                ];
              },
            ),
            headerStyle: pw.TextStyle(fontSize: 8, fontWeight: pw.FontWeight.bold, color: PdfColors.white),
            headerDecoration: const pw.BoxDecoration(color: PdfColors.brown900),
            rowDecoration: const pw.BoxDecoration(border: pw.Border(bottom: pw.BorderSide(color: PdfColors.grey300, width: 0.5))),
            cellStyle: const pw.TextStyle(fontSize: 7),
            cellAlignment: pw.Alignment.centerLeft,
          ),
        ],
      ),
    );

    return pdf;
  }

  // Export Real XLSX Excel File
  Future<String> _generateExcelFile(String title) async {
    final excel = excel_pkg.Excel.createExcel();
    final sheet = excel['Visitor_Report'];
    excel.setDefaultSheet('Visitor_Report');

    // Header Row
    sheet.appendRow([
      excel_pkg.TextCellValue('#'),
      excel_pkg.TextCellValue('Visitor ID'),
      excel_pkg.TextCellValue('Name'),
      excel_pkg.TextCellValue('Phone Number'),
      excel_pkg.TextCellValue('Village'),
      excel_pkg.TextCellValue('Purpose'),
      excel_pkg.TextCellValue('Members Count'),
      excel_pkg.TextCellValue('Date'),
      excel_pkg.TextCellValue('Time In'),
      excel_pkg.TextCellValue('Time Out'),
      excel_pkg.TextCellValue('Duration'),
      excel_pkg.TextCellValue('Status'),
    ]);

    for (var i = 0; i < _visitors.length; i++) {
      final v = _visitors[i];
      sheet.appendRow([
        excel_pkg.IntCellValue(i + 1),
        excel_pkg.TextCellValue(v.id),
        excel_pkg.TextCellValue(v.name),
        excel_pkg.TextCellValue(v.phoneNumber),
        excel_pkg.TextCellValue(v.village),
        excel_pkg.TextCellValue(v.purpose),
        excel_pkg.IntCellValue(v.personsCount),
        excel_pkg.TextCellValue(v.visitorDate),
        excel_pkg.TextCellValue(v.timeIn),
        excel_pkg.TextCellValue(v.timeOut ?? ''),
        excel_pkg.TextCellValue(v.formattedDuration),
        excel_pkg.TextCellValue(v.displayStatus),
      ]);
    }

    final tempDir = await getTemporaryDirectory();
    final nowStr = DateTime.now().toIso8601String().replaceAll(':', '-').split('.').first;
    final filePath = '${tempDir.path}/${title.replaceAll(' ', '_')}_$_selectedFilter\_$nowStr.xlsx';
    final fileBytes = excel.save();

    if (fileBytes != null) {
      final file = File(filePath);
      await file.writeAsBytes(fileBytes);
      return filePath;
    }
    throw Exception('Failed to generate Excel bytes');
  }

  // Export CSV File
  Future<String> _generateCsvFile(String title) async {
    final tempDir = await getTemporaryDirectory();
    final nowStr = DateTime.now().toIso8601String().replaceAll(':', '-').split('.').first;
    final filePath = '${tempDir.path}/${title.replaceAll(' ', '_')}_$_selectedFilter\_$nowStr.csv';
    final buffer = StringBuffer();
    buffer.writeln('Visitor ID,Name,Phone Number,Village,Purpose,Members Count,Date,Time In,Time Out,Duration,Status');

    for (var v in _visitors) {
      buffer.writeln('"${v.id}","${v.name}","${v.phoneNumber}","${v.village}","${v.purpose}",${v.personsCount},"${v.visitorDate}","${v.timeIn}","${v.timeOut ?? ''}","${v.formattedDuration}","${v.displayStatus}"');
    }

    final file = File(filePath);
    await file.writeAsString(buffer.toString());
    return filePath;
  }

  // Action Handler: Export & Share
  Future<void> _handleExport(String title, String type) async {
    try {
      if (type.contains('PDF')) {
        final pdf = await _buildPdfDocument(title);
        final bytes = await pdf.save();
        final tempDir = await getTemporaryDirectory();
        final filePath = '${tempDir.path}/${title.replaceAll(' ', '_')}_$_selectedFilter.pdf';
        final file = File(filePath);
        await file.writeAsBytes(bytes);
        await Share.shareXFiles([XFile(filePath)], text: 'Temple Visitor Report — $title (PDF)');
      } else if (type.contains('Excel')) {
        final filePath = await _generateExcelFile(title);
        await Share.shareXFiles([XFile(filePath)], text: 'Temple Visitor Report — $title (Excel XLSX)');
      } else {
        final filePath = await _generateCsvFile(title);
        await Share.shareXFiles([XFile(filePath)], text: 'Temple Visitor Report — $title (CSV)');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Export Failed: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  // Action Handler: Print PDF document
  Future<void> _handlePrint(String title) async {
    final pdf = await _buildPdfDocument(title);
    final bytes = await pdf.save();
    final tempDir = await getTemporaryDirectory();
    final filePath = '${tempDir.path}/${title.replaceAll(' ', '_')}_$_selectedFilter\_print.pdf';
    final file = File(filePath);
    await file.writeAsBytes(bytes);
    await Share.shareXFiles([XFile(filePath)], text: 'Print Temple Visitor Report — $title');
  }

  Widget _filterTab(String label, String key) {
    final isSelected = _selectedFilter == key;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() => _selectedFilter = key);
          _loadReportData();
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFFD4AF37) : Colors.grey.shade200,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isSelected ? Colors.black : Colors.grey.shade700,
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final totalVisits = _visitors.length;
    final totalDevotees = _visitors.fold<int>(0, (sum, v) => sum + v.personsCount);
    final insideDevotees = _visitors.where((v) => v.status == 'CHECKED_IN' || v.status == 'INSIDE').fold<int>(0, (sum, v) => sum + v.personsCount);
    final completedDevotees = _visitors.where((v) => v.status == 'CHECKED_OUT').fold<int>(0, (sum, v) => sum + v.personsCount);

    return Scaffold(
      appBar: const TempleAppBar(title: 'Reports & Analytics Center'),
      body: Column(
        children: [
          // Dataset Filter Bar
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Row(
              children: [
                _filterTab('Today', 'TODAY'),
                const SizedBox(width: 6),
                _filterTab('Weekly', 'WEEKLY'),
                const SizedBox(width: 6),
                _filterTab('Monthly', 'MONTHLY'),
                const SizedBox(width: 6),
                _filterTab('All Time', 'CUSTOM'),
              ],
            ),
          ),

          // Analytics Summary Header Card
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12.0),
            child: Card(
              elevation: 2,
              color: const Color(0xFF2C1A11),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _analyticsItem('Visits', '$totalVisits', const Color(0xFFD4AF37)),
                    _analyticsItem('Devotees', '$totalDevotees', Colors.white),
                    _analyticsItem('Inside', '$insideDevotees', Colors.greenAccent),
                    _analyticsItem('Completed', '$completedDevotees', Colors.lightBlueAccent),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Action Export Cards
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
                : ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    children: [
                      _buildReportCard(
                        title: 'Daily & Period Visitor Report',
                        formatDesc: 'PDF / Excel XLSX / CSV',
                        subtitle: 'Complete throughput breakdown and formatted visitor tables',
                        icon: Icons.picture_as_pdf,
                      ),
                      _buildReportCard(
                        title: 'Demographic & Village Audit',
                        formatDesc: 'Excel XLSX / CSV',
                        subtitle: 'Village-level visitor counts and group sizes',
                        icon: Icons.table_chart,
                      ),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _analyticsItem(String label, String val, Color color) {
    return Column(
      children: [
        Text(val, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.white70)),
      ],
    );
  }

  Widget _buildReportCard({
    required String title,
    required String formatDesc,
    required String subtitle,
    required IconData icon,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: const Color(0xFFD4AF37).withOpacity(0.3)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: const Color(0xFFD4AF37), size: 28),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title, style: GoogleFonts.cinzel(fontSize: 15, fontWeight: FontWeight.bold, color: const Color(0xFF2C1A11))),
                      Text(subtitle, style: GoogleFonts.inter(fontSize: 11, color: Colors.grey.shade700)),
                    ],
                  ),
                ),
              ],
            ),
            const Divider(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon: const Icon(Icons.print, color: Color(0xFF2C1A11)),
                  tooltip: 'Print PDF',
                  onPressed: () => _handlePrint(title),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: () => _handleExport(title, 'PDF'),
                  icon: const Icon(Icons.picture_as_pdf, size: 14),
                  label: const Text('PDF'),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2C1A11), foregroundColor: Colors.white),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: () => _handleExport(title, 'Excel'),
                  icon: const Icon(Icons.description, size: 14),
                  label: const Text('Excel'),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFD4AF37), foregroundColor: Colors.black),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
