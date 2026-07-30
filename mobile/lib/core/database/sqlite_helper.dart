import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class SQLiteHelper {
  static Database? _database;

  static Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB();
    return _database!;
  }

  static Future<Database> _initDB() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'temple_visitors.db');

    return await openDatabase(
      path,
      version: 2,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_uuid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            persons_count INTEGER NOT NULL,
            village_id INTEGER,
            village_name_custom TEXT,
            purpose_id INTEGER NOT NULL,
            temple_service TEXT,
            visitor_date TEXT NOT NULL,
            visitor_time TEXT NOT NULL,
            notes TEXT,
            sync_status TEXT NOT NULL DEFAULT 'PENDING',
            created_at TEXT NOT NULL
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
      onUpgrade: (db, oldVersion, newVersion) async {
        if (oldVersion < 2) {
          await db.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
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
          await db.execute('CREATE INDEX IF NOT EXISTS idx_sync_queue_status_retry ON sync_queue (status, next_retry_at, client_timestamp ASC);');
          await db.execute('CREATE INDEX IF NOT EXISTS idx_sync_queue_entity ON sync_queue (entity_type, entity_id);');
          await db.execute('CREATE INDEX IF NOT EXISTS idx_sync_queue_event_id ON sync_queue (event_id);');
        }
      },
    );
  }

  static Future<int> insertVisitor(Map<String, dynamic> row) async {
    final db = await database;
    return await db.insert('visitors', row, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  static Future<List<Map<String, dynamic>>> getVisitors() async {
    final db = await database;
    return await db.query('visitors', orderBy: 'created_at DESC');
  }

  static Future<List<Map<String, dynamic>>> getPendingSyncVisitors() async {
    final db = await database;
    return await db.query('visitors', where: 'sync_status = ?', whereArgs: ['PENDING']);
  }

  static Future<int> updateVisitorSyncStatus(String visitorUuid, String status) async {
    final db = await database;
    return await db.update(
      'visitors',
      {'sync_status': status},
      where: 'visitor_uuid = ?',
      whereArgs: [visitorUuid],
    );
  }
}
