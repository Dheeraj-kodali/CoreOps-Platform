import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/network/api_client.dart';
import 'package:temple_visitor_app/core/services/app_logger.dart';
import 'package:temple_visitor_app/core/services/storage_service.dart';
import 'package:temple_visitor_app/models/sync_queue_model.dart';

class SyncRepository {
  final Dio _dio = ApiClient.createDio();

  /// Get pending count of events in sync_queue or visitors table
  Future<int> getPendingCount() async {
    final queueCount = await SQLiteDatabase.getPendingSyncQueueCount();
    final pendingVisitors = await SQLiteDatabase.getPendingSyncVisitors();
    return queueCount + pendingVisitors.length;
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
      String purposeId = '3ef2daff-d716-4285-ac7c-81e702530b44';
      try {
        final purpRes = await _dio.get('/analytics/purpose-breakdown');
        if (purpRes.statusCode == 200 && purpRes.data != null) {
          final breakdown = purpRes.data['breakdown'] as List?;
          if (breakdown != null && breakdown.isNotEmpty) {
            purposeId = breakdown[0]['purpose_id'] ?? purposeId;
          }
        }
      } catch (_) {}

      // 2. Fetch pending visitors from SQLite database visitors table
      final pendingVisitors = await SQLiteDatabase.getPendingSyncVisitors();
      AppLogger.info('Found ${pendingVisitors.length} pending visitors in visitors table to sync to Neon DB');

      bool allSuccess = true;

      for (final visitorMap in pendingVisitors) {
        final visitorId = visitorMap['id']?.toString() ?? '';
        final visitorUuid = visitorMap['visitor_uuid']?.toString() ?? visitorId;
        final name = visitorMap['name']?.toString() ?? '';
        final phone = visitorMap['phone_number']?.toString() ?? '';
        final count = int.tryParse(visitorMap['persons_count']?.toString() ?? '1') ?? 1;
        final notes = visitorMap['notes']?.toString() ?? '';
        final visitorDate = visitorMap['visitor_date']?.toString() ?? DateTime.now().toIso8601String().split('T')[0];
        final timeIn = visitorMap['time_in']?.toString() ?? '10:00:00';

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
          'visitor_uuid': visitorUuid.isNotEmpty ? visitorUuid : visitorId,
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
          AppLogger.info('Posting visitor $name ($visitorUuid) to Render backend...');
          final res = await _dio.post('/visitors/', data: payload);
          if (res.statusCode == 200 || res.statusCode == 201) {
            await SQLiteDatabase.markVisitorSynced(visitorId);
            if (visitorUuid.isNotEmpty) {
              await SQLiteDatabase.markVisitorSynced(visitorUuid);
            }
            AppLogger.info('[SYNC SUCCESS] Visitor $name ($visitorUuid) successfully synced to Neon DB');
          } else {
            allSuccess = false;
          }
        } on DioException catch (e) {
          if (e.response?.statusCode == 409) {
            AppLogger.warning('Visitor $name ($visitorUuid) already exists on backend (409 Conflict). Marking synced.');
            await SQLiteDatabase.markVisitorSynced(visitorId);
            if (visitorUuid.isNotEmpty) {
              await SQLiteDatabase.markVisitorSynced(visitorUuid);
            }
          } else {
            AppLogger.error('Failed to post visitor $visitorUuid to backend: $e');
            allSuccess = false;
          }
        } catch (e) {
          AppLogger.error('Failed to post visitor $visitorUuid to backend: $e');
          allSuccess = false;
        }
      }

      // 3. Process items from sync_queue table
      final queueItems = await SQLiteDatabase.getSyncQueueItems(status: 'PENDING');
      AppLogger.info('Found ${queueItems.length} pending items in sync_queue table');
      for (final item in queueItems) {
        final qId = item['queue_id'] as int;
        final op = item['operation']?.toString().toUpperCase() ?? 'CREATE';
        final entityId = item['entity_id']?.toString() ?? '';

        try {
          final rawPayload = item['payload'] as String?;
          if (rawPayload != null && rawPayload.isNotEmpty) {
            final Map<String, dynamic> payload = jsonDecode(rawPayload);

            if (op == 'CHECKOUT') {
              final visitId = payload['visit_id']?.toString() ?? entityId;
              final checkoutTime = payload['check_out']?.toString();
              final duration = payload['visit_duration']?.toString();
              final checkoutBody = {
                'checkout_time': checkoutTime,
                'duration': duration,
              };
              AppLogger.info('Posting checkout for visitor $visitId to backend...');
              final res = await _dio.put('/visitors/$visitId/checkout', data: checkoutBody);
              if (res.statusCode == 200 || res.statusCode == 201) {
                await SQLiteDatabase.updateSyncQueueStatusByQueueId(qId, 'SUCCESS');
                AppLogger.info('[SYNC CHECKOUT SUCCESS] sync_queue event $qId checkout synced to Neon DB');
              } else {
                allSuccess = false;
              }
            } else {
              if (!payload.containsKey('purpose_id') || payload['purpose_id'] == null) {
                payload['purpose_id'] = purposeId;
              }
              final res = await _dio.post('/visitors/', data: payload);
              if (res.statusCode == 200 || res.statusCode == 201) {
                await SQLiteDatabase.updateSyncQueueStatusByQueueId(qId, 'SUCCESS');
                final vUuid = payload['visitor_uuid']?.toString();
                if (vUuid != null) {
                  await SQLiteDatabase.markVisitorSynced(vUuid);
                }
                AppLogger.info('[SYNC SUCCESS] sync_queue event $qId successfully synced to Neon DB');
              }
            }
          }
        } on DioException catch (e) {
          if (op == 'CHECKOUT' && e.response?.statusCode == 404) {
            // Visitor not found on backend (e.g. checked out before check-in synced)
            AppLogger.warning('Visitor $entityId checkout 404 on backend. Marking sync_queue item SUCCESS.');
            await SQLiteDatabase.updateSyncQueueStatusByQueueId(qId, 'SUCCESS');
          } else if (e.response?.statusCode == 409) {
            AppLogger.warning('Event $qId returned 409 Conflict. Marking SUCCESS.');
            await SQLiteDatabase.updateSyncQueueStatusByQueueId(qId, 'SUCCESS');
          } else {
            AppLogger.error('Failed to sync queue event $qId ($op): $e');
            allSuccess = false;
          }
        } catch (e) {
          AppLogger.error('Failed to sync queue event $qId ($op): $e');
          allSuccess = false;
        }
      }

      return allSuccess;
    } catch (e) {
      AppLogger.error('Error during processSyncQueue execution: $e');
      return false;
    }
  }
}
