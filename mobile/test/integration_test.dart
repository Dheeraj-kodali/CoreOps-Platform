import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/core/services/communication_service.dart';
import 'package:temple_visitor_app/models/communication_models.dart';
import 'package:uuid/uuid.dart';

void main() {
  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  group('Temple Visitor End-to-End Automated Integration Suite', () {
    final repository = VisitorRepository();
    final commService = CommunicationService();
    final uniqueId = const Uuid().v4().substring(0, 6);

    test('1. Visitor Registration & Repeat Visitor Lookup', () async {
      final phone = '98765$uniqueId';
      
      // Register New Visitor
      final v1 = await repository.registerVisitor(
        name: 'Ramesh Kumar',
        phoneNumber: phone,
        village: 'Tirupati',
        purpose: 'Special Archana',
        personsCount: 4,
        notes: 'VIP Seva',
      );

      expect(v1.name, 'Ramesh Kumar');
      expect(v1.personsCount, 4);
      expect(v1.status, 'CHECKED_IN');

      // Verify Database Person & Visit Records
      final personMap = await SQLiteDatabase.getPersonByPhone(phone);
      expect(personMap, isNotNull);
      expect(personMap!['name'], 'Ramesh Kumar');
      expect(personMap['village'], 'Tirupati');
      expect(personMap['total_visits'], 1);

      // Register Repeat Visit for Same Phone Number
      final v2 = await repository.registerVisitor(
        name: 'Ramesh Kumar',
        phoneNumber: phone,
        village: 'Tirupati',
        purpose: 'Annadanam',
        personsCount: 2,
      );

      expect(v2.name, 'Ramesh Kumar');
      expect(v2.purpose, 'Annadanam');

      final personMapUpdated = await SQLiteDatabase.getPersonByPhone(phone);
      expect(personMapUpdated!['total_visits'], 2);
    });

    test('2. Visitor Checkout ("Visitor Left") & Duration Calculation', () async {
      final phone = '91234$uniqueId';
      final v = await repository.registerVisitor(
        name: 'Sita Devi',
        phoneNumber: phone,
        village: 'Chittoor',
        purpose: 'General Darshan',
        personsCount: 3,
      );

      final checkedOut = await repository.checkOutVisitor(v.id);
      expect(checkedOut, isNotNull);
      expect(checkedOut!.status, 'CHECKED_OUT');
      expect(checkedOut.displayStatus, 'Completed');
      expect(checkedOut.timeOut, isNotNull);
      expect(checkedOut.formattedDuration, isNot('null'));
      expect(checkedOut.formattedDuration.contains('min'), isTrue);
    });

    test('3. Dashboard Statistics Real-Time Aggregation', () async {
      final stats = await repository.getTodayStatistics();
      expect(stats.containsKey('total_records'), isTrue);
      expect(stats.containsKey('total_visitors'), isTrue);
      expect(stats.containsKey('visitors_inside'), isTrue);
      expect(stats.containsKey('visitors_left'), isTrue);
      expect(stats.containsKey('avg_duration_str'), isTrue);
      expect(stats.containsKey('top_purpose'), isTrue);

      final totalRecords = stats['total_records'] as int;
      final totalMembers = stats['total_visitors'] as int;
      expect(totalMembers >= totalRecords, isTrue);
    });

    test('4. Reports & Date Range Filtering', () async {
      final todayList = await repository.getFilteredVisitors(filterType: 'TODAY');
      final allList = await repository.getFilteredVisitors(filterType: 'CUSTOM');

      expect(todayList, isNotNull);
      expect(allList, isNotNull);
      expect(allList.length >= todayList.length, isTrue);
    });

    test('5. Communication Settings Persistence & Defaults', () async {
      final settings = await commService.getSettings();
      expect(settings.mode, isNotNull);
      expect(settings.autoSend, isNotNull);

      final updated = CommunicationSettings(
        id: 'comm_settings_default',
        mode: 'META_CLOUD_API',
        accessToken: 'EAAG12345TESTTOKEN',
        phoneNumberId: '1290699690788322',
        businessAccountId: '26770219812654236',
        autoSend: true,
        allowEdit: true,
        saveHistory: true,
        retryFailed: true,
        updatedAt: DateTime.now().toIso8601String(),
      );

      await commService.saveSettings(updated);

      final reloaded = await commService.getSettings();
      expect(reloaded.mode, 'META_CLOUD_API');
      expect(reloaded.accessToken, 'EAAG12345TESTTOKEN');
      expect(reloaded.phoneNumberId, '1290699690788322');
      expect(reloaded.businessAccountId, '26770219812654236');
      expect(reloaded.autoSend, isTrue);
    });

    test('6. Template Persistence & Save', () async {
      final now = DateTime.now().toIso8601String();
      await SQLiteDatabase.saveMessageTemplate({
        'id': 'tmpl_entry',
        'template_type': 'ENTRY',
        'title': 'Visitor Entry Message',
        'message': 'Welcome {name} to {temple}',
        'is_enabled': 1,
        'created_at': now,
        'updated_at': now,
      });

      final entryTemplate = await SQLiteDatabase.getTemplate('ENTRY');
      expect(entryTemplate, isNotNull);
      expect(entryTemplate!['message'].toString().contains('{name}'), isTrue);
    });

    test('7. Database Path Access & Integrity', () async {
      final path = await SQLiteDatabase.getDatabaseFilePath();
      expect(path, isNotEmpty);
      expect(path.contains('temple_visitors_prod_v1.db'), isTrue);
    });
  });
}
