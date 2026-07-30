import 'package:uuid/uuid.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/services/communication_service.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/models/person_model.dart';
import 'package:temple_visitor_app/models/visit_model.dart';

class VisitorRepository {
  final CommunicationService _commService = CommunicationService();

  /// Search Person by phone number for Auto-Fill in Reception Form
  Future<PersonModel?> getPersonByPhone(String phone) async {
    if (phone.trim().length < 5) return null;
    final map = await SQLiteDatabase.getPersonByPhone(phone.trim());
    if (map != null) {
      return PersonModel.fromJson(map);
    }
    return null;
  }

  /// Get Person profile by ID
  Future<PersonModel?> getPersonById(String personId) async {
    final map = await SQLiteDatabase.getPersonById(personId);
    if (map != null) {
      return PersonModel.fromJson(map);
    }
    return null;
  }

  /// Get all visits for a person chronologically
  Future<List<VisitModel>> getVisitsForPerson(String personId) async {
    final list = await SQLiteDatabase.getVisitsForPerson(personId);
    return list.map((m) => VisitModel.fromJson(m)).toList();
  }

  /// Register a new visit (Separate Person and Visit in SQLite)
  Future<VisitorModel> registerVisitor({
    required String name,
    required String phoneNumber,
    required String village,
    required String purpose,
    required int personsCount,
    String? notes,
  }) async {
    final now = DateTime.now();
    final dateStr = '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
    final timeInStr = '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';

    final visitId = await SQLiteDatabase.registerVisit(
      name: name,
      phone: phoneNumber,
      village: village,
      purpose: purpose,
      groupMembers: personsCount,
      notes: notes,
    );

    final visitorModel = VisitorModel(
      id: visitId,
      visitorUuid: visitId,
      name: name,
      phoneNumber: phoneNumber,
      village: village,
      purpose: purpose,
      personsCount: personsCount,
      notes: notes,
      visitorDate: dateStr,
      timeIn: timeInStr,
      status: 'CHECKED_IN',
      syncStatus: 'PENDING',
    );

    // Dispatch WhatsApp Check-In Message
    _commService.sendCheckInMessage(visitorModel);

    return visitorModel;
  }

  /// Format duration into exact specified strings ("18 min", "1 hr 25 min", "2 hr 03 min")
  static String formatDuration(Duration diff) {
    if (diff.inMinutes < 1) {
      return '1 min';
    }
    if (diff.inMinutes < 60) {
      return '${diff.inMinutes} min';
    }
    final hours = diff.inHours;
    final mins = diff.inMinutes % 60;
    final minsPadded = mins.toString().padLeft(2, '0');
    return '$hours hr $minsPadded min';
  }

  /// Get today's visitors joined with Person details
  Future<List<VisitorModel>> getTodayVisitors({String? search, String statusFilter = 'ALL'}) async {
    final todayStr = DateTime.now().toString().split(' ')[0];
    final rows = await SQLiteDatabase.getVisitsJoined(
      searchQuery: search,
      dateFilter: todayStr,
      statusFilter: statusFilter,
    );
    return rows.map((r) => VisitorModel.fromJson(r)).toList();
  }

  /// Get visitors by date filter range (Today, Weekly, Monthly, Custom)
  Future<List<VisitorModel>> getFilteredVisitors({
    String filterType = 'TODAY',
    String? customStartDate,
    String? customEndDate,
    String? search,
    String statusFilter = 'ALL',
  }) async {
    final now = DateTime.now();
    String? startDate;
    String? endDate;

    if (filterType == 'TODAY') {
      startDate = now.toString().split(' ')[0];
    } else if (filterType == 'WEEKLY') {
      final startOfWeek = now.subtract(Duration(days: now.weekday - 1));
      startDate = startOfWeek.toString().split(' ')[0];
    } else if (filterType == 'MONTHLY') {
      startDate = '${now.year}-${now.month.toString().padLeft(2, '0')}-01';
    } else if (filterType == 'CUSTOM') {
      startDate = customStartDate;
      endDate = customEndDate;
    }

    final rows = await SQLiteDatabase.getVisitsJoined(
      searchQuery: search,
      dateFilter: startDate,
      statusFilter: statusFilter,
    );
    return rows.map((r) => VisitorModel.fromJson(r)).toList();
  }

  /// Get real-time Statistics for Today's Dashboard Header
  Future<Map<String, dynamic>> getTodayStatistics() async {
    final todayVisitors = await getTodayVisitors();

    final totalRecords = todayVisitors.length;
    final totalMembers = todayVisitors.fold<int>(0, (sum, v) => sum + v.personsCount);
    final insideCount = todayVisitors.where((v) => v.status == 'CHECKED_IN').fold<int>(0, (sum, v) => sum + v.personsCount);
    final leftCount = todayVisitors.where((v) => v.status == 'CHECKED_OUT').fold<int>(0, (sum, v) => sum + v.personsCount);

    final checkedOutVisitors = todayVisitors.where((v) => v.status == 'CHECKED_OUT' && v.visitDuration != null && v.visitDuration != 'null').toList();

    String avgDurationStr = '0 min';
    if (checkedOutVisitors.isNotEmpty) {
      int totalMinutes = 0;
      int count = 0;
      for (var v in checkedOutVisitors) {
        if (v.visitDuration!.contains('min')) {
          try {
            final parts = v.visitDuration!.split(' ');
            if (parts.contains('hr')) {
              final h = int.parse(parts[0]);
              final m = int.parse(parts[2]);
              totalMinutes += (h * 60) + m;
            } else {
              final m = int.parse(parts[0]);
              totalMinutes += m;
            }
            count++;
          } catch (_) {}
        }
      }
      if (count > 0) {
        final avgMins = (totalMinutes / count).round();
        avgDurationStr = formatDuration(Duration(minutes: avgMins));
      }
    }

    // Top Purpose Calculation
    final purposeCounts = <String, int>{};
    for (var v in todayVisitors) {
      purposeCounts[v.purpose] = (purposeCounts[v.purpose] ?? 0) + 1;
    }
    String topPurpose = 'General Darshan';
    if (purposeCounts.isNotEmpty) {
      topPurpose = purposeCounts.entries.reduce((a, b) => a.value > b.value ? a : b).key;
    }

    return {
      'total_records': totalRecords,
      'total_visitors': totalMembers,
      'visitors_inside': insideCount,
      'visitors_left': leftCount,
      'avg_duration_str': avgDurationStr,
      'top_purpose': topPurpose,
    };
  }

  /// Perform Checkout action ("Visitor Left") & Dispatch Automated Thank You Message
  Future<VisitorModel?> checkOutVisitor(String id) async {
    final now = DateTime.now();
    final timeOutStr = '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';

    final rawVisitor = await SQLiteDatabase.getVisitorById(id);
    if (rawVisitor == null) return null;

    final visitor = VisitorModel.fromJson(rawVisitor);

    String durationStr = '1 min';
    try {
      final inParts = visitor.timeIn.split(':');
      final inHour = int.parse(inParts[0]);
      final inMinute = int.parse(inParts[1]);

      final timeInDt = DateTime(now.year, now.month, now.day, inHour, inMinute);
      final diff = now.difference(timeInDt);
      durationStr = formatDuration(diff);
    } catch (_) {
      durationStr = '1 min';
    }

    await SQLiteDatabase.checkOutVisitor(id, timeOutStr, durationStr);

    final updatedRaw = await SQLiteDatabase.getVisitorById(id);
    if (updatedRaw != null) {
      final updatedModel = VisitorModel.fromJson(updatedRaw);
      _commService.sendCheckOutMessage(updatedModel);
      return updatedModel;
    }

    return null;
  }
}
