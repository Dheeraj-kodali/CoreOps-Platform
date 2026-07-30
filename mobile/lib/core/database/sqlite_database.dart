import 'dart:convert';
import 'dart:io';
import 'package:crypto/crypto.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:uuid/uuid.dart';
import 'package:temple_visitor_app/core/services/app_logger.dart';

class SQLiteDatabase {
  static Database? _database;
  static const int _dbVersion = 6;
  static const _uuid = Uuid();

  static Future<Database> get instance async {
    if (_database != null) return _database!;
    _database = await _initDB();
    return _database!;
  }

  static String hashPassword(String password) {
    final bytes = utf8.encode('temple_admin_salt_$password');
    return sha256.convert(bytes).toString();
  }

  static Future<Database> _initDB() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'temple_visitors_prod_v1.db');

    AppLogger.info('Initializing Relational SQLite Database Version $_dbVersion at $path');

    final db = await openDatabase(
      path,
      version: _dbVersion,
      onCreate: (db, version) async {
        AppLogger.info('Creating Relational SQLite Schema Version $version');

        // 1. Users Table (Local Auth)
        await db.execute('''
          CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'SUPER_ADMIN',
            created_at TEXT NOT NULL
          )
        ''');

        // 2. Persons Table (Normalized Visitor Entity)
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

        // 3. Visits Table (Relational Visit Record)
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

        // Indexes for High Performance Queries
        await db.execute('CREATE INDEX idx_persons_phone ON persons(phone);');
        await db.execute('CREATE INDEX idx_visits_person_id ON visits(person_id);');
        await db.execute('CREATE INDEX idx_visits_status ON visits(status);');
        await db.execute('CREATE INDEX idx_visits_check_in ON visits(check_in);');

        // Legacy Visitors Table (Kept for compatibility)
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

        // Transactional Outbox Sync Queue Table (v2.0 Architecture)
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

        // Communication & Config Tables
        await db.execute('''
          CREATE TABLE communication_templates (
            id TEXT PRIMARY KEY,
            template_type TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            message TEXT NOT NULL,
            is_enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
          )
        ''');

        await db.execute('''
          CREATE TABLE temple_info (
            id TEXT PRIMARY KEY,
            temple_name TEXT NOT NULL,
            website TEXT NOT NULL,
            google_maps_link TEXT NOT NULL,
            donation_link TEXT NOT NULL,
            facebook TEXT NOT NULL,
            instagram TEXT NOT NULL,
            youtube TEXT NOT NULL,
            temple_phone TEXT NOT NULL,
            temple_address TEXT NOT NULL
          )
        ''');

        await db.execute('''
          CREATE TABLE today_activities (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
          )
        ''');

        await db.execute('''
          CREATE TABLE festival_info (
            id TEXT PRIMARY KEY,
            festival_name TEXT NOT NULL,
            festival_date TEXT NOT NULL,
            festival_description TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1
          )
        ''');

        await db.execute('''
          CREATE TABLE communication_history (
            id TEXT PRIMARY KEY,
            visitor_id TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT '',
            channel TEXT NOT NULL DEFAULT 'WHATSAPP',
            template_type TEXT NOT NULL,
            rendered_message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            meta_message_id TEXT,
            error_message TEXT,
            failure_reason TEXT,
            created_at TEXT NOT NULL
          )
        ''');

        // Seed Admin & Default Content
        final now = DateTime.now().toIso8601String();
        await db.insert('users', {
          'id': 'usr_admin_default',
          'username': 'admin',
          'password_hash': hashPassword('Admin@12345'),
          'role': 'SUPER_ADMIN',
          'created_at': now,
        });

        await db.insert('communication_templates', {
          'id': 'tmpl_check_in',
          'template_type': 'CHECK_IN',
          'message': 'Jai Kalki {{name}}! Welcome to {{temple_name}}. Your check-in for {{members}} person(s) from {{village}} at {{time}} is registered. Seva: {{activities}}. Maps: {{maps_link}}',
          'is_enabled': 1,
          'created_at': now,
          'updated_at': now,
        });

        await db.insert('communication_templates', {
          'id': 'tmpl_check_out',
          'template_type': 'CHECK_OUT',
          'message': 'Jai Kalki {{name}}! Thank you for visiting {{temple_name}}. May divine blessings be with you. Visit again! Website: {{website}} | Donate: {{donation_link}}',
          'is_enabled': 1,
          'created_at': now,
          'updated_at': now,
        });

        await db.insert('temple_info', {
          'id': 'temple_main',
          'temple_name': 'Sri Kalki Seva Alayam',
          'website': 'https://kalkiseva.org',
          'google_maps_link': 'https://maps.google.com/?q=Kalki+Temple',
          'donation_link': 'https://kalkiseva.org/donate',
          'facebook': 'https://facebook.com/kalkiseva',
          'instagram': 'https://instagram.com/kalkiseva',
          'youtube': 'https://youtube.com/kalkiseva',
          'temple_phone': '+91 98765 43210',
          'temple_address': 'Sacred Complex, Kalki Nagaram, Chittoor, AP 517001',
        });

        await db.insert('today_activities', {
          'id': 'act_1',
          'title': 'Grand Annadanam & Special Archana',
          'description': 'Daily Annadanam from 12:00 PM to 3:00 PM',
          'is_active': 1,
        });

        await db.insert('festival_info', {
          'id': 'fest_1',
          'festival_name': 'Maha Shivaratri Brahmotsavam',
          'festival_date': '2026-03-08',
          'festival_description': 'Special Night Prayers & Cultural Seva',
          'enabled': 1,
        });
      },
      onUpgrade: (db, oldVersion, newVersion) async {
        AppLogger.info('Upgrading Relational SQLite Database from Version $oldVersion to $newVersion');
        if (oldVersion < 4) {
          await _migrateToVersion4(db);
        }
        if (oldVersion < 5) {
          await _migrateToVersion5(db);
        }
        if (oldVersion < 6) {
          await _migrateToVersion6(db);
        }
      },
    );

    // Self-Healing Schema Verification
    await _verifyAndSelfHeal(db);

    return db;
  }

  /// Self-Healing Schema Verification Routine
  static Future<void> _verifyAndSelfHeal(Database db) async {
    try {
      AppLogger.info('Executing SQLite Self-Healing Routine...');
      final now = DateTime.now().toIso8601String();

      // 1. Verify 'users' table
      final usersTable = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='users';");
      if (usersTable.isEmpty) {
        await db.execute('''
          CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'SUPER_ADMIN',
            created_at TEXT NOT NULL
          )
        ''');
      }

      final adminUser = await db.query('users', where: 'username = ?', whereArgs: ['admin']);
      if (adminUser.isEmpty) {
        await db.insert('users', {
          'id': 'usr_admin_default',
          'username': 'admin',
          'password_hash': hashPassword('Admin@12345'),
          'role': 'SUPER_ADMIN',
          'created_at': now,
        });
      }

      // 2. Verify 'persons' and 'visits' (relational visitor tables)
      final personsTable = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='persons';");
      if (personsTable.isEmpty) {
        await _migrateToVersion4(db);
      } else {
        final visitCols = await db.rawQuery("PRAGMA table_info(visits)");
        final hasVisitDuration = visitCols.any((col) => col['name'] == 'visit_duration');
        if (!hasVisitDuration) {
          await db.execute("ALTER TABLE visits ADD COLUMN visit_duration TEXT;");
        }
      }

      // 3. Verify 'visitors' table for compatibility
      final visitorsTable = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='visitors';");
      if (visitorsTable.isEmpty) {
        await db.execute('''
          CREATE TABLE IF NOT EXISTS visitors (
            id TEXT PRIMARY KEY,
            visitor_uuid TEXT UNIQUE,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            village TEXT NOT NULL,
            purpose TEXT NOT NULL,
            persons_count INTEGER NOT NULL DEFAULT 1,
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
      }

      // 4. Verify 'communication_settings' table & default values
      final commSettingsTable = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='communication_settings';");
      if (commSettingsTable.isEmpty) {
        await db.execute('''
          CREATE TABLE IF NOT EXISTS communication_settings (
            id TEXT PRIMARY KEY,
            mode TEXT NOT NULL DEFAULT 'DISABLED',
            access_token TEXT,
            phone_number_id TEXT,
            business_account_id TEXT,
            verify_token TEXT,
            auto_send INTEGER NOT NULL DEFAULT 0,
            allow_edit INTEGER NOT NULL DEFAULT 1,
            save_history INTEGER NOT NULL DEFAULT 1,
            retry_failed INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL
          )
        ''');
      }

      final commSettings = await db.query('communication_settings');
      if (commSettings.isEmpty) {
        await db.insert('communication_settings', {
          'id': 'comm_settings_default',
          'mode': 'DISABLED',
          'access_token': null,
          'phone_number_id': null,
          'business_account_id': null,
          'verify_token': null,
          'auto_send': 0,
          'allow_edit': 1,
          'save_history': 1,
          'retry_failed': 1,
          'updated_at': now,
        });
      }

      // 5. Verify 'communication_templates' table & defaults
      final commTemplatesTable = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='communication_templates';");
      if (commTemplatesTable.isEmpty) {
        await db.execute('''
          CREATE TABLE IF NOT EXISTS communication_templates (
            id TEXT PRIMARY KEY,
            template_type TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            message TEXT NOT NULL,
            is_enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
          )
        ''');
      }

      // Seed default ENTRY & EXIT templates if missing
      final entryTemplate = await db.query('communication_templates', where: "template_type = 'ENTRY'");
      if (entryTemplate.isEmpty) {
        await db.insert('communication_templates', {
          'id': 'tmpl_entry',
          'template_type': 'ENTRY',
          'title': 'Visitor Entry Message',
          'message': '🙏 Welcome {name}\n\nYou have successfully entered\n{temple}\n\nEntry Time:\n{time}\n\nHave a blessed day.',
          'is_enabled': 1,
          'created_at': now,
          'updated_at': now,
        });
      }

      final exitTemplate = await db.query('communication_templates', where: "template_type = 'EXIT'");
      if (exitTemplate.isEmpty) {
        await db.insert('communication_templates', {
          'id': 'tmpl_exit',
          'template_type': 'EXIT',
          'title': 'Visitor Exit Message',
          'message': '🙏 Thank you {name}\n\nExit Time:\n{time}\n\nVisit Duration:\n{duration}\n\nThank you for visiting\n{temple}',
          'is_enabled': 1,
          'created_at': now,
          'updated_at': now,
        });
      }

      // 6. Verify 'communication_history' table
      final commHistoryTable = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='communication_history';");
      if (commHistoryTable.isEmpty) {
        await db.execute('''
          CREATE TABLE IF NOT EXISTS communication_history (
            id TEXT PRIMARY KEY,
            visitor_id TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT '',
            channel TEXT NOT NULL DEFAULT 'WHATSAPP',
            template_type TEXT NOT NULL,
            rendered_message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            meta_message_id TEXT,
            error_message TEXT,
            failure_reason TEXT,
            created_at TEXT NOT NULL
          )
        ''');
      } else {
        final historyCols = await db.rawQuery("PRAGMA table_info(communication_history)");
        final hasPhone = historyCols.any((col) => col['name'] == 'phone');
        if (!hasPhone) {
          await db.execute("ALTER TABLE communication_history ADD COLUMN phone TEXT NOT NULL DEFAULT '';");
        }
        final hasMetaId = historyCols.any((col) => col['name'] == 'meta_message_id');
        if (!hasMetaId) {
          await db.execute("ALTER TABLE communication_history ADD COLUMN meta_message_id TEXT;");
        }
        final hasErrMsg = historyCols.any((col) => col['name'] == 'error_message');
        if (!hasErrMsg) {
          await db.execute("ALTER TABLE communication_history ADD COLUMN error_message TEXT;");
        }
      }

      AppLogger.info('SQLite Self-Healing Schema Verification Complete. All 5 core tables verified.');
    } catch (e, st) {
      AppLogger.error('SQLite Self-Healing Routine Error', err: e, st: st);
    }
  }

  /// Migrate Legacy Visitor Table to Relational Person + Visit Schema
  static Future<void> _migrateToVersion4(Database db) async {
    AppLogger.info('Migrating legacy visitor data to Person + Visit relational schema...');

    await db.execute('''
      CREATE TABLE IF NOT EXISTS persons (
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
      CREATE TABLE IF NOT EXISTS visits (
        visit_id TEXT PRIMARY KEY,
        person_id TEXT NOT NULL,
        check_in TEXT NOT NULL,
        check_out TEXT,
        purpose TEXT NOT NULL,
        group_members INTEGER NOT NULL DEFAULT 1,
        notes TEXT,
        status TEXT NOT NULL DEFAULT 'CHECKED_IN',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (person_id) REFERENCES persons (person_id) ON DELETE CASCADE
      )
    ''');

    await db.execute('CREATE INDEX IF NOT EXISTS idx_persons_phone ON persons(phone);');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_visits_person_id ON visits(person_id);');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_visits_status ON visits(status);');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_visits_check_in ON visits(check_in);');

    // Read legacy visitors table if present
    final legacyTables = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='visitors';");
    if (legacyTables.isNotEmpty) {
      final legacyRows = await db.query('visitors');
      AppLogger.info('Found ${legacyRows.length} legacy visitor records to migrate.');

      for (final row in legacyRows) {
        final phone = (row['phone_number'] ?? row['phone'] ?? '').toString().trim();
        final name = (row['name'] ?? 'Unknown Visitor').toString().trim();
        final village = (row['village'] ?? 'Unknown Village').toString().trim();
        final dateStr = (row['visitor_date'] ?? DateTime.now().toIso8601String().split('T')[0]).toString();
        final timeIn = (row['time_in'] ?? '10:00 AM').toString();
        final checkInIso = '$dateStr $timeIn';

        if (phone.isEmpty) continue;

        // Check if person already exists by phone
        final existing = await db.query('persons', where: 'phone = ?', whereArgs: [phone]);
        String personId;

        if (existing.isEmpty) {
          personId = _uuid.v4();
          await db.insert('persons', {
            'person_id': personId,
            'name': name,
            'phone': phone,
            'village': village,
            'address': null,
            'first_visit': checkInIso,
            'last_visit': checkInIso,
            'total_visits': 1,
            'created_at': row['created_at']?.toString() ?? DateTime.now().toIso8601String(),
            'updated_at': row['updated_at']?.toString() ?? DateTime.now().toIso8601String(),
          });
        } else {
          personId = existing.first['person_id'].toString();
          final currentVisits = (existing.first['total_visits'] as int? ?? 1) + 1;
          await db.update(
            'persons',
            {
              'total_visits': currentVisits,
              'last_visit': checkInIso,
              'updated_at': DateTime.now().toIso8601String(),
            },
            where: 'person_id = ?',
            whereArgs: [personId],
          );
        }

        // Insert into Visits table
        final visitId = (row['id'] ?? row['visitor_uuid'] ?? _uuid.v4()).toString();
        final existingVisit = await db.query('visits', where: 'visit_id = ?', whereArgs: [visitId]);

        if (existingVisit.isEmpty) {
          await db.insert('visits', {
            'visit_id': visitId,
            'person_id': personId,
            'check_in': checkInIso,
            'check_out': row['time_out']?.toString(),
            'purpose': (row['purpose'] ?? 'General Darshan').toString(),
            'group_members': (row['persons_count'] as int? ?? 1),
            'notes': row['notes']?.toString(),
            'status': (row['status'] ?? 'CHECKED_IN').toString(),
            'created_at': row['created_at']?.toString() ?? DateTime.now().toIso8601String(),
            'updated_at': row['updated_at']?.toString() ?? DateTime.now().toIso8601String(),
          });
        }
      }
    }
    AppLogger.info('Relational Person + Visit Migration completed successfully.');
  }

  /// Migrate SQLite schema to Version 5 for Communication Settings & Meta Cloud API
  static Future<void> _migrateToVersion5(Database db) async {
    AppLogger.info('Migrating SQLite database to Version 5 (Communication Settings)...');

    await db.execute('''
      CREATE TABLE IF NOT EXISTS communication_settings (
        id TEXT PRIMARY KEY,
        mode TEXT NOT NULL DEFAULT 'DISABLED',
        access_token TEXT,
        phone_number_id TEXT,
        business_account_id TEXT,
        verify_token TEXT,
        auto_send INTEGER NOT NULL DEFAULT 0,
        allow_edit INTEGER NOT NULL DEFAULT 0,
        save_history INTEGER NOT NULL DEFAULT 1,
        retry_failed INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL
      )
    ''');

    final now = DateTime.now().toIso8601String();
    final existingSettings = await db.query('communication_settings');
    if (existingSettings.isEmpty) {
      await db.insert('communication_settings', {
        'id': 'comm_settings_default',
        'mode': 'DISABLED',
        'access_token': null,
        'phone_number_id': null,
        'business_account_id': null,
        'verify_token': null,
        'auto_send': 0,
        'allow_edit': 0,
        'save_history': 1,
        'retry_failed': 0,
        'updated_at': now,
      });
    }

    // Ensure title column on communication_templates
    final templateColumns = await db.rawQuery("PRAGMA table_info(communication_templates)");
    final hasTitle = templateColumns.any((col) => col['name'] == 'title');
    if (!hasTitle) {
      await db.execute("ALTER TABLE communication_templates ADD COLUMN title TEXT NOT NULL DEFAULT '';");
    }

    // Replace old CHECK_IN/CHECK_OUT templates with ENTRY/EXIT templates
    await db.delete('communication_templates', where: "template_type IN ('CHECK_IN', 'CHECK_OUT')");

    await db.insert('communication_templates', {
      'id': 'tmpl_entry',
      'template_type': 'ENTRY',
      'title': 'Visitor Entry Message',
      'message': '🙏 Welcome {name}\n\nYou have successfully entered\n{temple}\n\nEntry Time:\n{time}\n\nHave a blessed day.',
      'is_enabled': 1,
      'created_at': now,
      'updated_at': now,
    }, conflictAlgorithm: ConflictAlgorithm.ignore);

    await db.insert('communication_templates', {
      'id': 'tmpl_exit',
      'template_type': 'EXIT',
      'title': 'Visitor Exit Message',
      'message': '🙏 Thank you {name}\n\nExit Time:\n{time}\n\nVisit Duration:\n{duration}\n\nThank you for visiting\n{temple}',
      'is_enabled': 1,
      'created_at': now,
      'updated_at': now,
    }, conflictAlgorithm: ConflictAlgorithm.ignore);

    AppLogger.info('Version 5 Migration completed successfully.');
  }

  /// Migrate SQLite schema to Version 6 for Transactional Outbox & Sync Queue
  static Future<void> _migrateToVersion6(Database db) async {
    AppLogger.info('Migrating SQLite database to Version 6 (Transactional Outbox & sync_queue)...');

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

    // Backfill pending visitor registrations into sync_queue
    final legacyTables = await db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='visitors';");
    if (legacyTables.isNotEmpty) {
      final pendingVisitors = await db.query('visitors', where: "sync_status = 'PENDING' AND is_deleted = 0");
      AppLogger.info('Found ${pendingVisitors.length} pending visitors to backfill into sync_queue.');

      for (final row in pendingVisitors) {
        final uuid = (row['visitor_uuid'] ?? row['id'] ?? _uuid.v4()).toString();

        // Idempotency check: verify if outbox entry already exists
        final existing = await db.query('sync_queue', where: 'entity_id = ? AND operation = ?', whereArgs: [uuid, 'CREATE']);
        if (existing.isEmpty) {
          final nowIso = DateTime.now().toIso8601String();
          final clientTs = DateTime.now().millisecondsSinceEpoch;
          final payloadMap = {
            'visitor_uuid': uuid,
            'name': row['name'],
            'phone_number': row['phone_number'],
            'village': row['village'],
            'purpose': row['purpose'],
            'persons_count': row['persons_count'],
            'notes': row['notes'],
            'visitor_date': row['visitor_date'],
            'time_in': row['time_in'],
            'status': row['status'],
          };

          await db.insert('sync_queue', {
            'event_id': _uuid.v4(),
            'temple_id': 'TEMPLE_MAIN',
            'entity_type': 'VISITOR',
            'entity_id': uuid,
            'operation': 'CREATE',
            'payload': jsonEncode(payloadMap),
            'status': 'PENDING',
            'retry_count': 0,
            'max_retries': 10,
            'next_retry_at': null,
            'error_message': null,
            'client_timestamp': clientTs,
            'server_synced_at': null,
            'created_at': row['created_at']?.toString() ?? nowIso,
            'updated_at': nowIso,
          }, conflictAlgorithm: ConflictAlgorithm.ignore);
        }
      }
    }
    AppLogger.info('Version 6 Migration & Backfill completed successfully.');
  }

  // --- Person & Visit Operations ---

  /// Search Person by Phone for Registration Auto-Complete
  static Future<Map<String, dynamic>?> getPersonByPhone(String phone) async {
    final db = await instance;
    final results = await db.query('persons', where: 'phone = ?', whereArgs: [phone.trim()]);
    return results.isNotEmpty ? results.first : null;
  }

  static Future<Map<String, dynamic>?> getPersonById(String personId) async {
    final db = await instance;
    final results = await db.query('persons', where: 'person_id = ?', whereArgs: [personId]);
    return results.isNotEmpty ? results.first : null;
  }

  static Future<List<Map<String, dynamic>>> getVisitsForPerson(String personId) async {
    final db = await instance;
    return await db.query('visits', where: 'person_id = ?', whereArgs: [personId], orderBy: 'created_at DESC');
  }

  /// Register a Visit (Creates/Updates Person, Visit, Visitor and sync_queue event atomically in 1 transaction)
  static Future<String> registerVisit({
    required String name,
    required String phone,
    required String village,
    String? address,
    required String purpose,
    required int groupMembers,
    String? notes,
  }) async {
    final db = await instance;
    final cleanPhone = phone.trim();
    final cleanName = name.trim();
    final cleanVillage = village.trim();
    final now = DateTime.now();
    final dateStr = now.toIso8601String().split('T')[0];
    final timeStr = "${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}";
    final checkInTimestamp = "$dateStr $timeStr";
    final visitId = _uuid.v4();
    final eventId = _uuid.v4();
    final clientTs = now.millisecondsSinceEpoch;

    await db.transaction((txn) async {
      final existingPerson = await txn.query('persons', where: 'phone = ?', whereArgs: [cleanPhone]);
      String personId;

      if (existingPerson.isEmpty) {
        personId = _uuid.v4();
        await txn.insert('persons', {
          'person_id': personId,
          'name': cleanName,
          'phone': cleanPhone,
          'village': cleanVillage,
          'address': address,
          'first_visit': checkInTimestamp,
          'last_visit': checkInTimestamp,
          'total_visits': 1,
          'created_at': now.toIso8601String(),
          'updated_at': now.toIso8601String(),
        });
      } else {
        personId = existingPerson.first['person_id'].toString();
        final currentTotal = (existingPerson.first['total_visits'] as int? ?? 1) + 1;
        await txn.update(
          'persons',
          {
            'name': cleanName,
            'village': cleanVillage,
            'address': address ?? existingPerson.first['address'],
            'last_visit': checkInTimestamp,
            'total_visits': currentTotal,
            'updated_at': now.toIso8601String(),
          },
          where: 'person_id = ?',
          whereArgs: [personId],
        );
      }

      await txn.insert('visits', {
        'visit_id': visitId,
        'person_id': personId,
        'check_in': checkInTimestamp,
        'check_out': null,
        'purpose': purpose,
        'group_members': groupMembers,
        'notes': notes,
        'status': 'CHECKED_IN',
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      });

      // Mirror to legacy visitors table
      await txn.insert('visitors', {
        'id': visitId,
        'visitor_uuid': visitId,
        'name': cleanName,
        'phone_number': cleanPhone,
        'village': cleanVillage,
        'purpose': purpose,
        'persons_count': groupMembers,
        'notes': notes,
        'visitor_date': dateStr,
        'time_in': timeStr,
        'time_out': null,
        'visit_duration': null,
        'status': 'CHECKED_IN',
        'sync_status': 'PENDING',
        'is_deleted': 0,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      }, conflictAlgorithm: ConflictAlgorithm.replace);

      // Transactional Outbox Insertion
      final payloadMap = {
        'visitor_uuid': visitId,
        'person_id': personId,
        'name': cleanName,
        'phone_number': cleanPhone,
        'village': cleanVillage,
        'purpose': purpose,
        'persons_count': groupMembers,
        'notes': notes,
        'visitor_date': dateStr,
        'time_in': timeStr,
        'status': 'CHECKED_IN',
      };

      await txn.insert('sync_queue', {
        'event_id': eventId,
        'temple_id': 'TEMPLE_MAIN',
        'entity_type': 'VISITOR',
        'entity_id': visitId,
        'operation': 'CREATE',
        'payload': jsonEncode(payloadMap),
        'status': 'PENDING',
        'retry_count': 0,
        'max_retries': 10,
        'next_retry_at': null,
        'error_message': null,
        'client_timestamp': clientTs,
        'server_synced_at': null,
        'created_at': now.toIso8601String(),
        'updated_at': now.toIso8601String(),
      });
    });

    return visitId;
  }

  /// Query Visits Joined with Person Details
  static Future<List<Map<String, dynamic>>> getVisitsJoined({String? searchQuery, String? dateFilter, String? statusFilter}) async {
    final db = await instance;
    String sql = '''
      SELECT 
        v.visit_id,
        v.person_id,
        v.check_in,
        v.check_out,
        v.purpose,
        v.group_members,
        v.notes,
        v.visit_duration AS visit_duration,
        v.status,
        v.created_at,
        v.updated_at,
        p.name AS person_name,
        p.phone AS person_phone,
        p.village AS person_village,
        p.total_visits
      FROM visits v
      INNER JOIN persons p ON v.person_id = p.person_id
      WHERE 1=1
    ''';

    List<dynamic> args = [];

    if (dateFilter != null && dateFilter.isNotEmpty) {
      sql += ' AND v.check_in LIKE ?';
      args.add('$dateFilter%');
    }

    if (statusFilter != null && statusFilter != 'ALL') {
      String sqlStatus = statusFilter;
      if (statusFilter == 'INSIDE') sqlStatus = 'CHECKED_IN';
      if (statusFilter == 'COMPLETED') sqlStatus = 'CHECKED_OUT';
      sql += ' AND v.status = ?';
      args.add(sqlStatus);
    }

    if (searchQuery != null && searchQuery.isNotEmpty) {
      sql += ' AND (p.name LIKE ? OR p.phone LIKE ? OR p.village LIKE ?)';
      final pattern = '%$searchQuery%';
      args.addAll([pattern, pattern, pattern]);
    }

    sql += ' ORDER BY v.created_at DESC';

    return await db.rawQuery(sql, args);
  }

  static Future<int> checkOutVisit(String visitId, String checkOutTime, String duration) async {
    final db = await instance;
    final now = DateTime.now();
    final nowIso = now.toIso8601String();
    final clientTs = now.millisecondsSinceEpoch;
    int affected = 0;

    await db.transaction((txn) async {
      // Update visits table
      await txn.update(
        'visits',
        {
          'check_out': checkOutTime,
          'visit_duration': duration,
          'status': 'CHECKED_OUT',
          'updated_at': nowIso,
        },
        where: 'visit_id = ?',
        whereArgs: [visitId],
      );

      // Update legacy visitors table
      affected = await txn.update(
        'visitors',
        {
          'time_out': checkOutTime,
          'visit_duration': duration,
          'status': 'CHECKED_OUT',
          'updated_at': nowIso,
        },
        where: 'id = ? OR visitor_uuid = ?',
        whereArgs: [visitId, visitId],
      );

      // Insert Checkout Outbox Event
      final outboxPayload = {
        'visit_id': visitId,
        'check_out': checkOutTime,
        'visit_duration': duration,
        'status': 'CHECKED_OUT',
      };

      await txn.insert('sync_queue', {
        'event_id': _uuid.v4(),
        'temple_id': 'TEMPLE_MAIN',
        'entity_type': 'VISITOR',
        'entity_id': visitId,
        'operation': 'CHECKOUT',
        'payload': jsonEncode(outboxPayload),
        'status': 'PENDING',
        'retry_count': 0,
        'max_retries': 10,
        'next_retry_at': null,
        'error_message': null,
        'client_timestamp': clientTs,
        'server_synced_at': null,
        'created_at': nowIso,
        'updated_at': nowIso,
      });
    });

    return affected;
  }

  // --- Local SQLite Authentication Operations ---
  static Future<Map<String, dynamic>?> getUserByUsername(String username) async {
    final db = await instance;
    final results = await db.query('users', where: 'username = ?', whereArgs: [username]);
    return results.isNotEmpty ? results.first : null;
  }

  // --- Parameterized Legacy Visitor Operations ---
  static Future<int> insertVisitor(Map<String, dynamic> row) async {
    final db = await instance;
    return await db.insert('visitors', row, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  static Future<List<Map<String, dynamic>>> getVisitors({String? searchQuery, String? dateFilter}) async {
    final db = await instance;
    String whereClause = 'is_deleted = 0';
    List<dynamic> whereArgs = [];

    if (dateFilter != null && dateFilter.isNotEmpty) {
      whereClause += ' AND visitor_date = ?';
      whereArgs.add(dateFilter);
    }

    if (searchQuery != null && searchQuery.isNotEmpty) {
      whereClause += ' AND (name LIKE ? OR phone_number LIKE ? OR village LIKE ?)';
      final pattern = '%$searchQuery%';
      whereArgs.addAll([pattern, pattern, pattern]);
    }

    return await db.query('visitors', where: whereClause, whereArgs: whereArgs, orderBy: 'created_at DESC');
  }

  static Future<List<Map<String, dynamic>>> getPendingSyncVisitors() async {
    final db = await instance;
    return await db.query('visitors', where: "sync_status = 'PENDING' AND is_deleted = 0");
  }

  static Future<int> updateSyncStatus(String uuid, String status) async {
    final db = await instance;
    return await db.update(
      'visitors',
      {'sync_status': status, 'updated_at': DateTime.now().toIso8601String()},
      where: 'visitor_uuid = ? OR id = ?',
      whereArgs: [uuid, uuid],
    );
  }

  static Future<int> checkOutVisitor(String id, String timeOut, String duration) async {
    return await checkOutVisit(id, timeOut, duration);
  }

  static Future<Map<String, dynamic>?> getVisitorById(String id) async {
    final db = await instance;
    final results = await db.query('visitors', where: 'id = ? OR visitor_uuid = ?', whereArgs: [id, id]);
    if (results.isNotEmpty) return results.first;

    final joined = await db.rawQuery('''
      SELECT 
        v.visit_id AS id,
        v.visit_id AS visitor_uuid,
        p.name AS name,
        p.phone AS phone_number,
        p.village AS village,
        v.purpose AS purpose,
        v.group_members AS persons_count,
        v.notes AS notes,
        v.check_in AS visitor_date,
        v.check_in AS time_in,
        v.check_out AS time_out,
        v.visit_duration AS visit_duration,
        v.status AS status
      FROM visits v
      INNER JOIN persons p ON v.person_id = p.person_id
      WHERE v.visit_id = ?
    ''', [id]);

    return joined.isNotEmpty ? joined.first : null;
  }

  // --- Communication & Template Operations ---
  static Future<Map<String, dynamic>> getCommunicationSettings() async {
    final db = await instance;
    final results = await db.query('communication_settings');
    if (results.isNotEmpty) return results.first;
    final defaultMap = {
      'id': 'comm_settings_default',
      'mode': 'DISABLED',
      'access_token': null,
      'phone_number_id': null,
      'business_account_id': null,
      'verify_token': null,
      'auto_send': 0,
      'allow_edit': 0,
      'save_history': 1,
      'retry_failed': 0,
      'updated_at': DateTime.now().toIso8601String(),
    };
    await db.insert('communication_settings', defaultMap, conflictAlgorithm: ConflictAlgorithm.replace);
    return defaultMap;
  }

  static Future<int> saveCommunicationSettings(Map<String, dynamic> settings) async {
    final db = await instance;
    settings['updated_at'] = DateTime.now().toIso8601String();
    return await db.insert('communication_settings', settings, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  static Future<Map<String, dynamic>?> getTemplate(String type) async {
    final db = await instance;
    final results = await db.query('communication_templates', where: 'template_type = ?', whereArgs: [type]);
    return results.isNotEmpty ? results.first : null;
  }

  static Future<int> saveMessageTemplate(Map<String, dynamic> template) async {
    final db = await instance;
    template['updated_at'] = DateTime.now().toIso8601String();
    return await db.insert('communication_templates', template, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  static Future<Map<String, dynamic>> getTempleInfo() async {
    final db = await instance;
    final results = await db.query('temple_info');
    if (results.isNotEmpty) return results.first;
    return {
      'temple_name': 'Sri Kalki Seva Alayam',
      'website': 'https://kalkiseva.org',
      'google_maps_link': 'https://maps.google.com/?q=Kalki+Temple',
      'donation_link': 'https://kalkiseva.org/donate',
      'facebook': 'https://facebook.com/kalkiseva',
      'instagram': 'https://instagram.com/kalkiseva',
      'youtube': 'https://youtube.com/kalkiseva',
      'temple_phone': '+91 98765 43210',
      'temple_address': 'Sacred Complex, Kalki Nagaram, Chittoor, AP 517001',
    };
  }

  static Future<String> getActiveActivities() async {
    final db = await instance;
    final results = await db.query('today_activities', where: 'is_active = 1');
    if (results.isEmpty) return 'Special Darshan & Prasadam';
    return results.map((r) => r['title'].toString()).join(', ');
  }

  static Future<String> getActiveFestival() async {
    final db = await instance;
    final results = await db.query('festival_info', where: 'enabled = 1');
    if (results.isEmpty) return 'Sri Kalki Seva Utsav';
    return results.first['festival_name'].toString();
  }

  static Future<int> insertCommunicationHistory(Map<String, dynamic> row) async {
    final db = await instance;
    return await db.insert('communication_history', row);
  }

  static Future<List<Map<String, dynamic>>> getCommunicationHistoryByVisitor(String visitorId) async {
    final db = await instance;
    return await db.query(
      'communication_history',
      where: 'visitor_id = ?',
      whereArgs: [visitorId],
      orderBy: 'created_at DESC',
    );
  }

  static Future<String> getDatabaseFilePath() async {
    final dbPath = await getDatabasesPath();
    return join(dbPath, 'temple_visitors_prod_v1.db');
  }

  static Future<String> exportDatabase(String targetPath) async {
    final currentDbPath = await getDatabaseFilePath();
    final sourceFile = File(currentDbPath);
    if (!await sourceFile.exists()) {
      throw Exception('Database file does not exist at $currentDbPath');
    }

    if (_database != null && _database!.isOpen) {
      await _database!.close();
      _database = null;
    }

    final targetFile = await sourceFile.copy(targetPath);
    AppLogger.info('Database exported successfully to ${targetFile.path}');
    return targetFile.path;
  }

  static Future<bool> importDatabase(String sourcePath) async {
    final newDbFile = File(sourcePath);
    if (!await newDbFile.exists()) {
      throw Exception('Backup file does not exist at $sourcePath');
    }

    if (_database != null && _database!.isOpen) {
      await _database!.close();
      _database = null;
    }

    final currentDbPath = await getDatabaseFilePath();
    await newDbFile.copy(currentDbPath);

    _database = await _initDB();
    AppLogger.info('Database imported & re-initialized successfully from $sourcePath');
    return true;
  }

  // --- Transactional Outbox Sync Queue Operations ---

  /// Get pending count of sync_queue events
  static Future<int> getPendingSyncQueueCount() async {
    final db = await instance;
    final result = await db.rawQuery(
      "SELECT COUNT(*) as count FROM sync_queue WHERE status IN ('PENDING', 'FAILED') AND (next_retry_at IS NULL OR next_retry_at <= ?)",
      [DateTime.now().millisecondsSinceEpoch ~/ 1000],
    );
    return Sqflite.firstIntValue(result) ?? 0;
  }

  /// Get sync queue events pending transmission
  static Future<List<Map<String, dynamic>>> getSyncQueueItems({String status = 'PENDING', int limit = 100}) async {
    final db = await instance;
    return await db.query(
      'sync_queue',
      where: 'status = ?',
      whereArgs: [status],
      orderBy: 'client_timestamp ASC',
      limit: limit,
    );
  }

  /// Insert raw sync_queue event (used for direct event enqueueing)
  static Future<int> insertSyncQueueEvent(Map<String, dynamic> row) async {
    final db = await instance;
    return await db.insert('sync_queue', row, conflictAlgorithm: ConflictAlgorithm.ignore);
  }

  /// Update sync_queue status, retry count, and next retry timestamp
  static Future<int> updateSyncQueueStatus(
    String eventId,
    String status, {
    String? errorMessage,
    int? nextRetryAt,
  }) async {
    final db = await instance;
    final nowIso = DateTime.now().toIso8601String();
    final Map<String, dynamic> updateValues = {
      'status': status,
      'updated_at': nowIso,
    };

    if (status == 'SUCCESS') {
      updateValues['server_synced_at'] = DateTime.now().millisecondsSinceEpoch;
    }
    if (errorMessage != null) {
      updateValues['error_message'] = errorMessage;
    }
    if (nextRetryAt != null) {
      updateValues['next_retry_at'] = nextRetryAt;
    }

    return await db.update(
      'sync_queue',
      updateValues,
      where: 'event_id = ?',
      whereArgs: [eventId],
    );
  }
}
