import 'package:dio/dio.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/network/api_client.dart';
import 'package:temple_visitor_app/core/services/app_logger.dart';
import 'package:temple_visitor_app/core/services/storage_service.dart';
import 'package:temple_visitor_app/models/sync_queue_model.dart';

class SyncRepository {
  final Dio _dio = ApiClient.createDio();

  /// Get pending count of events in sync_queue
  Future<int> getPendingCount() async {
    final queueCount = await SQLiteDatabase.getPendingSyncQueueCount();
    if (queueCount > 0) return queueCount;

    final pendingVisitors = await SQLiteDatabase.getPendingSyncVisitors();
    return pendingVisitors.length;
  }

  /// Get pending sync queue models
  Future<List<SyncQueueModel>> getPendingQueueEvents({int limit = 100}) async {
    final rows = await SQLiteDatabase.getSyncQueueItems(status: 'PENDING', limit: limit);
    return rows.map((r) => SyncQueueModel.fromMap(r)).toList();
  }

  /// Ensure JWT Access Token exists before sending API requests
  Future<String?> _ensureAccessToken() async {
    String? token = await StorageService.getAccessToken();
    if (token != null && token.isNotEmpty) return token;

    try {
      AppLogger.info('Authenticating mobile client with Render backend...');
      final response = await _dio.post(
        '/auth/login',
        data: {
          'username': 'admin',
          'password': 'Admin@12345',
        },
      );

      if (response.statusCode == 200 && response.data != null) {
        final accessToken = response.data['access_token'] as String?;
        final refreshToken = response.data['refresh_token'] as String?;
        if (accessToken != null) {
          await StorageService.saveTokens(
            accessToken: accessToken,
            refreshToken: refreshToken ?? '',
          );
          return accessToken;
        }
      }
    } catch (e) {
      AppLogger.error('Failed to obtain JWT token for sync: $e');
    }
    return null;
  }

  /// Process offline outbox sync queue items to Render backend & Neon PostgreSQL DB
  Future<bool> processSyncQueue() async {
    try {
      final token = await _ensureAccessToken();
      if (token == null) {
        AppLogger.warning('Cannot process sync queue: Mobile client unauthenticated');
        return false;
      }

      // 1. Fetch backend default purpose ID
      String purposeId = 'p-darshan-1';
      try {
        final purpRes = await _dio.get('/analytics/purpose-breakdown');
        if (purpRes.statusCode == 200 && purpRes.data != null) {
          final breakdown = purpRes.data['breakdown'] as List?;
          if (breakdown != null && breakdown.isNotEmpty) {
            purposeId = breakdown[0]['purpose_id'] ?? purposeId;
          }
        }
      } catch (_) {}

      // 2. Fetch pending visitors from SQLite database
      final pendingVisitors = await SQLiteDatabase.getPendingSyncVisitors();
      AppLogger.info('Found ${pendingVisitors.length} pending visitors to sync to Neon DB');

      bool allSuccess = true;

      for (final visitorMap in pendingVisitors) {
        final visitorId = visitorMap['id'] as String;
        final visitorUuid = (visitorMap['visitor_uuid'] ?? visitorId) as String;
        final name = visitorMap['name'] as String;
        final phone = visitorMap['phone_number'] as String;
        final count = (visitorMap['persons_count'] as int?) ?? 1;
        final notes = visitorMap['notes'] as String? ?? '';
        final visitorDate = visitorMap['visitor_date'] as String? ?? DateTime.now().toIso8601String().split('T')[0];
        final timeIn = visitorMap['time_in'] as String? ?? '10:00:00';

        // Extract latitude and longitude if present in notes or fields
        double? latitude;
        double? longitude;
        if (notes.contains('[GPS:')) {
          try {
            final gpsMatch = RegExp(r'\[GPS:\s*(-?\d+\.\d+),\s*(-?\d+\.\d+)\]').firstMatch(notes);
            if (gpsMatch != null) {
              latitude = double.tryParse(gpsMatch.group(1)!);
              longitude = double.tryParse(gpsMatch.group(2)!);
            }
          } catch (_) {}
        }

        final payload = {
          'visitor_uuid': visitorUuid,
          'name': name,
          'phone_number': phone,
          'gender': 'MALE',
          'age': 30,
          'persons_count': count,
          'purpose_id': purposeId,
          'visitor_date': visitorDate.contains('T') ? visitorDate.split('T')[0] : visitorDate,
          'visitor_time': timeIn.length == 5 ? '$timeIn:00' : timeIn,
          'notes': notes,
          'latitude': latitude,
          'longitude': longitude,
        };

        try {
          final res = await _dio.post('/visitors/', data: payload);
          if (res.statusCode == 200 || res.statusCode == 201) {
            await SQLiteDatabase.markVisitorSynced(visitorId);
            AppLogger.info('Successfully synced visitor $visitorUuid to Render backend');
          } else {
            allSuccess = false;
          }
        } catch (e) {
          AppLogger.error('Failed to post visitor $visitorUuid to backend: $e');
          allSuccess = false;
        }
      }

      // 3. Mark sync_queue items as SUCCESS
      final queueItems = await SQLiteDatabase.getSyncQueueItems(status: 'PENDING');
      for (final item in queueItems) {
        final qId = item['queue_id'] as int;
        await SQLiteDatabase.updateSyncQueueStatusByQueueId(qId, 'SUCCESS');
      }

      return allSuccess;
    } catch (e) {
      AppLogger.error('Error during processSyncQueue execution: $e');
      return false;
    }
  }
}
