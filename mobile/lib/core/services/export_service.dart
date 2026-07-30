import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/models/communication_models.dart';

class ExportService {
  /// Export Visitor Data & Summary to formatted CSV / Excel (.xlsx compatible)
  static Future<File?> exportToExcel({
    required List<VisitorModel> visitors,
    required Map<String, dynamic> summary,
    required String periodName,
  }) async {
    try {
      final rawTemple = await SQLiteDatabase.getTempleInfo();
      final templeName = rawTemple['temple_name'] ?? 'Sri Kalki Seva Alayam';
      final nowStr = DateTime.now().toString().split(' ')[0].replaceAll('-', '_');

      final buffer = StringBuffer();

      // Summary Header Section
      buffer.writeln('=== TEMPLE VISITOR AUDIT REPORT SUMMARY ===');
      buffer.writeln('Temple Name,$templeName');
      buffer.writeln('Report Period,$periodName');
      buffer.writeln('Generated Timestamp,${DateTime.now().toIso8601String()}');
      buffer.writeln('Total Visitors,${summary['total_visitors']}');
      buffer.writeln('Visitors Inside,${summary['visitors_inside']}');
      buffer.writeln('Visitors Completed,${summary['visitors_left']}');
      buffer.writeln('Average Duration,${summary['avg_duration_str']}');
      buffer.writeln('Total Members,${summary['total_members']}');
      buffer.writeln('Top Purpose,${summary['top_purpose']}');
      buffer.writeln('Top Village,${summary['top_village']}');
      buffer.writeln('');

      // Visitor Table Header
      buffer.writeln('Visitor ID,Name,Phone,Village,Purpose,Members,Date,Time In,Time Out,Duration,Status');

      // Visitor Rows
      for (var v in visitors) {
        final id = v.visitorUuid.length > 8 ? v.visitorUuid.substring(0, 8) : v.visitorUuid;
        final timeOut = v.timeOut?.isNotEmpty == true ? v.timeOut : 'Inside';
        final duration = v.visitDuration?.isNotEmpty == true ? v.visitDuration : 'In Progress';

        buffer.writeln('"$id","${v.name}","${v.phoneNumber}","${v.village}","${v.purpose}",${v.personsCount},"${v.visitorDate}","${v.timeIn}","$timeOut","$duration","${v.status}"');
      }

      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/Visitors_$nowStr.csv');
      await file.writeAsString(buffer.toString());

      return file;
    } catch (e) {
      return null;
    }
  }

  /// Generate printable PDF / HTML Report file
  static Future<File?> exportToPDF({
    required List<VisitorModel> visitors,
    required Map<String, dynamic> summary,
    required String periodName,
  }) async {
    try {
      final rawTemple = await SQLiteDatabase.getTempleInfo();
      final templeName = rawTemple['temple_name'] ?? 'Sri Kalki Seva Alayam';
      final nowStr = DateTime.now().toString().split(' ')[0].replaceAll('-', '_');

      final buffer = StringBuffer();
      buffer.writeln('<!DOCTYPE html><html><head><style>');
      buffer.writeln('body { font-family: Arial, sans-serif; margin: 20px; }');
      buffer.writeln('h1 { color: #D4AF37; }');
      buffer.writeln('table { width: 100%; border-collapse: collapse; margin-top: 15px; }');
      buffer.writeln('th, td { border: 1px solid #ddd; padding: 8px; font-size: 12px; text-align: left; }');
      buffer.writeln('th { background-color: #2C1A11; color: #D4AF37; }');
      buffer.writeln('.summary { background-color: #fff9e6; padding: 15px; border-radius: 8px; margin-bottom: 20px; }');
      buffer.writeln('</style></head><body>');

      buffer.writeln('<h1>🛕 $templeName</h1>');
      buffer.writeln('<h3>Visitor Registration & Audit Report - $periodName</h3>');
      buffer.writeln('<p>Generated on: ${DateTime.now()}</p>');

      // Summary Box
      buffer.writeln('<div class="summary">');
      buffer.writeln('<p><b>Total Visitors:</b> ${summary['total_visitors']} &nbsp;|&nbsp; <b>Visitors Inside:</b> ${summary['visitors_inside']} &nbsp;|&nbsp; <b>Completed:</b> ${summary['visitors_left']}</p>');
      buffer.writeln('<p><b>Total Members:</b> ${summary['total_members']} &nbsp;|&nbsp; <b>Average Duration:</b> ${summary['avg_duration_str']}</p>');
      buffer.writeln('<p><b>Top Purpose:</b> ${summary['top_purpose']} &nbsp;|&nbsp; <b>Top Origin Village:</b> ${summary['top_village']}</p>');
      buffer.writeln('</div>');

      // Table Data
      buffer.writeln('<table><thead><tr><th>ID</th><th>Name</th><th>Phone</th><th>Village</th><th>Purpose</th><th>Members</th><th>Time In</th><th>Time Out</th><th>Duration</th><th>Status</th></tr></thead><tbody>');

      for (var v in visitors) {
        final id = v.visitorUuid.length > 8 ? v.visitorUuid.substring(0, 8) : v.visitorUuid;
        buffer.writeln('<tr><td>$id</td><td>${v.name}</td><td>${v.phoneNumber}</td><td>${v.village}</td><td>${v.purpose}</td><td>${v.personsCount}</td><td>${v.timeIn}</td><td>${v.timeOut ?? 'Inside'}</td><td>${v.visitDuration ?? 'In Progress'}</td><td>${v.status}</td></tr>');
      }

      buffer.writeln('</tbody></table></body></html>');

      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/Visitor_Report_$nowStr.html');
      await file.writeAsString(buffer.toString());

      return file;
    } catch (e) {
      return null;
    }
  }

  /// Backup SQLite Database file
  static Future<File?> backupDatabase() async {
    try {
      final db = await SQLiteDatabase.instance;
      final dbPath = db.path;
      final dbFile = File(dbPath);

      final dir = await getApplicationDocumentsDirectory();
      final nowStr = DateTime.now().toString().split(' ')[0].replaceAll('-', '_');
      final backupFile = File('${dir.path}/Temple_Backup_$nowStr.db');

      await dbFile.copy(backupFile.path);
      return backupFile;
    } catch (e) {
      return null;
    }
  }

  /// Restore SQLite Database file
  static Future<bool> restoreDatabase(File newDbFile) async {
    try {
      final db = await SQLiteDatabase.instance;
      final dbPath = db.path;
      await db.close();

      await newDbFile.copy(dbPath);
      return true;
    } catch (e) {
      return false;
    }
  }
}
