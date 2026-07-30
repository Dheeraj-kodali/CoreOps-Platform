import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/models/sync_queue_model.dart';

class SyncRepository {
  /// Get pending count of events in sync_queue
  Future<int> getPendingCount() async {
    final queueCount = await SQLiteDatabase.getPendingSyncQueueCount();
    if (queueCount > 0) return queueCount;

    // Fallback check on legacy visitors table if sync_queue count is 0
    final pendingVisitors = await SQLiteDatabase.getPendingSyncVisitors();
    return pendingVisitors.length;
  }

  /// Get pending sync queue models
  Future<List<SyncQueueModel>> getPendingQueueEvents({int limit = 100}) async {
    final rows = await SQLiteDatabase.getSyncQueueItems(status: 'PENDING', limit: limit);
    return rows.map((r) => SyncQueueModel.fromMap(r)).toList();
  }

  /// Outbox transmission logic deferred to Step 3 per specification
  Future<bool> processSyncQueue() async {
    // Zero API calls executed in Step 1 foundation phase
    return true;
  }
}
