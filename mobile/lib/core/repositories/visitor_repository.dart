import 'package:uuid/uuid.dart';
import 'package:dio/dio.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/network/api_client.dart';
import 'package:temple_visitor_app/core/services/central_sync_manager.dart';
import 'package:temple_visitor_app/core/services/communication_service.dart';
import 'package:temple_visitor_app/core/services/storage_service.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/models/person_model.dart';
import 'package:temple_visitor_app/models/visit_model.dart';

class VisitorRepository {
  final CommunicationService _commService = CommunicationService();
  final Dio _dio = ApiClient.createDio();

  Future<String?> _getAuthHeader() async {
    final token = await StorageService.getAccessToken();
    return token != null && token.isNotEmpty ? 'Bearer $token' : null;
  }

  /// Fetch live production analytics dashboard from Render FastAPI Backend
  Future<Map<String, dynamic>?> fetchLiveDashboardStats() async {
    try {
      final authHeader = await _getAuthHeader();
      final options = authHeader != null ? Options(headers: {'Authorization': authHeader}) : null;
      final res = await _dio.get('/analytics/dashboard', options: options);
      if (res.statusCode == 200 && res.data != null) {
        return Map<String, dynamic>.from(res.data);
      }
    } catch (_) {}
    return null;
  }

  /// Pull remote today's ledger sessions from Render Backend & insert into local SQLite
  Future<void> syncRemoteLedgerSessions() async {
    try {
      final authHeader = await _getAuthHeader();
      final options = authHeader != null ? Options(headers: {'Authorization': authHeader}) : null;
      final res = await _dio.get('/visitors/ledgers/today', options: options);
      if (res.statusCode == 200 && res.data != null && res.data['sessions'] != null) {
        final List sessions = res.data['sessions'];
        for (var s in sessions) {
          final sId = s['id']?.toString() ?? s['visitor_uuid']?.toString() ?? '';
          if (sId.isEmpty) continue;
          final name = s['name']?.toString() ?? '';
          final phone = s['phone_number']?.toString() ?? '';
          if (phone == '9876543210' || name.contains('Sri Krishna Devotee')) continue;
          final pCount = int.tryParse(s['persons_count']?.toString() ?? '1') ?? 1;
          final notes = s['notes']?.toString() ?? '';
          final status = s['status']?.toString() == 'CHECKED_OUT' ? 'CHECKED_OUT' : 'CHECKED_IN';
          
          final existing = await SQLiteDatabase.getVisitorById(sId);
          if (existing == null) {
            await SQLiteDatabase.registerVisit(
              name: name,
              phone: phone,
              village: s['village_name_custom']?.toString() ?? '',
              purpose: s['purpose']?['name_en']?.toString() ?? 'General Darshan',
              groupMembers: pCount,
              notes: notes,
            );
            await SQLiteDatabase.markVisitorSynced(sId);
          }
        }
      }
    } catch (_) {}
  }

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

    final combinedNotes = (notes ?? "").trim();

    final visitId = await SQLiteDatabase.registerVisit(
      name: name,
      phone: phoneNumber,
      village: village,
      purpose: purpose,
      groupMembers: personsCount,
      notes: combinedNotes,
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

    // Trigger Centralized Sync Manager to process outbox, fetch ledgers, and refresh all app screens
    CentralSyncManager.instance.triggerSync(
      type: SyncEventType.registration,
      reason: 'Visitor Registration Completed',
    );

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

  /// Get last 3 days of visitors joined with Person details
  Future<List<VisitorModel>> getTodayVisitors({String? search, String statusFilter = 'ALL'}) async {
    final now = DateTime.now();
    final dates = [
      now.toString().split(' ')[0],
      now.subtract(const Duration(days: 1)).toString().split(' ')[0],
      now.subtract(const Duration(days: 2)).toString().split(' ')[0],
    ];
    final rows = await SQLiteDatabase.getVisitsJoinedMultiDates(
      searchQuery: search,
      dateFilters: dates,
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

  /// Perform Phone Lookup via Remote Render FastAPI Backend
  Future<Map<String, dynamic>?> lookupPhone(String phone) async {
    try {
      final authHeader = await _getAuthHeader();
      final options = authHeader != null ? Options(headers: {'Authorization': authHeader}) : null;
      final res = await _dio.get('/visitors/lookup-phone', queryParameters: {'phone_number': phone}, options: options);
      if (res.statusCode == 200 && res.data != null) {
        return Map<String, dynamic>.from(res.data);
      }
    } catch (_) {}
    return null;
  }

  /// Get real-time Statistics for Today's Dashboard Header
  Future<Map<String, dynamic>> getTodayStatistics() async {
    final liveStats = await fetchLiveDashboardStats();
    final todayVisitors = await getTodayVisitors();

    int localRecords = todayVisitors.length;
    int localMembers = todayVisitors.fold<int>(0, (sum, v) => sum + v.personsCount);
    int localInside = todayVisitors.where((v) => v.status == 'CHECKED_IN').fold<int>(0, (sum, v) => sum + v.personsCount);
    int localLeft = todayVisitors.where((v) => v.status == 'CHECKED_OUT').fold<int>(0, (sum, v) => sum + v.personsCount);

    int totalRecords = localRecords;
    int totalMembers = localMembers;
    int insideCount = localInside;
    int leftCount = localLeft;

    if (liveStats != null) {
      final remoteVisitors = liveStats['todays_visitors'] as int? ?? 0;
      final remoteInside = liveStats['visitors_inside'] as int? ?? 0;
      final remoteCheckIns = liveStats['todays_check_ins'] as int? ?? 0;
      final remoteCheckOuts = liveStats['todays_check_outs'] as int? ?? 0;

      totalMembers = localMembers > remoteVisitors ? localMembers : remoteVisitors;
      insideCount = localInside > remoteInside ? localInside : remoteInside;
      totalRecords = localRecords > remoteCheckIns ? localRecords : remoteCheckIns;
      leftCount = localLeft > remoteCheckOuts ? localLeft : remoteCheckOuts;
    }

    final checkedOutVisitors = todayVisitors.where((v) => v.status == 'CHECKED_OUT' && v.visitDuration != null && v.visitDuration != 'null').toList();

    String avgDurationStr = '42 min';
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

    // Trigger Centralized Sync Manager for Checkout Event
    CentralSyncManager.instance.triggerSync(
      type: SyncEventType.checkout,
      reason: 'Visitor Checkout Completed',
    );

    final updatedRaw = await SQLiteDatabase.getVisitorById(id);
    if (updatedRaw != null) {
      final updatedModel = VisitorModel.fromJson(updatedRaw);
      _commService.sendCheckOutMessage(updatedModel);
      return updatedModel;
    }

    return null;
  }
}
