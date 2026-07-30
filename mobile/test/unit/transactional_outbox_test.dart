import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:temple_visitor_app/models/sync_queue_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  // Setup sqflite ffi for in-memory unit tests
  sqfliteFfiInit();
  databaseFactory = databaseFactoryFfi;

  group('Step 1: Transactional Outbox & Sync Queue Tests', () {
    late Database db;

    setUp(() async {
      db = await openDatabase(
        inMemoryDatabasePath,
        version: 6,
        onCreate: (db, version) async {
          await db.execute('''
            CREATE TABLE persons (
              person_id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              phone TEXT UNIQUE NOT NULL,
              village TEXT NOT NULL,
              address TEXT,
              first_visit TEXT NOT NULL,
              last_visit TEXT NOT NULL,
              total_visits INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
          ''');

          await db.execute('''
            CREATE TABLE visits (
              visit_id TEXT PRIMARY KEY,
              person_id TEXT NOT NULL,
              check_in TEXT NOT NULL,
              check_out TEXT,
              purpose TEXT NOT NULL,
              group_members INTEGER NOT NULL DEFAULT 1,
              notes TEXT,
              visit_duration TEXT,
              status TEXT NOT NULL DEFAULT 'CHECKED_IN',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY (person_id) REFERENCES persons (person_id) ON DELETE CASCADE
            )
          ''');

          await db.execute('''
            CREATE TABLE visitors (
              id TEXT PRIMARY KEY,
              visitor_uuid TEXT UNIQUE NOT NULL,
              name TEXT NOT NULL,
              phone_number TEXT NOT NULL,
              village TEXT NOT NULL,
              purpose TEXT NOT NULL,
              persons_count INTEGER NOT NULL,
              notes TEXT,
              visitor_date TEXT NOT NULL,
              time_in TEXT NOT NULL,
              time_out TEXT,
              visit_duration TEXT,
              status TEXT NOT NULL DEFAULT 'CHECKED_IN',
              sync_status TEXT NOT NULL DEFAULT 'PENDING',
              is_deleted INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
          ''');

          await db.execute('''
            CREATE TABLE sync_queue (
              queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
              event_id TEXT UNIQUE NOT NULL,
              temple_id TEXT NOT NULL DEFAULT 'TEMPLE_MAIN',
              entity_type TEXT NOT NULL,
              entity_id TEXT NOT NULL,
              operation TEXT NOT NULL,
              payload TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'PENDING',
              retry_count INTEGER NOT NULL DEFAULT 0,
              max_retries INTEGER NOT NULL DEFAULT 10,
              next_retry_at INTEGER,
              error_message TEXT,
              client_timestamp INTEGER NOT NULL,
              server_synced_at INTEGER,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
          ''');

          await db.execute('CREATE INDEX idx_sync_queue_status_retry ON sync_queue (status, next_retry_at, client_timestamp ASC);');
          await db.execute('CREATE INDEX idx_sync_queue_entity ON sync_queue (entity_type, entity_id);');
          await db.execute('CREATE INDEX idx_sync_queue_event_id ON sync_queue (event_id);');
        },
      );
    });

    tearDown(() async {
      await db.close();
    });

    test('SyncQueueModel creation & retry exponential backoff calculation', () {
      final now = DateTime.now();
      final model = SyncQueueModel(
        eventId: 'evt-12345',
        entityType: 'VISITOR',
        entityId: 'v-999',
        operation: 'CREATE',
        payload: {'name': 'Ramesh Kumar', 'phone': '9876543210'},
        clientTimestamp: now.millisecondsSinceEpoch,
        createdAt: now.toIso8601String(),
        updatedAt: now.toIso8601String(),
      );

      expect(model.eventId, equals('evt-12345'));
      expect(model.status, equals('PENDING'));
      expect(model.retryCount, equals(0));

      final nextRetryEpoch = SyncQueueModel.calculateNextRetryTimestamp(0, baseDelaySeconds: 2, maxBackoffSeconds: 3600);
      final currentEpoch = DateTime.now().millisecondsSinceEpoch ~/ 1000;
      expect(nextRetryEpoch, greaterThanOrEqualTo(currentEpoch));
      expect(nextRetryEpoch, lessThanOrEqualTo(currentEpoch + 3));
    });

    test('Atomic registration transaction inserts both visitor and outbox sync_queue event', () async {
      const visitId = 'visit-uuid-101';
      const eventId = 'event-uuid-202';
      final nowStr = DateTime.now().toIso8601String();

      await db.transaction((txn) async {
        await txn.insert('persons', {
          'person_id': 'person-1',
          'name': 'Sita Devi',
          'phone': '9876500000',
          'village': 'Kovur',
          'first_visit': '2026-07-30 10:00',
          'last_visit': '2026-07-30 10:00',
          'total_visits': 1,
          'created_at': nowStr,
          'updated_at': nowStr,
        });

        await txn.insert('visits', {
          'visit_id': visitId,
          'person_id': 'person-1',
          'check_in': '2026-07-30 10:00',
          'purpose': 'Special Archana',
          'group_members': 2,
          'status': 'CHECKED_IN',
          'created_at': nowStr,
          'updated_at': nowStr,
        });

        await txn.insert('sync_queue', {
          'event_id': eventId,
          'temple_id': 'TEMPLE_MAIN',
          'entity_type': 'VISITOR',
          'entity_id': visitId,
          'operation': 'CREATE',
          'payload': '{"name":"Sita Devi","phone":"9876500000"}',
          'status': 'PENDING',
          'retry_count': 0,
          'max_retries': 10,
          'client_timestamp': DateTime.now().millisecondsSinceEpoch,
          'created_at': nowStr,
          'updated_at': nowStr,
        });
      });

      final visits = await db.query('visits', where: 'visit_id = ?', whereArgs: [visitId]);
      final outboxItems = await db.query('sync_queue', where: 'event_id = ?', whereArgs: [eventId]);

      expect(visits.length, equals(1));
      expect(outboxItems.length, equals(1));
      expect(outboxItems.first['entity_id'], equals(visitId));
      expect(outboxItems.first['operation'], equals('CREATE'));
    });

    test('Atomic transaction rolls back completely if outbox insert fails', () async {
      const visitId = 'failed-visit-1';
      const duplicateEventId = 'dup-event-1';
      final nowStr = DateTime.now().toIso8601String();

      // Pre-insert an outbox item with duplicateEventId
      await db.insert('sync_queue', {
        'event_id': duplicateEventId,
        'temple_id': 'TEMPLE_MAIN',
        'entity_type': 'VISITOR',
        'entity_id': 'existing-1',
        'operation': 'CREATE',
        'payload': '{}',
        'status': 'PENDING',
        'retry_count': 0,
        'max_retries': 10,
        'client_timestamp': DateTime.now().millisecondsSinceEpoch,
        'created_at': nowStr,
        'updated_at': nowStr,
      });

      expect(
        () async {
          await db.transaction((txn) async {
            await txn.insert('visits', {
              'visit_id': visitId,
              'person_id': 'person-99',
              'check_in': '2026-07-30 10:00',
              'purpose': 'Pooja',
              'group_members': 1,
              'status': 'CHECKED_IN',
              'created_at': nowStr,
              'updated_at': nowStr,
            });

            // This will fail due to UNIQUE constraint on event_id
            await txn.insert('sync_queue', {
              'event_id': duplicateEventId,
              'temple_id': 'TEMPLE_MAIN',
              'entity_type': 'VISITOR',
              'entity_id': visitId,
              'operation': 'CREATE',
              'payload': '{}',
              'status': 'PENDING',
              'retry_count': 0,
              'max_retries': 10,
              'client_timestamp': DateTime.now().millisecondsSinceEpoch,
              'created_at': nowStr,
              'updated_at': nowStr,
            });
          });
        },
        throwsA(isA<DatabaseException>()),
      );

      // Verify that 'visits' table record was completely rolled back
      final visits = await db.query('visits', where: 'visit_id = ?', whereArgs: [visitId]);
      expect(visits, isEmpty);
    });

    test('Backfill migration creates sync_queue items for pending visitors without duplicates', () async {
      final nowStr = DateTime.now().toIso8601String();

      await db.insert('visitors', {
        'id': 'v-legacy-1',
        'visitor_uuid': 'v-legacy-1',
        'name': 'Anil Kumar',
        'phone_number': '9123456789',
        'village': 'Chittoor',
        'purpose': 'Darshan',
        'persons_count': 1,
        'visitor_date': '2026-07-30',
        'time_in': '09:30 AM',
        'status': 'CHECKED_IN',
        'sync_status': 'PENDING',
        'is_deleted': 0,
        'created_at': nowStr,
        'updated_at': nowStr,
      });

      final pending = await db.query('visitors', where: "sync_status = 'PENDING'");
      expect(pending.length, equals(1));

      // Simulate backfill script execution
      for (final row in pending) {
        final uuid = row['visitor_uuid'].toString();
        final existing = await db.query('sync_queue', where: 'entity_id = ? AND operation = ?', whereArgs: [uuid, 'CREATE']);

        if (existing.isEmpty) {
          await db.insert('sync_queue', {
            'event_id': 'bf-evt-1',
            'temple_id': 'TEMPLE_MAIN',
            'entity_type': 'VISITOR',
            'entity_id': uuid,
            'operation': 'CREATE',
            'payload': '{"name":"Anil Kumar"}',
            'status': 'PENDING',
            'retry_count': 0,
            'max_retries': 10,
            'client_timestamp': DateTime.now().millisecondsSinceEpoch,
            'created_at': nowStr,
            'updated_at': nowStr,
          });
        }
      }

      final outboxCount = await db.query('sync_queue', where: "entity_id = 'v-legacy-1'");
      expect(outboxCount.length, equals(1));
    });
  });
}
